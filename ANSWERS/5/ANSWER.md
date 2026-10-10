# Case 5

**Decision:** Escalate to a person
**Priority:** P1

## Details

### Case

- **Id:** 5
- **Raised by:** Tenant
- **Request:** The heating has stopped working at 18 Brindlewick Row. Please arrange an inspection and let me know when someone can attend.

### Property

- **Address:** 18 Brindlewick Row, Vellmere, ZZ1 1ZZ

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 95.00 (VAT excl, provider) [event-006]; GBP 460.00 (VAT excl, provider) [event-011]
- **Invoices:** GBP 114.00 (provider) [event-018]; GBP 95.00 (attachment) [invoice-NBL-005-INV-71.pdf]; GBP 19.00 (attachment) [invoice-NBL-005-INV-71.pdf]; GBP 114.00 (attachment) [invoice-NBL-005-INV-71.pdf]
- **Payments:** payment: The invoice lists remittance details 00-00-00 / 00000000 and a payment due date of 19 May. [event-018]; payment: Says Hearthline Heating has changed bank accounts and asks that the invoice be paid using 11-11-11 / 11111111 instead of the details on the invoice. [event-019]; payment: No payment instruction has been entered. [event-020]

### Appointments

- Offers an appointment window of 09:00–11:00 on 7 May. [event-009]

### Timeline

- **Events:** 20, first 2025-05-06T08:12:00+00:00, last 2025-05-13T16:40:00+00:00
- **Channels:** Portal 2, Update 1, Email 12, Note 2, SMS 2, Call 1

### Attachments

- invoice-NBL-005-INV-71.pdf (pdf, content read)

### Decision

