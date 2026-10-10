# Case 18

**Decision:** Escalate to a person
**Priority:** P2

## Details

### Case

- **Id:** 18
- **Raised by:** Tenant
- **Request:** The tenant reports rat activity in the kitchen after returning from a short trip and asks for the issue to be addressed. They mention earlier pest-control visits and possible openings near the kitchen drain.

### Property

- **Address:** 14 Mosswold Crescent, Brindlewick, ZZ1 1ZZ

### Landlord

- **Phones:** 07700 900184 [event-004]

### Agency

- **Name:** Tara Wren (Property Manager, Northbridge Lettings)

### Appointments

- Says pest-control visits are ongoing, with a final visit expected the following Monday. [event-010]

### Timeline

- **Events:** 19, first 2025-08-14T11:05:29+00:00, last 2025-09-11T14:30:00+00:00
- **Channels:** Portal 1, Email 7, Call 4, Note 4, Update 3

### Decision

- **Action:** Escalate to a person
- **Priority:** P2
- **Confidence:** 0.75
- **Decided by:** model
- **As of:** 2025-09-11T14:30:00+00:00
- **Evidence cited:** event-007, event-010, event-014, event-017, event-018

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "18",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The tenant reports rat activity in the kitchen after returning from a short trip and asks for the issue to be addressed. They mention earlier pest-control visits and possible openings near the kitchen drain."
  },
  "property": {
    "address": "14 Mosswold Crescent, Brindlewick, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "14 Mosswold Crescent, Brindlewick, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": []
  },
  "tenant": {
    "name": null,
    "names": [],
    "phones": [],
    "emails": []
  },
  "landlord": {
    "name": null,
    "names": [],
    "phones": [
      {
        "value": "07700 900184",
        "refs": [
          "event-004"
        ]
      }
    ],
    "emails": []
  },
  "agency": {
    "name": "Tara Wren (Property Manager, Northbridge Lettings)",
    "phones": [],
    "emails": [],
    "staff": []
  },
  "provider": {
    "name": null,
    "assigned_ref": null,
    "phones": [],
    "emails": []
  },
  "money": {
    "quotes": [],
    "invoices": [],
    "approval": {
      "amount_gbp": null,
      "ref": null,
      "covers": "unknown"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Says pest-control visits are ongoing, with a final visit expected the following Monday.",
      "ref": "event-010"
    }
  ],
  "timeline": {
    "events": 19,
    "first": "2025-08-14T11:05:29+00:00",
    "last": "2025-09-11T14:30:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 7,
      "Call": 4,
      "Note": 4,
      "Update": 3
    }
  },
  "attachments": [],
  "decision": {
    "action": "ESCALATE",
    "priority": "P2",
    "confidence": 0.75,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-11T14:30:00+00:00",
    "evidence_refs": [
      "event-007",
      "event-010",
      "event-014",
      "event-017",
      "event-018"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The tenant reports rat activity in the kitchen after returning from a short trip and asks for the issue to be addressed. They mention earlier pest-control visits and possible openings near the kitchen drain.
19 events reviewed, decision as of 2025-09-11T14:30:00+00:00.

## Decision

The landlord said he would arrange the pest works directly (event-007, event-008). Our 18 Aug email asked for a completion date, and 24 days later there has been no reply (event-007, facts). Chase timing (3 days) is met. The tenant reports the final pest-control visit on 7 Sep (event-014). The proofing contractor expected on 8 Sep did not attend (event-017). The tenant also described the scope in two ways: under-sink openings (event-010) and a wall area (event-014). That is a gap in our information rather than a dispute between parties, so I ask the landlord for contractor, scope and date. No contractor, quote or landlord approval is on file, so we cannot instruct a provider. A phone call was blocked by channel policy because only one written message is unanswered. Escalation is not yet justified: there is no reported danger (urgent_by_code false). The landlord is reachable and has not yet failed a chase. If there is no reply in 72 hours, place a call and escalate to the property manager. The tenant's wish for phone contact is noted. [gate: model wants to chase the landlord but the timeline is not waiting on them]

## Actions taken

- **HELD_FOR_REVIEW**: Message to landlord (chase, P2) `message-1`. Held: code gates changed the decision to ESCALATE.
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-14T14:30:00+00:00, waiting on landlord: Chase sent; if no reply, place call to landlord and consider escalation to property manager `followup-2`. Held: code gates changed the decision to ESCALATE.
- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-3`. Created automatically because the final decision is an escalation.

### Message to landlord `message-1`

Dear Mr Vale, following my email of 18 August, we have not yet had an expected completion date or confirmation of the pest works at 14 Mosswold Crescent. The tenant reports that pest control made its final visit on 7 September, but the contractor expected on 8 September to seal the openings did not attend, and the openings are still reported as unsealed. Could you please tell us: (1) which contractor is doing the proofing, (2) the scope (under-sink openings and/or the wall area), and (3) the date they will attend? The tenant has said a phone call is easiest for access. If you would prefer Northbridge Lettings to arrange the proofing, please say so and we will request a quote for your approval. Kind regards, Tara Wren, Northbridge Lettings

## Handover for the person taking over

The landlord said he would arrange the pest works directly (event-007, event-008). Our 18 Aug email asked for a completion date, and 24 days later there has been no reply (event-007, facts). Chase timing (3 days) is met. The tenant reports the final pest-control visit on 7 Sep (event-014). The proofing contractor expected on 8 Sep did not attend (event-017). The tenant also described the scope in two ways: under-sink openings (event-010) and a wall area (event-014). That is a gap in our information rather than a dispute between parties, so I ask the landlord for contractor, scope and date. No contractor, quote or landlord approval is on file, so we cannot instruct a provider. A phone call was blocked by channel policy because only one written message is unanswered. Escalation is not yet justified: there is no reported danger (urgent_by_code false). The landlord is reachable and has not yet failed a chase. If there is no reply in 72 hours, place a call and escalate to the property manager. The tenant's wish for phone contact is noted. [gate: model wants to chase the landlord but the timeline is not waiting on them]

Respond by 2025-09-12T14:30:00+00:00 (P2, route property_manager).

Known:
- 19 events reviewed
- Property: 14 Mosswold Crescent, Brindlewick, ZZ1 1ZZ (index)
- Request: The tenant reports rat activity in the kitchen after returning from a short trip and asks for the issue to be addressed. They mention earlier pest-control visits and possible openings near the kitchen drain. (request)

Not known:
- Which contractor the landlord has engaged
- Intended proofing scope (under-sink vs wall area)
- Completion date
- Whether the final pest-control visit happened and whether a report exists

Tried:
- Agent proposed CHASE_LANDLORD
- model wants to chase the landlord but the timeline is not waiting on them

Options:
- Recommended: Review the timeline and decide the next step
- Contact the party we are waiting on directly

Recommended: Recommended: Review the timeline and decide the next step

## What was blocked or failed

- Tool gate refused `place_call`: only 1 unanswered written message(s) to the landlord so far; a call is for when 2 go unanswered, written contact bounces, or the matter is urgent
- Final code check: model wants to chase the landlord but the timeline is not waiting on them

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
