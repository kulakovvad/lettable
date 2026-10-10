"""One-time setup of the ElevenLabs side: the phone agent and the Twilio number.

Creating the agent, updating it and importing the number all change the account, so the CLI describes
them and needs --yes to run them. Create and update send the same configuration.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agent.config import Config
from agent.voice_elevenlabs import request
from agent.voice_prompt import (DATA_COLLECTION, FIRST_MESSAGE, MAX_CALL_MESSAGE, MAX_CALL_SECONDS, PLACEHOLDERS, PROMPT,
                                TTS, VOICEMAIL_MESSAGE)


def agent_config(llm: Optional[str] = None) -> Dict[str, Any]:
    """Everything we set on the phone agent: what it says, how it sounds, what it extracts."""
    prompt: Dict[str, Any] = {"prompt": PROMPT, "built_in_tools": {"voicemail_detection": {
        "name": "voicemail_detection", "description": "",
        "params": {"system_tool_type": "voicemail_detection", "voicemail_message": VOICEMAIL_MESSAGE}}}}
    if llm:
        prompt["llm"] = llm
    return {
        "conversation_config": {
            "agent": {"first_message": FIRST_MESSAGE, "language": "en", "prompt": prompt,
                      "max_conversation_duration_message": MAX_CALL_MESSAGE,
                      "dynamic_variables": {"dynamic_variable_placeholders": dict(PLACEHOLDERS)}},
            "conversation": {"max_duration_seconds": MAX_CALL_SECONDS},
            "tts": dict(TTS),
        },
        "platform_settings": {"data_collection": DATA_COLLECTION},
    }


def agent_body(name: str, llm: Optional[str] = None) -> Dict[str, Any]:
    return {"name": name, **agent_config(llm)}


def create_agent(api_key: str, name: str = "Lettings call agent", llm: Optional[str] = None,
                 cfg: Optional[Config] = None) -> str:
    return request("POST", "/v1/convai/agents/create", api_key, cfg or Config(), agent_body(name, llm), retry_5xx=False)["agent_id"]


def update_agent(api_key: str, agent_id: str, llm: Optional[str] = None, cfg: Optional[Config] = None) -> None:
    """Apply the current configuration to an agent that already exists (its name and phone numbers are left alone)."""
    request("PATCH", "/v1/convai/agents/" + agent_id, api_key, cfg or Config(), agent_config(llm), retry_5xx=False)


def import_twilio_number(api_key: str, phone: str, sid: str, token: str, label: str = "Lettings calls",
                         cfg: Optional[Config] = None) -> str:
    body = {"phone_number": phone, "label": label, "sid": sid, "token": token, "provider": "twilio"}
    return request("POST", "/v1/convai/phone-numbers", api_key, cfg or Config(), body, retry_5xx=False)["phone_number_id"]
