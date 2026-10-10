# Case 11

**Decision:** Escalate to a person
**Priority:** P1

## Details

### Case

- **Id:** 11
- **Raised by:** Tenant
- **Request:** Please arrange an inspection of a damp patch and occasional dripping from the kitchen ceiling. The patch has returned after rain.

### Property

- **Address:** 16 Brindlewick Mews, Fenbarrow, ZZ1 1ZZ

### Agency

- **Name:** Mara Voss (Property Manager, Northbridge Lettings)

### Timeline

- **Events:** 24, first 2025-06-10T08:12:00+00:00, last 2025-06-13T15:26:00+00:00
- **Channels:** Portal 4, Update 2, Note 3, Email 10, Call 4, SMS 1

### Decision

- **Action:** Escalate to a person
- **Priority:** P1
- **Confidence:** 0.70
- **Decided by:** model
- **As of:** 2025-06-13T15:26:00+00:00
- **Evidence cited:** event-007, event-009, event-013, event-017, event-018, event-020, event-022, event-023, event-024

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "11",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "Please arrange an inspection of a damp patch and occasional dripping from the kitchen ceiling. The patch has returned after rain."
  },
  "property": {
    "address": "16 Brindlewick Mews, Fenbarrow, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "16 Brindlewick Mews, Fenbarrow, ZZ1 1ZZ",
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
    "phones": [],
    "emails": []
  },
  "agency": {
    "name": "Mara Voss (Property Manager, Northbridge Lettings)",
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
  "appointments": [],
  "timeline": {
    "events": 24,
    "first": "2025-06-10T08:12:00+00:00",
    "last": "2025-06-13T15:26:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 4,
      "Update": 2,
      "Note": 3,
      "Email": 10,
      "Call": 4,
      "SMS": 1
    }
  },
  "attachments": [],
  "decision": {
    "action": "ESCALATE",
    "priority": "P1",
    "confidence": 0.7,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-06-13T15:26:00+00:00",
    "evidence_refs": [
      "event-007",
      "event-009",
      "event-013",
      "event-017",
      "event-018",
      "event-020",
      "event-022",
      "event-023",
      "event-024"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Please arrange an inspection of a damp patch and occasional dripping from the kitchen ceiling. The patch has returned after rain.
24 events reviewed, decision as of 2025-06-13T15:26:00+00:00.

## Decision

The kitchen ceiling leak is confirmed at a compression joint above the hatch (event-009, event-011). It recurred on 13 June when the tap was used (event-020). The authorised repair cannot go ahead. On the return visit the contractor found an unidentified pale fibrous lining and paused (event-017). We told him not to disturb it (event-018), and he left without opening the ceiling (event-023). No survey exists (event-006, event-013, event-022). A young child lives in the flat (event-007). The leak is ongoing and a possible hazardous material blocks the fix, so a person should decide how to proceed. I rate it P1, not P0: the tenant reports no electrics affected, no sagging, and only a small drip with the tap now out of use (event-003, event-020). The landlord's approval covers only the quoted plumbing scope (event-013). She has declined to extend it without cost and timing (event-022), and the contractor cannot price an assessment (event-023). I cannot approve spend or instruct more work, and routing for approval has no amount to cite. Waiting would leave a recurring leak with no route to repair. I already asked the landlord for a decision (event-024), and her reply is not overdue. If she authorises assessment, or the leak worsens, the plan changes. Escalating to the property manager gives a person the task of arranging the assessment and tenant advice.

## Actions taken

- **COMMITTED**: Escalation ticket P1 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Kitchen ceiling leak at 16 Brindlewick Mews is confirmed (leaking compression joint above the hatch) and recurs when the kitchen tap is used. The authorised repair is blocked. The contractor found an unidentified pale fibrous lining behind the ceiling board and stopped. A young child lives in the flat. A person needs to decide how to handle the suspect material and the ongoing leak. The landlord has only approved the quoted plumbing scope.

Respond by 2025-06-13T19:26:00+00:00 (P1, route property_manager).

Known:
- Tenant reported damp patch and drips on 2025-06-10 (event-001). No electrics affected, no sagging (event-003, event-020).
- Mossbarrow Pipe Services saw moisture at a compression joint above the hatch with the tap running. The hatch is too small to reach the joint (event-009, event-011).
- Landlord authorised the quoted plumbing scope only, up to the estimate, and wants to be contacted before any scope or cost increase (event-013). The estimate amount is not stated in the case.
- On the 13 June return visit Kellan saw a pale fibrous-looking lining. He has not touched it, cannot identify it, and paused (event-017). Mara told him not to drill, cut, sample or remove (event-018) and he left without opening the ceiling (event-023).
- No survey or ceiling alteration records exist. The landlord and building manager have none (event-006, event-013, event-022).
- Tenant reported a small drip when the tap was used on the morning of 13 June and has stopped using that tap. A young child is present (event-007, event-020).
- Landlord said her authorisation does not cover specialist material assessment and asked for likely cost and timing first (event-022). Mara has asked for a decision on further scope; nothing extra is agreed (event-024).
- The communal roof inspection is planned for the week after 10 June (event-006).
- Property: 16 Brindlewick Mews, Fenbarrow, ZZ1 1ZZ (index)
- Request: Please arrange an inspection of a damp patch and occasional dripping from the kitchen ceiling. The patch has returned after rain. (request)

Not known:
- What the lining is, and whether it contains asbestos
- Cost and timing of a specialist assessment. The contractor cannot price it (event-023).
- Whether the leak can be isolated, for example at a stopcock or isolation valve, to stop further drips
- Whether the leak is wholly from the joint or whether the roof or communal stack contributes
- The amount of the approved estimate (not in the case data)
- Whether the landlord will authorise assessment or repair
- Identity of the lining and whether it contains asbestos
- Cost and timing of an assessment

Tried:
- Asked the building manager about leaks and records (event-005, event-006)
- Inspection, then quote, then landlord approval, then return visit (event-008 to event-016)
- Stopped work and told the tenant not to touch the hatch or ceiling (event-018, event-019)
- Sent the landlord an update requesting a decision on further scope (event-024). Her reply is not yet due.
- Agent proposed ESCALATE

Options:
- Recommended: Ask the landlord to authorise a specialist asbestos/material assessment (get a quote first, as she asked) before any opening. Meanwhile ask the contractor whether the supply can be isolated or the tap/joint made safe without disturbing the lining.
- Have the tenant keep the kitchen tap out of use and report any new drips or sagging. Send safety advice to the tenant (keep the child away from the area, do not disturb the ceiling) and set a short follow-up for the landlord's decision.
- If the leak worsens, spreads, reaches electrics or the ceiling sags, treat it as P0 and send on-call. Consider a different contractor or a specialist if the landlord approves.

Recommended: Recommended: Ask the landlord to authorise a specialist asbestos/material assessment (get a quote first, as she asked) before any opening. Meanwhile ask the contractor whether the supply can be isolated or the tap/joint made safe without disturbing the lining.

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
