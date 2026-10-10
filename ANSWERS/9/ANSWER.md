# Case 9

**Decision:** Escalate to a person
**Priority:** P3

## Details

### Case

- **Id:** 9
- **Raised by:** Tenant
- **Request:** The bedroom window has not been closing fully. The handle appears to work, but the window does not seal. The tenant believes the hinges may be the cause and says the window is a standard type. No special access arrangements were reported.

### Property

- **Address:** 24 Bramblewick Lane, Alderfen, ZZ1 1ZZ
- **References:** reference NBL-009-GSR-25 [forwarded-document.pdf]

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Money

- **Landlord approval:** for the visit, no amount [event-004]

### Appointments

- Relays the tenant's availability through 26 August and asks whether it suits his proposed visit. [event-009]
- He offers to attend the following morning between 10:00 and 12:00. [event-014]

### Timeline

- **Events:** 20, first 2025-08-12T09:10:00+00:00, last 2025-09-10T18:20:00+00:00
- **Channels:** Portal 1, Email 15, Call 4

### Attachments

- forwarded-document.pdf (pdf, content read)

### Decision

- **Action:** Escalate to a person
- **Priority:** P3
- **Confidence:** 0.75
- **Decided by:** model
- **As of:** 2025-09-10T18:20:00+00:00
- **Evidence cited:** event-001, event-018, event-019, event-020, forwarded-document.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "9",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The bedroom window has not been closing fully. The handle appears to work, but the window does not seal. The tenant believes the hinges may be the cause and says the window is a standard type. No special access arrangements were reported."
  },
  "property": {
    "address": "24 Bramblewick Lane, Alderfen, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "24 Bramblewick Lane, Alderfen, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-009-GSR-25",
        "refs": [
          "forwarded-document.pdf"
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
      "when_text": "Relays the tenant's availability through 26 August and asks whether it suits his proposed visit.",
      "ref": "event-009"
    },
    {
      "when_text": "He offers to attend the following morning between 10:00 and 12:00.",
      "ref": "event-014"
    }
  ],
  "timeline": {
    "events": 20,
    "first": "2025-08-12T09:10:00+00:00",
    "last": "2025-09-10T18:20:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 15,
      "Call": 4
    }
  },
  "attachments": [
    {
      "name": "forwarded-document.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "ESCALATE",
    "priority": "P3",
    "confidence": 0.75,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-10T18:20:00+00:00",
    "evidence_refs": [
      "event-001",
      "event-018",
      "event-019",
      "event-020",
      "forwarded-document.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The bedroom window has not been closing fully. The handle appears to work, but the window does not seal. The tenant believes the hinges may be the cause and says the window is a standard type. No special access arrangements were reported.
20 events reviewed, decision as of 2025-09-10T18:20:00+00:00.

## Decision

The job is the bedroom window at 24 Bramblewick Lane (event-001). The landlord's forwarded Gas Safety Record (event-019, forwarded-document.pdf) is for 8 Thistledown Mews, Vellumby, so it is a property mismatch. It is not filed or relied on, and the forwarding email has no message, so I asked the landlord which property it was meant for. The tenant's "All jobs was done" (event-020) is vague and names a contractor, Richard, who is not in the case. No provider is assigned (event-014, event-018), and there is no invoice, quote or approved amount. Completion is therefore unverified, and the closing policy rules out CLOSE. I asked the tenant to confirm that the window now closes (staged message-2). I asked the landlord to confirm completion, the contractor and the invoice position (staged message-1). Escalation is not needed because both parties can answer, and this is routine with no hazard. The partly open window was a concern in event-013 but is not a reported danger. A tenant reply that the window is still faulty, or a landlord reply that the record belongs to another property, would change the decision. The mismatched record may mean the landlord has another property, which a person may later want to check. [gate: documents disagree on property_address ('24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ'); a person must confirm which is right]

## Actions taken

- **HELD_FOR_REVIEW**: Message to landlord (request_info, P3) `message-1`. Held: code gates changed the decision to ESCALATE.
- **HELD_FOR_REVIEW**: Message to tenant (request_info, P3) `message-2`. Held: code gates changed the decision to ESCALATE.
- **COMMITTED**: Escalation ticket P3 to property_manager `escalation-3`. Created automatically because the final decision is an escalation.

### Message to landlord `message-1`

Dear Dorian, thank you for forwarding the Landlord Gas Safety Record (ref NBL-009-GSR-25) today. It is for 8 Thistledown Mews, Vellumby, not 24 Bramblewick Lane, Alderfen, which is the property for this case. Could you confirm which property it relates to and whether you meant to send it for 24 Bramblewick Lane? We will not file it against this property until we hear from you. Separately, the tenant says the work has now been done by a contractor called Richard. Could you confirm that the bedroom window repair at 24 Bramblewick Lane is complete, and let us know who the contractor was and whether any invoice will come to us or you are paying directly? Kind regards, Maya Chen, Northbridge Lettings

### Message to tenant `message-2`

Dear Elena, thank you for your message. To make sure we record this correctly, could you confirm that the bedroom window at 24 Bramblewick Lane now closes and seals fully, and that this is the work Richard completed? If anything is still outstanding, please tell us. Kind regards, Maya Chen, Northbridge Lettings

## Handover for the person taking over

The job is the bedroom window at 24 Bramblewick Lane (event-001). The landlord's forwarded Gas Safety Record (event-019, forwarded-document.pdf) is for 8 Thistledown Mews, Vellumby, so it is a property mismatch. It is not filed or relied on, and the forwarding email has no message, so I asked the landlord which property it was meant for. The tenant's "All jobs was done" (event-020) is vague and names a contractor, Richard, who is not in the case. No provider is assigned (event-014, event-018), and there is no invoice, quote or approved amount. Completion is therefore unverified, and the closing policy rules out CLOSE. I asked the tenant to confirm that the window now closes (staged message-2). I asked the landlord to confirm completion, the contractor and the invoice position (staged message-1). Escalation is not needed because both parties can answer, and this is routine with no hazard. The partly open window was a concern in event-013 but is not a reported danger. A tenant reply that the window is still faulty, or a landlord reply that the record belongs to another property, would change the decision. The mismatched record may mean the landlord has another property, which a person may later want to check. [gate: documents disagree on property_address ('24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ'); a person must confirm which is right]

Respond by 2025-09-13T18:20:00+00:00 (P3, route property_manager).

Conflicts:
- property_address: 24 Bramblewick Lane, Alderfen, ZZ1 1ZZ (index) vs 8 Thistledown Mews, Vellumby, ZZ1 1ZZ (forwarded-document.pdf)

Known:
- 20 events reviewed
- Property: 24 Bramblewick Lane, Alderfen, ZZ1 1ZZ (index)
- Request: The bedroom window has not been closing fully. The handle appears to work, but the window does not seal. The tenant believes the hinges may be the cause and says the window is a standard type. No special access arrangements were reported. (request)

Not known:
- Which property the gas record is for
- Whether the window repair is complete
- Who Richard is and who did the work
- Invoice position
- Which conflicting value is right (see conflicts)

Tried:
- Agent proposed ASK_LANDLORD
- documents disagree on property_address ('24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ'); a person must confirm which is right

Options:
- Recommended: Wait for landlord and tenant replies
- Escalate to the property manager if the gas record turns out to be for another property

Recommended: Recommended: Wait for landlord and tenant replies

## What was blocked or failed

- Final code check: documents disagree on property_address ('24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ'); a person must confirm which is right

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ' (similarity 0.01). [forwarded-document.pdf, index]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Gas safety record for 8 Thistledown Mews forwarded; needs separate handling and is not for this property
