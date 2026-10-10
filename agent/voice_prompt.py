"""What the phone agent is told. Plain data, so the wording is reviewed like any other text.

ElevenLabs fills the {{placeholders}} from the call's dynamic variables; the
dialer supplies every name in VARIABLES, so no placeholder is ever left empty.
"""

from __future__ import annotations

import re

from typing import Any, Dict

from agent.voice import STAFF_PARTY, CallRequest

VARIABLES = ("agency_name", "party", "job", "objective", "known_facts", "case_id", "audience")

PROMPT = """You are an automated phone assistant calling on behalf of {{agency_name}}, a UK letting agency. \
You are calling the {{party}} about {{job}} (case {{case_id}}).

Your objective: {{objective}}

What you know (use only this; never invent anything): {{known_facts}}

Who you are speaking to: {{audience}}. If this is "staff", you are briefing a colleague on call, not asking for \
anything: say the case and the property, what was found and what has already been done, using only what you know; \
then ask "Can you confirm you have this?", take a yes or a no, repeat the briefing once if they ask, say thank you, \
and use the end_call tool. Do not ask for a visit date or a price. Every rule below still applies.

How to behave
- The first message has already said who you are, why you are calling and that the call is recorded. Do not repeat \
it. When the person replies, go straight to your objective.
- Speak UK English in plain words. Each turn is one or two short sentences, one question at a time. Let the person \
finish before you speak; if they interrupt, stop and answer what they asked.
- Never read out a long explanation and never repeat your whole introduction. If they did not follow, say it again \
in one short sentence.
- If they ask who you are, answer in one sentence. If they cannot talk now, say a colleague will call back at a \
better time, then use the end_call tool.
- Ask only for what the objective needs. Confirm any date, time or amount back to the person before you finish.
- If they give a weekday or a relative day ("Tuesday", "next Friday", "next week"), ask which date that is, with \
the day, month and year, and read back exactly what they say. Never state a date they did not say.
- When the objective is done, say one short goodbye and then use the end_call tool. If the person says thanks or \
goodbye after that, do not reply again: end the call.
- Say words only. Never write bracketed tags or stage directions such as [sad], [slow] or [laughs].
- You have NO authority to approve spend, accept or promise a price, a date or compensation. If asked, say a \
colleague will confirm.
- Never share one party's phone number, email or personal details with another party.
- If the person reports a danger (gas smell, fire, flooding, injury), tell them to call the emergency services on 999 \
now (for gas also the National Gas Emergency line on 0800 111 999), say that a colleague will call back, then use the \
end_call tool.
- If you are asked something outside the objective, the person is upset or seems vulnerable, or asks for a human, say \
that a colleague will call back, then use the end_call tool.
- If you reach voicemail, the voicemail tool leaves the standard short message for you; add nothing, and never say \
the objective, a price or any personal detail to a machine.
- If someone phones you (you did not start the call), say this is an automated line that cannot take requests, ask \
them to contact the agency directly, then use the end_call tool. The danger rule above still comes first.
- Never claim anything that is not in what you know."""

# One short sentence of context, then the agent waits for the person. No question, so nobody is asked to confirm who they
# are. The platform speaks this before the model runs, so it must also be true when someone phones the number back:
# it says "for", not "calling for".
FIRST_MESSAGE = "Hello, this is an automated assistant for {{agency_name}}, about {{job}}. This call is recorded."

# Hard limits on a call, so a stuck or hostile call cannot run on (and cost) unbounded. The ringing limit is set per call
# (Config.call_ring_timeout_s); the length limit is part of the agent.
MAX_CALL_SECONDS = 180
MAX_CALL_MESSAGE = "I need to end the call now. A colleague will follow up. Goodbye."
SILENCE_END_SECONDS = 60  # hang up after this long without the person speaking; the platform default never hangs up,
# and a person checking a diary goes quiet for a while (the agent re-prompts every few seconds in between)

# What a machine hears. A voicemail is a durable recording, so it carries no case-derived text except the agency name
# (cleaned and capped, see _speakable): no job, objective, price, name or number.
VOICEMAIL_MESSAGE = ("Hello, this is an automated assistant calling for {{agency_name}} about a maintenance job. "
                     "We will follow up another way. Thank you.")

# Spoken defaults for every variable, used when someone phones the number back and no call set the values.
PLACEHOLDERS: Dict[str, str] = {
    "agency_name": "the letting agency", "party": "the contact", "job": "a maintenance job",
    "objective": "This is an automated line: ask the caller to contact the agency directly.",
    "known_facts": "nothing further", "case_id": "none", "audience": "external",
}

# Plain, non-expressive voice: the expressive models read stage directions such as [sad] aloud.
# The voice itself is left as the agent already has it.
TTS: Dict[str, Any] = {"model_id": "eleven_flash_v2", "expressive_mode": False}

OUTCOMES = {
    "confirmed": "the person gave what the objective asked for (for example a visit date or a yes)",
    "declined": "the person refused or said they cannot do it",
    "no_answer": "nobody picked up, or only voicemail; never use this when a person answered",
    "callback_requested": "the person asked to be called back later or on another number",
    "needs_human": "a colleague must follow up: a safety danger, a complaint, a price or approval request, or an upset person",
    "unclear": "a person answered but gave no usable answer (interrupted, confused, a bad line, off topic)",
}

