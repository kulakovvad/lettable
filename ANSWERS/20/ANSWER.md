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
- **Evidence cited:** event-001, event-004, event-011, event-015, event-016, event-017, event-023, event-024, event-025

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
      "event-015",
      "event-016",
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

Tenant reports a persistent burning smell and warmth at a kitchen socket (event-001, event-017, event-025), with a 10-year-old child at home (event-004). The case treats this as a reported electrical fire risk, so it is P0 until verified. Nothing has been inspected or isolated. The landlord's handyman has no electrical competence or test equipment (event-011, event-015) and did not enter (event-023). The landlord has authorised only a look-and-report visit and has not answered the authority and electrician request since 15:02 (event-016, event-020, event-024). The agency cannot approve spend, and waiting or chasing again would leave the hazard open, so a person on call must decide on an emergency electrician. The file note records that no emergency guidance had reached the tenant (event-009, event-025). I have staged safety advice to the tenant now, since urgent_by_code is true. This covers not using the socket, leaving and calling 999 if smoke, sparks or a stronger smell appear, and not opening the socket. The decision would change if the landlord approves an electrician or the tenant reports the hazard has resolved.

## Actions taken

- **COMMITTED**: Message to tenant (safety_advice, P0) `message-1`. Recorded in the local outbox (no external delivery connected).
- **COMMITTED**: Escalation ticket P0 to on_call_emergency `escalation-2`. Recorded in the local outbox (no external delivery connected).

### Message to tenant `message-1`

Hi Nora, thank you for the update. A warm socket with a burning smell can be an electrical fire risk, so please: keep everything unplugged from that socket and do not use it. Do not touch the socket face or try to open it. If you see smoke or sparks, hear buzzing or crackling, or the smell gets stronger, leave the property with your son straight away and call 999. If you can see a consumer unit switch clearly labelled for the kitchen or sockets and can reach it safely with dry hands, you may switch that one off, but do not open anything or guess at breakers. If the fridge is affected, move any essentials to a cooler place. We have passed this to our on-call team as urgent and will update you as soon as we have an electrician or inspection arranged. Maya Chen, Northbridge Lettings

## Handover for the person taking over

Reported hot/burning smell and warm socket at kitchen counter, 8 Brindlewick Row. Tenant and 10-year-old son at home. Unresolved for ~8.5 hours; no inspection, no isolation, no qualified electrician; landlord unresponsive on authority since 15:02. Needs urgent decision to commission an emergency electrician.

Respond by 2025-04-12T17:42:00+00:00 (P0, route on_call_emergency).

Known:
- Event-001: burning smell, socket face warm after kettle; kettle unplugged
- Event-017/025: smell still noticeable, area still warm near socket as of 16:42; no breaker switched off; fridge running
- Event-004: tenant at home with 10-year-old son; tenant is back at property as of event-025
- Event-011/015: landlord's handyman Rowan Pike does not do fixed wiring, has no test equipment, only a voltage pen; did not enter (event-023)
- Event-006/016: landlord has only authorised handyman to look and report; no approval for electrician call-out or repairs
- Event-020/024: calls/emails to landlord on authority and electrician unanswered since 13:14
- Event-009/025: no emergency guidance had been given to tenant before now; safety advice sent at 16:42 decision time
- Property: 8 Brindlewick Row, Oakhollow, ZZ1 1ZZ (index)
- Request: There is a hot smell near the kitchen socket by the counter, and the socket face feels warm. Please arrange an inspection. I am not sure whether the socket is safe to use. (request)

Not known:
- Whether the socket/circuit is currently hot or live-faulty (no test, photo or temperature)
- Which breaker serves the socket
- Whether landlord will approve an electrician; whether agency emergency contractor protocol applies without landlord approval
- Whether Tessa or anyone else can give access (tenant now home)
- Actual condition of socket/circuit
- Landlord's decision on electrician and access
- Which breaker serves the kitchen socket

Tried:
- Asked tenant for symptoms and circuit (events 3, 7)
- Emailed landlord 09:03 and 15:02; called 13:14, voicemail
- Arranged landlord's handyman visit; failed, no access and not competent for fixed wiring (event-23)
- Sent tenant safety advice at decision time
- Agent proposed ESCALATE

Options:
- Recommended: Commission an emergency electrician immediately under agency emergency authority/protocol and inform landlord
- Keep trying the landlord by phone for urgent electrician approval while advising tenant to isolate the circuit/leave if worse
- If tenant reports worsening signs (smoke, sparks, stronger smell), tenant calls 999 / fire service attends

Recommended: Recommended: Commission an emergency electrician immediately under agency emergency authority/protocol and inform landlord

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

**Possible safety hazard mentioned. Treat as urgent.**
