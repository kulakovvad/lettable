# Case 27

**Decision:** Escalate to a person
**Priority:** P3

## Details

### Case

- **Id:** 27
- **Raised by:** Agency
- **Request:** Please obtain a quotation for the maintenance items recorded at the vacant property following the move-out inspection. The property is being prepared for re-letting.

### Property

- **Address:** 46 Fernwick Lane, Aldermead, ZZ1 1ZZ
- **References:** reference NBL-027-CHECKOUT [checkout-report.pdf]; reference NBL-027-Q1 [move-out-works-quotation.pdf]

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 3865.68 (VAT unknown, attachment) [move-out-works-quotation.pdf]

### Timeline

- **Events:** 17, first 2025-09-03T18:03:18+00:00, last 2025-09-15T16:25:18+00:00
- **Waiting on:** the landlord for 0.0 days
- **Channels:** Note 2, Update 4, Email 9, Call 2

### Attachments

- checkout-report.pdf (pdf, content read)
- move-out-works-quotation.pdf (pdf, content read)

### Decision

- **Action:** Escalate to a person
- **Priority:** P3
- **Confidence:** 0.85
- **Decided by:** model
- **As of:** 2025-09-15T16:25:18+00:00
- **Evidence cited:** event-013, event-014, event-015, event-016, event-017, move-out-works-quotation.pdf, checkout-report.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "27",
    "title": null,
    "source_role": "Agency",
    "status": null,
    "request": "Please obtain a quotation for the maintenance items recorded at the vacant property following the move-out inspection. The property is being prepared for re-letting."
  },
  "property": {
    "address": "46 Fernwick Lane, Aldermead, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "46 Fernwick Lane, Aldermead, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-027-CHECKOUT",
        "refs": [
          "checkout-report.pdf"
        ]
      },
      {
        "kind": "reference",
        "value": "NBL-027-Q1",
        "refs": [
          "move-out-works-quotation.pdf"
        ]
      }
    ]
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
    "name": "Maya Chen (Property Manager, Northbridge Lettings)",
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
    "quotes": [
      {
        "amount_gbp": 3865.68,
        "vat": "unknown",
        "from": "attachment",
        "ref": "move-out-works-quotation.pdf"
      }
    ],
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
    "events": 17,
    "first": "2025-09-03T18:03:18+00:00",
    "last": "2025-09-15T16:25:18+00:00",
    "waiting_on": {
      "party": "landlord",
      "since": "2025-09-15T16:23:44+00:00",
      "days": 0.0
    },
    "channels": {
      "Note": 2,
      "Update": 4,
      "Email": 9,
      "Call": 2
    }
  },
  "attachments": [
    {
      "name": "checkout-report.pdf",
      "available": true,
      "kind": "pdf"
    },
    {
      "name": "move-out-works-quotation.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "ESCALATE",
    "priority": "P3",
    "confidence": 0.85,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-15T16:25:18+00:00",
    "evidence_refs": [
      "event-013",
      "event-014",
      "event-015",
      "event-016",
      "event-017",
      "move-out-works-quotation.pdf",
      "checkout-report.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Please obtain a quotation for the maintenance items recorded at the vacant property following the move-out inspection. The property is being prepared for re-letting.
17 events reviewed, decision as of 2025-09-15T16:25:18+00:00.

## Decision

The job is move-out works at the vacant 46 Fernwick Lane. The Alderwick quote NBL-027-Q1 for £3,865.68 arrived on 15 Sept (event-013) and matches the property and assigned provider. The quote is well above the £300 approval limit. No landlord approval of the quote is in the case; the workflow note (event-002) only says approval is "normally" in place, and event-004 told the provider the works were agreed, which is not evidence of approval. Nobody has approved the quote, so we must not instruct the provider. We asked the landlord to approve at 13:53 (event-014), about 2.5 hours before the decision time. The 16:25 call (event-017) captured only a recording notice and an unclear utterance, so it counts as no reply, approval or rejection. The policy chase threshold is 3 days and urgent_by_code is false, so a chase now would be premature. The case is not an escalation: there is no safety hazard, dispute or fraud flag. The checkout report lists a boiler casing held with tape and needing inspection, plus water-ingress items. These are not reported as an active danger, and the quote does not cover them. The kitchen worktop, carpets, boiler inspection, curtains and bulbs are not in the quote scope. Another point is that the quote is one lump sum with no itemised prices or exclusions. The landlord should be told of both when they respond, and an itemised breakdown may be needed. The reference-number flag is just two different document types, so it is not a mismatch. I will chase the landlord after 3 days if there is no reply. The decision changes if the landlord approves (instruct the provider) or rejects or queries the quote. [gate: amount GBP 3865.68 is above the approval limit GBP 300.00]

## Actions taken

- **HELD_FOR_REVIEW**: Follow-up at 2025-09-18T16:25:18+00:00, waiting on landlord: Landlord asked 2025-09-15 13:53 (event-014) to approve quote NBL-027-Q1 £3,865.68; call at 16:25 (event-017) captured nothing. Chase is due after 3 days if there is no reply. `followup-1`. Held: code gates changed the decision to ESCALATE.
- **COMMITTED**: Escalation ticket P3 to property_manager `escalation-2`. Created automatically because the final decision is an escalation.

## Handover for the person taking over

The job is move-out works at the vacant 46 Fernwick Lane. The Alderwick quote NBL-027-Q1 for £3,865.68 arrived on 15 Sept (event-013) and matches the property and assigned provider. The quote is well above the £300 approval limit. No landlord approval of the quote is in the case; the workflow note (event-002) only says approval is "normally" in place, and event-004 told the provider the works were agreed, which is not evidence of approval. Nobody has approved the quote, so we must not instruct the provider. We asked the landlord to approve at 13:53 (event-014), about 2.5 hours before the decision time. The 16:25 call (event-017) captured only a recording notice and an unclear utterance, so it counts as no reply, approval or rejection. The policy chase threshold is 3 days and urgent_by_code is false, so a chase now would be premature. The case is not an escalation: there is no safety hazard, dispute or fraud flag. The checkout report lists a boiler casing held with tape and needing inspection, plus water-ingress items. These are not reported as an active danger, and the quote does not cover them. The kitchen worktop, carpets, boiler inspection, curtains and bulbs are not in the quote scope. Another point is that the quote is one lump sum with no itemised prices or exclusions. The landlord should be told of both when they respond, and an itemised breakdown may be needed. The reference-number flag is just two different document types, so it is not a mismatch. I will chase the landlord after 3 days if there is no reply. The decision changes if the landlord approves (instruct the provider) or rejects or queries the quote. [gate: amount GBP 3865.68 is above the approval limit GBP 300.00]

Respond by 2025-09-18T16:25:18+00:00 (P3, route property_manager).

Conflicts:
- reference_number: NBL-027-CHECKOUT (checkout-report.pdf) vs NBL-027-Q1 (move-out-works-quotation.pdf)

Known:
- 17 events reviewed
- Property: 46 Fernwick Lane, Aldermead, ZZ1 1ZZ (index)
- Request: Please obtain a quotation for the maintenance items recorded at the vacant property following the move-out inspection. The property is being prepared for re-letting. (request)

Not known:
- Landlord's decision on the £3,865.68 quote
- Itemised pricing and exclusions in the quote
- Whether the boiler casing inspection, kitchen worktop and carpet replacement are to be quoted separately
- Provider attendance date
- Which conflicting value is right (see conflicts)

Tried:
- Agent proposed WAIT
- amount GBP 3865.68 is above the approval limit GBP 300.00

Options:
- Recommended: Review the timeline and decide the next step
- Contact the party we are waiting on directly

Recommended: Recommended: Review the timeline and decide the next step

## What was blocked or failed

- Final code check: amount GBP 3865.68 is above the approval limit GBP 300.00

## Inconsistencies and mismatches

- **document consistency** (flag): reference number differs between documents: 'NBL-027-CHECKOUT' vs 'NBL-027-Q1' (similarity 0.347). [checkout-report.pdf, move-out-works-quotation.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Checkout items not in the quote: boiler casing held with tape needing inspection, warped worktop with water ingress, carpet replacement quote, missing curtains, curtain pole and bulbs, kitchen/laminate flooring.