# Extracted after each call. The collect step reads these fields from the conversation.
DATA_COLLECTION: Dict[str, Dict[str, str]] = {
    "outcome": {
        "type": "string",
        "description": "Exactly one of: " + "; ".join("%s = %s" % kv for kv in OUTCOMES.items()) + ".",
    },
    "confirmed_date": {"type": "string", "description": "Any date or time slot the person confirmed, as spoken. Empty if none."},
    "confirmed_date_iso": {"type": "string", "description": "YYYY-MM-DD, only if the person gave an exact calendar date "
                           "(for example 'the 14th of October'). Empty for anything relative or vague such as 'Tuesday' or "
                           "'next week': never work a date out."},
    "quoted_amount_gbp": {"type": "number", "description": "Any price the person quoted, in pounds. Leave empty if none."},
    "callback_number": {"type": "string", "description": "A number the person asked us to call back on. Empty if none."},
    "notes": {"type": "string", "description": "One or two sentences on what was said, including anything unexpected."},
}


JOB_CHARS = 80
AGENCY_CHARS = 60
DEFAULT_JOB = "a maintenance job"  # spoken when the case supplies no short description of the job
UNNAMED_AGENCY = "the letting agency"  # said when the case does not name the agency; "the agency" alone sounds odd aloud

_EMAIL = re.compile(r"\S+@\S+")
_URL = re.compile(r"(?i)\b(?:https?://|www\.)\S+")
_MONEY = re.compile(r"(?i)(?:£|GBP\s?)\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s?(?:GBP|pounds)\b")
_LONG_NUMBER = re.compile(r"\+?\d[\d\s().-]{4,}\d")  # phone numbers, references, account numbers
_BARE_NUMBER = re.compile(r"\b\d{3,}\b")
_EDGE = " ,.;:-"


def _cut(text: str, limit: int, edge: str = _EDGE) -> str:
    text = " ".join(text.split())
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0]
    return text.strip(edge)


def _speakable(text: str, limit: int) -> str:
    """Case-derived words that are spoken in the greeting (and so recorded): no amounts, numbers of three or more digits,
    emails or links, and short. Words only; whatever is not clearly harmless is dropped rather than read out."""
    for pattern in (_EMAIL, _URL, _MONEY, _LONG_NUMBER, _BARE_NUMBER):
        text = pattern.sub(" ", text)
    return _cut(text.replace("£", " "), limit)


def _prompt_text(text: str, limit: int) -> str:
    """Case-derived text the agent may rely on in conversation. Lighter than _speakable (an amount to confirm with the
    right person is fine), but never an email, a link or a phone or account number."""
    for pattern in (_EMAIL, _URL, _LONG_NUMBER):
        text = pattern.sub(" ", text)
    return _cut(text, limit, edge=" ")  # keep the sentence as written, including its full stop


def _job(facts: Dict[str, str]) -> str:
    """What the call is about, in a few words. Only the 'job' fact is used: the objective is an instruction
    ("Confirm a visit date...") and does not read as a topic when spoken."""
    return _speakable(facts.get("job", ""), JOB_CHARS) or DEFAULT_JOB


def _agency(facts: Dict[str, str]) -> str:
    """The agency's name as spoken. A real name is short and plain, so one that had to be cleaned for safety (a number,
    an amount, a link) or cut is not trusted: the neutral wording is spoken instead. Trailing punctuation is harmless."""
    raw = " ".join(facts.get("agency_name", "").split()).strip(_EDGE)
    if raw in ("", "the agency") or re.search(r"\d", raw) or _speakable(raw, AGENCY_CHARS) != raw:
        return UNNAMED_AGENCY  # "the agency" is the case-reading code's own placeholder
    return raw


_FACT_KEY = re.compile(r"[A-Za-z][A-Za-z0-9 _-]{0,29}\Z")
KNOWN_FACTS_CHARS = 500


def _known_facts(facts: Dict[str, str]) -> str:
    """'key: value' pairs the agent may rely on, cleaned. The job and agency are already said elsewhere."""
    parts = []
    for key, value in facts.items():
        text = _prompt_text(value, 150)
        if key not in ("agency_name", "job") and _FACT_KEY.match(key) and text:
            parts.append("%s: %s" % (key, text))
    return "; ".join(parts)[:KNOWN_FACTS_CHARS].rsplit("; ", 1)[0] if len("; ".join(parts)) > KNOWN_FACTS_CHARS else "; ".join(parts) or "nothing further"


def dynamic_variables(req: CallRequest) -> Dict[str, Any]:
    """Exactly the declared variables, every value a string. Raw case facts are never passed on as they are: what
    the agent can say comes from the cleaned job, agency name, objective and known facts."""
    facts = {str(k): str(v) for k, v in req.facts.items()}
    return {
        "agency_name": _agency(facts),
        "party": req.party,
        "job": _job(facts),
        "objective": _prompt_text(req.objective, 300) or "Find out where the job stands.",
        "known_facts": _known_facts(facts),
        "case_id": _cut(req.case_id, 40) or "none",
        "audience": "staff" if req.party == STAFF_PARTY else "external",  # set by code from the party, never from facts
    }
