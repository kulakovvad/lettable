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
- **Evidence cited:** event-023, event-010, event-011, event-012, event-021, event-014, glazing-invoice.pdf

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
      "event-010",
      "event-011",
      "event-012",
      "event-021",
      "event-014",
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

Clearfirth (assigned, event-6) invoice NBL-013-INV-09 (event-23, glazing-invoice.pdf) matches the property and the work description, but the Amount is blank, so I cannot compare it with the approval. The landlord's approval is ambiguous: event-10 was conditional on £180 being the total, while event-11 described £150 plus VAT, and event-12 recorded approval. Both come to £180 including VAT, so the invoice must show £180 or less. There is also no completion evidence: the last provider contact (event-21) said the glass had not arrived, and no visit was arranged. The tenant wanted to be present (event-14), and the 'awaiting post-visit documents' note (event-22) is internal and not proof. I am therefore not closing and not forwarding the invoice. I am asking the provider for an invoice with the amount and VAT shown, and for confirmation of whether the pane was fitted, when, and who was present. Escalating is not needed: this is a routine missing fact held by the provider. The damp and cold concern (event-1) has no health impact or vulnerable occupant reported and was never assessed (event-5). It should be raised with the landlord or a person after the glazing is done, since fitting a pane does not itself resolve damp. If the invoice exceeds £180 it goes back to the landlord for approval.

## Actions taken

- **COMMITTED**: Message to provider (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).

### Message to provider `message-1`

Hello Sella, we have received Clearfirth Glazing invoice NBL-013-INV-09 dated 10 September 2025 for 8 Brackenmere Walk (supply and fit 1 pane of glass to the kitchen glazing). The amount field on our copy is blank, so please send a copy showing the amount, with any VAT itemised. Our last update (2 September) was that the glass had not arrived and no appointment had been arranged. Please also confirm whether the pane has been fitted, and if so on what date and who was present, as the tenant asked to be at the visit. If it has not been fitted yet, please give the expected delivery and fitting dates. Kind regards, Tamsin Rook, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Tenant's wider damp and cold concern in the kitchen was never assessed; follow up after the glazing is complete
