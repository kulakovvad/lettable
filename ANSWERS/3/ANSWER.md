# Case 3

**Decision:** Ask the provider for more information
**Priority:** P2

## Details

### Case

- **Id:** 3
- **Raised by:** Tenant
- **Request:** The tenant reports that the kitchen tap drips and the bathroom hot tap drips and is difficult to shut off. During heavy rain, water drips through the bathroom vent. Damp patches have appeared on the ceiling and wall of the smaller bedroom. Photos were supplied with the report.

### Property

- **Address:** Flat 4, 8-12 Juniper Mews, Vellumford, ZZ1 1ZZ
- **References:** reference NBL-003-INV-14 [tap-works-invoice.pdf]

### Agency

- **Name:** Priya Nair (Property Manager, Northbridge Lettings)

### Money

- **Landlord approval:** for the visit, no amount [event-004]

### Appointments

- Offered several all-day options, including Friday 12 September, and said the contractor could collect keys from Northbridge Lettings and attend while the tenant [event-007]
- Confirmed the proposed Friday 12 September visit at around 09:00. [event-011]
- Updated the landlord that a contractor visit was booked for Friday 12 September. [event-012]
- The earlier cancellation request was superseded; the revised appointment remained on 12 September. [event-017]
- Confirmed the revised appointment for Friday 12 September, late morning. [event-019]

### Timeline

- **Events:** 23, first 2025-09-03T17:43:15+00:00, last 2025-09-14T09:20:00+00:00
- **Channels:** Portal 1, Email 13, Note 3, SMS 2, Call 2, Update 1, Document 1

### Attachments

- tap-works-invoice.pdf (pdf, content read)

### Decision

- **Action:** Ask the provider for more information
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-14T09:20:00+00:00
- **Evidence cited:** event-022, tap-works-invoice.pdf, event-001, event-004, event-014, event-015, event-020, event-021

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "3",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The tenant reports that the kitchen tap drips and the bathroom hot tap drips and is difficult to shut off. During heavy rain, water drips through the bathroom vent. Damp patches have appeared on the ceiling and wall of the smaller bedroom. Photos were supplied with the report."
  },
  "property": {
    "address": "Flat 4, 8-12 Juniper Mews, Vellumford, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "Flat 4, 8-12 Juniper Mews, Vellumford, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-003-INV-14",
        "refs": [
          "tap-works-invoice.pdf"
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
    "name": "Priya Nair (Property Manager, Northbridge Lettings)",
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
      "ref": "event-004",
      "covers": "visit"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Offered several all-day options, including Friday 12 September, and said the contractor could collect keys from Northbridge Lettings and attend while the tenant",
      "ref": "event-007"
    },
    {
      "when_text": "Confirmed the proposed Friday 12 September visit at around 09:00.",
      "ref": "event-011"
    },
    {
      "when_text": "Updated the landlord that a contractor visit was booked for Friday 12 September.",
      "ref": "event-012"
    },
    {
      "when_text": "The earlier cancellation request was superseded; the revised appointment remained on 12 September.",
      "ref": "event-017"
    },
    {
      "when_text": "Confirmed the revised appointment for Friday 12 September, late morning.",
      "ref": "event-019"
    }
  ],
  "timeline": {
    "events": 23,
    "first": "2025-09-03T17:43:15+00:00",
    "last": "2025-09-14T09:20:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 13,
      "Note": 3,
      "SMS": 2,
      "Call": 2,
      "Update": 1,
      "Document": 1
    }
  },
  "attachments": [
    {
      "name": "tap-works-invoice.pdf",
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
    "as_of": "2025-09-14T09:20:00+00:00",
    "evidence_refs": [
      "event-022",
      "tap-works-invoice.pdf",
      "event-001",
      "event-004",
      "event-014",
      "event-015",
      "event-020",
      "event-021"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The tenant reports that the kitchen tap drips and the bathroom hot tap drips and is difficult to shut off. During heavy rain, water drips through the bathroom vent. Damp patches have appeared on the ceiling and wall of the smaller bedroom. Photos were supplied with the report.
23 events reviewed, decision as of 2025-09-14T09:20:00+00:00.

## Decision

The invoice (event-022, tap-works-invoice.pdf) from the assigned provider Copper Finch lists the property as Flat 4, 28 Larkspur Quay, Brindlewick. Our job is Flat 4, 8-12 Juniper Mews, Vellumford (event-001). That is a property mismatch under verify_claims, so I will not close, pay, forward the invoice or report the work as done on it. The invoice also shows no amount, and no quote or cost approval exists. The landlord approved only attendance (event-004). The contractor's completion messages are contradictory: "job done today" on 11 Sept (event-014) was corrected the next message (event-015), and the visit took place on 12 Sept (event-020). Nothing in the case shows the vent leak or bedroom damp were investigated (event-021). Damp has been reported with no health impact or vulnerable occupants, and no active danger is stated, so I set P2 rather than P1. The right step is a specific question to the invoice's sender, not escalation: ask which property it relates to, request a corrected itemised invoice, and ask for the visit report on the vent and damp. The landlord's separate requests about insurance and roof-leak history (event-004) have no recorded follow-up. The case cannot close while the damp and vent issues are unresolved. If the provider confirms the wrong property or disputes the address, a person should review it.

## Actions taken

- **COMMITTED**: Message to provider (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).

### Message to provider `message-1`

Hi Gareth, thanks for invoice NBL-003-INV-14 dated 14 September 2025. It lists the property as Flat 4, 28 Larkspur Quay, Brindlewick, ZZ1 1ZZ. Our job, and your visit on Friday 12 September, was for Flat 4, 8-12 Juniper Mews, Vellumford, ZZ1 1ZZ. Please confirm which property the invoice relates to and, if it is the wrong one, send a corrected invoice for Juniper Mews. We can't process it until this is clear. The invoice also shows no amounts. Please include an itemised cost on the corrected version. Separately, your visit report is still outstanding. Please tell us whether you looked at the rainwater coming through the bathroom vent and the damp patches in the smaller bedroom, and what you found. Kind regards, Priya Nair, Northbridge Lettings

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: 'Flat 4, 8-12 Juniper Mews, Vellumford, ZZ1 1ZZ' vs '8-10 Juniper Mews' vs '8-12 Juniper Mews, Flat 4' vs 'Flat 4, 28 Larkspur Quay, Brindlewick, ZZ1 1ZZ' (similarity 0.21). [event-020, index, tap-works-invoice.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Landlord's request to check building insurance cover (event-004), not actioned
- Landlord's request to review the flat's roof-leak history (event-004), not actioned
