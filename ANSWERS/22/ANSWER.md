# Case 22

**Decision:** Escalate to a person
**Priority:** P2

## Details

### Case

- **Id:** 22
- **Raised by:** Tenant
- **Request:** The washer-dryer displays error E13. The tenant has tried draining the water, but the appliance still does not work.

### Property

- **Address:** 8 Brackenmere Walk, Vellumford, ZZ1 1ZZ

### Agency

- **Name:** Mara Venn (Property Manager, Northbridge Lettings)

### Money

- **Landlord approval:** for the visit, no amount [event-010]

### Appointments

- Reported that an engineer had been booked for 9 September between 12:00 and 17:00. [event-018]
- Passed on the reported 9 September appointment window and asked that someone be available for access. [event-019]

### Timeline

- **Events:** 31, first 2025-08-20T16:32:01+00:00, last 2025-09-25T09:08:19+00:00
- **Channels:** Email 28, Call 2, Note 1

### Decision

- **Action:** Escalate to a person
- **Priority:** P2
- **Confidence:** 0.75
- **Decided by:** model
- **As of:** 2025-09-25T09:08:19+00:00
- **Evidence cited:** event-029, event-030, event-031, event-028, event-022

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "22",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The washer-dryer displays error E13. The tenant has tried draining the water, but the appliance still does not work."
  },
  "property": {
    "address": "8 Brackenmere Walk, Vellumford, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "8 Brackenmere Walk, Vellumford, ZZ1 1ZZ",
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
    "name": "Mara Venn (Property Manager, Northbridge Lettings)",
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
      "ref": "event-010",
      "covers": "visit"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Reported that an engineer had been booked for 9 September between 12:00 and 17:00.",
      "ref": "event-018"
    },
    {
      "when_text": "Passed on the reported 9 September appointment window and asked that someone be available for access.",
      "ref": "event-019"
    }
  ],
  "timeline": {
    "events": 31,
    "first": "2025-08-20T16:32:01+00:00",
    "last": "2025-09-25T09:08:19+00:00",
    "waiting_on": null,
    "channels": {
      "Email": 28,
      "Call": 2,
      "Note": 1
    }
  },
  "attachments": [],
  "decision": {
    "action": "ESCALATE",
    "priority": "P2",
    "confidence": 0.75,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-25T09:08:19+00:00",
    "evidence_refs": [
      "event-029",
      "event-030",
      "event-031",
      "event-028",
      "event-022"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The washer-dryer displays error E13. The tenant has tried draining the water, but the appliance still does not work.
31 events reviewed, decision as of 2025-09-25T09:08:19+00:00.

## Decision

The tenant's "Yes, the job is completed" (event-031) is not reliable. The day before, the tenant said no replacement had arrived and there was no packaging (event-030). The landlord says delivery, setup and disposal were arranged but gave no date (event-029). The tenant's same message asks whether the washing-machine change is still happening, which is an unanswered question, so closing is blocked under policy. The landlord also complained that our response took too long (event-029), and policy sends complaints about delays to a person. There is a conflict between the tenant's completion claim and the delivery evidence. No provider is assigned and no quote or amount is in the case, although the landlord asked for a quote (event-028). The invoice position is unknown. The landlord has not been asked for a delivery date since event-026, but a routine ask would not deal with the complaint. I staged a holding update to the tenant, which says the job is not treated as complete and asks for the other email. No hazard is reported and the machine has been out of use since August, so I rated it P2. The decision would change if the landlord confirms a delivery date or the tenant confirms installation.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to complaints `escalation-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Message to tenant (update, P2) `message-2`. Held: not part of the final action ESCALATE; a person can release it.

### Message to tenant `message-2`

Hello Ari, thank you for your reply. We understand from your call yesterday that the replacement washing machine has not arrived yet, so we are not treating the job as complete. The landlord has told us a replacement is being arranged, but we have no delivery date yet. We are checking with them and will update you as soon as we know. Could you also forward us the other email you received about the washing-machine change? Kind regards, Mara Venn, Northbridge Lettings

## Handover for the person taking over

Washer-dryer (E13) case at 8 Brackenmere Walk is not complete, although the tenant's latest email says "the job is completed". The landlord has complained about slow responses, and the replacement delivery is unconfirmed. The tenant has had no working machine since 20 Aug.

Respond by 2025-09-26T09:08:19+00:00 (P2, route complaints).

Known:
- Tenant reported E13 fault on 20 Aug; machine unusable (event-007).
- Landlord said the insurer approved a repair (event-010). An engineer was reportedly booked for 9 Sep and was said to be about to arrive (events 18, 21). No outcome was ever recorded; the tenant was asked on 10 Sep (event-022) and no answer is in the case.
- Landlord then said a replacement was needed (event-023), ordered one (event-027) and later said delivery, setup and disposal were arranged (event-029). No delivery date was given, and no quote or amount is in the case.
- Landlord complained that our response took too long (event-029).
- On 24 Sep the tenant said no replacement had arrived and there was no packaging (event-030).
- On 25 Sep the tenant wrote 'Yes, the job is completed' in reply to a maintenance follow-up. The same message asks whether the planned washing-machine change is still happening (event-031).
- Property: 8 Brackenmere Walk, Vellumford, ZZ1 1ZZ (index)
- Request: The washer-dryer displays error E13. The tenant has tried draining the water, but the appliance still does not work. (request)

Not known:
- Whether the tenant's 'completed' refers to this job. It conflicts with event-030 (nothing delivered the day before), so it is not safe to rely on.
- Delivery and installation date and the installer or supplier. No provider is recorded on the case.
- Who is paying for the replacement and whether any cost is outstanding. The landlord asked for a quote in event-028 and no amount is in the case.
- What the 9 Sep engineer found.
- Which 'other email' about the washing-machine change the tenant received.
- Delivery and installation date
- Which provider or installer is involved
- Cost and who pays

Tried:
- Asked the tenant for appliance details several times (events 2, 12) and the details were eventually passed to the landlord (event-017).
- Asked the tenant for an outcome on 10 Sep (event-022), measurements on 14 Sep (event-024) and delivery status by call on 24 Sep (event-030).
- Passed the tenant's measurements to the landlord on 16 Sep (event-026). The landlord has not been asked for delivery details since.
- Agent proposed ESCALATE

Options:
- Recommended: Reply to the landlord's complaint, and ask for the delivery date, installer and cost or insurer arrangements. Then update the tenant. Do not close until the new machine is installed and the tenant confirms.
- Ask the tenant what the 'completed' message and the 'other email' referred to, and confirm whether the machine is installed. Close only after landlord and tenant confirmation and invoice position are known.
- If the landlord cannot give delivery details, agree with them whether the agency should arrange a provider, which needs the landlord's written approval of any quote.

Recommended: Recommended: Reply to the landlord's complaint, and ask for the delivery date, installer and cost or insurer arrangements. Then update the tenant. Do not close until the new machine is installed and the tenant confirms.

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
