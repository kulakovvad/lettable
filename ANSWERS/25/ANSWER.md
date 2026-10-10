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
- **Confidence:** 0.75
- **Decided by:** model
- **As of:** 2025-09-15T11:11:18+00:00
- **Evidence cited:** event-022, event-019, event-020, event-021, event-003, event-016, event-018, event-012

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
    "confidence": 0.75,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-15T11:11:18+00:00",
    "evidence_refs": [
      "event-022",
      "event-019",
      "event-020",
      "event-021",
      "event-003",
      "event-016",
      "event-018",
      "event-012"
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

The corrected invoice (event-22, corrected-plumbing-invoice.pdf) now shows the right property and the assigned provider, so the postcode query in event-19/20 is resolved. However we cannot close or forward it. The invoice shows no amount, and no quote or landlord-approved amount exists. Landlord approval (event-3) covered only general maintenance works and a visit, not a quote. No event records the visit date, completion, or that the new tap was fitted. The contractor was told he could collect the spare key (events 16, 18), and no event confirms its return. The cloudy-water concern and tenant's drawer defect (event-12) are unanswered. The boiler mention in event-21 is undocumented for this job. Escalation is not needed because the provider can supply these facts. I asked for the date, completion confirmation, an itemised amount and key return. The amount will then go to the landlord for approval if needed; the agency cannot approve spend. A tap replacement was not explicitly approved by the landlord either.

## Actions taken

- **COMMITTED**: Message to provider (request_info, P3) `message-1`. Recorded in the local outbox (no external delivery connected).

### Message to provider `message-1`

Hello Ivo, thank you for the corrected invoice NBL-025-INV-15; the postcode now matches our record for 18 Thistlewick Row. Before we can process it, please could you send: (1) the date you attended and confirmation that the new mono kitchen tap was fitted and the drip is fixed; (2) the invoice amount itemised (labour, tap, VAT), as the document shows no amount and we hold no quote for it; (3) confirmation that you returned the spare key to our office. Please also confirm whether you noted anything about the cloudy water while you were there. Kind regards, Tessa Wren, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Tenant reports loose top kitchen drawer with snapped metal brackets (event-12) needs its own request
- Boiler matter mentioned on call (event-21) is separate; check with the relevant engineer
