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

The landlord said he would arrange the works himself (event-007), and no contractor, scope or date has been given in the 24 days since. The tenant says the expected contractors did not attend on 8 September and the openings are still unsealed (event-010, event-017). The earlier note said pest control made a final visit on 7 September (event-014), but the intended scope is unclear: under-sink openings versus the wall area. Nothing confirms completion (event-018). The three-day waiting period has expired (event-015, event-018), so a chase is due. We hold no approval to instruct a provider, so INSTRUCT_PROVIDER and ROUTE_FOR_APPROVAL do not apply. Escalation is not yet needed: no danger is reported, the landlord is reachable, and no chase has gone unanswered. The tenant reported rats indoors, but no health hazard or vulnerable occupant is stated, so P2. If the landlord stays silent after this chase, escalate to the property manager or place a call. The wait notes in events 13 and 16 were not a chase. [gate: model wants to chase the landlord but the timeline is not waiting on them]

## Actions taken

- **HELD_FOR_REVIEW**: Message to landlord (chase, P2) `message-1`. Held: code gates changed the decision to ESCALATE.
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-13T14:30:00+00:00, waiting on landlord: Chase sent for contractor, scope and date. If there is no reply, consider a call, since the tenant prefers phone and the landlord asked for a call earlier, and consider a handover to the property manager. `followup-2`. Held: code gates changed the decision to ESCALATE.
- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-3`. Created automatically because the final decision is an escalation.

### Message to landlord `message-1`

Dear Mr Vale, we are following up on the rat activity at 14 Mosswold Crescent, Brindlewick. On 18 August we recorded that you would arrange the works directly, and we asked for an expected completion date and confirmation when complete. We have not had that. The tenant reports that pest control made what they understood to be a final visit on 7 September, but that the contractors expected to fill or work on the openings did not attend on 8 September, and the openings are still unsealed. Please could you tell us: (1) who your contractor is and what work is planned (the under-sink openings, the wall area or the external drain openings), (2) the date it will be done, and (3) whether you can share any pest-control report. If you would rather Northbridge Lettings arrange an inspection, please say so. We cannot instruct anyone without your written approval. Kind regards, Tara Wren, Northbridge Lettings

## Handover for the person taking over

The landlord said he would arrange the works himself (event-007), and no contractor, scope or date has been given in the 24 days since. The tenant says the expected contractors did not attend on 8 September and the openings are still unsealed (event-010, event-017). The earlier note said pest control made a final visit on 7 September (event-014), but the intended scope is unclear: under-sink openings versus the wall area. Nothing confirms completion (event-018). The three-day waiting period has expired (event-015, event-018), so a chase is due. We hold no approval to instruct a provider, so INSTRUCT_PROVIDER and ROUTE_FOR_APPROVAL do not apply. Escalation is not yet needed: no danger is reported, the landlord is reachable, and no chase has gone unanswered. The tenant reported rats indoors, but no health hazard or vulnerable occupant is stated, so P2. If the landlord stays silent after this chase, escalate to the property manager or place a call. The wait notes in events 13 and 16 were not a chase. [gate: model wants to chase the landlord but the timeline is not waiting on them]

Respond by 2025-09-12T14:30:00+00:00 (P2, route property_manager).

Known:
- 19 events reviewed
- Property: 14 Mosswold Crescent, Brindlewick, ZZ1 1ZZ (index)
- Request: The tenant reports rat activity in the kitchen after returning from a short trip and asks for the issue to be addressed. They mention earlier pest-control visits and possible openings near the kitchen drain. (request)

Not known:
- Landlord's contractor and the scope of work
- Whether the pest-control report exists
- Whether any openings have been sealed
- Which openings are meant: under the sink, the wall area or the external drain

Tried:
- Agent proposed CHASE_LANDLORD
- model wants to chase the landlord but the timeline is not waiting on them

Options:
- Recommended: Wait for the landlord's reply
- Place a call to the landlord if there is no reply in 48 hours
- Escalate to the property manager to propose an agency inspection with landlord approval

Recommended: Recommended: Wait for the landlord's reply

## What was blocked or failed

- Final code check: model wants to chase the landlord but the timeline is not waiting on them

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
