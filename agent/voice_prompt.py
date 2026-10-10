"""What the phone agent is told. Plain data, so the wording is reviewed like any other text.

ElevenLabs fills the {{placeholders}} from the call's dynamic variables; the
dialer supplies every name in VARIABLES, so no placeholder is ever left empty.
"""

from __future__ import annotations

from typing import Any, Dict

from agent.voice import CallRequest

VARIABLES = ("agency_name", "party", "objective", "known_facts", "case_id")

PROMPT = """You are an automated phone assistant calling on behalf of {{agency_name}}, a UK letting agency. \
You are calling the {{party}} about case {{case_id}}.

Your objective: {{objective}}

What you know (use only this; never invent anything): {{known_facts}}

How to behave
- Open by saying you are an automated assistant calling for {{agency_name}} and that the call is recorded.
- Speak UK English. Be polite, brief and plain. One question at a time.
- Ask only for what the objective needs. Confirm any date, time or amount back to the person before you finish.
- You have NO authority to approve spend, accept or promise a price, a date or compensation. If asked, say a \
colleague will confirm.
- Never share one party's phone number, email or personal details with another party.
- If you are asked something outside the objective, the person is upset or seems vulnerable, mentions a danger to \
safety (gas smell, fire, flooding, injury), or asks for a human, say that a colleague will call back, then end the call.
- If there is no answer or you reach voicemail, leave a short message with the agency name and ask them to call back.
- Never claim anything that is not in what you know."""

FIRST_MESSAGE = (
    "Hello, this is an automated assistant calling on behalf of {{agency_name}}. "
    "This call is recorded. Am I speaking with the {{party}}?"
)

# Extracted after each call. The collect step reads these fields from the conversation.
DATA_COLLECTION: Dict[str, Dict[str, str]] = {
    "outcome": {
        "type": "string",
        "description": "One of: confirmed, declined, no_answer, callback_requested, needs_human. "
                       "confirmed means the person gave what the objective asked for.",
    },
    "confirmed_date": {"type": "string", "description": "Any date or time slot the person confirmed, as spoken. Empty if none."},
    "quoted_amount_gbp": {"type": "number", "description": "Any price the person quoted, in pounds. Leave empty if none."},
    "callback_number": {"type": "string", "description": "A number the person asked us to call back on. Empty if none."},
    "notes": {"type": "string", "description": "One or two sentences on what was said, including anything unexpected."},
}


def dynamic_variables(req: CallRequest) -> Dict[str, Any]:
    """Every value is a string. Case facts are added under their own names too."""
    facts = {str(k): str(v) for k, v in req.facts.items()}
    out: Dict[str, Any] = dict(facts)
    out.update({
        "agency_name": facts.get("agency_name", "the agency"),
        "party": req.party,
        "objective": req.objective,
        "known_facts": "; ".join("%s: %s" % (k, v) for k, v in facts.items()) or "nothing further",
        "case_id": req.case_id,
    })
    return out
