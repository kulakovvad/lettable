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
- **Confidence:** 0.70
- **Decided by:** model
- **As of:** 2025-09-11T06:58:16+00:00
- **Evidence cited:** event-005, event-008, event-013, event-014, event-016, remedial-works-invoice.pdf

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
    "confidence": 0.7,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-11T06:58:16+00:00",
    "evidence_refs": [
      "event-005",
      "event-008",
      "event-013",
      "event-014",
      "event-016",
      "remedial-works-invoice.pdf"
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

Alder & Finch (assigned provider, event-007/008) sent invoice NBL-019-INV-11 for £174 (event-014, remedial-works-invoice.pdf). The address and provider match the job. The only variation is the shortened address in event-002, which is not a real mismatch. However, we asked for a quotation only and told them not to start work until we issued written authority (event-008). Rowan said he misunderstood and had already done the work (event-013). The landlord's approval (event-005) was to proceed with the remedial works. It set no price and was given before any quote, so it does not clearly cover a specific amount. The £174 is below the £300 threshold but that is not an agency allowance. The invoice is a single lump sum with no itemisation, and there is no quote, no attendance date, no access details and no photos. The former tenant had returned the keys on 27 August (event-003) and the agency held a set, so how access was gained is unexplained. Completion is only the provider's claim, so I am not closing or paying, and I am not telling the landlord the work is done. I chose a specific question to the provider over escalation because the provider holds the missing facts. If the answers show unauthorised access or a dispute, or if the landlord questions the cost, route it to a person. Once the details are in, route the invoice to the landlord for approval of £174, or check completion with the landlord. The tenant has left, so the closing check on completion must come from the provider or landlord. No hazard is reported.

## Actions taken

- **COMMITTED**: Message to provider (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-13T06:58:16+00:00, waiting on provider: Awaiting itemised invoice, attendance/access details and photos from Alder & Finch before routing the £174 invoice to the landlord. `followup-2`. Held: not part of the final action ASK_PROVIDER; a person can release it.

### Message to provider `message-1`

Hello Rowan, thank you for sending invoice NBL-019-INV-11 (£174.00) for 18 Brindle Row. Before we can take it to the landlord, please send us the following:
1. An itemised breakdown of the £174.00 across the six items (floorboard and carpet, new Venetian blind, cupboard handle, kitchen blind, toilet seat, gate hinge), including materials and labour.
2. The date and time you attended, and how you got access to the property. The former tenant vacated on 27 August, and we had asked for inspection windows and access details first.
3. Any before and after photos of the work.
To confirm, our request was for a quotation only. No price has been agreed and no written authority to start work was issued. The invoice is not approved or payable at this stage. We will put it to the landlord once we have this information.
Kind regards,
Maya Chen, Northbridge Lettings

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '18 Brindle Row, Larkspur Vale, ZZ1 1ZZ' vs '18 Brindle Row' (similarity 0.677). [event-002, index, remedial-works-invoice.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
