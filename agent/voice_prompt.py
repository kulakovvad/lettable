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
- If there is no answer or you reach voicemail, leave a short message with the agency name and ask them to call back.
- Never claim anything that is not in what you know."""

# One short sentence of context, then the agent waits for the person. No question, so nobody is asked to confirm who they are.
FIRST_MESSAGE = "Hello, this is an automated assistant calling for {{agency_name}} about {{job}}. This call is recorded."

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
    "quoted_amount_gbp": {"type": "number", "description": "Any price the person quoted, in pounds. Leave empty if none."},
    "callback_number": {"type": "string", "description": "A number the person asked us to call back on. Empty if none."},
    "notes": {"type": "string", "description": "One or two sentences on what was said, including anything unexpected."},
}


def _job(facts: Dict[str, str], objective: str) -> str:
    """What the call is about, in a few words: the 'job' fact, else the start of the objective."""
    if facts.get("job"):
        return facts["job"]
    first = re.split(r"(?<=[.!?])\s", objective.strip(), maxsplit=1)[0].rstrip(".!?")
    return first[:80] or "a job"


def dynamic_variables(req: CallRequest) -> Dict[str, Any]:
    """Every value is a string. Case facts are added under their own names too."""
    facts = {str(k): str(v) for k, v in req.facts.items()}
    out: Dict[str, Any] = dict(facts)
    out.update({
        "agency_name": facts.get("agency_name", "the agency"),
        "party": req.party,
        "job": _job(facts, req.objective),
        "objective": req.objective,
        "known_facts": "; ".join("%s: %s" % (k, v) for k, v in facts.items()) or "nothing further",
        "case_id": req.case_id,
    })
    return out
