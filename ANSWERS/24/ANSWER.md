# Case 24

**Decision:** Escalate to a person
**Priority:** P2

## Details

### Case

- **Id:** 24
- **Raised by:** Agency
- **Request:** Please obtain a quote for removing the remaining items from the kitchen drawers, garden storage box, kitchen bins and cellar, followed by a final property-preparation service at the vacant home.

### Property

- **Address:** 7 Brackenmere Walk, Vellumford, ZZ1 1ZZ
- **References:** reference NBL-024-CHECKOUT [checkout-report.pdf]; reference NBL-024-Q1 [property-service-quotation.pdf]

### Agency

- **Name:** Elowen Pryce (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 180.00 (VAT excl, provider) [event-011]; GBP 180.00 (VAT unknown, attachment) [property-service-quotation.pdf]; GBP 36.00 (VAT unknown, attachment) [property-service-quotation.pdf]; GBP 216.00 (VAT unknown, attachment) [property-service-quotation.pdf]
- **Deposit:** Internal note says the deposit claim is awaiting a decision before work proceeds. [event-015]; A further wait is recorded while the deposit claim decision is pending. [event-016]

### Timeline

- **Events:** 21, first 2025-09-04T09:01:00+00:00, last 2025-09-24T16:11:00+00:00
- **Channels:** Portal 1, Note 5, Email 9, Update 5, Call 1

### Attachments

- checkout-report.pdf (pdf, content read)
- property-service-quotation.pdf (pdf, content read)

### Decision

- **Action:** Escalate to a person
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-24T16:11:00+00:00
- **Evidence cited:** event-002, event-004, event-005, event-011, event-014, event-015, event-016, event-017, event-018, event-019, event-020, event-021, property-service-quotation.pdf, checkout-report.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "24",
    "title": null,
    "source_role": "Agency",
    "status": null,
    "request": "Please obtain a quote for removing the remaining items from the kitchen drawers, garden storage box, kitchen bins and cellar, followed by a final property-preparation service at the vacant home."
  },
  "property": {
    "address": "7 Brackenmere Walk, Vellumford, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "7 Brackenmere Walk, Vellumford, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-024-CHECKOUT",
        "refs": [
          "checkout-report.pdf"
        ]
      },
      {
        "kind": "reference",
        "value": "NBL-024-Q1",
        "refs": [
          "property-service-quotation.pdf"
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
    "name": "Elowen Pryce (Property Manager, Northbridge Lettings)",
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
        "amount_gbp": 180.0,
        "vat": "excl",
        "from": "provider",
        "ref": "event-011"
      },
      {
        "amount_gbp": 180.0,
        "vat": "unknown",
        "from": "attachment",
        "ref": "property-service-quotation.pdf"
      },
      {
        "amount_gbp": 36.0,
        "vat": "unknown",
        "from": "attachment",
        "ref": "property-service-quotation.pdf"
      },
      {
        "amount_gbp": 216.0,
        "vat": "unknown",
        "from": "attachment",
        "ref": "property-service-quotation.pdf"
      }
    ],
    "invoices": [],
    "approval": {
      "amount_gbp": null,
      "ref": null,
      "covers": "unknown"
    },
    "payments": [],
    "deposit": [
      {
        "text": "Internal note says the deposit claim is awaiting a decision before work proceeds.",
        "amount_gbp": null,
        "ref": "event-015"
      },
      {
        "text": "A further wait is recorded while the deposit claim decision is pending.",
        "amount_gbp": null,
        "ref": "event-016"
      }
    ]
  },
  "appointments": [],
  "timeline": {
    "events": 21,
    "first": "2025-09-04T09:01:00+00:00",
    "last": "2025-09-24T16:11:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Note": 5,
      "Email": 9,
      "Update": 5,
      "Call": 1
    }
  },
  "attachments": [
    {
      "name": "checkout-report.pdf",
      "available": true,
      "kind": "pdf"
    },
    {
      "name": "property-service-quotation.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "ESCALATE",
    "priority": "P2",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-24T16:11:00+00:00",
    "evidence_refs": [
      "event-002",
      "event-004",
      "event-005",
      "event-011",
      "event-014",
      "event-015",
      "event-016",
      "event-017",
      "event-018",
      "event-019",
      "event-020",
      "event-021",
      "property-service-quotation.pdf",
      "checkout-report.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Please obtain a quote for removing the remaining items from the kitchen drawers, garden storage box, kitchen bins and cellar, followed by a final property-preparation service at the vacant home.
21 events reviewed, decision as of 2025-09-24T16:11:00+00:00.

## Decision

Event-20 is an internal note saying the work was "done today", and it conflicts with the rest of the record. The workflow is still at landlord quote approval (event-17, event-21). The landlord has not replied to the approval request (event-18) or the reminder (event-19). The "approval already obtained" flag (event-2, event-5) has no supporting message or document, and event-4 was informational only. Nothing shows Larkspan was instructed, attended, or confirmed completion, and no completion photos are in the case. An agency note is not proof of completion, so I cannot close or tell the landlord the work is done (closing and verify_claims policy). Larkspan's quote (event-11, property-service-quotation.pdf) covers only cleaning tasks. The checkout report and request (event-1, checkout-report.pdf) also require removal of items from the drawers, garden box, bins and cellar. The task lists differ and no clarification is recorded (event-14). The £216 incl. VAT total is under the £300 limit, but the agency has no spend authority and there is no written approval. Events 15 and 16 link the work to a deposit claim decision, which is a never-touch topic. A person needs to establish who did the work and under what authority. A chase to the landlord or a question to the provider alone would not settle that, so I am escalating. The property addresses match across documents, and the differing reference numbers are not a mismatch. The decision would change if written landlord approval or a Larkspan completion confirmation for this property turned up.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

7 Brackenmere Walk: an internal note (event-20) says the clear-out and property service was "done today" (23 Sep). The case has no landlord approval, no instruction to Larkspan, and no completion confirmation from Larkspan, the landlord or any other party. The quote has also never been matched to the requested scope. A deposit claim is linked to the job and needs a person.

Respond by 2025-09-25T16:11:00+00:00 (P2, route property_manager).

Conflicts:
- reference_number: NBL-024-CHECKOUT (checkout-report.pdf) vs NBL-024-Q1 (property-service-quotation.pdf)

Known:
- Landlord Sella Voss was asked to approve the £180 + VAT quote (£216 incl. VAT) on 18 Sep (event-18) and reminded on 21 Sep (event-19). No reply is recorded.
- Event-2 and event-5 carry a 'landlord approval already obtained' flag, but no approval message or document is in the case. Event-4 was informational only. The workflow is still at landlord quote approval (event-17, event-21).
- Larkspan's quote NBL-024-Q1 (event-11, property-service-quotation.pdf) covers only cleaning: windows, white goods and kitchen units, bathroom, carpets, floors, light fittings and air fresheners. It does not mention removing items from the kitchen drawers, garden storage box, kitchen bins or cellar, which the checkout report and request require (checkout-report.pdf, event-1). No clarification is re
- The call on 9 Sep did not establish scope or price (event-10).
- Event-20 is an agency note and is not proof of completion. It does not say who did the work, what was done, or whether it was the Larkspan visit. No completion photos were received, although the contractor said they would send them (event-11).
- Events 15 and 16 say work was on hold pending a deposit claim decision. Deposits are a never-touch topic for the agent.
- The quote and the checkout report carry the correct property address. The reference numbers differ (NBL-024-Q1 and NBL-024-CHECKOUT), which is a different document type and not a mismatch.
- The £216 incl. VAT total is under the £300 limit, but the agency still cannot approve spend, so written landlord approval is required.
- Property: 7 Brackenmere Walk, Vellumford, ZZ1 1ZZ (index)
- Request: Please obtain a quote for removing the remaining items from the kitchen drawers, garden storage box, kitchen bins and cellar, followed by a final property-preparation service at the vacant home. (request)

Not known:
- Who carried out the work on 23 Sep, and under what instruction?
- Did the landlord approve anything in writing outside this record?
- Was item removal done, and is it covered by the £180 quote?
- Is the deposit claim decision a reason to hold the work, and who owns it?
- Are agency-held keys still with the agency or with a contractor?
- Who performed the work on 23 Sep, and under what instruction
- Whether written landlord approval exists
- Whether item removal was done and priced

Tried:
- Quote requested on 4 Sep and chased on 7 Sep.
- Landlord approval requested on 18 Sep and reminded on 21 Sep. No reply.
- Agent proposed ESCALATE

Options:
- Recommended: Check who attended on 23 Sep. Ask Larkspan to confirm in writing what was done, with completion photos and whether item removal was included. Then ask the landlord for written approval or ratification of the quote.
- Chase Sella Voss again, or phone them, for the quote decision. Do not tell them the work is done until Larkspan has confirmed it.
- Handle the deposit-claim link separately. Do not close the case and do not pay any invoice until written approval and an invoice matching the approved amount are on file.

Recommended: Recommended: Check who attended on 23 Sep. Ask Larkspan to confirm in writing what was done, with completion photos and whether item removal was included. Then ask the landlord for written approval or ratification of the quote.

## Inconsistencies and mismatches

- **document consistency** (flag): reference number differs between documents: 'NBL-024-CHECKOUT' vs 'NBL-024-Q1' (similarity 0.243). [checkout-report.pdf, property-service-quotation.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Deposit claim decision (never-touch topic) is cited as a reason the work is on hold
