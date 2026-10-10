"""Provider-agnostic tool-calling chat clients, standard library only.

The loop speaks one neutral transcript format; each client converts it to its
provider's wire format. Transcript entries:

    {"role": "user", "text": str}
    {"role": "assistant", "text": str, "calls": [ToolCall, ...]}
    {"role": "tool", "results": [{"id": str, "name": str, "content": str}, ...]}

Only transport problems are retried (timeouts, 429, 5xx). Anything else raises
and the runner turns it into a fallback escalation.
"""

from __future__ import annotations

import json
import os
import random
import socket
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from email.utils import parsedate_to_datetime
from typing import Any, Dict, List, Optional

from agent.config import Config


@dataclass(frozen=True)
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]
    raw_arguments: str = ""  # kept when the provider sent arguments that are not valid JSON


@dataclass
class Turn:
    text: str = ""
    calls: List[ToolCall] = field(default_factory=list)
    tokens: int = 0


class ChatError(RuntimeError):
    pass


class ChatBackend:
    name = "chat"
    model = ""

    def chat(self, system: str, transcript: List[Dict[str, Any]], tools: List[Dict[str, Any]]) -> Turn:
        raise NotImplementedError


def retry_delay(attempt: int, retry_after: Optional[str], cfg: Config) -> float:
    """Seconds to wait before the next attempt: the server's retry-after when given, else backoff with jitter."""
    if retry_after:
        try:
            return min(max(0.0, float(retry_after)), cfg.retry_after_cap_s)
        except ValueError:
            try:
                when = parsedate_to_datetime(retry_after)
                return min(max(0.0, when.timestamp() - time.time()), cfg.retry_after_cap_s)
            except (TypeError, ValueError, OverflowError):
                pass
    # Jitter spreads retries out, so parallel cases that hit the same rate limit do not retry in step.
    return min(2 ** attempt, 8) * (0.5 + random.random() / 2)


def _post(url: str, headers: Dict[str, str], body: Dict[str, Any], cfg: Config) -> Dict[str, Any]:
    data = json.dumps(body).encode("utf-8")
    attempt = 0
    while True:
        req = urllib.request.Request(url, data=data, headers={"content-type": "application/json", **headers})
        retry_after = None
        try:
            with urllib.request.urlopen(req, timeout=cfg.call_timeout_s) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
            retryable = exc.code in (408, 429) or exc.code >= 500  # 529: Anthropic is overloaded
            if not retryable or attempt >= cfg.max_retries:
                raise ChatError("HTTP %d from model provider: %s" % (exc.code, detail))
            retry_after = exc.headers.get("retry-after") if exc.headers else None
        except (urllib.error.URLError, socket.timeout, TimeoutError, ConnectionError) as exc:
            if attempt >= cfg.max_retries:
                raise ChatError("model provider unreachable: %s" % exc)
        time.sleep(retry_delay(attempt, retry_after, cfg))
        attempt += 1


def _parse_args(raw: Any) -> Dict[str, Any]:
    if isinstance(raw, dict):
        return raw
    try:
        value = json.loads(raw or "{}")
    except (TypeError, ValueError):
        return {}
    return value if isinstance(value, dict) else {}


