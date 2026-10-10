# Case 25

**Decision:** Ask the provider for more information
**Priority:** P3

## Details

### Case

- **Id:** 25
- **Raised by:** Tenant
- **Request:** The kitchen mixer tap is constantly dripping and wasting water. The water looks cloudy when I fill a glass. I suspect limescale may be involved and would like to know whether a new tap could be considered.

### Property

- **Address:** 18 Thistlewick Row, Fenmere, ZZ1 1ZZ
- **References:** reference NBL-025-INV-15 [corrected-plumbing-invoice.pdf]

### Agency

- **Name:** Tessa Wren (Property Manager, Northbridge Lettings)

### Appointments

- Offers 11, 13 and 14 August, all day, for an appointment. [event-007]
- Confirms a visit for 10 September, with timing potentially varying because the contractor needs to collect keys from the office. [event-016]

### Timeline

- **Events:** 22, first 2025-08-04T18:10:50+00:00, last 2025-09-15T11:11:18+00:00
- **Channels:** Portal 1, Email 17, Call 2, Document 2

### Attachments

- corrected-plumbing-invoice.pdf (pdf, content read)

### Decision

- **Action:** Ask the provider for more information
- **Priority:** P3
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-15T11:11:18+00:00
- **Evidence cited:** event-022, event-019, event-021, event-003, event-012, event-015, corrected-plumbing-invoice.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "25",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The kitchen mixer tap is constantly dripping and wasting water. The water looks cloudy when I fill a glass. I suspect limescale may be involved and would like to know whether a new tap could be considered."
  },
  "property": {
    "address": "18 Thistlewick Row, Fenmere, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "18 Thistlewick Row, Fenmere, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-025-INV-15",
        "refs": [
          "corrected-plumbing-invoice.pdf"
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
    "name": "Tessa Wren (Property Manager, Northbridge Lettings)",
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
      "amount_gbp": null,
      "ref": null,
      "covers": "unknown"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Offers 11, 13 and 14 August, all day, for an appointment.",
      "ref": "event-007"
    },
    {
      "when_text": "Confirms a visit for 10 September, with timing potentially varying because the contractor needs to collect keys from the office.",
      "ref": "event-016"
    }
  ],
  "timeline": {
    "events": 22,
    "first": "2025-08-04T18:10:50+00:00",
    "last": "2025-09-15T11:11:18+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 17,
      "Call": 2,
      "Document": 2
    }
  },
  "attachments": [
    {
      "name": "corrected-plumbing-invoice.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "ASK_PROVIDER",
    "priority": "P3",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-15T11:11:18+00:00",
    "evidence_refs": [
      "event-022",
      "event-019",
      "event-021",
      "event-003",
      "event-012",
      "event-015",
      "corrected-plumbing-invoice.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The kitchen mixer tap is constantly dripping and wasting water. The water looks cloudy when I fill a glass. I suspect limescale may be involved and would like to know whether a new tap could be considered.
22 events reviewed, decision as of 2025-09-15T11:11:18+00:00.

## Decision

The corrected invoice (event-22, corrected-plumbing-invoice.pdf) now has the right address and the right provider, so the earlier postcode problem (event-19, event-20) is resolved. It still can't be passed on or closed. It shows no amount, no VAT, no completion date and no itemisation. There is no quote in the case and no approval for any amount: the landlord's only approval (event-3) was for "maintenance works" generally. The case also contains no completion confirmation from the provider or the tenant, and nothing on whether the spare key was returned (event-15, event-16). The tenant's drawer defect (event-12) has had no reply. The boiler matter raised on the call (event-21) isn't part of this job, and I promised to check it. I am asking the provider for an itemised invoice, completion date, quote and key return. Escalation isn't needed, because the provider can supply these facts. Once I have them I can route the invoice to the landlord for approval, or ask the landlord if the amount is above the approved sum. Nothing can be paid or closed until then.

## Actions taken

- **COMMITTED**: Message to provider (request_info, P3) `message-1`. Recorded in the local outbox (no external delivery connected).

### Message to provider `message-1`

Hello Ivo, thank you for the corrected invoice NBL-025-INV-15. The postcode now matches 18 Thistlewick Row. Before we can pass it to the landlord, please send an itemised invoice that shows: (1) the total amount, with VAT shown separately, and the cost of the tap and of labour; (2) the date you attended and completed the tap replacement at 18 Thistlewick Row; (3) confirmation that the spare key has been returned to our office. We have no quote on file for this job, so please send any quote you gave. The invoice does not show a price. Nothing can be paid until we have this. Separately, we will check the boiler matter you mentioned with the relevant engineer. It is not part of this tap job. Kind regards, Tessa Wren, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Tenant reports a loose top kitchen drawer with snapped metal front brackets (event-12), which needs its own request.
- Boiler matter mentioned by the contractor on the call (event-21): I said I would check with the relevant engineer. It is not documented as part of this job.
