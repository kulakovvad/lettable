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
- **Evidence cited:** event-002, event-005, event-011, event-014, event-015, event-016, event-017, event-018, event-019, event-020, event-021, property-service-quotation.pdf, checkout-report.pdf

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

The case has conflicting versions of fact. Event-20 says the work was done on 23 Sept. Event-21 says the request is still at landlord quote approval, and no landlord approval exists. The workflow's 'approval already obtained' flag (event-2, event-5) has no supporting document. The completion note is an internal agency note, so it is not proof (closing policy). There is no provider confirmation, completion photos, invoice or tenant/landlord confirmation. The quote in event-11 and property-service-quotation.pdf (£180 + VAT = £216) covers only a clean and does not mention removing the listed items, and event-14 says no clarification is recorded. Notes 15 and 16 tie the work to a pending deposit claim, which is a never-touch topic. I rejected CLOSE and telling the landlord the work is done because those rest on an unverified claim. I rejected a plain landlord chase and INSTRUCT_PROVIDER because no approval exists and it is unclear whether work was already done without instruction. The handover also covers whether the keys held by the agency are accounted for. Priority is P2 because there is no safety hazard and the clock is only operational. Property and provider addresses match on both PDFs. The 'Sella' name variant and the differing reference numbers are not material. A person should reconcile the record, then decide on retrospective approval or a chase.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Internal note (event-20) says the clear-out and property service was done on 23 Sept and asks us to tell the landlord. The case has no landlord approval, no provider completion and no invoice. The only quote on file does not cover the item removal. A deposit claim is also recorded as pending before work proceeds. A person needs to establish what happened before anything goes to the landlord.

Respond by 2025-09-25T16:11:00+00:00 (P2, route property_manager).

Conflicts:
- landlord_name: Sella Voss (event-004, event-018, event-019) vs Sella (event-020)
- reference_number: NBL-024-CHECKOUT (checkout-report.pdf) vs NBL-024-Q1 (property-service-quotation.pdf)

Known:
- Property 7 Brackenmere Walk, Vellumford, ZZ1 1ZZ; assigned provider Larkspan Property Care (Perrin Holt) – address matches on both PDFs.
- Request (event-1, checkout-report.pdf): remove items from kitchen drawers, garden storage box, kitchen bins and cellar, then a final property-preparation service.
- Quote (event-11, property-service-quotation.pdf, NBL-024-Q1): £180 + VAT = £216 for an end-of-occupancy clean only (windows, white goods, bathroom, carpets, floors, lights, air fresheners). It does not mention removing the listed items or waste; event-14 notes no clarification on removal is recorded.
- Event-2 and event-5: the workflow carries a 'landlord approval already obtained' flag, but no approval message or document exists. Event-4 to the landlord was informational only.
- Event-17/18: the quote went to landlord Sella Voss for approval on 18 Sept; reminder on 21 Sept (event-19). No landlord reply is recorded. The workflow is still at landlord quote approval (event-21).
- Event-20 (23 Sept) says work was 'done today', but no source is given. There is no provider completion message, no completion photos (promised in event-11), no invoice and no tenant or landlord confirmation. Our agency-held keys are not accounted for.
- Events 15 and 16 say work is on hold pending a deposit claim decision. Deposits are never-touch for the agent.
- The call in event-10 does not establish the agreed scope or price.
- Request: Please obtain a quote for removing the remaining items from the kitchen drawers, garden storage box, kitchen bins and cellar, followed by a final property-preparation service at the vacant home. (request)

Not known:
- Whether landlord approval was ever given, and in what form.
- Who did the work on 23 Sept, if anyone, and under what instruction, since no provider was instructed on this record.
- Whether the item removal was included in or priced within Larkspan's £216, or needs a separate quote.
- Whether the keys were issued to or returned by a contractor.
- How the deposit claim affects whether the work should proceed.
- Whether landlord approval was ever given
- Who performed any work on 23 Sept
- Whether item removal is covered by the quote

Tried:
- Quote requested and chased from Larkspan (events 3, 6, 9); quote received (event-11).
- Approval requested from the landlord 18 Sept (event-18) and reminded 21 Sept (event-19); no reply.
- I did not instruct the provider, chase the landlord or tell the landlord the work is done, because the completion claim and the approval flag are both unverified.
- Agent proposed ESCALATE

Options:
- Recommended: Ask Larkspan to confirm whether it attended on 23 Sept, what it did including the item removal, and to send completion photos and an invoice. Then route the £216 inc VAT (£180 + VAT) to the landlord for retrospective approval if appropriate, and confirm the keys position.
- If nobody instructed any work, treat event-20 as an error, correct the workflow record and keep waiting for the landlord's decision, with a chase to Sella Voss (the reminder is now more than 3 days old).
- Have the person handling the deposit claim confirm whether work should proceed, and clarify the removal scope with Larkspan before any approval is requested.

Recommended: Recommended: Ask Larkspan to confirm whether it attended on 23 Sept, what it did including the item removal, and to send completion photos and an invoice. Then route the £216 inc VAT (£180 + VAT) to the landlord for retrospective approval if appropriate, and confirm the keys position.

## Inconsistencies and mismatches

- **document consistency** (flag): landlord name differs between documents: 'Sella Voss' vs 'Sella' (similarity 0.657). [event-004, event-018, event-019, event-020]
- **document consistency** (flag): reference number differs between documents: 'NBL-024-CHECKOUT' vs 'NBL-024-Q1' (similarity 0.103). [checkout-report.pdf, property-service-quotation.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
