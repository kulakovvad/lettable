# Case 15

**Decision:** Escalate to a person
**Priority:** P2

## Details

### Case

- **Id:** 15
- **Raised by:** Agency
- **Request:** Please arrange post-tenancy sanitation, removal of waste left inside the property, and clearance of the rear garden.

### Property

- **Address:** 18 Thistlevaunt Lane, Orvelune, ZZ1 1ZZ
- **References:** reference NBL-015-INSPECTION [move-out-inspection-report.pdf]; reference NBL-015-Q1 [property-preparation-quotation.pdf]

### Agency

- **Name:** Mira Venn (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 665.00 (VAT unknown, provider) [event-006]; GBP 665.00 (VAT unknown, attachment) [property-preparation-quotation.pdf]
- **Landlord approval:** GBP 665.00 [event-016]
- **Deposit:** Reported that post-tenancy costs and tenant-attributed damage together exceed the £650 deposit held, and that a claim for the full deposit amount was being prepared through the deposit process. (GBP 650.00) [event-011]; Asked the contractor not to book the work until further notice while the deposit dispute was being handled. [event-012]

### Timeline

- **Events:** 21, first 2025-09-03T18:04:18+00:00, last 2025-09-25T08:34:11+00:00
- **Channels:** Note 3, Email 15, Update 2, Call 1

### Attachments

- move-out-inspection-report.pdf (pdf, content read)
- property-preparation-quotation.pdf (pdf, content read)

### Decision

- **Action:** Escalate to a person
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-25T08:34:11+00:00
- **Evidence cited:** event-006, event-007, event-008, event-009, event-010, event-011, event-012, event-016, event-021

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "15",
    "title": null,
    "source_role": "Agency",
    "status": null,
    "request": "Please arrange post-tenancy sanitation, removal of waste left inside the property, and clearance of the rear garden."
  },
  "property": {
    "address": "18 Thistlevaunt Lane, Orvelune, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "18 Thistlevaunt Lane, Orvelune, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-015-INSPECTION",
        "refs": [
          "move-out-inspection-report.pdf"
        ]
      },
      {
        "kind": "reference",
        "value": "NBL-015-Q1",
        "refs": [
          "property-preparation-quotation.pdf"
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
    "name": "Mira Venn (Property Manager, Northbridge Lettings)",
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
        "amount_gbp": 665.0,
        "vat": "unknown",
        "from": "provider",
        "ref": "event-006"
      },
      {
        "amount_gbp": 665.0,
        "vat": "unknown",
        "from": "attachment",
        "ref": "property-preparation-quotation.pdf"
      }
    ],
    "invoices": [],
    "approval": {
      "amount_gbp": 665.0,
      "ref": "event-016",
      "covers": "amount"
    },
    "payments": [],
    "deposit": [
      {
        "text": "Reported that post-tenancy costs and tenant-attributed damage together exceed the £650 deposit held, and that a claim for the full deposit amount was being prepared through the deposit process.",
        "amount_gbp": 650.0,
        "ref": "event-011"
      },
      {
        "text": "Asked the contractor not to book the work until further notice while the deposit dispute was being handled.",
        "amount_gbp": null,
        "ref": "event-012"
      }
    ]
  },
  "appointments": [],
  "timeline": {
    "events": 21,
    "first": "2025-09-03T18:04:18+00:00",
    "last": "2025-09-25T08:34:11+00:00",
    "waiting_on": null,
    "channels": {
      "Note": 3,
      "Email": 15,
      "Update": 2,
      "Call": 1
    }
  },
  "attachments": [
    {
      "name": "move-out-inspection-report.pdf",
      "available": true,
      "kind": "pdf"
    },
    {
      "name": "property-preparation-quotation.pdf",
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
    "as_of": "2025-09-25T08:34:11+00:00",
    "evidence_refs": [
      "event-006",
      "event-007",
      "event-008",
      "event-009",
      "event-010",
      "event-011",
      "event-012",
      "event-016",
      "event-021"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Please arrange post-tenancy sanitation, removal of waste left inside the property, and clearance of the rear garden.
21 events reviewed, decision as of 2025-09-25T08:34:11+00:00.

## Decision

The landlord's approval of the £665 quote is conditional on bond recovery (event-8, event-10). That makes the case a deposit matter, which is a never_touch topic, and the code flagged it at event-12 (forcing escalation). Event-16, "approved quote", does not say which quote it covers or whether the bond condition still applies. It may refer to the separate maintenance quote. Event-9 told the contractor the quote was approved without the condition, so the instructions are inconsistent. Event-7 did not list the carpet or garden tasks, and the quote does not expressly cover the disturbed soil (event-6). The work is on hold until separate maintenance is scheduled (event-15, 18, 20, 21), and nothing is booked. A tenant wants to move in on 28 September. Waiting would not resolve the deposit or approval ambiguity, and instructing the contractor would risk work the landlord has not clearly approved. Escalating to the property manager is therefore the right step, not a chase. The quote's address matches the job, and the reference mismatch only reflects two different document types, so no document fraud is suspected. There is no safety hazard, so priority is P2 because of the move-in date. If the landlord confirms unconditional approval of the £665 quote and the maintenance is scheduled, the contractor can be instructed.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Post-tenancy sanitation/waste/garden job at 18 Thistlevaunt Lane is on hold. The landlord's approval of the £665 quote is tied to bond recovery, which is a deposit matter the agent cannot decide. Their later "approved quote" (event-16) is ambiguous. A prospective tenant wants to move in on 28 September, and the work is still not booked.

Respond by 2025-09-26T08:34:11+00:00 (P2, route property_manager).

Conflicts:
- reference_number: NBL-015-INSPECTION (move-out-inspection-report.pdf) vs NBL-015-Q1 (property-preparation-quotation.pdf)

Known:
- Quote £665 from Brindlewick Turnover Services (event-6, property-preparation-quotation.pdf), property address matches the job.
- Landlord event-8 and event-10: approval only if costs are recovered from the former tenants' bond. Event-9 told the contractor the quote was approved without mentioning that condition.
- Event-11: agency told the landlord that costs plus damage exceed the £650 deposit and that a full-deposit claim was being prepared. Event-12: contractor told to hold because of the deposit dispute.
- Event-16 (17 Sep): landlord wrote only 'approved quote', with no quote identified and no statement on the bond condition. It may refer to the separate maintenance quote.
- Event-7: the approval request did not list the carpet or garden tasks. Quote scope does not expressly cover making good the disturbed soil (event-6).
- Event-15/18/20/21: work is held until separate major maintenance is scheduled, and no completion date is recorded. Contractor has offered no confirmed slot (event-19, event-20).
- Inspection report (event-4/5): wrong report was first sent to the contractor and corrected in event-5. The current report is attached. Reference numbers differ only because the documents are different types.
- Property: 18 Thistlevaunt Lane, Orvelune, ZZ1 1ZZ (index)
- Request: Please arrange post-tenancy sanitation, removal of waste left inside the property, and clearance of the rear garden. (request)

Not known:
- ["Whether event-16 'approved quote' refers to the £665 sanitation quote or to the separate maintenance quote", "Whether the landlord still makes approval conditional on bond recovery, and the outcome of the deposit claim", "Status and date of the separate major maintenance", "Whether the soil making-good is in scope", "Whether the 28 September move-in is still on"]</unknown>
<parameter name="tried
- Which quote event-16 approves
- Whether bond-recovery condition still applies
- Date of the separate maintenance
- Whether soil making-good is in scope
- Which conflicting value is right (see conflicts)

Tried:
- Agent proposed ESCALATE

Options:
- Recommended: Confirm in writing with the landlord which quote event-16 approved, and whether the £665 is approved without the bond condition. The deposit side stays with a person. Then instruct the contractor.
- Keep the hold until the deposit claim and the maintenance schedule are settled, and tell the contractor and landlord about the likely delay to the 28 September move-in.
- Ask the contractor to quote for the disturbed-soil making good and the carpet scope, then route the revised figure to the landlord.

Recommended: Recommended: Confirm in writing with the landlord which quote event-16 approved, and whether the £665 is approved without the bond condition. The deposit side stays with a person. Then instruct the contractor.

## Inconsistencies and mismatches

- **document consistency** (flag): reference number differs between documents: 'NBL-015-INSPECTION' vs 'NBL-015-Q1' (similarity 0.383). [move-out-inspection-report.pdf, property-preparation-quotation.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Separate major maintenance work awaiting landlord quote approval and scheduling
- Deposit claim (£650) handled through the deposit process
