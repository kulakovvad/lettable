# Case 29

**Decision:** Ask the tenant for more information
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

- **Action:** Ask the tenant for more information
- **Priority:** P2
- **Confidence:** 0.60
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
    "action": "ASK_TENANT",
    "priority": "P2",
    "confidence": 0.6,
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

The tenant asked what has been arranged. The record shows no confirmed appointment (event-002, event-013). The landlord authorised a diagnostic visit only by a "suitably identified" contractor. He has not confirmed that Bram Alder is engaged by Hearthline, has not agreed an external key arrangement, and has not agreed entry while the tenant is out (event-014). Our 14 May clarification request to him (event-019) is only about 4 hours old, so a chase is not due (policy chases after 3 days). Bram's identity is still unverified: he gave no work reference or business address (event-009, event-012, event-016). He has asked twice for a key to be left in a shared outside cabinet (event-018, event-020). He proposed a Saturday window of 08:00 to 13:00 (event-020), but the tenant offered only 10:00 to 12:00 (event-015). The tenant has no consent recorded for sharing her number (event-017). I told her that nothing is confirmed, not to leave a key outside, not to confirm yet, and that her number has not been shared. I asked her to confirm her availability window. I did not escalate because there is no reported danger: the heating works (event-015), so priority is P2. There is also no conflict of fact between sources, and the landlord is not yet overdue. I would escalate if the landlord does not respond, or if the contractor's identity cannot be verified before Saturday 17 May. I did not call the contractor because the code gate did not require it. Nothing in the case tries to change my process.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-05-15T13:48:00+00:00, waiting on landlord: Landlord reply on contractor identity and access (event-019) due; tenant reply on Saturday window. Chase landlord if silent; escalate if identity stays unverified before Saturday. `followup-2`. Held: not part of the final action ASK_TENANT; a person can release it.

### Message to tenant `message-1`

Hello Elowen, thank you for your messages. To answer your question: no appointment is confirmed. Our work order has no booked visit. The landlord has authorised a diagnostic visit for the boiler pressure loss, but only by a suitably identified contractor. We have not yet verified Bram Alder's business details, and we are waiting for the landlord to confirm the access arrangements. Please do not leave a key in the meter cabinet or anywhere outside, and please do not confirm Saturday with the 07700 900683 number yet. We have not shared your mobile number with him and will not without your agreement. His suggested window of 08:00 to 13:00 is wider than the 10:00 to 12:00 you said you could do on Saturday 17 May. Please confirm that you can only be home for 10:00 to 12:00 and that you want any visit limited to that window. We will write again once identity, purpose and timing are confirmed. Northbridge Lettings (Tamsin Rook)

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
