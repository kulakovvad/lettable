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
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-10T18:20:00+00:00
- **Evidence cited:** event-020, event-019, event-018, event-014, forwarded-document.pdf

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
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-10T18:20:00+00:00",
    "evidence_refs": [
      "event-020",
      "event-019",
      "event-018",
      "event-014",
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

The tenant's "All jobs was done" (event-020) is vague, and no provider confirmation, invoice position or landlord confirmation is in the case. It does not say that the bedroom window now closes. The landlord inspected himself (event-014), then a contractor said parts needed ordering (event-018). Closing is therefore not supported. The landlord's forwarded Gas Safety Record (event-019, forwarded-document.pdf) is for 8 Thistledown Mews, Vellumby, which is a property mismatch with 24 Bramblewick Lane. I will not file it or treat it as relevant to this job. I am asking the landlord which property it belongs to and whether the window repair is complete. This is a question to a single sender, not a conflict, so escalation is not needed. There is no reported danger. The window was partly open earlier (event-013), but the work is reportedly done. Priority is P3. The earlier electrical report (event-011) is also unexplained and has no content in the case. If the tenant and landlord confirm completion for this property, and nothing else is outstanding, the case can close. [gate: documents disagree on property_address ('24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ'); a person must confirm which is right]

## Actions taken

- **HELD_FOR_REVIEW**: Message to tenant (request_info, P3) `message-1`. Held: code gates changed the decision to ESCALATE.
- **HELD_FOR_REVIEW**: Message to landlord (request_info, P3) `message-2`. Held: code gates changed the decision to ESCALATE.
- **COMMITTED**: Escalation ticket P3 to property_manager `escalation-3`. Created automatically because the final decision is an escalation.

### Message to tenant `message-1`

Hello Elena, thank you for your message. Before we record anything as finished, could you confirm that the bedroom window at 24 Bramblewick Lane now closes and seals fully? Please also tell us which job(s) you mean by "all jobs", and the full name of the contractor (you mention Richard) and the date he attended. If anything is still outstanding, please let us know. Kind regards, Maya Chen, Northbridge Lettings

### Message to landlord `message-2`

Hello Dorian, thank you for forwarding the Landlord Gas Safety Record (ref NBL-009-GSR-25). It lists the property as 8 Thistledown Mews, Vellumby, not 24 Bramblewick Lane, Alderfen, which is the property for this case. Could you confirm which property it is meant for? We will not file it against 24 Bramblewick Lane until this is clear. Separately, could you confirm whether the bedroom window repair has been completed and which contractor attended? Kind regards, Maya Chen, Northbridge Lettings

## Handover for the person taking over

The tenant's "All jobs was done" (event-020) is vague, and no provider confirmation, invoice position or landlord confirmation is in the case. It does not say that the bedroom window now closes. The landlord inspected himself (event-014), then a contractor said parts needed ordering (event-018). Closing is therefore not supported. The landlord's forwarded Gas Safety Record (event-019, forwarded-document.pdf) is for 8 Thistledown Mews, Vellumby, which is a property mismatch with 24 Bramblewick Lane. I will not file it or treat it as relevant to this job. I am asking the landlord which property it belongs to and whether the window repair is complete. This is a question to a single sender, not a conflict, so escalation is not needed. There is no reported danger. The window was partly open earlier (event-013), but the work is reportedly done. Priority is P3. The earlier electrical report (event-011) is also unexplained and has no content in the case. If the tenant and landlord confirm completion for this property, and nothing else is outstanding, the case can close. [gate: documents disagree on property_address ('24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ'); a person must confirm which is right]

Respond by 2025-09-13T18:20:00+00:00 (P3, route property_manager).

Conflicts:
- property_address: 24 Bramblewick Lane, Alderfen, ZZ1 1ZZ (index) vs 8 Thistledown Mews, Vellumby, ZZ1 1ZZ (forwarded-document.pdf)

Known:
- 20 events reviewed
- Property: 24 Bramblewick Lane, Alderfen, ZZ1 1ZZ (index)
- Request: The bedroom window has not been closing fully. The handle appears to work, but the window does not seal. The tenant believes the hinges may be the cause and says the window is a standard type. No special access arrangements were reported. (request)

Not known:
- Whether the window now closes and seals
- Contractor identity (Richard) and attendance date
- Which property the gas safety record belongs to
- Invoice position
- Content and relevance of the EICR forwarded in event-011
- Which conflicting value is right (see conflicts)

Tried:
- Agent proposed ASK_TENANT
- documents disagree on property_address ('24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ'); a person must confirm which is right

Options:
- Recommended: Review the timeline and decide the next step
- Contact the party we are waiting on directly

Recommended: Recommended: Review the timeline and decide the next step

## What was blocked or failed

- Final code check: documents disagree on property_address ('24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ'); a person must confirm which is right

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '24 Bramblewick Lane, Alderfen, ZZ1 1ZZ' vs '8 Thistledown Mews, Vellumby, ZZ1 1ZZ' (similarity 0.01). [forwarded-document.pdf, index]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Gas Safety Record for 8 Thistledown Mews forwarded by landlord
- Electrical installation condition report forwarded in event-011, not explained
- Tenant's earlier query about unfamiliar callers (event-008, event-013)
