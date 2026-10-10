# Case 13

**Decision:** Ask the provider for more information
**Priority:** P2

## Details

### Case

- **Id:** 13
- **Raised by:** Tenant
- **Request:** The kitchen glazing has been misted between the panes for some time. Water gathers around the frame, the kitchen feels very cold, and I am concerned about damp, particularly in winter. The sash opens, closes and locks. There are pets in the home.

### Property

- **Address:** 8 Brackenmere Walk, Vellumbrook, ZZ1 1ZZ
- **References:** reference NBL-013-INV-09 [glazing-invoice.pdf]

### Agency

- **Name:** Tamsin Rook (Property Manager, Northbridge Lettings)

### Money

- **Landlord approval:** GBP 180.00 [event-010]

### Timeline

- **Events:** 24, first 2025-07-31T08:11:00+00:00, last 2025-09-10T10:10:00+00:00
- **Channels:** Email 17, Note 3, Call 2, Document 1, Update 1

### Attachments

- glazing-invoice.pdf (pdf, content read)

### Decision

- **Action:** Ask the provider for more information
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-10T10:10:00+00:00
- **Evidence cited:** event-023, event-021, event-010, event-011, event-009, event-022, glazing-invoice.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "13",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The kitchen glazing has been misted between the panes for some time. Water gathers around the frame, the kitchen feels very cold, and I am concerned about damp, particularly in winter. The sash opens, closes and locks. There are pets in the home."
  },
  "property": {
    "address": "8 Brackenmere Walk, Vellumbrook, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "8 Brackenmere Walk, Vellumbrook, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-013-INV-09",
        "refs": [
          "glazing-invoice.pdf"
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
    "name": "Tamsin Rook (Property Manager, Northbridge Lettings)",
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
      "amount_gbp": 180.0,
      "ref": "event-010",
      "covers": "amount"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [],
  "timeline": {
    "events": 24,
    "first": "2025-07-31T08:11:00+00:00",
    "last": "2025-09-10T10:10:00+00:00",
    "waiting_on": null,
    "channels": {
      "Email": 17,
      "Note": 3,
      "Call": 2,
      "Document": 1,
      "Update": 1
    }
  },
  "attachments": [
    {
      "name": "glazing-invoice.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "ASK_PROVIDER",
    "priority": "P2",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-10T10:10:00+00:00",
    "evidence_refs": [
      "event-023",
      "event-021",
      "event-010",
      "event-011",
      "event-009",
      "event-022",
      "glazing-invoice.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The kitchen glazing has been misted between the panes for some time. Water gathers around the frame, the kitchen feels very cold, and I am concerned about damp, particularly in winter. The sash opens, closes and locks. There are pets in the home.
24 events reviewed, decision as of 2025-09-10T10:10:00+00:00.

## Decision

The invoice (glazing-invoice.pdf, event-23) is from the assigned provider, Clearfirth Glazing. It names the correct property and its reference is consistent, but its Amount field is blank. We therefore cannot compare it with the landlord's approval. The landlord's conditional reply (event-10) was happy if £180 was the total. Our own request (event-11) then stated £150 plus VAT, so the approval record is somewhat ambiguous, although £180 including VAT is consistent with £150 plus VAT (event-9). Nothing in the case confirms the work was done. The last provider contact (event-21, 2 Sept) said the glass had still not arrived, and no visit or appointment is recorded. The note at event-22 moving the case to post-visit documents is not proof of completion. The tenant also wanted to be present for the visit (event-14). Closing is therefore not possible. Routing for approval is not possible either without an amount. The provider holds both facts, so I asked for an itemised invoice with the amount and for confirmation of fitting. Escalation is not needed. Nothing is unsafe: the sash locks, and the damp concern is not a reported health impact. The earlier damp concern has no site assessment recorded (event-5). That is a point to revisit once the glass is fitted. I scheduled a follow-up in 72 hours. The decision would change if the invoice amount exceeds £180, which would go back to the landlord, or if the provider says the work was not done.

## Actions taken

- **COMMITTED**: Message to provider (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-13T10:10:00+00:00, waiting on provider: Awaiting invoice with amount and confirmation that the glass was fitted `followup-2`. Held: not part of the final action ASK_PROVIDER; a person can release it.

### Message to provider `message-1`

Hello Sella, we have received invoice NBL-013-INV-09 dated 10 September 2025 for 8 Brackenmere Walk (supply and fit 1 pane of glass to the kitchen glazing). The amount field is blank, so we cannot check it against the landlord's approval. Please could you send a copy showing the amount, with VAT shown separately? Please also confirm whether the glass has arrived and the pane has been fitted. If it has, tell us the date of the visit. If it has not, tell us the expected delivery and fitting date. The tenant asked to be present for the visit. Thank you, Tamsin Rook, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Tenant's wider damp and cold concern in the kitchen has had no site assessment (event-5)