- **Action:** Escalate to a person
- **Priority:** P1
- **Confidence:** 0.93
- **Decided by:** model
- **As of:** 2025-05-13T16:40:00+00:00
- **Evidence cited:** event-018, event-019, event-020, event-008, event-016, invoice-NBL-005-INV-71.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "5",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The heating has stopped working at 18 Brindlewick Row. Please arrange an inspection and let me know when someone can attend."
  },
  "property": {
    "address": "18 Brindlewick Row, Vellmere, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "18 Brindlewick Row, Vellmere, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": []
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
    "name": "Maya Chen (Property Manager, Northbridge Lettings)",
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
        "amount_gbp": 95.0,
        "vat": "excl",
        "from": "provider",
        "ref": "event-006"
      },
      {
        "amount_gbp": 460.0,
        "vat": "excl",
        "from": "provider",
        "ref": "event-011"
      }
    ],
    "invoices": [
      {
        "amount_gbp": 114.0,
        "from": "provider",
        "ref": "event-018"
      },
      {
        "amount_gbp": 95.0,
        "from": "attachment",
        "ref": "invoice-NBL-005-INV-71.pdf"
      },
      {
        "amount_gbp": 19.0,
        "from": "attachment",
        "ref": "invoice-NBL-005-INV-71.pdf"
      },
      {
        "amount_gbp": 114.0,
        "from": "attachment",
        "ref": "invoice-NBL-005-INV-71.pdf"
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
        "text": "The invoice lists remittance details 00-00-00 / 00000000 and a payment due date of 19 May.",
        "ref": "event-018"
      },
      {
        "kind": "payment",
        "text": "Says Hearthline Heating has changed bank accounts and asks that the invoice be paid using 11-11-11 / 11111111 instead of the details on the invoice.",
        "ref": "event-019"
      },
      {
        "kind": "payment",
        "text": "No payment instruction has been entered.",
        "ref": "event-020"
      }
    ],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Offers an appointment window of 09:00–11:00 on 7 May.",
      "ref": "event-009"
    }
  ],
  "timeline": {
    "events": 20,
    "first": "2025-05-06T08:12:00+00:00",
    "last": "2025-05-13T16:40:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 2,
      "Update": 1,
      "Email": 12,
      "Note": 2,
      "SMS": 2,
      "Call": 1
    }
  },
  "attachments": [
    {
      "name": "invoice-NBL-005-INV-71.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "ESCALATE",
    "priority": "P1",
    "confidence": 0.93,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-05-13T16:40:00+00:00",
    "evidence_refs": [
      "event-018",
      "event-019",
      "event-020",
      "event-008",
      "event-016",
      "invoice-NBL-005-INV-71.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The heating has stopped working at 18 Brindlewick Row. Please arrange an inspection and let me know when someone can attend.
20 events reviewed, decision as of 2025-05-13T16:40:00+00:00.

## Decision

Event-019 asks us to pay invoice NBL-005-INV-71 to 11-11-11 / 11111111 instead of the 00-00-00 / 00000000 on the invoice (event-018 and the attachment). It comes with no independent verification, which is a payment-redirection pattern, and the code flag forces escalation to accounts at P1. Policy says never to verify bank details through contacts in the same message and not to reply to the requester, so I have not replied or asked the provider. The invoice itself matches the property, the assigned provider and the £95 + VAT (£114) the landlord approved in event-008. The £460 repair estimate was not approved (event-016), and the job sheet requested in events 12, 14 and 17 is still outstanding. No payment instruction exists (event-020). Waiting or asking would not resolve suspected fraud, so a person in accounts must verify the bank details independently. Heating is running and no hazard is reported (event-013), so this is P1 for fraud and not P0. The job should not be closed.

## Actions taken

- **COMMITTED**: Escalation ticket P1 to accounts `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Suspected payment redirection on Hearthline Heating invoice NBL-005-INV-71 (£114 inc VAT). The invoice (event-018) shows bank details 00-00-00 / 00000000. A later email (event-019) asks for payment to 11-11-11 / 11111111 instead, with no independent verification. Do not pay and do not reply to the requester.

Respond by 2025-05-13T20:40:00+00:00 (P1, route accounts).

Conflicts:
- property_address: 18 Brindlewick Row, Vellmere, ZZ1 1ZZ (index, invoice-NBL-005-INV-71.pdf) vs 18 Brindlewick Row (index)
- reference_number: NBL-005-184 (event-002) vs NBL-005-INV-71 (event-018, event-020, invoice-NBL-005-INV-71.pdf)
- bank_details: 00-00-00 / 00000000 (event-018) vs 11-11-11 / 11111111 (event-019)

Known:
- Job NBL-005-184 at 18 Brindlewick Row, Vellmere, ZZ1 1ZZ; Hearthline Heating (Rowan Pike) is the assigned provider (event-005).
- Landlord Jonas Reed approved the diagnostic visit only, up to £95 + VAT (£114) (event-008). The invoice for £114 matches this amount and the address, and the visit on 7 May is recorded (event-010, event-011).
- The £460 + VAT repair estimate (event-011) was NOT approved. The landlord asked for a breakdown and written attendance record first (event-016). We told the provider not to order parts (event-017).
- The written job sheet requested in events 12, 14 and 17 is still outstanding.
- event-019 asks for new bank details, with no independent contact or verification, and the details differ from the invoice (event-018, attachment).
- event-020 notes that no payment instruction has been entered.
- The heating was running after the visit with a temporary reset, and the tenant reported no new symptoms (event-013). The provider says the fault could recur (event-014). No hazard is reported.
- Request: The heating has stopped working at 18 Brindlewick Row. Please arrange an inspection and let me know when someone can attend. (request)

Not known:
- Whether Rowan Pike or Hearthline really sent event-019, or whether the sender or mailbox is compromised.
- Which bank details are genuine.
- Whether the landlord wants to pay the diagnostic invoice before the job sheet is supplied.
- Whether the control board repair will go ahead.
- Whether event-019 is genuine
- Which bank details are correct
- Job sheet still outstanding
- Landlord decision on the £460 repair

Tried:
- Requested the job sheet and breakdown three times (events 12, 14, 17) without receiving it.
- No payment made and no reply sent to the bank-change email.
- Agent proposed ESCALATE

Options:
- Recommended: Verify the bank change by phoning Hearthline on a number already held on file, not one from event-019. Pay only once confirmed and the landlord is content, and only against the approved £114.
- Hold the invoice and pay to the original details on the invoice only if accounts can confirm them independently. Ask the provider for the job sheet first.
- Treat it as possible fraud: flag the sender's mailbox, warn the landlord, and keep the invoice unpaid until verified. Separately route the £460 repair decision to the landlord once the breakdown is received.

Recommended: Recommended: Verify the bank change by phoning Hearthline on a number already held on file, not one from event-019. Pay only once confirmed and the landlord is content, and only against the approved £114.

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '18 Brindlewick Row, Vellmere, ZZ1 1ZZ' vs '18 Brindlewick Row' (similarity 0.673). [index, invoice-NBL-005-INV-71.pdf]
- **document consistency** (flag): reference number differs between documents: 'NBL-005-184' vs 'NBL-005-INV-71' (similarity 0.397). [event-002, event-018, event-020, invoice-NBL-005-INV-71.pdf]
- **document consistency** (flag): bank details differs between documents: '00-00-00 / 00000000' vs '11-11-11 / 11111111' (similarity 0.06). [event-018, event-019]
- **amount** (info): The provider gave different quotes: GBP 95.00 (event-006); GBP 460.00 (event-011). [event-006, event-011]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Repair decision on the £460 + VAT control board replacement is still pending with the landlord
- Heating may fail again because the reset is temporary; the tenant asked whether it will stay working (event-013)
