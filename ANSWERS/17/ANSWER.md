# Case 17

**Decision:** Wait, nothing to do yet
**Priority:** P2

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
- **Priority:** P2
- **Confidence:** 0.70
- **Decided by:** model
- **As of:** 2025-02-12T16:10:00+00:00
- **Evidence cited:** event-017, event-018, event-013, event-005, event-011, event-014, fire-door-quotation.pdf

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
    "priority": "P2",
    "confidence": 0.7,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-02-12T16:10:00+00:00",
    "evidence_refs": [
      "event-017",
      "event-018",
      "event-013",
      "event-005",
      "event-011",
      "event-014",
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

The job is a flaking-paint and catching-door report at 14 Lantern Mews. Pale Finch Decorating inspected on 7 Feb (event-10) and quoted £186 (fire-door-quotation.pdf, event-11). The quote is below the £300 threshold, but the agency cannot approve spend. The landlord's event-17 asks whether it can be approved "from the repair budget" and wants the scope and the building response confirmed before booking. That is not a clear written approval, so I am not instructing the provider. I am also not routing for approval yet. The building manager's reply to our scope query of 12 Feb 09:30 (event-18) is pending and is not overdue. The building manager has repeatedly asked to be consulted about the door (events 5, 13). The building file lists the flat entrance doors as fire-resisting (event-5). Slow closing was noted before (event-13). The quote excludes any door-set or fire-door inspection, adjustment or hardware work, and makes no statement on the door's fire performance. The landlord's question in event-14 about further inspection costs is unanswered. No danger is reported: the door latches with a firm pull and the tenant reports no access issue (events 1, 15). So this is P2, not P0 or P1, and not an escalation. The quote address matches the job (the document check flag is only a postcode-format difference). The tenant was sent an update (message-1) with no cost promises. A follow-up is set. This decision would change if the building manager replies (then route the quote for approval), if the door stops latching (then escalate as a safety risk), or if the building manager does not reply (then chase).

## Actions taken

- **HELD_FOR_REVIEW**: Message to tenant (update, P2) `message-1`. Held: not part of the final action WAIT; a person can release it.
- **COMMITTED**: Follow-up at 2025-02-14T16:10:00+00:00, waiting on internal: Building manager's reply to the 12 Feb scope query (event-018) is pending. Once it arrives, route the £186 quote for the landlord's written approval with the building response and the exclusions stated. Chase the building manager if there is no reply, and ask the landlord whether to commission a competent door inspection (event-014 question still open). `followup-2`. Recorded in the local outbox (no external delivery connected).

### Message to tenant `message-1`

Hi Iona, thank you for your update on 10 February. A contractor's quotation for repainting the flat-side face of the door is on file. It covers decorating only. It does not include adjusting the door or checking how it closes. We are waiting for the building manager to confirm whether any approval or specific process applies, and the landlord has asked for that before any work is booked. Nothing is booked yet. We will give you advance notice before any access, and we will keep to your preference for visits after 10:00. We will come back to you on your question about whether painting would affect the door once we have the building manager's response. In the meantime, please tell us if the door stops latching or becomes harder to close. Northbridge Lettings (Maya Chen)

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '14 Lantern Mews, Brindlewick, ZZ1 1ZZ' vs '14 Lantern Mews' (similarity 0.69). [event-001, event-002, event-003, event-006, event-007, event-008, event-009, event-014, event-015, event-017, event-019, fire-door-quotation.pdf, index]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
