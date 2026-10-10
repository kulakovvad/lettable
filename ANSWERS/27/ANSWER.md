# Case 27

**Decision:** Wait, nothing to do yet
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

- **Action:** Wait, nothing to do yet
- **Priority:** P3
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-15T16:25:18+00:00
- **Evidence cited:** event-013, event-014, event-016, event-017, move-out-works-quotation.pdf, checkout-report.pdf, event-002

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
    "action": "WAIT",
    "priority": "P3",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-15T16:25:18+00:00",
    "evidence_refs": [
      "event-013",
      "event-014",
      "event-016",
      "event-017",
      "move-out-works-quotation.pdf",
      "checkout-report.pdf",
      "event-002"
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

Alderwick's quote (event-013, move-out-works-quotation.pdf, ref NBL-027-Q1) is for the right property, 46 Fernwick Lane, from the assigned provider, and totals £3,865.68. That is far above the £300 approval limit. The workflow note (event-002) said approval is "normally" in place, but no landlord approval appears anywhere in the case, so I treated none as given. Maya has already asked Owen Vale to approve the quote (event-014, 13:53 on 15 Sep) and has noted she is waiting (event-016). The follow-up call (event-017) captured only a recording notice and an unclear utterance, so it is not an approval or a rejection. The landlord's reply is not overdue, because chasing is allowed after 3 days and only about 2.5 hours have passed. ROUTE_FOR_APPROVAL would only repeat the request already sent, and Alderwick must not be instructed without written approval. Nothing is unsafe: the property is vacant and no hazard is reported, so P3 applies. The checkout report does mention a taped boiler casing needing inspection, a non-working smoke detector and reported water ingress, so these should be dealt with before re-letting. The quote has a single lump sum with no itemisation and no exclusions. It leaves out the kitchen worktop, flooring, carpets, boiler inspection, curtains and bulbs. It also lacks an attendance date and says nothing on VAT. The landlord should know this when deciding. The reference mismatch flagged between the report and the quote is only two different document types, not a real conflict. I scheduled a follow-up for 72 hours. A decision would change if the landlord approves in writing (instruct Alderwick), rejects or queries the quote, or stays silent past 3 days (chase, then a call or escalation).

## Actions taken

- **COMMITTED**: Follow-up at 2025-09-18T16:25:18+00:00, waiting on landlord: Landlord asked at 13:53 on 15 Sep (event-014) to approve the £3,865.68 quote; the call at 16:25 (event-017) captured nothing. Chase is due after 3 days if there is no reply. Do not instruct Alderwick before written approval. `followup-1`. Recorded in the local outbox (no external delivery connected).

## Inconsistencies and mismatches

- **document consistency** (flag): reference number differs between documents: 'NBL-027-CHECKOUT' vs 'NBL-027-Q1' (similarity 0.293). [checkout-report.pdf, move-out-works-quotation.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Boiler casing held with tape needs a separate inspection by a qualified engineer, not covered by the quote
- Warped kitchen worktop with water ingress, kitchen flooring and carpet replacement are not in the quote
