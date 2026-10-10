# Case 23

**Decision:** Escalate to a person
**Priority:** P2

## Details

### Case

- **Id:** 23
- **Raised by:** Tenant
- **Request:** The radiators have stopped heating intermittently. Hot water is still available. Please arrange an inspection.

### Property

- **Address:** 7 Larkspur Fold, Orvane Heath, ZZ1 1ZZ
- **References:** reference NBL-CFM-250210-A [invoice-NBL-CFM-250210-A.pdf]; reference NBL-CFM-250210-B [invoice-NBL-CFM-250210-B.pdf]

### Agency

- **Name:** Ivo Merrick (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 138.00 (VAT incl, provider) [event-007]; GBP 372.00 (VAT incl, provider) [event-009]; GBP 138.00 (VAT unknown, provider) [event-009]
- **Invoices:** GBP 138.00 (provider) [event-018]; GBP 372.00 (provider) [event-018]; GBP 138.00 (attachment) [invoice-NBL-CFM-250210-A.pdf]; GBP 372.00 (attachment) [invoice-NBL-CFM-250210-B.pdf]
- **Payments:** payment: The message did not say whether one replaced the other, whether both amounts were payable, or whether either had been paid. [event-017]; payment: The two invoice records remain on file; there is no recorded payment, confirmed supersession or authorization for actuator work. [event-023]

### Appointments

- Said she recalled the 5 February visit but did not know whether the actuator had been replaced. [event-020]

### Timeline

- **Events:** 23, first 2025-02-03T08:14:00+00:00, last 2025-02-12T16:35:00+00:00
- **Channels:** Portal 5, Update 2, Email 13, SMS 1, Document 1, Note 1

### Attachments

- invoice-NBL-CFM-250210-A.pdf (pdf, content read)
- invoice-NBL-CFM-250210-B.pdf (pdf, content read)

### Decision

- **Action:** Escalate to a person
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-02-12T16:35:00+00:00
- **Evidence cited:** event-005, event-007, event-009, event-012, event-016, event-017, event-018, event-019, event-020, event-022, event-023, invoice-NBL-CFM-250210-A.pdf, invoice-NBL-CFM-250210-B.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "23",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The radiators have stopped heating intermittently. Hot water is still available. Please arrange an inspection."
  },
  "property": {
    "address": "7 Larkspur Fold, Orvane Heath, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "7 Larkspur Fold, Orvane Heath, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-CFM-250210-A",
        "refs": [
          "invoice-NBL-CFM-250210-A.pdf"
        ]
      },
      {
        "kind": "reference",
        "value": "NBL-CFM-250210-B",
        "refs": [
          "invoice-NBL-CFM-250210-B.pdf"
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
    "name": "Ivo Merrick (Property Manager, Northbridge Lettings)",
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
        "amount_gbp": 138.0,
        "vat": "incl",
        "from": "provider",
        "ref": "event-007"
      },
      {
        "amount_gbp": 372.0,
        "vat": "incl",
        "from": "provider",
        "ref": "event-009"
      },
      {
        "amount_gbp": 138.0,
        "vat": "unknown",
        "from": "provider",
        "ref": "event-009"
      }
    ],
    "invoices": [
      {
        "amount_gbp": 138.0,
        "from": "provider",
        "ref": "event-018"
      },
      {
        "amount_gbp": 372.0,
        "from": "provider",
        "ref": "event-018"
      },
      {
        "amount_gbp": 138.0,
        "from": "attachment",
        "ref": "invoice-NBL-CFM-250210-A.pdf"
      },
      {
        "amount_gbp": 372.0,
        "from": "attachment",
        "ref": "invoice-NBL-CFM-250210-B.pdf"
      }
    ],
    "approval": {
      "amount_gbp": null,
      "ref": null,
      "covers": "unknown"
    },
    "payments": [
      {
        "kind": "payment",
        "text": "The message did not say whether one replaced the other, whether both amounts were payable, or whether either had been paid.",
        "ref": "event-017"
      },
      {
        "kind": "payment",
        "text": "The two invoice records remain on file; there is no recorded payment, confirmed supersession or authorization for actuator work.",
        "ref": "event-023"
      }
    ],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Said she recalled the 5 February visit but did not know whether the actuator had been replaced.",
      "ref": "event-020"
    }
  ],
  "timeline": {
    "events": 23,
    "first": "2025-02-03T08:14:00+00:00",
    "last": "2025-02-12T16:35:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 5,
      "Update": 2,
      "Email": 13,
      "SMS": 1,
      "Document": 1,
      "Note": 1
    }
  },
  "attachments": [
    {
      "name": "invoice-NBL-CFM-250210-A.pdf",
      "available": true,
      "kind": "pdf"
    },
    {
      "name": "invoice-NBL-CFM-250210-B.pdf",
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
    "as_of": "2025-02-12T16:35:00+00:00",
    "evidence_refs": [
      "event-005",
      "event-007",
      "event-009",
      "event-012",
      "event-016",
      "event-017",
      "event-018",
      "event-019",
      "event-020",
      "event-022",
      "event-023",
      "invoice-NBL-CFM-250210-A.pdf",
      "invoice-NBL-CFM-250210-B.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The radiators have stopped heating intermittently. Hot water is still available. Please arrange an inspection.
23 events reviewed, decision as of 2025-02-12T16:35:00+00:00.

## Decision

Copper Finch Mechanical sent two overlapping invoices dated 10 Feb, both for the correct address and the assigned firm: A for £138 and B for £372 (invoice-NBL-CFM-250210-A.pdf, invoice-NBL-CFM-250210-B.pdf, event-017, event-018). Invoice A matches the £138 diagnostic quote (event-007) and sits within the landlord's £180 diagnosis-only authority (event-005). Invoice B bills actuator replacement as done on 5 Feb. The landlord never approved that work (event-012), the £372 estimate was only sent after the visit (event-009), and the file has no authorization or completion record (event-019). The tenant does not know whether the actuator was replaced (event-020). The contractor has twice failed to say whether one invoice replaces the other, whether the diagnosis is credited, or whether the work was done (event-016, event-022). The two documents conflict with the history, and the charge is disputed in effect. Policy sends duplicate or suspicious invoices and conflicting versions to a person. A third question to the provider or a further chase would repeat what has already failed. Routing the £372 for approval would be wrong, because the work may not have been done and the landlord has not asked for it. Nothing is payable meanwhile. I set P2, not P0 or P1: the heating works intermittently and hot water is available. There is no gas, leak or smell concern (event-008, event-011). A portable heater is in use and a child lives at the property, which the handover flags. The reference-number flag only reflects the two different invoice suffixes. The landlord has been asked for a decision (event-023). A follow-up is set for 48 hours to check for his reply. This would change if the contractor produces job notes and a parts record, or the landlord gives written direction.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to accounts `escalation-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-02-14T16:35:00+00:00, waiting on landlord: Landlord asked on 12 Feb (event-023) how to proceed on the invoices and further work. Check for a reply and chase if none. `followup-2`. Held: not part of the final action ESCALATE; a person can release it.

## Handover for the person taking over

Copper Finch Mechanical sent two overlapping invoices dated 10 Feb for 7 Larkspur Fold (A £138, B £372). B bills actuator replacement for 5 Feb, but there is no authorization or completion evidence for that work. Do not pay either invoice until a person has reviewed them. Heating is still intermittent, and a child lives at the property.

Respond by 2025-02-13T16:35:00+00:00 (P2, route accounts).

Conflicts:
- reference_number: NBL-CFM-250210-A (invoice-NBL-CFM-250210-A.pdf) vs NBL-CFM-250210-B (invoice-NBL-CFM-250210-B.pdf)

Known:
- Landlord authorized diagnosis only, up to £180 incl VAT, and asked to be consulted before any remedial work (event-005, event-012).
- Contractor quoted £138 incl VAT for attendance, diagnosis and testing, with parts and remedial work excluded (event-007). Invoice A for £138 matches that quote (invoice-NBL-CFM-250210-A.pdf).
- Estimate of £372 for actuator replacement was sent 5 Feb at 14:54, after the visit (event-009). The landlord has not approved it (event-012). Our note records no written authorization and no completion entry (event-019).
- Invoice B for £372 describes actuator supply and replacement as done on 5 Feb. It overlaps invoice A's attendance and diagnosis, and no credit is stated (invoice-NBL-CFM-250210-B.pdf, event-018).
- On 7 Feb the contractor said parts availability and the estimate details were still being checked (event-016). On 12 Feb she said she could not confirm whether the records are separate chargeable work or whether one replaces the other, and gave no completion evidence (event-022).
- The tenant does not know whether the actuator was replaced and has seen no contractor since 5 Feb (event-020). Heating is still intermittent, and hot water is available.
- Both invoices carry the correct address and the assigned firm's name. Property and provider match; the problem is the duplication and the missing authority.
- We emailed the landlord on 12 Feb at 16:35 for a decision, and there is no reply yet (event-023).
- Property: 7 Larkspur Fold, Orvane Heath, ZZ1 1ZZ (index)
- Request: The radiators have stopped heating intermittently. Hot water is still available. Please arrange an inspection. (request)

Not known:
- Whether the actuator was actually replaced, and when.
- Whether invoice B replaces A or both are claimed.
- Whether the £138 diagnostic charge is credited against the repair.
- Whether the landlord will authorize the repair and the £372 cost.
- The cause of the continuing intermittent heating.
- Whether the actuator was replaced
- Whether invoice B supersedes A
- Whether the diagnosis charge is credited

Tried:
- Asked the contractor for the breakdown and credit on 7 Feb (event-015). Asked again on 11 Feb for job notes, parts record and authorization evidence (event-021). The reply on 12 Feb gave no evidence (event-022).
- Asked the landlord for a decision on the invoices and any further work (event-023).
- Agent proposed ESCALATE

Options:
- Recommended: Hold both invoices. Wait for the landlord's reply and the contractor's job notes and parts record. Consider paying only invoice A (£138), which is within the diagnosis authority, once the landlord confirms.
- Dispute invoice B in writing as unauthorized and unevidenced. Ask the contractor for a single corrected invoice, with any credit stated, before any payment.
- If the landlord wants the repair done, get a written approval and a fixed, itemised price from the contractor. Book an access-confirmed return visit with the tenant, who can give access after 14:00 on weekdays, to restore the heating.

Recommended: Recommended: Hold both invoices. Wait for the landlord's reply and the contractor's job notes and parts record. Consider paying only invoice A (£138), which is within the diagnosis authority, once the landlord confirms.

## Inconsistencies and mismatches

- **document consistency** (flag): reference number differs between documents: 'NBL-CFM-250210-A' vs 'NBL-CFM-250210-B' (similarity 0.323). [invoice-NBL-CFM-250210-A.pdf, invoice-NBL-CFM-250210-B.pdf]
- **amount** (info): The provider gave different quotes: GBP 138.00 (event-007); GBP 372.00 (event-009). [event-007, event-009]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Tenant is using a portable heater plugged directly into a wall socket (event-011). Consider giving safe-use advice.
