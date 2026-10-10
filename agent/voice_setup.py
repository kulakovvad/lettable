"""One-time setup of the ElevenLabs side: the phone agent and the Twilio number.

Both are create calls on the account, so the CLI describes them and needs --yes to run them.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agent.config import Config
from agent.voice_elevenlabs import request
from agent.voice_prompt import DATA_COLLECTION, FIRST_MESSAGE, PROMPT


def agent_body(name: str, llm: Optional[str] = None) -> Dict[str, Any]:
    prompt: Dict[str, Any] = {"prompt": PROMPT}
    if llm:
        prompt["llm"] = llm
    return {
        "name": name,
        "conversation_config": {"agent": {"first_message": FIRST_MESSAGE, "language": "en", "prompt": prompt}},
        "platform_settings": {"data_collection": DATA_COLLECTION},
    }


def create_agent(api_key: str, name: str = "Lettings call agent", llm: Optional[str] = None,
                 cfg: Optional[Config] = None) -> str:
    return request("POST", "/v1/convai/agents/create", api_key, cfg or Config(), agent_body(name, llm), retry_5xx=False)["agent_id"]


def import_twilio_number(api_key: str, phone: str, sid: str, token: str, label: str = "Lettings calls",
                         cfg: Optional[Config] = None) -> str:
    body = {"phone_number": phone, "label": label, "sid": sid, "token": token, "provider": "twilio"}
    return request("POST", "/v1/convai/phone-numbers", api_key, cfg or Config(), body, retry_5xx=False)["phone_number_id"]
