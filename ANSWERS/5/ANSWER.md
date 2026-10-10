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
- **Evidence cited:** event-018, event-019, event-008, event-016, event-020, invoice-NBL-005-INV-71.pdf

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
      "event-008",
      "event-016",
      "event-020",
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

Event-019 asks us to pay invoice NBL-005-INV-71 to new bank details (11-11-11 / 11111111). These differ from the details on the invoice itself (00-00-00 / 00000000, event-018 and the PDF), and the email gives no independent verification. Policy treats this as suspected payment redirection: escalate P1 to accounts, do not reply to the requester and do not pay. The invoice otherwise matches the job. Property, provider and amount are right: £95 + VAT = £114, which equals the landlord's approval of the diagnostic visit (event-008). Even so, the claim is unverified. The job sheet was requested three times and not supplied (events 12, 14, 17, 20). The £460 + VAT repair was never approved (event-016), and the diagnostic invoice does not include it. Waiting or asking Rowan would send a query to the possibly compromised channel, so a person should verify through a known contact. No reply to the requester is staged. The tenant reported no danger (events 1, 4, 13) and there is no hazard, so the P1 comes from the payment fraud flag. Whether the event-019 email is genuine would change the decision.

## Actions taken

- **COMMITTED**: Escalation ticket P1 to accounts `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Suspected payment redirection on Hearthline Heating invoice NBL-005-INV-71 (£114 inc VAT) for 18 Brindlewick Row. Two days after sending the invoice, the sender asked for payment to different bank details (11-11-11 / 11111111) from those printed on it (00-00-00 / 00000000), with no independent verification. Do not pay on either set of details until verified by a person through a known contact.

Respond by 2025-05-13T20:40:00+00:00 (P1, route accounts).

Conflicts:
- property_address: 18 Brindlewick Row, Vellmere, ZZ1 1ZZ (index, invoice-NBL-005-INV-71.pdf) vs 18 Brindlewick Row (index)
- tenant_name: Iris Bell (event-001, event-002, event-003, event-004, event-010) vs Iris (event-010)
- reference_number: NBL-005-184 (event-002) vs NBL-005-INV-71 (invoice-NBL-005-INV-71.pdf)

Known:
- Hearthline Heating (Rowan Pike) is the assigned provider for NBL-005-184; the invoice matches the property address and the approved £95 + VAT diagnostic visit of 7 May (£114 inc VAT) (event-008, event-018, invoice PDF).
- Invoice dated 12 May, due 19 May, lists remittance 00-00-00 / 00000000 (event-018).
- Event-019 (13 May 15:51) asks for payment to 11-11-11 / 11111111 instead, with no independent contact or verification, and offers a revised invoice.
- Landlord approved the diagnostic visit only, up to £95 + VAT, and asked to be contacted before any repair (event-008). The £460 + VAT repair estimate was not approved (event-016).
- Job sheet / written attendance record requested on 7 May, 8 May and 9 May and still not supplied (event-12, event-14, event-17, event-20).
- No payment instruction has been entered (event-020).
- Property: 18 Brindlewick Row, Vellmere, ZZ1 1ZZ (index)
- Request: The heating has stopped working at 18 Brindlewick Row. Please arrange an inspection and let me know when someone can attend. (request)

Not known:
- Whether event-019 genuinely came from Hearthline or from a compromised or spoofed mailbox.
- Which bank details are genuine.
- Whether the job sheet exists.
- Heating status: it was temporarily restored by a reset and the fault could recur (event-014); the tenant has not updated since event-013.
- Whether event-019 is genuine
- Which bank details are correct
- Whether a job sheet exists
- Current heating status

Tried:
- No reply sent to the requester, deliberately, per policy.
- Job sheet requested three times without result.
- Agent proposed ESCALATE

Options:
- Recommended: Verify the bank change by phoning Hearthline on a number already held on file (not one from event-019). Pay the £114 only after confirmation, the job sheet is received and accounts agrees.
- Hold payment and keep the original remittance details. Ask Hearthline to confirm via a known contact. Check Rowan's mailbox for compromise.
- Tell the landlord about the invoice and the bank change request. Separately, the landlord still needs to decide on the £460 + VAT repair once an itemised breakdown arrives.

Recommended: Recommended: Verify the bank change by phoning Hearthline on a number already held on file (not one from event-019). Pay the £114 only after confirmation, the job sheet is received and accounts agrees.

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '18 Brindlewick Row, Vellmere, ZZ1 1ZZ' vs '18 Brindlewick Row' (similarity 0.667). [index, invoice-NBL-005-INV-71.pdf]
- **document consistency** (flag): tenant name differs between documents: 'Iris Bell' vs 'Iris' (similarity 0.667). [event-001, event-002, event-003, event-004, event-010]
- **document consistency** (flag): reference number differs between documents: 'NBL-005-184' vs 'NBL-005-INV-71' (similarity 0.28). [event-002, invoice-NBL-005-INV-71.pdf]
- **amount** (info): The provider gave different quotes: GBP 95.00 (event-006); GBP 460.00 (event-011). [event-006, event-011]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Repair estimate £460 + VAT is still unapproved: the landlord asked for a breakdown and attendance record (event-016)
- Tenant asked whether the heating will stay on and has had no answer (event-013)
