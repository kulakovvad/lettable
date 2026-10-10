# Case 28

**Decision:** Wait, nothing to do yet
**Priority:** P3

## Details

### Case

- **Id:** 28
- **Raised by:** Agency
- **Request:** Following the move-out inspection, arrange attention to the electric meter cabinet door hinges, four nails and paint in Bedroom 1, and sticker residue on the front door. The property is vacant.

### Property

- **Address:** 42 Mallowfen Crescent, Ternwick, ZZ1 1ZZ
- **References:** reference NBL-028-CHECKOUT [checkout-report.pdf]; reference NBL-028-Q1 [provider-quotation.pdf]

### Agency

- **Name:** Talia Wren (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 564.48 (VAT unknown, attachment) [provider-quotation.pdf]
- **Landlord approval:** GBP 564.48 [event-012]

### Timeline

- **Events:** 25, first 2025-09-04T10:50:28+00:00, last 2025-09-18T14:50:04+00:00
- **Channels:** Note 8, Email 12, Update 3, Call 2

### Attachments

- checkout-report.pdf (pdf, content read)
- provider-quotation.pdf (pdf, content read)

### Decision

- **Action:** Wait, nothing to do yet
- **Priority:** P3
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-18T14:50:04+00:00
- **Evidence cited:** event-012, event-017, event-020, event-021, event-022, event-023, event-024, event-025

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "28",
    "title": null,
    "source_role": "Agency",
    "status": null,
    "request": "Following the move-out inspection, arrange attention to the electric meter cabinet door hinges, four nails and paint in Bedroom 1, and sticker residue on the front door. The property is vacant."
  },
  "property": {
    "address": "42 Mallowfen Crescent, Ternwick, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "42 Mallowfen Crescent, Ternwick, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-028-CHECKOUT",
        "refs": [
          "checkout-report.pdf"
        ]
      },
      {
        "kind": "reference",
        "value": "NBL-028-Q1",
        "refs": [
          "provider-quotation.pdf"
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
    "name": "Talia Wren (Property Manager, Northbridge Lettings)",
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
        "amount_gbp": 564.48,
        "vat": "unknown",
        "from": "attachment",
        "ref": "provider-quotation.pdf"
      }
    ],
    "invoices": [],
    "approval": {
      "amount_gbp": 564.48,
      "ref": "event-012",
      "covers": "amount"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [],
  "timeline": {
    "events": 25,
    "first": "2025-09-04T10:50:28+00:00",
    "last": "2025-09-18T14:50:04+00:00",
    "waiting_on": null,
    "channels": {
      "Note": 8,
      "Email": 12,
      "Update": 3,
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
      "name": "provider-quotation.pdf",
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
    "as_of": "2025-09-18T14:50:04+00:00",
    "evidence_refs": [
      "event-012",
      "event-017",
      "event-020",
      "event-021",
      "event-022",
      "event-023",
      "event-024",
      "event-025"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Following the move-out inspection, arrange attention to the electric meter cabinet door hinges, four nails and paint in Bedroom 1, and sticker residue on the front door. The property is vacant.
25 events reviewed, decision as of 2025-09-18T14:50:04+00:00.

## Decision

The landlord declined the Pineglass quote of £564.48 (event-017) and chose her own contractor. We stood Pineglass down (event-018, event-020). The £564.48 was never approved: event-012 only asked for approval, and the "approval in force" flag in the code facts is wrong. On 18 Sept the landlord wrote that the work is complete (event-021). That is a claim only, with no date, photos, contractor name or invoice. Oren's "completed" marking (event-022) is a system note and is not proof (closing policy). We asked the landlord for an itemised cost breakdown and any responsibility allocation (event-023) about 6 hours before the decision time, so no reply is due yet. The chase threshold is 3 days. Closing is blocked because our own question is unanswered and the invoice position is unknown. Escalating is not needed: there is no hazard, no dispute, and no sign of fraud, and the property is vacant. The reference-number flag is only the usual suffixes on NBL-028, and both PDFs show the correct address. If the landlord's reply raises tenant charges, deposit deductions or the tenancy account, it must go to a person, because that is never_touch. Event-023 mentioned reviewing the tenancy account, so a person should be aware of that. If there is no reply by about 21 Sept, chase the landlord. Once the invoice position and completion are confirmed, close. The workflow task was dismissed (event-024), so I have set a follow-up to keep the case from being forgotten.

## Actions taken

- **COMMITTED**: Follow-up at 2025-09-21T14:50:04+00:00, waiting on landlord: Awaiting landlord reply to event-023 (itemised costs of own-contractor works, invoice position). Chase is due after 3 days. Any reply that raises tenant responsibility or deposit deductions goes to a person. Case should not be closed until the invoice position and works are confirmed. `followup-1`. Recorded in the local outbox (no external delivery connected).

## Inconsistencies and mismatches

- **document consistency** (flag): reference number differs between documents: 'NBL-028' vs 'NBL-028-CHECKOUT' vs 'NBL-028-Q1' (similarity 0.56). [checkout-report.pdf, event-001, provider-quotation.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
