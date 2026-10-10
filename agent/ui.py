"""python3 -m agent ui OUT_DIR: a local page over a run's decision.json files.

Read-only apart from review.json, where a person's choice for a case is recorded.
"""

from __future__ import annotations

import json
import re
import threading
import webbrowser
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Optional
from urllib.parse import unquote, urlparse

from agent import call_results
from agent.files import atomic_write

STATIC_DIR = Path(__file__).parent / "ui_static"
MAX_BODY = 16 * 1024
MAX_FILE = 8 * 1024 * 1024
MAX_TEXT = 2000
REVIEW_CHOICES = ("option", "take_over", "new_case")
ALLOWED_HOSTS = ("127.0.0.1", "localhost")
CSP = ("default-src 'self'; style-src 'self' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "img-src 'self' data:; object-src 'none'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'")

ACTION_LABELS = {
    "WAIT": "Wait, nothing to do yet",
    "CHASE_LANDLORD": "Chase the landlord",
    "CHASE_PROVIDER": "Chase the provider",
    "ASK_TENANT": "Ask the tenant",
    "ASK_PROVIDER": "Ask the provider",
    "ASK_LANDLORD": "Ask the landlord",
    "ROUTE_FOR_APPROVAL": "Route the quote for approval",
    "INSTRUCT_PROVIDER": "Instruct the provider",
    "SEND_REMINDER": "Send a reminder",
    "CLOSE": "Close the case",
    "ESCALATE": "Escalate to a person",
}
_PRIORITY_RANK = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
_REF = re.compile(r"(event-\d{3}(?:/\d{3})*)")
_ITEMS = re.compile(r"^(\d+) item")
_review_lock = threading.Lock()


def _read_json(path: Path, limit: int = MAX_FILE):
    try:
        if path.stat().st_size > limit:
            return None
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def _dict(value) -> dict:
    return value if isinstance(value, dict) else {}


def _real_child(out: Path, d: Path) -> bool:
    """A real folder directly inside OUT_DIR holding a real decision.json (no symlinks anywhere)."""
    dec = d / "decision.json"
    return (not d.is_symlink() and d.is_dir() and d.resolve().parent == out.resolve()
            and not dec.is_symlink() and dec.is_file())


def case_dir(out: Path, cid: str) -> Optional[Path]:
    """The folder for a case id, only if it is a direct child of OUT_DIR with a decision.json."""
    if not cid or cid in (".", "..") or "/" in cid or "\\" in cid or "\x00" in cid:
        return None
    d = out / cid
    return d if _real_child(out, d) else None


def _case_seconds(out: Path) -> dict:
    """Seconds per case from the latest trace.jsonl row for it."""
    secs = {}
    try:
        lines = (out / "trace.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return secs
    for line in lines:
        try:
            row = json.loads(line)
        except ValueError:
            continue
        if isinstance(row, dict) and row.get("case_id") is not None and row.get("seconds") is not None:
            secs[str(row["case_id"])] = row["seconds"]
    return secs


def _sort_key(row: dict):
    return (0 if row["action"] == "ESCALATE" else 1, _PRIORITY_RANK.get(row["priority"] or "", 9), row["id"])


def list_cases(out: Path) -> dict:
    cases = []
    for d in sorted(p for p in out.iterdir() if _real_child(out, p)) if out.is_dir() else []:
        dec = _read_json(d / "decision.json")
        if not isinstance(dec, dict):
            cases.append({"id": d.name, "title": "", "priority": None, "action": None, "source": None,
                          "hazard": False, "unreadable": True})
            continue
        cases.append({"id": d.name, "title": dec.get("title") or "", "priority": dec.get("priority"),
                      "action": dec.get("action"), "source": dec.get("source"), "hazard": bool(dec.get("hazard"))})
    cases.sort(key=_sort_key)
    summary = _read_json(out / "summary.json")
    return {"out_dir": str(out), "summary": summary if isinstance(summary, dict) else None, "cases": cases}


def _items(value) -> str:
    m = _ITEMS.match(str(value or ""))
    return m.group(1) if m else ""


def _plural(n: str, word: str) -> str:
    return "%s %s%s" % (n, word, "" if n == "1" else "s")


def step_summary(step: dict) -> str:
    """One short line describing a tool call, as in the Reasoning column."""
    tool, args, res = step.get("tool"), _dict(step.get("args")), _dict(step.get("result"))
    if tool == "read_events":
        first, last = args.get("first"), args.get("last")
        text = "event %s" % first if first == last else "events %s–%s" % (first, last)
        n = _items(res.get("events"))
        text += " · " + _plural(n, "item") if n else ""
    elif tool == "search_case":
        n = _items(res.get("hits"))
        text = "“%s”" % args.get("query", "") + (" · " + _plural(n, "hit") if n else "")
    elif tool == "check_policy":
        text = ", ".join(t.strip() for t in str(args.get("topic", "")).split(",") if t.strip())
    elif tool == "read_attachment":
        text = str(args.get("name", ""))
    elif tool == "read_case_file":
        text = str(args.get("path", ""))
    elif tool == "escalate_to_human":
        text = "%s → %s" % (args.get("priority", "?"), args.get("route", "?"))
    elif tool == "submit_decision":
        conf = args.get("confidence")
        text = " · ".join(str(x) for x in (args.get("action"), args.get("priority"),
                                            "conf %.2f" % conf if isinstance(conf, (int, float)) else None) if x)
    elif tool == "schedule_followup":
        text = "%s h · waiting on %s" % (args.get("after_hours", "?"), args.get("waiting_on", "?"))
    elif tool == "send_message":
        text = "to %s · %s" % (args.get("to", "?"), args.get("purpose", "?"))
    elif tool == "place_call":
        text = "%s · %s" % (args.get("party", "?"), args.get("purpose", "?"))
    elif tool == "route_for_approval":
        amount = args.get("amount_gbp")
        text = ("GBP %.2f" % amount if isinstance(amount, (int, float)) else "GBP ?") + " · " + str(args.get("scope", ""))
    elif tool == "close_case":
        text = "invoice %s · keys %s" % (args.get("invoice_status", "?"), args.get("keys_status", "?"))
    elif tool == "consistency_check":
        checks = res.get("checks")
        text = ", ".join(str(c) for c in checks) if isinstance(checks, list) and checks else "no differences"
    elif not args:
        text = "—"
    else:
        text = json.dumps(args, ensure_ascii=False)
        text = text if len(text) <= 120 else text[:119] + "…"
    note = res.get("why") or res.get("error")
    return text + (" — " + str(note) if note else "") if text else (str(note) if note else "—")


def split_refs(text: str) -> list:
    return [{"t": part, "ref": bool(_REF.fullmatch(part))} for part in _REF.split(text or "") if part]


def _review(d: Path) -> dict:
    data = _read_json(d / "review.json")
    entries = data.get("entries") if isinstance(data, dict) and isinstance(data.get("entries"), list) else []
    latest = next((e for e in reversed(entries) if isinstance(e, dict) and e.get("choice") in ("option", "take_over")), None)
    new_cases = [e.get("text") for e in entries if isinstance(e, dict) and e.get("choice") == "new_case"]
    return {"latest": latest, "new_cases": new_cases}


class UnreadableCase(Exception):
    pass


_LIST_FIELDS = ("unknowns", "options", "evidence_refs", "unrelated_issues", "gate_notes", "warnings", "actions", "blocked",
                "trace", "red_flags")
_TEXT_FIELDS = ("reason", "title", "request", "message", "model", "as_of", "decided_at", "answer")
_PROPERTY_LINE = re.compile(r"^Property:\s*(.+?)\s*\(index\)\s*$")


_CALL_TEXT = ("id", "party", "purpose", "priority", "number", "state", "call_status", "conversation_id", "placed_at", "objective", "detail")


def _scalar(value, limit: int = 500):
    return value if value is None or isinstance(value, (int, float)) and not isinstance(value, bool) else str(value)[:limit]


def _clean_call_result(r) -> Optional[dict]:
    if not isinstance(r, dict):
        return None
    out = {"status": _scalar(r.get("status")), "success": _scalar(r.get("success")), "summary": _scalar(r.get("summary"), 1500),
           "outcome": _scalar(r.get("outcome")), "decisions": call_results.decisions_from(r.get("decisions")),
           "duration_s": r.get("duration_s") if isinstance(r.get("duration_s"), (int, float)) and not isinstance(r.get("duration_s"), bool) else None,
           "record": _scalar(r.get("record"))}
    out.update(call_results.transcript_from(r.get("transcript")))
    return out


def _clean_calls(dec: dict) -> list:
    """decision["calls"] with every field forced to a known type (it is shown by the page), derived from the actions
    when an older decision.json has none."""
    raw = dec.get("calls")
    entries = raw if isinstance(raw, list) and raw else call_results.call_entries(dec.get("actions"))
    out = []
    for e in entries:
        if not isinstance(e, dict):
            continue
        clean = {k: _scalar(e.get(k)) for k in _CALL_TEXT}
        clean["dry_run"] = bool(e.get("dry_run"))
        clean["result"] = _clean_call_result(e.get("result"))
        out.append(clean)
        if len(out) == 10:
            break
    return out


def _load_decision(d: Path) -> dict:
    """decision.json with list and text fields forced to the right type, so a hand-edited file cannot break the page."""
    dec = _read_json(d / "decision.json")
    if not isinstance(dec, dict):
        raise UnreadableCase("decision.json could not be read (half-written, not UTF-8, not JSON or over %d MB)"
                             % (MAX_FILE // (1024 * 1024)))
    for k in _LIST_FIELDS:
        dec[k] = dec[k] if isinstance(dec.get(k), list) else []
    for k in ("unknowns", "options", "evidence_refs", "unrelated_issues", "gate_notes", "warnings"):
        dec[k] = [str(x) for x in dec[k]]
    for k in ("actions", "blocked", "trace", "red_flags"):
        dec[k] = [x for x in dec[k] if isinstance(x, dict)]
    for k in _TEXT_FIELDS:
        dec[k] = dec[k] if isinstance(dec.get(k), str) else ""
    dec["calls"] = _clean_calls(dec)
    return dec


def _strings(value) -> list:
    return [str(x) for x in value if str(x).strip()] if isinstance(value, list) else []


def _text(value) -> str:
    return value if isinstance(value, str) else ""


def _conflicts(value) -> list:
    out = []
    for c in value if isinstance(value, list) else []:
        if not isinstance(c, dict):
            continue
        values = [{"value": str(v.get("value", "")), "refs": _strings(v.get("refs"))}
                  for v in c.get("values") or [] if isinstance(v, dict)]
        out.append({"field": str(c.get("field") or ""), "values": values})
    return out


def _escalation_view(ticket: Optional[dict]) -> Optional[dict]:
    """The handover ticket with every field forced to the type the page expects."""
    if not ticket:
        return None
    return {
        "priority": _text(ticket.get("priority")), "route": _text(ticket.get("route")), "state": _text(ticket.get("state")),
        "respond_by": _text(ticket.get("respond_by")), "summary": _text(ticket.get("summary")),
        "recommended": _text(ticket.get("recommended")), "known": _strings(ticket.get("known")),
        "tried": _strings(ticket.get("tried")), "failed": _strings(ticket.get("failed")),
        "conflicts": _conflicts(ticket.get("conflicts")),
    }


def _flags_view(flags: list) -> list:
    keys = ("category", "ref", "excerpt", "guidance", "route", "priority")
    return [{**{k: _text(f.get(k)) for k in keys}, "force": f.get("force") is True} for f in flags]


def _property(dec: dict, ticket: Optional[dict]) -> str:
    """details.property.address, or the 'Property: … (index)' line handover adds, for runs written before details existed."""
    address = _dict(_dict(dec.get("details")).get("property")).get("address")
    if isinstance(address, str) and address.strip():
        return address
    for line in _strings((ticket or {}).get("known")):
        m = _PROPERTY_LINE.match(line)
        if m:
            return m.group(1)
    return ""


def case_view(out: Path, cid: str) -> Optional[dict]:
    """None for an unknown case id; raises UnreadableCase when decision.json exists but cannot be read."""
    d = case_dir(out, cid)
    if d is None:
        return None
    dec = _load_decision(d)
    trace, actions = dec["trace"], dec["actions"]
    submit = next((t for t in reversed(trace) if t.get("tool") == "submit_decision"), None)
    amount = _dict((submit or {}).get("args")).get("amount_gbp")
    escalation = next((a for a in actions if a.get("kind") == "escalation"), None)
    steps = []
    for t in trace:
        if "tool" in t:
            steps.append({"step": t.get("step"), "tool": str(t["tool"]), "arg": step_summary(t),
                          "status": str(_dict(t.get("result")).get("status", ""))})
        elif "thought" in t:
            steps.append({"step": t.get("step"), "thought": str(t["thought"])})
    return {
        "decision": dec,
        "derived": {
            "action_label": ACTION_LABELS.get(dec.get("action"), dec.get("action") or "—"),
            "amount": amount if isinstance(amount, (int, float)) else None,
            "route": {"route": escalation.get("route"), "state": escalation.get("state")} if escalation else None,
            "escalation": _escalation_view(escalation),
            "red_flags": _flags_view(dec["red_flags"]),
            "property": _property(dec, escalation),
            "followup_missing": any(t.get("tool") == "schedule_followup" and _dict(t.get("result")).get("status") == "skipped"
                                    for t in trace),
            "reason_parts": split_refs(dec["reason"]),
            "seconds": _case_seconds(out).get(d.name),
            "steps": steps,
            "calls": sum(1 for t in trace if "tool" in t),
        },
        "review": _review(d),
    }


class ReviewError(ValueError):
    def __init__(self, message: str, status: int = 400):
        super().__init__(message)
        self.status = status


def save_review(out: Path, cid: str, payload) -> dict:
    """Append a person's choice to <case>/review.json and return the new review view."""
    d = case_dir(out, cid)
    if d is None:
        raise ReviewError("unknown case", 404)
    if not isinstance(payload, dict) or payload.get("choice") not in REVIEW_CHOICES:
        raise ReviewError("choice must be one of %s" % ", ".join(REVIEW_CHOICES))
    try:
        dec = _load_decision(d)
    except UnreadableCase as exc:
        raise ReviewError(str(exc), 422)
    entry = {"choice": payload["choice"], "at": datetime.now(timezone.utc).isoformat(timespec="seconds")}
    if entry["choice"] == "option":
        options = dec["options"]
        n = payload.get("option")
        if not isinstance(n, int) or isinstance(n, bool) or not 1 <= n <= len(options):
            raise ReviewError("option must be a number from 1 to %d" % len(options))
        entry.update(option=n, option_text=options[n - 1])
    elif entry["choice"] == "new_case":
        text = payload.get("text")
        if not isinstance(text, str) or not text.strip() or len(text) > MAX_TEXT:
            raise ReviewError("text must be a non-empty string of at most %d characters" % MAX_TEXT)
        entry["text"] = text.strip()
    with _review_lock:
        data = _read_json(d / "review.json")
        entries = data.get("entries") if isinstance(data, dict) and isinstance(data.get("entries"), list) else []
        entries.append(entry)
        atomic_write(d / "review.json", json.dumps({"case_id": d.name, "entries": entries}, indent=2, ensure_ascii=False) + "\n")
    return _review(d)


_CONTENT_TYPES = {".html": "text/html; charset=utf-8", ".css": "text/css; charset=utf-8",
                  ".js": "text/javascript; charset=utf-8", ".svg": "image/svg+xml"}


class _Handler(BaseHTTPRequestHandler):
    server_version = "lettable-ui"

    def log_message(self, fmt, *args):
        pass

    def _send(self, status: int, body: bytes, ctype: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", CSP)
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, obj) -> None:
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _host_ok(self) -> bool:
        host = (self.headers.get("Host") or "").rsplit(":", 1)[0].strip("[]")
        return host in ALLOWED_HOSTS

    def _route(self):
        parts = [unquote(p) for p in urlparse(self.path).path.split("/") if p]
        return parts

    def do_GET(self):
        self._safely(self._get)

    def do_POST(self):
        self._safely(self._post)

    def _safely(self, handler) -> None:
        try:
            handler()
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception as exc:
            try:
                self._json(500, {"error": "%s: %s" % (type(exc).__name__, str(exc)[:300])})
            except OSError:
                pass

    def _get(self):
        if not self._host_ok():
            return self._json(403, {"error": "forbidden host"})
        out, parts = self.server.out_dir, self._route()
        if not parts or parts == ["index.html"]:
            return self._static("index.html")
        if len(parts) == 2 and parts[0] == "static":
            return self._static(parts[1])
        if parts == ["api", "run"]:
            return self._json(200, list_cases(out))
        if len(parts) == 3 and parts[:2] == ["api", "cases"]:
            try:
                view = case_view(out, parts[2])
            except UnreadableCase as exc:
                return self._json(422, {"error": str(exc)})
            return self._json(200, view) if view else self._json(404, {"error": "unknown case"})
        self._json(404, {"error": "not found"})

    def _post(self):
        if not self._host_ok():
            return self._json(403, {"error": "forbidden host"})
        parts = self._route()
        if not (len(parts) == 4 and parts[:2] == ["api", "cases"] and parts[3] == "review"):
            return self._json(404, {"error": "not found"})
        if not (self.headers.get("Content-Type") or "").startswith("application/json"):
            return self._json(415, {"error": "send application/json"})
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            length = -1
        if not 0 < length <= MAX_BODY:
            return self._json(413, {"error": "body must be 1 to %d bytes" % MAX_BODY})
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return self._json(400, {"error": "invalid JSON"})
        try:
            review = save_review(self.server.out_dir, parts[2], payload)
        except ReviewError as exc:
            return self._json(exc.status, {"error": str(exc)})
        self._json(200, review)

    def _static(self, name: str) -> None:
        path = STATIC_DIR / name
        if "/" in name or name.startswith(".") or not path.is_file():
            return self._json(404, {"error": "not found"})
        self._send(200, path.read_bytes(), _CONTENT_TYPES.get(path.suffix, "application/octet-stream"))


def make_server(out: Path, port: int = 8765) -> ThreadingHTTPServer:
    server = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    server.out_dir = out
    server.daemon_threads = True
    return server


def serve(out: Path, port: int = 8765, open_browser: bool = False) -> None:
    server = make_server(out, port)
    url = "http://127.0.0.1:%d/" % server.server_address[1]
    print("Lettable UI for %s at %s (Ctrl+C to stop)" % (out, url), flush=True)
    if open_browser:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
