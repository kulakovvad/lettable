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
- **Evidence cited:** event-005, event-008, event-009, event-012, event-016, event-017, event-018, event-019, event-020, event-022, event-023, invoice-NBL-CFM-250210-A.pdf, invoice-NBL-CFM-250210-B.pdf

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
      "event-008",
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

Two Copper Finch invoices dated 10 Feb (event-017, event-018) overlap: A is £138 for diagnosis, B is £372 for actuator replacement plus diagnosis. Both give a service date of 5 Feb. Both name the right property, customer and provider, so there is no address or provider mismatch. The landlord authorised diagnosis only, up to £180 inc VAT (event-005), and explicitly declined to authorise remedial work or more spend (event-012). The £372 estimate came after the visit (event-009). The provider's visit report (event-008) mentions no remedial work, and on 7 Feb she still had to check parts (event-016). The file has no completion evidence (event-019), and the tenant does not know whether the actuator was replaced (event-020). The provider has been asked twice for clarification and gave only a holding reply (event-022). This is a duplicate or overlapping invoice case with a charge disputed in effect, which policy sends to a person. ROUTE_FOR_APPROVAL would be wrong, because it would imply the work is validly claimed. ASK_PROVIDER has already been tried twice (event-015, event-021). WAIT is not enough, because a person needs to decide how to handle the invoices and the unresolved heating fault. The landlord was asked at event-023 and is not yet overdue. Nothing is payable, and the case can't close. I did not read the claim in invoice B as proof of completion. Priority is P2 because there is no reported danger and no gas concern, but a child lives at the property, the heating is intermittent, and the tenant is using a portable heater. Neither invoice contains any instruction to change process. A person should decide the invoice handling and the next heating step if the landlord's answer changes things.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Copper Finch Mechanical sent two overlapping invoices for 7 Larkspur Fold: A £138 (diagnosis) and B £372 (actuator supply/replacement, diagnosis, testing). Both give a service date of 5 Feb. The file has no evidence the actuator was replaced, and the landlord authorised diagnosis only. The invoices should not be paid or closed until a person rules on them. The heating fault is also still unresolved.

Respond by 2025-02-13T16:35:00+00:00 (P2, route property_manager).

Known:
- Landlord authorised diagnosis only, up to £180 inc VAT (event-005); the £138 diagnostic quote is within that (event-007).
- £372 estimate was sent at 14:54 on 5 Feb, after the visit, asking for written authorisation (event-009). Landlord did not authorise remedial work (event-012).
- Provider's 5 Feb visit report mentions no remedial work (event-008). On 7 Feb she still had to check parts and estimate details (event-016).
- Invoice B (£372) describes actuator replacement as done on 5 Feb. Its wording overlaps invoice A, and neither says whether it credits or supersedes the other (event-017, event-018, invoice PDFs).
- Provider replied on 12 Feb that she is still checking records and gave no completion evidence, revised invoice or parts confirmation (event-022).
- Tenant doesn't know if the actuator was replaced and has seen no contractor since 5 Feb. Heating is working intermittently with one radiator cooler (event-020).
- A child lives at the property (event-001). The tenant is using a portable heater plugged into a wall socket (event-011). No leak, smell or hazard has been reported.
- I asked the landlord on 12 Feb how to proceed (event-023). No reply yet, and it is not overdue. Invoice, address and customer details match the job and the assigned provider. No payment is recorded.
- Property: 7 Larkspur Fold, Orvane Heath, ZZ1 1ZZ (index)
- Request: The radiators have stopped heating intermittently. Hot water is still available. Please arrange an inspection. (request)

Not known:
- Whether the actuator was actually replaced, and when.
- Whether invoice B supersedes A or both are claimed (£510 in total).
- Whether the £138 diagnosis is credited against the £372.
- The landlord's decision on repair or replacement and on any spend.
- The boiler label details the tenant supplied in event-014 are not itemised in the summary.
- Whether the actuator was replaced
- Whether invoice B supersedes A
- Whether the diagnosis is credited

Tried:
- Asked the provider on 7 Feb and 11 Feb for a breakdown, credit position, job notes and parts records (event-015, event-021). Only a holding reply (event-022).
- Asked the tenant for a status update (event-013, event-020).
- Asked the landlord on 12 Feb to decide on the invoices and any further work (event-023).
- Agent proposed ESCALATE

Options:
- Recommended: Hold both invoices as unpayable. Tell the provider that only invoice A (£138, within the £180 authorisation) can be considered, once confirmed. Invoice B is disputed until she shows authorisation and completion evidence.
- Wait for the landlord's reply to event-023, then ask the provider for one corrected itemised invoice with job notes and a parts record. Route any actuator work to the landlord for written approval.
- Arrange an attendance to check the actuator and the heating, with the landlord's approval, to establish what was done. Review interim heating for the child in the household.

Recommended: Recommended: Hold both invoices as unpayable. Tell the provider that only invoice A (£138, within the £180 authorisation) can be considered, once confirmed. Invoice B is disputed until she shows authorisation and completion evidence.

## Inconsistencies and mismatches

- **amount** (info): The provider gave different quotes: GBP 138.00 (event-007); GBP 372.00 (event-009). [event-007, event-009]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check unavailable.