class OpenAIChat(ChatBackend):
    name = "openai"

    def __init__(self, cfg: Config) -> None:
        self.key = os.environ.get("OPENAI_API_KEY", "")
        if not self.key:
            raise RuntimeError("OPENAI_API_KEY is not set")
        self.model = os.environ.get("OPENAI_MODEL") or cfg.openai_model
        self.url = (os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1").rstrip("/") + "/chat/completions"
        self.cfg = cfg

    def _messages(self, system: str, transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = [{"role": "system", "content": system}]
        for entry in transcript:
            if entry["role"] == "user":
                out.append({"role": "user", "content": entry["text"]})
            elif entry["role"] == "assistant":
                msg: Dict[str, Any] = {"role": "assistant", "content": entry.get("text") or None}
                if entry.get("calls"):
                    msg["tool_calls"] = [
                        {"id": c.id, "type": "function",
                         "function": {"name": c.name, "arguments": c.raw_arguments or json.dumps(c.arguments)}}
                        for c in entry["calls"]
                    ]
                out.append(msg)
            else:
                for r in entry["results"]:
                    out.append({"role": "tool", "tool_call_id": r["id"], "content": r["content"]})
        return out

    def chat(self, system, transcript, tools):
        body = {
            "model": self.model,
            "messages": self._messages(system, transcript),
            "tools": [{"type": "function", "function": {"name": t["name"], "description": t["description"],
                                                        "parameters": t["parameters"]}} for t in tools],
            "tool_choice": "required",
            "max_completion_tokens": self.cfg.loop_max_tokens_per_turn,
        }
        data = _post(self.url, {"authorization": "Bearer %s" % self.key}, body, self.cfg)
        try:
            msg = data["choices"][0]["message"]
        except (KeyError, IndexError, TypeError):
            raise ChatError("unexpected OpenAI response shape")
        calls = [
            ToolCall(id=c["id"], name=c["function"]["name"], arguments=_parse_args(c["function"].get("arguments")),
                     raw_arguments=c["function"].get("arguments") or "")
            for c in (msg.get("tool_calls") or [])
        ]
        return Turn(text=msg.get("content") or "", calls=calls, tokens=int((data.get("usage") or {}).get("total_tokens", 0)))


class AnthropicChat(ChatBackend):
    name = "anthropic"

    def __init__(self, cfg: Config) -> None:
        self.key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not self.key:
            raise RuntimeError("ANTHROPIC_API_KEY is not set")
        self.model = os.environ.get("ANTHROPIC_MODEL") or cfg.model
        self.url = (os.environ.get("ANTHROPIC_BASE_URL") or "https://api.anthropic.com").rstrip("/") + "/v1/messages"
        self.cfg = cfg

    @staticmethod
    def _messages(transcript: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for entry in transcript:
            if entry["role"] == "user":
                images = entry.get("images") or []
                if images:
                    blocks: List[Dict[str, Any]] = [{"type": "text", "text": entry.get("text") or ""}]
                    for img in images:
                        blocks.append({"type": "image", "source": {
                            "type": "base64", "media_type": img["media_type"], "data": img["data"]}})
                    out.append({"role": "user", "content": blocks})
                else:
                    out.append({"role": "user", "content": entry["text"]})
            elif entry["role"] == "assistant":
                blocks: List[Dict[str, Any]] = []
                if entry.get("text"):
                    blocks.append({"type": "text", "text": entry["text"]})
                blocks += [{"type": "tool_use", "id": c.id, "name": c.name, "input": c.arguments} for c in entry.get("calls", [])]
                out.append({"role": "assistant", "content": blocks or [{"type": "text", "text": "(no output)"}]})
            else:
                out.append({"role": "user", "content": [
                    {"type": "tool_result", "tool_use_id": r["id"], "content": r["content"]} for r in entry["results"]]})
        return out

    @staticmethod
    def _mark_cache(messages: List[Dict[str, Any]]) -> None:
        """Cache the conversation so far, so the next turn re-reads it instead of paying for it again."""
        if not messages:
            return
        last = messages[-1]
        if isinstance(last["content"], str):
            last["content"] = [{"type": "text", "text": last["content"]}]
        last["content"][-1]["cache_control"] = {"type": "ephemeral"}

    def chat(self, system, transcript, tools):
        messages = self._messages(transcript)
        self._mark_cache(messages)
        body = {
            "model": self.model,
            "max_tokens": self.cfg.loop_max_tokens_per_turn,
            # Tools and this system block form the cached prefix; it must not contain per-case text.
            "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
            "messages": messages,
            "tools": [{"name": t["name"], "description": t["description"], "input_schema": t["parameters"]} for t in tools],
            "tool_choice": {"type": "auto"},
        }
        headers = {"x-api-key": self.key, "anthropic-version": "2023-06-01"}
        data = _post(self.url, headers, body, self.cfg)
        text, calls = [], []
        for block in data.get("content") or []:
            if block.get("type") == "text":
                text.append(block.get("text", ""))
            elif block.get("type") == "tool_use":
                calls.append(ToolCall(id=block["id"], name=block["name"], arguments=_parse_args(block.get("input"))))
        usage = data.get("usage") or {}
        tokens = sum(int(usage.get(k) or 0) for k in (
            "input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"))
        return Turn(text="\n".join(text), calls=calls, tokens=tokens)


class ScriptedChat(ChatBackend):
    """Replays a fixed list of turns; used by tests and the offline demo."""
    name = "scripted"
    model = "scripted"

    def __init__(self, turns: List[Turn]) -> None:
        self.turns = list(turns)
        self.seen: List[List[Dict[str, Any]]] = []

    def chat(self, system, transcript, tools):
        self.seen.append(list(transcript))
        if not self.turns:
            return Turn(text="(script exhausted)")
        return self.turns.pop(0)


def make_chat(name: str, cfg: Config) -> ChatBackend:
    """auto picks Anthropic when its key is present, else OpenAI. Only used when asked for by name."""
    if name == "auto":
        name = "anthropic" if os.environ.get("ANTHROPIC_API_KEY") else "openai"
    if name in ("anthropic", "claude"):
        return AnthropicChat(cfg)
    if name == "openai":
        return OpenAIChat(cfg)
    raise ValueError("unknown chat backend %r" % name)
