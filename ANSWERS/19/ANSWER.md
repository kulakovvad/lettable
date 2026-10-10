# Case 19

**Decision:** Ask the provider for more information
**Priority:** P2

## Details

### Case

- **Id:** 19
- **Raised by:** Agency
- **Request:** Move-out inspection identified six maintenance items: a cracked section of chipboard flooring beside the fireplace; a living-room front-window blind needing repair; a loose under-stairs cupboard handle; a kitchen blind that does not operate correctly; a loose bathroom toilet seat; and a bottom hinge

### Property

- **Address:** 18 Brindle Row, Larkspur Vale, ZZ1 1ZZ
- **References:** reference NBL-019-INV-11 [remedial-works-invoice.pdf]

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Money

- **Invoices:** GBP 174.00 (attachment) [remedial-works-invoice.pdf]
- **Landlord approval:** for the visit, no amount [event-005]
- **Payments:** payment: No quotation, itemised prices, prior approval of variations, or payment terms are described in the accompanying message. [event-016]

### Timeline

- **Events:** 16, first 2025-09-04T13:25:54+00:00, last 2025-09-11T06:58:16+00:00
- **Channels:** Note 7, Email 7, Call 1, Document 1

### Attachments

- remedial-works-invoice.pdf (pdf, content read)

### Decision

- **Action:** Ask the provider for more information
- **Priority:** P2
- **Confidence:** 0.75
- **Decided by:** model
- **As of:** 2025-09-11T06:58:16+00:00
- **Evidence cited:** event-005, event-008, event-013, event-014, event-016, remedial-works-invoice.pdf, event-003

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "19",
    "title": null,
    "source_role": "Agency",
    "status": null,
    "request": "Move-out inspection identified six maintenance items: a cracked section of chipboard flooring beside the fireplace; a living-room front-window blind needing repair; a loose under-stairs cupboard handle; a kitchen blind that does not operate correctly; a loose bathroom toilet seat; and a bottom hinge"
  },
  "property": {
    "address": "18 Brindle Row, Larkspur Vale, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "18 Brindle Row, Larkspur Vale, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-019-INV-11",
        "refs": [
          "remedial-works-invoice.pdf"
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
    "quotes": [],
    "invoices": [
      {
        "amount_gbp": 174.0,
        "from": "attachment",
        "ref": "remedial-works-invoice.pdf"
      }
    ],
    "approval": {
      "amount_gbp": null,
      "ref": "event-005",
      "covers": "visit"
    },
    "payments": [
      {
        "kind": "payment",
        "text": "No quotation, itemised prices, prior approval of variations, or payment terms are described in the accompanying message.",
        "ref": "event-016"
      }
    ],
    "deposit": []
  },
  "appointments": [],
  "timeline": {
    "events": 16,
    "first": "2025-09-04T13:25:54+00:00",
    "last": "2025-09-11T06:58:16+00:00",
    "waiting_on": null,
    "channels": {
      "Note": 7,
      "Email": 7,
      "Call": 1,
      "Document": 1
    }
  },
  "attachments": [
    {
      "name": "remedial-works-invoice.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "ASK_PROVIDER",
    "priority": "P2",
    "confidence": 0.75,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-11T06:58:16+00:00",
    "evidence_refs": [
      "event-005",
      "event-008",
      "event-013",
      "event-014",
      "event-016",
      "remedial-works-invoice.pdf",
      "event-003"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Move-out inspection identified six maintenance items: a cracked section of chipboard flooring beside the fireplace; a living-room front-window blind needing repair; a loose under-stairs cupboard handle; a kitchen blind that does not operate correctly; a loose bathroom toilet seat; and a bottom hinge detached from the front gate's brick pillar.
16 events reviewed, decision as of 2025-09-11T06:58:16+00:00.

## Decision

Alder & Finch is the assigned provider (event-7, event-8) and the invoice matches the property address (the "18 Brindle Row" in event-2 is a shortened form, not a mismatch). But the invoice (event-14, event-16, remedial-works-invoice.pdf) is a single unitemised £174.00 line, and the work was done without the quote and written authority we required (event-8). The landlord's approval (event-5) was a general go-ahead with no price, and no quote exists. The £174 is under the £300 threshold, but the agency cannot approve spend. There is no evidence of completion beyond the contractor's own claim: no visit date, no access details (the tenant left on 27 August and keys were returned, event-3, so how access was gained is unknown), and no photos. The invoice also says a new Venetian blind was supplied, where the request was for a blind repair, which is a scope variation nobody approved. I am asking the provider for an itemised breakdown, visit date, access details, photos and the reason for the blind replacement, and not treating the invoice as payable meanwhile. I am not closing: the invoice position and approval do not match, and completion is unverified. Escalation is not needed yet because the provider can supply these facts. Once the provider replies, the likely next step is routing to the landlord for approval of the invoice, or a person if the access or authorisation answers are disputed. The agency should also tell the landlord about the invoice once its details are clarified.

## Actions taken

- **COMMITTED**: Message to provider (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-13T06:58:16+00:00, waiting on provider: Awaiting itemised invoice, visit date/access details and photos before routing the invoice to landlord. `followup-2`. Held: not part of the final action ASK_PROVIDER; a person can release it.

### Message to provider `message-1`

Hello Rowan, thank you for sending invoice NBL-019-INV-11 (£174.00) for 18 Brindle Row, Larkspur Vale, ZZ1 1ZZ. Before we can take it to the landlord, please send: (1) an itemised breakdown of the £174.00 for each of the six items, including labour and materials; (2) the date of the visit and how you got access to the property; (3) before/after photos of the completed work, if you have them. Please also confirm whether the lounge blind was replaced with a new Venetian blind rather than repaired, and why. As set out in our email of 7 September, we asked for a quotation only, and written authority had not been issued, so the invoice is not approved for payment at this stage. Kind regards, Maya Chen, Northbridge Lettings

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '18 Brindle Row, Larkspur Vale, ZZ1 1ZZ' vs '18 Brindle Row' (similarity 0.683). [event-002, index, remedial-works-invoice.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
