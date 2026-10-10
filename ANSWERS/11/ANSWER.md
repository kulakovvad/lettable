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
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-06-13T15:26:00+00:00
- **Evidence cited:** event-009, event-017, event-018, event-020, event-022, event-023, event-024

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
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-06-13T15:26:00+00:00",
    "evidence_refs": [
      "event-009",
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

The repair is blocked and a person needs to decide the next step. The leaking compression joint was confirmed by the contractor and the tenant (event-009, event-010), and the leak recurred on 13 June when the tap was used (event-020). The joint cannot be reached through the hatch. The contractor found an unidentified fibrous lining behind the ceiling board, paused, and left without opening it (event-017, event-023). We told him not to disturb the lining (event-018). No survey or alteration records exist (event-006, event-013, event-022). A young child lives in the flat (event-007). The landlord's authority covers the quoted plumbing scope only. She has refused to extend it to a material assessment without cost and timing (event-013, event-022). The contractor cannot price that assessment (event-023). We have no authority to approve spend, and there is no quote to route for approval, so ROUTE_FOR_APPROVAL does not fit. WAIT is wrong because the leak is active and the landlord decision was already requested (event-024). I set P1 because the leak is ongoing, a child is present and the material is unidentified. I did not set P0 because the tenant reports no electrical impact, no sagging and a small drip only, and the tap is out of use (event-003, event-020). This would become P0 if the drip worsens, the ceiling sags, or water reaches electrics. No attachments exist and no instruction in the case tried to change our process.

## Actions taken

- **COMMITTED**: Escalation ticket P1 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

16 Brindlewick Mews: the kitchen ceiling leak from a compression joint is recurring and the repair is blocked. An unidentified fibrous lining sits behind the ceiling board, and nobody can say whether it is hazardous. A young child lives in the flat. The landlord authorised the plumbing scope only and wants cost and timing for any assessment, which we cannot supply yet.

Respond by 2025-06-13T19:26:00+00:00 (P1, route property_manager).

Known:
- Tenant reported damp patch and drips on 10 June (event-001); no electrics affected, no sagging (event-003).
- Mossbarrow Pipe Services saw moisture at a compression joint above the hatch with the tap running; the joint is unreachable through the hatch (event-009, event-011).
- Landlord authorised the quoted plumbing scope only, up to the estimate, and asked to be told before any scope or cost increase (event-013). On 13 June she confirmed that this does not cover a specialist material assessment and asked for likely cost and timing (event-022).
- On 13 June Kellan saw a pale fibrous-looking lining behind the board, could not identify it, and paused (event-017). We told him not to disturb it or drill, cut, sample or remove (event-018). He left without opening the ceiling (event-023).
- Tenant reported a small drip when the tap was used on the morning of 13 June, has stopped using that tap, and the ceiling is not sagging (event-020). A young child will be present (event-007).
- No survey or ceiling alteration records exist from the landlord or the building manager (event-006, event-013, event-022).
- Event-024 asked the landlord for a decision on further assessment or repair scope; no extra cost or appointment is agreed.
- Property: 16 Brindlewick Mews, Fenbarrow, ZZ1 1ZZ (index)
- Request: Please arrange an inspection of a damp patch and occasional dripping from the kitchen ceiling. The patch has returned after rain. (request)

Not known:
- What the lining is, and whether it contains asbestos.
- Cost and timing of a specialist assessment, and who should provide it.
- Whether the landlord will authorise an assessment and the later repair.
- Whether the leak is getting worse, and how long the isolated tap can stay out of use.
- Composition of the lining
- Cost and timing of an assessment
- Landlord decision on further scope

Tried:
- Asked the building manager for records (event-005, event-006).
- Asked the landlord for survey records and authorisation (event-012, event-013).
- Paused the contractor and kept the ceiling undisturbed (event-018).
- Told the tenant not to touch the hatch and to report any new dripping (event-019).
- Asked the landlord for a decision on further scope (event-024).
- Agent proposed ESCALATE

Options:
- Recommended: Ask the landlord to approve a specialist surveyor attending or quoting for identification of the lining, then route the quote for approval; give the landlord an interim cost and timing indication once known.
- Ask the landlord for approval to use a licensed contractor who can isolate the supply or make a temporary non-invasive control of the leak, without disturbing the lining, while the assessment is arranged.
- Keep the tenant updated, tell them to keep the tap out of use, and report any worsening drip, sagging or electrical effect at once for re-triage to P0.

Recommended: Recommended: Ask the landlord to approve a specialist surveyor attending or quoting for identification of the lining, then route the quote for approval; give the landlord an interim cost and timing indication once known.

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
