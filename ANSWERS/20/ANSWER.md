# Case 20

**Decision:** Escalate to a person
**Priority:** P0

## Details

### Case

- **Id:** 20
- **Raised by:** Tenant
- **Request:** There is a hot smell near the kitchen socket by the counter, and the socket face feels warm. Please arrange an inspection. I am not sure whether the socket is safe to use.

### Property

- **Address:** 8 Brindlewick Row, Oakhollow, ZZ1 1ZZ

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Money

- **Landlord approval:** for the visit, no amount [event-006]

### Appointments

- Confirmed he could attend between 13:00 and 15:00. [event-011]

### Timeline

- **Events:** 25, first 2025-04-12T08:14:00+00:00, last 2025-04-12T16:42:00+00:00
- **Channels:** Portal 10, Update 1, Email 8, Note 2, Call 2, SMS 2

### Decision

- **Action:** Escalate to a person
- **Priority:** P0
- **Confidence:** 0.93
- **Decided by:** model
- **As of:** 2025-04-12T16:42:00+00:00
- **Evidence cited:** event-001, event-004, event-011, event-017, event-023, event-024, event-025

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "20",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "There is a hot smell near the kitchen socket by the counter, and the socket face feels warm. Please arrange an inspection. I am not sure whether the socket is safe to use."
  },
  "property": {
    "address": "8 Brindlewick Row, Oakhollow, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "8 Brindlewick Row, Oakhollow, ZZ1 1ZZ",
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
    "quotes": [],
    "invoices": [],
    "approval": {
      "amount_gbp": null,
      "ref": "event-006",
      "covers": "visit"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Confirmed he could attend between 13:00 and 15:00.",
      "ref": "event-011"
    }
  ],
  "timeline": {
    "events": 25,
    "first": "2025-04-12T08:14:00+00:00",
    "last": "2025-04-12T16:42:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 10,
      "Update": 1,
      "Email": 8,
      "Note": 2,
      "Call": 2,
      "SMS": 2
    }
  },
  "attachments": [],
  "decision": {
    "action": "ESCALATE",
    "priority": "P0",
    "confidence": 0.93,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-04-12T16:42:00+00:00",
    "evidence_refs": [
      "event-001",
      "event-004",
      "event-011",
      "event-017",
      "event-023",
      "event-024",
      "event-025"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: There is a hot smell near the kitchen socket by the counter, and the socket face feels warm. Please arrange an inspection. I am not sure whether the socket is safe to use.
25 events reviewed, decision as of 2025-04-12T16:42:00+00:00.

## Decision

The tenant reports a hot, burning smell and a warm socket (event-001). At 16:42 she says the smell persists and nobody has inspected (event-025). Warmth near the socket was still noticed at event-017. A 10-year-old child is in the home (event-004). I treat this as a reported electrical fire risk, so it is P0 until verified. The landlord only offered a handyman who cannot do fixed wiring, has no test equipment and did not enter (events 6, 11, 15, 23). The landlord has given no electrician approval and has not answered the access question or the latest request (events 16, 20, 24). So waiting or chasing alone would leave the risk uncontrolled. The agency cannot approve spend, so a person on call must decide on an emergency electrician. No emergency guidance had been given (event-009, event-025). I staged immediate safety advice to the tenant: keep appliances off, leave and call 999 if there is smoke, sparks or a stronger smell, and isolate the circuit only if she can identify it with certainty. No documents conflict. Unknowns are the real condition of the socket and the landlord's decision.

## Actions taken

- **COMMITTED**: Message to tenant (safety_advice, P0) `message-1`. Recorded in the local outbox (no external delivery connected).
- **COMMITTED**: Escalation ticket P0 to on_call_emergency `escalation-2`. Recorded in the local outbox (no external delivery connected).

### Message to tenant `message-1`

Hi Nora, thank you for the update. Please keep the kettle and all other appliances away from that socket and do not touch its face. If you see smoke, sparks or scorch marks, hear crackling or buzzing, or the smell gets stronger, leave the flat with your son straight away and call 999. Please do not open or work on the socket yourself. If you can identify the kitchen breaker with certainty you may switch it off, but do not guess or take any risk. We have passed this to our on-call team as urgent and will update you as soon as a person has reviewed it. Northbridge Lettings (Maya Chen)

## Handover for the person taking over

Tenant reports hot/burning smell and warm kitchen socket at 8 Brindlewick Row since 08:14; tenant and 10-year-old son at home. Nine hours on, nobody has inspected; landlord has not authorised an electrician; the only attendee (handyman) is not qualified and could not get in. Needs an emergency electrician decision now.

Respond by 2025-04-12T17:42:00+00:00 (P0, route on_call_emergency).

Known:
- Reported 08:14: burning smell, socket face warm after kettle use (event-001); kettle unplugged, no smoke/sparks (event-004)
- Smell still faint at 16:42; area still feels warm to hand near it (event-017, event-025)
- Tenant is home with 10-year-old son (event-004); fridge running, breaker not identified or switched off (event-025)
- Landlord only offered handyman Rowan Pike (event-006, event-016); no electrician approval given
- Rowan does not do fixed wiring, has only a voltage pen, did not enter, no inspection or isolation done (event-011, event-015, event-023)
- Landlord not reached by phone (event-020), no reply to event-024; no access authority given for keys (event-021)
- No emergency guidance had been given to tenant before now (event-009, event-025); basic safety advice sent at decision time
- No photo, temperature reading or electrical test available (event-018)
- Property: 8 Brindlewick Row, Oakhollow, ZZ1 1ZZ (index)
- Request: There is a hot smell near the kitchen socket by the counter, and the socket face feels warm. Please arrange an inspection. I am not sure whether the socket is safe to use. (request)

Not known:
- Actual condition of socket/wiring
- Which breaker serves the socket
- Whether the landlord will approve an emergency electrician
- Whether smell is changing
- Socket and wiring condition
- Landlord's decision on an electrician and access

Tried:
- Portal triage with tenant (events 3,7)
- Email and voicemail to landlord (events 5,20,24)
- Handyman booked 13:00-15:00 but could not attend usefully (events 14,23)
- Agent proposed ESCALATE

Options:
- Recommended: Arrange an emergency qualified electrician now and seek landlord approval urgently, treating it as a safety matter
- Advise tenant to isolate the circuit at the consumer unit if safe, and call 999 or the fire service if the smell or heat worsens
- Keep trying the landlord by every channel and record the lack of response, while on-call decides whether to proceed on safety grounds

Recommended: Recommended: Arrange an emergency qualified electrician now and seek landlord approval urgently, treating it as a safety matter

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

**Possible safety hazard mentioned. Treat as urgent.**
