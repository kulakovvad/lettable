"""What the phone agent is told. Plain data, so the wording is reviewed like any other text.

ElevenLabs fills the {{placeholders}} from the call's dynamic variables; the
dialer supplies every name in VARIABLES, so no placeholder is ever left empty.
"""

from __future__ import annotations

import re

from typing import Any, Dict

from agent.voice import CallRequest

VARIABLES = ("agency_name", "party", "job", "objective", "known_facts", "case_id")

PROMPT = """You are an automated phone assistant calling on behalf of {{agency_name}}, a UK letting agency. \
You are calling the {{party}} about {{job}} (case {{case_id}}).

Your objective: {{objective}}

What you know (use only this; never invent anything): {{known_facts}}

How to behave
- The first message has already said who you are, why you are calling and that the call is recorded. Do not repeat \
it. When the person replies, go straight to your objective.
- Speak UK English in plain words. Each turn is one or two short sentences, one question at a time. Let the person \
finish before you speak; if they interrupt, stop and answer what they asked.
- Never read out a long explanation and never repeat your whole introduction. If they did not follow, say it again \
in one short sentence.
- If they ask who you are, answer in one sentence. If they cannot talk now, say a colleague will call back at a \
better time, then end the call politely.
- Ask only for what the objective needs. Confirm any date, time or amount back to the person before you finish.
- Say words only. Never write bracketed tags or stage directions such as [sad], [slow] or [laughs].
- You have NO authority to approve spend, accept or promise a price, a date or compensation. If asked, say a \
colleague will confirm.
- Never share one party's phone number, email or personal details with another party.
- If you are asked something outside the objective, the person is upset or seems vulnerable, mentions a danger to \
safety (gas smell, fire, flooding, injury), or asks for a human, say that a colleague will call back, then end the call.
- If you reach voicemail, the voicemail tool leaves the standard short message for you; add nothing, and never say \
the objective, a price or any personal detail to a machine.
- If someone phones you (you did not start the call), say this is an automated line that cannot take requests, ask \
them to contact the agency directly, then end the call politely. If they report a danger (gas smell, fire, flooding, \
injury), tell them to call the emergency services on 999 now and then contact the agency.
- Never claim anything that is not in what you know."""

# One short sentence of context, then the agent waits for the person. No question, so nobody is asked to confirm who they are.
FIRST_MESSAGE = "Hello, this is an automated assistant calling for {{agency_name}} about {{job}}. This call is recorded."

# Hard limits on a call, so a stuck or hostile call cannot run on (and cost) unbounded. The ringing limit is set per call
# (Config.call_ring_timeout_s); the length limit is part of the agent.
MAX_CALL_SECONDS = 180
MAX_CALL_MESSAGE = "I need to end the call now. A colleague will follow up. Goodbye."

# What a machine hears. A voicemail is a durable recording, so it carries no case-derived text except the agency name
# (cleaned and capped, see _speakable): no job, objective, price, name or number.
VOICEMAIL_MESSAGE = ("Hello, this is an automated assistant calling for {{agency_name}} about a maintenance job. "
                     "We will follow up another way. Thank you.")

# Spoken defaults for every variable, used when someone phones the number back and no call set the values.
PLACEHOLDERS: Dict[str, str] = {
    "agency_name": "the letting agency", "party": "the contact", "job": "a maintenance job",
    "objective": "This is an automated line: ask the caller to contact the agency directly.",
    "known_facts": "nothing further", "case_id": "none",
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


def _speakable(text: str, limit: int) -> str:
    """Case-derived words that are spoken aloud (and recorded): no amounts, numbers, emails or links, and short.
    Words only; whatever is not clearly harmless is dropped rather than read out."""
    for pattern in (_EMAIL, _URL, _MONEY, _LONG_NUMBER):
        text = pattern.sub(" ", text)
    text = " ".join(text.replace("£", " ").split())
    if len(text) > limit:
        text = text[:limit].rsplit(" ", 1)[0]
    return text.strip(" ,;:-")


def _job(facts: Dict[str, str]) -> str:
    """What the call is about, in a few words. Only the 'job' fact is used: the objective is an instruction
    ("Confirm a visit date...") and does not read as a topic when spoken."""
    return _speakable(facts.get("job", ""), JOB_CHARS) or DEFAULT_JOB


def _agency(facts: Dict[str, str]) -> str:
    """The agency's name as spoken. A real name is short and plain, so one that had to be cleaned or cut (a number,
    an amount, a link, too long) is not trusted: the neutral wording is spoken instead."""
    raw = " ".join(facts.get("agency_name", "").split())
    name = _speakable(raw, AGENCY_CHARS)
    if name != raw or name in ("", "the agency"):  # "the agency" is the case-reading code's own placeholder
        return UNNAMED_AGENCY
    return name


def dynamic_variables(req: CallRequest) -> Dict[str, Any]:
    """Every value is a string. Case facts are added under their own names too."""
    facts = {str(k): str(v) for k, v in req.facts.items()}
    out: Dict[str, Any] = dict(facts)
    out.update({
        "agency_name": _agency(facts),
        "party": req.party,
        "job": _job(facts),
        "objective": req.objective or "Find out where the job stands.",
        "known_facts": "; ".join("%s: %s" % (k, v) for k, v in facts.items()) or "nothing further",
        "case_id": req.case_id,
    })
    return out
