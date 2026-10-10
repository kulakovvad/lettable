# Case 28

**Decision:** Escalate to a person
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

- **Action:** Escalate to a person
- **Priority:** P3
- **Confidence:** 0.70
- **Decided by:** model
- **As of:** 2025-09-18T14:50:04+00:00
- **Evidence cited:** event-012, event-017, event-020, event-021, event-022, event-023, event-024

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
    "action": "ESCALATE",
    "priority": "P3",
    "confidence": 0.7,
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
      "event-024"
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

The landlord declined the £564.48 Pineglass quote (event-017) and arranged her own contractor, and the provider was stood down (event-020). Her only completion claim (event-021) has no date, photos, invoice or contractor name. Event-022 marked the request complete on that email alone, and event-024 dismissed the workflow task. Agency notes are not proof, so I am not closing yet. Our own event-023 asked which repairs are the former tenant's responsibility so the tenancy account could be reviewed. That touches deposit deductions, which policy says never to act on, so a person must take it over. I rejected WAIT or a chase because event-023 is only about 6 hours old and is not due for a chase. I rejected CLOSE because the invoice position and the actual work are unverified and the cost and responsibility question is still open. The code's "approval in force" flag for £564.48 is wrong: event-012 only asked for approval, and the landlord declined. The reference-number flag is only the normal NBL-028 prefix variants on the documents, and the address matches on both. There is no hazard and no tenant, so priority is P3. If the landlord supplies evidence and a person confirms there is no deduction issue, the case can close.

## Actions taken

- **COMMITTED**: Escalation ticket P3 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Move-out works at 42 Mallowfen Crescent: landlord declined our provider's £564.48 quote and used her own contractor. She says the work is done, with no evidence. Our own message (event-023) also raised former-tenant responsibility and the tenancy account, which is deposit-deduction territory and needs a person.

Respond by 2025-09-21T14:50:04+00:00 (P3, route property_manager).

Conflicts:
- reference_number: NBL-028 (event-001) vs NBL-028-CHECKOUT (checkout-report.pdf) vs NBL-028-Q1 (provider-quotation.pdf)

Known:
- Pineglass quote NBL-028-Q1 for £564.48 (bundled, not itemised) was sent to landlord for approval in event-012. The landlord declined it in event-017 and said she would use her own company.
- Pineglass was told to stand down in event-020. There is no reply from Pineglass and none is needed.
- Landlord email event-021 (2025-09-18) says 'The work has been completed'. It gave no date, photos, invoice or contractor name.
- Event-022 marked the request completed on that email alone. Event-024 dismissed the workflow task.
- Event-023 (2025-09-18 08:46) asked the landlord for an itemised cost breakdown and which repairs she considers the former tenant's responsibility. No reply yet, and it is only about 6 hours old.
- The property is vacant. No tenant is in the case and no keys are recorded as held by a provider.
- The £564.48 quote exceeds the £300 approval limit. The landlord never approved it, so the 'approval in force' flag in the code facts does not apply.
- Property: 42 Mallowfen Crescent, Ternwick, ZZ1 1ZZ (index)
- Request: Following the move-out inspection, arrange attention to the electric meter cabinet door hinges, four nails and paint in Bedroom 1, and sticker residue on the front door. The property is vacant. (request)

Not known:
- Which contractor did the work, and when
- Whether all three items were done: meter cabinet hinges, four nails and paint in Bedroom 1, and front door sticker residue
- What the work cost, and who pays
- Whether any deduction from the former tenant is intended; this is for a person to handle, not the agent
- Contractor identity and completion date
- Whether all three items were completed
- Cost and who pays
- Whether any deduction from the former tenant is intended

Tried:
- Quote requested and chased from Pineglass; the quote arrived 2025-09-10.
- Landlord approval requested (event-012, event-015).
- Provider stood down (event-020).
- Cost breakdown and responsibility question sent to landlord (event-023).
- Agent proposed ESCALATE

Options:
- Recommended: Take over the deposit/tenancy-account question, and decide whether the cost breakdown request in event-023 should stand. Any reply from the landlord should be handled by a person.
- Ask the landlord for completion evidence (photos, contractor invoice or name) and confirm the invoice position as landlord pays directly. Then close the case once those are in.
- Reopen the request status until evidence arrives, because event-022 marked it complete on an unsupported claim.

Recommended: Recommended: Take over the deposit/tenancy-account question, and decide whether the cost breakdown request in event-023 should stand. Any reply from the landlord should be handled by a person.

## Inconsistencies and mismatches

- **document consistency** (flag): reference number differs between documents: 'NBL-028' vs 'NBL-028-CHECKOUT' vs 'NBL-028-Q1' (similarity 0.58). [checkout-report.pdf, event-001, provider-quotation.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Former-tenant responsibility and tenancy account review (deposit-related, never_touch)
