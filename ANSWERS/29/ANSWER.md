# Case 29

**Decision:** Wait, nothing to do yet
**Priority:** P2

## Details

### Case

- **Id:** 29
- **Raised by:** Tenant
- **Request:** I have received a message about a possible heating-system visit, but I do not have a confirmed appointment. Please check what has been arranged.

### Property

- **Address:** 62 Brindlewick Row, Vellumby, ZZ1 1ZZ

### Tenant

- **Phones:** 07700 900683 [event-003]

### Agency

- **Name:** Tamsin Rook (Property Manager, Northbridge Lettings)

### Provider

- **Phones:** 07700 900683 [event-020]

### Appointments

- Tenant reports that a caller identifying himself as a heating contractor asked her to leave the front-door key in the outside meter cabinet for a possible visit [event-001]
- Bram says Wednesday was not booked as a confirmed appointment and that he has not started travelling. [event-012]
- Appointment correspondence logged: tenant message of 13 May at 11:41 and contractor email of 13 May at 12:26. [event-017]

### Timeline

- **Events:** 20, first 2025-05-12T08:10:00+00:00, last 2025-05-14T13:48:00+00:00
- **Channels:** Portal 4, Note 3, SMS 2, Email 9, Call 2

### Decision

- **Action:** Wait, nothing to do yet
- **Priority:** P2
- **Confidence:** 0.72
- **Decided by:** model
- **As of:** 2025-05-14T13:48:00+00:00
- **Evidence cited:** event-002, event-013, event-014, event-015, event-017, event-018, event-019, event-020

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "29",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "I have received a message about a possible heating-system visit, but I do not have a confirmed appointment. Please check what has been arranged."
  },
  "property": {
    "address": "62 Brindlewick Row, Vellumby, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "62 Brindlewick Row, Vellumby, ZZ1 1ZZ",
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
    "phones": [
      {
        "value": "07700 900683",
        "refs": [
          "event-003"
        ]
      }
    ],
    "emails": []
  },
  "landlord": {
    "name": null,
    "names": [],
    "phones": [],
    "emails": []
  },
  "agency": {
    "name": "Tamsin Rook (Property Manager, Northbridge Lettings)",
    "phones": [],
    "emails": [],
    "staff": []
  },
  "provider": {
    "name": null,
    "assigned_ref": null,
    "phones": [
      {
        "value": "07700 900683",
        "refs": [
          "event-020"
        ]
      }
    ],
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
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Tenant reports that a caller identifying himself as a heating contractor asked her to leave the front-door key in the outside meter cabinet for a possible visit",
      "ref": "event-001"
    },
    {
      "when_text": "Bram says Wednesday was not booked as a confirmed appointment and that he has not started travelling.",
      "ref": "event-012"
    },
    {
      "when_text": "Appointment correspondence logged: tenant message of 13 May at 11:41 and contractor email of 13 May at 12:26.",
      "ref": "event-017"
    }
  ],
  "timeline": {
    "events": 20,
    "first": "2025-05-12T08:10:00+00:00",
    "last": "2025-05-14T13:48:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 4,
      "Note": 3,
      "SMS": 2,
      "Email": 9,
      "Call": 2
    }
  },
  "attachments": [],
  "decision": {
    "action": "WAIT",
    "priority": "P2",
    "confidence": 0.72,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-05-14T13:48:00+00:00",
    "evidence_refs": [
      "event-002",
      "event-013",
      "event-014",
      "event-015",
      "event-017",
      "event-018",
      "event-019",
      "event-020"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: I have received a message about a possible heating-system visit, but I do not have a confirmed appointment. Please check what has been arranged.
20 events reviewed, decision as of 2025-05-14T13:48:00+00:00.

## Decision

The tenant asked what has been arranged. The record shows no confirmed appointment (event-002, event-013). The landlord authorised only a diagnostic visit by a "suitably identified" contractor. He has not confirmed Bram Alder is engaged by Hearthline, and has not agreed to entry while the tenant is out or to any key drop (event-014). Bram's later messages (event-018, event-020) keep asking for a key in the shared outside meter cabinet. They give no business address or work reference and they ask the tenant to confirm a Saturday 08:00-13:00 window. The tenant said she can only do Saturday 10:00-12:00, and only if the visitor and purpose are confirmed (event-015). Her consent to share her mobile number is empty (event-017), so we have not given it out. The heating is working and no hazard has been reported, so this is not P0 or P1. The pressure issue is intermittent and the visit is not yet fixed, so P2. We asked the landlord at 09:36 today (event-019) and the reply is not yet due. The chase threshold is 3 days. I rejected chasing, because we only just asked. I rejected escalating, because the facts do not conflict. The landlord, tenant and contractor are all contactable, and the landlord is the party who can settle the open question. I staged an update to the tenant: no confirmed appointment, do not leave a key outside, and no number shared. I scheduled a follow-up. The decision would change if the landlord confirms the contractor and access. We would then instruct the visit for a time that suits the tenant while she is home. It would change to ESCALATE if the landlord does not answer or the contractor keeps pushing for the key drop. The tenant's reports of pressure on her to leave a key outside are worth a person's attention if they continue.

## Actions taken

- **HELD_FOR_REVIEW**: Message to tenant (update, P2) `message-1`. Held: not part of the final action WAIT; a person can release it.
- **COMMITTED**: Follow-up at 2025-05-15T09:48:00+00:00, waiting on landlord: Landlord asked 14 May 09:36 (event-019) to confirm contractor and access; check for reply before Saturday 17 May visit proposal. If still none, chase. `followup-2`. Recorded in the local outbox (no external delivery connected).

### Message to tenant `message-1`

Hello Elowen, thank you for your messages. Here is where things stand. There is no confirmed appointment on our records, and nothing is booked for today or this Wednesday. The landlord has authorised a diagnostic visit for the intermittent boiler pressure loss, but only by a suitably identified heating contractor. He has not agreed to entry while you are out, or to any key being left outside. We have not confirmed the identity or business details of the person who has been contacting you, so please do not leave a key in the meter cabinet or anywhere outside. We have not given your mobile number to anyone, and we won't without your consent. You do not need to reply to the contractor's text about Saturday. We have asked the landlord to clarify who he is engaging and what access he is authorising. Once we have that, we will confirm the visitor, the purpose and a time in writing. We will only arrange it for when you are home, and you said that could be Saturday between 10:00 and 12:00. Please tell us if you hear from the caller again. Kind regards, Tamsin Rook, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
