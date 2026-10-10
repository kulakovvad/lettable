# Case 2

**Decision:** Escalate to a person
**Priority:** P2

## Details

### Case

- **Id:** 2
- **Raised by:** Tenant
- **Request:** Please send me the current gas safety paperwork for the flat. The boiler has also started locking out occasionally; could you check whether that is being looked at?

### Property

- **Address:** 8 Brindlewick Row, Vellum Quay, ZZ1 1ZZ
- **References:** job reference NBL-48217 [gas-portal-record.pdf]

### Agency

- **Name:** Oren Vale (Property Manager, Northbridge Lettings)

### Money

- **Payments:** payment: I have paid Flintmere for the visit. [event-016]

### Appointments

- I arranged the annual gas visit with Flintmere Gas Services for 9 October. [event-005]
- Flintmere has the 9 October appointment booked for the annual gas visit. [event-006]
- I can provide access after 21 October if a further visit is arranged. [event-022]

### Timeline

- **Events:** 24, first 2025-10-01T08:42:00+00:00, last 2025-10-18T16:35:00+00:00
- **Channels:** Portal 6, Note 3, Email 11, SMS 2, Document 2

### Attachments

- gas-portal-record.pdf (pdf, content read)

### Decision

- **Action:** Escalate to a person
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-10-18T16:35:00+00:00
- **Evidence cited:** event-001, event-002, event-014, event-019, event-021, event-022, event-023, event-024, gas-portal-record.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "2",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "Please send me the current gas safety paperwork for the flat. The boiler has also started locking out occasionally; could you check whether that is being looked at?"
  },
  "property": {
    "address": "8 Brindlewick Row, Vellum Quay, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "8 Brindlewick Row, Vellum Quay, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "job reference",
        "value": "NBL-48217",
        "refs": [
          "gas-portal-record.pdf"
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
    "name": "Oren Vale (Property Manager, Northbridge Lettings)",
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
      "ref": null,
      "covers": "unknown"
    },
    "payments": [
      {
        "kind": "payment",
        "text": "I have paid Flintmere for the visit.",
        "ref": "event-016"
      }
    ],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "I arranged the annual gas visit with Flintmere Gas Services for 9 October.",
      "ref": "event-005"
    },
    {
      "when_text": "Flintmere has the 9 October appointment booked for the annual gas visit.",
      "ref": "event-006"
    },
    {
      "when_text": "I can provide access after 21 October if a further visit is arranged.",
      "ref": "event-022"
    }
  ],
  "timeline": {
    "events": 24,
    "first": "2025-10-01T08:42:00+00:00",
    "last": "2025-10-18T16:35:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 6,
      "Note": 3,
      "Email": 11,
      "SMS": 2,
      "Document": 2
    }
  },
  "attachments": [
    {
      "name": "gas-portal-record.pdf",
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
    "as_of": "2025-10-18T16:35:00+00:00",
    "evidence_refs": [
      "event-001",
      "event-002",
      "event-014",
      "event-019",
      "event-021",
      "event-022",
      "event-023",
      "event-024",
      "gas-portal-record.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Please send me the current gas safety paperwork for the flat. The boiler has also started locking out occasionally; could you check whether that is being looked at?
24 events reviewed, decision as of 2025-10-18T16:35:00+00:00.

## Decision

The tenant asked for current gas paperwork (event-001). The file holds only the 16 Oct 2024 record (event-002, event-024), so no in-date CP12 is in the case. The portal screenshot (gas-portal-record.pdf) is a job card with 'Customer document: Processing'. It is not a signed certificate, so I told the tenant it is not their paperwork and did not call anything safe. Flintmere's quality desk has paused the signed paperwork over an appliance installation-detail query and gave no date (event-019). The engineer cannot resolve it (event-021). The tenant reports lockouts on 1, 13 and 16 Oct (event-003, 017, 022), each time with no gas smell and a restart after reset. So there is no reported imminent danger and the priority is P2. Under the compliance policy, a missing or unconfirmed gas certificate goes to a person. A diagnostic would be a separate job, and the landlord has refused any extra spend so far (event-016, 023), so I cannot instruct it. Waiting or a routine chase would not help: Flintmere has already answered with no date, and a person must decide how to settle the certificate, the lockout diagnostic and the landlord's authority. I staged a tenant update with gas emergency advice. The handover lists options. No instructions embedded in the case tried to change my process. Unknowns are what the installation detail is, whether it is a safety issue, and when the certificate will arrive.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Message to tenant (update, P2) `message-2`. Held: not part of the final action ESCALATE; a person can release it.

### Message to tenant `message-2`

Hello Iona, thank you for your updates. The attached portal item is a Flintmere job record showing the 9 October visit as complete. It is not the signed gas safety certificate, so please do not treat it as your paperwork. Flintmere is still processing the signed certificate and has not given a date. We have no signed certificate for the visit to send you yet. We are chasing it, and I have passed the repeated boiler lockouts to a colleague to decide the next step with the landlord. A lockout diagnostic is a separate job and has not been approved yet. Thank you for the access offer after 21 October. If you smell gas, leave the property, avoid switches and flames, and call the National Gas Emergency line on 0800 111 999. Please tell us straight away if the heating stops completely. Regards, Oren Vale, Northbridge Lettings

## Handover for the person taking over

No current signed gas safety certificate (CP12) in the file for 8 Brindlewick Row. The last record is dated 16 Oct 2024, so it is now a year old. Flintmere's signed paperwork for the 9 Oct visit is paused by its quality desk over an appliance installation detail, with no date given. The tenant reports repeated boiler lockouts. The landlord has not authorised a diagnostic or any further spend.

Respond by 2025-10-19T16:35:00+00:00 (P2, route property_manager).

Known:
- Tenant asked for current gas paperwork and reported boiler lockouts (event-001, 003).
- File holds only the 16 Oct 2024 gas record (event-002, 024).
- Landlord booked the annual gas visit with Flintmere; the engineer attended 9 Oct and recorded 'satisfactory' in the job app (event-005, 009, 010).
- The portal screenshot (gas-portal-record.pdf) shows Customer document 'Processing'. It is not a signed certificate.
- Flintmere says its quality desk paused issuing the signed paperwork while it reconciles an appliance installation detail (event-019). It gave no date. The engineer cannot resolve that query (event-021).
- Lockout diagnostic is a separate job per Flintmere (event-019). Landlord has not approved a diagnostic or extra charge and wants to know what is outstanding first (event-016, 023).
- Lockouts reported 3 times: 1 Oct, 13 Oct, 16 Oct. Each time the boiler restarted after a reset and the tenant noticed no gas smell (event-003, 017, 022).
- Tenant can give access after 21 Oct (event-022). Tenant's question in event-014 is still unanswered.
- Property: 8 Brindlewick Row, Vellum Quay, ZZ1 1ZZ (index)
- Request: Please send me the current gas safety paperwork for the flat. The boiler has also started locking out occasionally; could you check whether that is being looked at? (request)

Not known:
- What the installation detail query is, and whether it points to a safety issue with the boiler or cooker.
- When Flintmere will issue the signed certificate, or whether the result will change.
- Whether the lockouts are a fault needing a separate diagnostic visit.
- Whether the landlord will authorise a diagnostic.
- Nature of Flintmere's installation-detail query
- Date for the signed certificate
- Whether the lockouts need a diagnostic and whether the landlord will authorise it

Tried:
- Asked the landlord about the visit and authorised work (event-004).
- Asked Flintmere what the record represents and when paperwork will be available (event-018). They replied (event-019).
- Asked the landlord what extra work they authorise (event-020). They have not approved any (event-023).
- Agent proposed ESCALATE

Options:
- Recommended: Ask Flintmere in writing for the nature of the installation-detail query, a date for the signed CP12, and an explicit statement of whether any appliance is unsafe or needs work. Then take the result to the landlord, and ask the landlord to authorise a lockout diagnostic from 21 Oct if one is needed.
- Ask the landlord whether they would use their own Gas Safe engineer to carry out the lockout diagnostic and a fresh certificate, if Flintmere's paperwork stays blocked.
- Tell the tenant what is known, without calling the appliances safe, and repeat the gas emergency advice. Raise to P1 at once if the tenant reports a gas smell or a loss of heating, or if Flintmere finds an unsafe installation.

Recommended: Recommended: Ask Flintmere in writing for the nature of the installation-detail query, a date for the signed CP12, and an explicit statement of whether any appliance is unsafe or needs work. Then take the result to the landlord, and ask the landlord to authorise a lockout diagnostic from 21 Oct if one is needed.

## Inconsistencies and mismatches

- **completion** (flag): The provider reports the job done (event-009), but the tenant later reports a problem (event-022). [event-009, event-022]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Intermittent boiler lockouts (repair or diagnostic, separate from the certificate request, needs landlord approval)
