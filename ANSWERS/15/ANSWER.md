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
- **Evidence cited:** event-006, event-007, event-008, event-009, event-010, event-011, event-012, event-016, event-018, event-020, event-021

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
      "event-018",
      "event-020",
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

The job is the post-tenancy clean, waste removal and garden clearance at 18 Thistlevaunt Lane, with Brindlewick's £665 quote (event-006, property-preparation-quotation.pdf). Property, provider and amount match the job. The reference differs between the two PDFs (NBL-015-INSPECTION and NBL-015-Q1), but they are different document types, so I did not treat that as a mismatch. The landlord's approval (event-008, event-010) is conditional on recovering the cost from the former tenants' bond. That is a deposit matter, which policy says we never act on or decide, and the code flagged it (event-012, legal red flag). Event-009 told the contractor the quote was approved without that condition. Event-016 ("approved quote") does not say which quote it means. Event-007 also described the work only generally. The contractor is on hold (event-012, event-015), and the work depends on separate major maintenance with no completion date (event-018, event-020, event-021). A new tenant wants to move in on 28 September, so there is time pressure but no safety hazard, hence P2. A routine INSTRUCT_PROVIDER is not safe because the approval is ambiguous and conditional. Waiting or chasing is not suitable because the deposit topic cannot be waited on, and the blocker is a person's judgement. A person should confirm the landlord's approval and the bond condition, and sort out the maintenance sequencing. Nothing in the case tried to change my process.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Post-tenancy clean/waste/garden job at 18 Thistlevaunt Lane (Brindlewick, £665 quote) is stalled. The landlord's approval is tied to recovering the cost from the former tenants' bond, which is a deposit matter we cannot act on. Landlord's later "approved quote" is ambiguous. Work is on hold for separate maintenance with no date, and a new tenant wants to move in on 28 Sept.

Respond by 2025-09-26T08:34:11+00:00 (P2, route property_manager).

Conflicts:
- reference_number: NBL-015-INSPECTION (move-out-inspection-report.pdf) vs NBL-015-Q1 (property-preparation-quotation.pdf)

Known:
- Quote £665 from Brindlewick (event-006, property-preparation-quotation.pdf, NBL-015-Q1) for the correct property; it does not expressly cover making good the disturbed rear-garden soil from the inspection.
- Approval request (event-007) described the work only generally, without listing the carpet and garden tasks.
- Landlord (event-008, event-010): approval is conditional on recovery from the former tenants' bond. Our message to the contractor (event-009) said 'approved' without that condition.
- Event-011: costs plus damage exceed the £650 deposit held; a full-deposit claim is being prepared; final itemised figures awaited.
- Event-012: contractor told not to book 'while the deposit dispute is being handled'; contractor has been on hold since (event-013, event-014, event-015).
- Event-016: landlord sent 'approved quote' with no identification of which quote; it may refer to this £665 quote or to the separate maintenance quote.
- Events 18, 19, 20 and 21: sanitation is held until the separate major maintenance is scheduled and completed. No maintenance completion date is recorded, no visit is booked, and the contractor has given no slot. Event-21 says wait three more working days.
- Prospective tenant wants to move in 28 Sept (event-015). Property is vacant. No safety hazard reported.
- Property: 18 Thistlevaunt Lane, Orvelune, ZZ1 1ZZ (index)
- Request: Please arrange post-tenancy sanitation, removal of waste left inside the property, and clearance of the rear garden. (request)

Not known:
- Which quote the landlord meant in event-016.
- Whether the landlord's bond-recovery condition still stands. Deposit handling is for a person.
- Status and date of the separate major maintenance, and whether the landlord has approved its quote.
- Whether the 28 Sept move-in is still planned and the clean can be done before it.
- Whether the soil making-good is in scope or needs a separate quote.
- Which quote event-016 approves
- Whether the bond-recovery condition still applies
- Date and approval status of the separate maintenance

Tried:
- Quote requested and received (event-002, event-006).
- Landlord approval requested (event-007) and replied to (event-008, event-010, event-016).
- Contractor put on hold (event-012), then asked for dates (event-017) and called (event-019). No slot given.
- No contact attempted with the landlord since event-011, apart from their own update at event-016.
- Agent proposed ESCALATE

Options:
- Recommended: Ask the landlord to confirm in writing that event-016 approves the £665 Brindlewick quote, and whether the bond condition still applies. Handle the deposit claim separately through the deposit process. Then instruct the contractor.
- Chase the separate maintenance approval and scheduling so a sanitation slot can be fixed before 28 Sept. Tell the landlord if the move-in date is at risk.
- If the landlord will not approve without bond recovery, hold the work and have the landlord decide whether to proceed at their own cost. Ask the contractor whether the soil making-good needs a separate quote.

Recommended: Recommended: Ask the landlord to confirm in writing that event-016 approves the £665 Brindlewick quote, and whether the bond condition still applies. Handle the deposit claim separately through the deposit process. Then instruct the contractor.

## Inconsistencies and mismatches

- **document consistency** (flag): reference number differs between documents: 'NBL-015-INSPECTION' vs 'NBL-015-Q1' (similarity 0.41). [move-out-inspection-report.pdf, property-preparation-quotation.pdf]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Separate major maintenance quote and scheduling, still awaiting landlord approval and no date
- Former tenants' deposit claim (person to handle)
