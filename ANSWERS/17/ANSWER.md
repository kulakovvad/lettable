# Case 17

**Decision:** Wait, nothing to do yet
**Priority:** P3

## Details

### Case

- **Id:** 17
- **Raised by:** Tenant
- **Request:** The paint on the inside of my flat entrance door is flaking, and the door has started catching near the top. Could someone inspect it and let me know what can be done?

### Property

- **Address:** 14 Lantern Mews, Brindlewick, ZZ1 1ZZ
- **References:** reference NBL-017-Q1 [fire-door-quotation.pdf]

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 186.00 (VAT unknown, attachment) [fire-door-quotation.pdf]
- **Landlord approval:** for the visit, no amount [event-017]

### Appointments

- Offered an inspection visit on 7 February between 10:30 and 12:00. [event-008]

### Timeline

- **Events:** 19, first 2025-02-03T08:20:00+00:00, last 2025-02-12T16:10:00+00:00
- **Channels:** Portal 3, Email 9, Note 3, Call 2, SMS 2

### Attachments

- fire-door-quotation.pdf (pdf, content read)

### Decision

- **Action:** Wait, nothing to do yet
- **Priority:** P3
- **Confidence:** 0.72
- **Decided by:** model
- **As of:** 2025-02-12T16:10:00+00:00
- **Evidence cited:** event-007, event-017, event-018, event-019, event-005, event-013, fire-door-quotation.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "17",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The paint on the inside of my flat entrance door is flaking, and the door has started catching near the top. Could someone inspect it and let me know what can be done?"
  },
  "property": {
    "address": "14 Lantern Mews, Brindlewick, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "14 Lantern Mews, Brindlewick, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-017-Q1",
        "refs": [
          "fire-door-quotation.pdf"
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
        "amount_gbp": 186.0,
        "vat": "unknown",
        "from": "attachment",
        "ref": "fire-door-quotation.pdf"
      }
    ],
    "invoices": [],
    "approval": {
      "amount_gbp": null,
      "ref": "event-017",
      "covers": "visit"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Offered an inspection visit on 7 February between 10:30 and 12:00.",
      "ref": "event-008"
    }
  ],
  "timeline": {
    "events": 19,
    "first": "2025-02-03T08:20:00+00:00",
    "last": "2025-02-12T16:10:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 3,
      "Email": 9,
      "Note": 3,
      "Call": 2,
      "SMS": 2
    }
  },
  "attachments": [
    {
      "name": "fire-door-quotation.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "WAIT",
    "priority": "P3",
    "confidence": 0.72,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-02-12T16:10:00+00:00",
    "evidence_refs": [
      "event-007",
      "event-017",
      "event-018",
      "event-019",
      "event-005",
      "event-013",
      "fire-door-quotation.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The paint on the inside of my flat entrance door is flaking, and the door has started catching near the top. Could someone inspect it and let me know what can be done?
19 events reviewed, decision as of 2025-02-12T16:10:00+00:00.

## Decision

Pale Finch's quote (NBL-017-Q1, £186, valid to 28 Feb) is on file and was received from the assigned contractor. The property matches (the only address difference is the fuller postcode form). The landlord's event-017 asks whether it can be approved from the repair budget, but it also asks for the scope and the building's response to be confirmed before booking. That is not a clear written approval of the quote, and event-007 only authorised an inspection. The building manager was asked on 12 Feb at 09:30 (event-018), under four hours before the decision time, so a reply is not overdue. Building management has asked twice to be consulted (events 5 and 13), and no work is booked (event-019). Nothing in the case reports danger: the door latches and the tenant reports no access issue (events 1, 15). The building file lists the door as fire-resisting (event-5), and the quote expressly excludes any door or fire-performance inspection. That gap does not need an escalation now, but it should go to the landlord with the approval request. I considered ROUTE_FOR_APPROVAL now. It is premature because the landlord asked for the building response first, and the 12 Feb note (event-19) already told him it is pending. Chasing Ravi is too early. Escalation is not needed because there is no conflict, danger or spend above the £300 limit. This decision would change if Ravi replies, if the landlord gives explicit written approval, or if the tenant reports the door no longer latching. In those cases I would route the quote for approval or escalate.

## Actions taken

- **COMMITTED**: Follow-up at 2025-02-13T16:10:00+00:00, waiting on internal: Building manager (Ravi Dast) reply to the 12 Feb 09:30 scope query is pending. When it arrives, route the £186 quote (NBL-017-Q1) to the landlord for written approval together with the building response. Tell the tenant no work is booked and give advance notice. Raise the unresolved door catching/slow closing and the lack of any door-set inspection with the landlord as a separate question. `followup-1`. Recorded in the local outbox (no external delivery connected).

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '14 Lantern Mews, Brindlewick, ZZ1 1ZZ' vs '14 Lantern Mews' (similarity 0.683). [event-001, event-002, event-003, event-006, event-007, event-008, event-009, event-014, event-015, event-017, event-019, fire-door-quotation.pdf, index]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
