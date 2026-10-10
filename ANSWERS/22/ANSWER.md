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
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-25T09:08:19+00:00
- **Evidence cited:** event-029, event-030, event-031, event-028, event-027

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
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-25T09:08:19+00:00",
    "evidence_refs": [
      "event-029",
      "event-030",
      "event-031",
      "event-028",
      "event-027"
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

The tenant's "Yes, the job is completed" (event-031) is a claim that conflicts with the tenant's own call the day before, when they said no replacement had arrived and there was no packaging (event-030). The landlord said delivery, setup and disposal were arranged but gave no date (event-029). The same message from the tenant asks whether a washing-machine change is still happening, which is an unanswered question. The job also shifted from a repair (events 10, 18, 21) to a replacement (events 23, 27). The landlord asked for a removal and replacement quote (event-028) and complained about delays (event-029). Two versions of the same fact, plus a landlord complaint, are positive escalation reasons, so closing is not allowed. There is no assigned provider, no invoice and no amount in the case, so there is nothing to approve or instruct. A routine ask to the tenant alone would not resolve the conflict with the landlord's account, and a person should handle the complaint and decide how to reconcile it. The tenant has no working machine, but no danger is reported, so I set P2 rather than P0 or P1. Nothing in the case tries to alter our process.

## Actions taken

- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Washer-dryer E13 case: the tenant says "the job is completed" (event-031), but the replacement machine has not been delivered (event-030). The landlord has also complained about delays (event-029). Do not close.

Respond by 2025-09-26T09:08:19+00:00 (P2, route property_manager).

Known:
- Tenant reported E13 on 20 Aug; the machine is unusable and the tenant is washing by hand (events 7, 13).
- Landlord said the insurer approved a repair (event-010). An engineer was reported booked for 9 Sep and was expected that day (events 18, 21). No engineer report or confirmation is in the case.
- Landlord later said a replacement was needed (event-023) and that a new machine was ordered (event-027). On 21 Sep they said delivery, setup and disposal were arranged, with no date given (event-029). They also asked for a quote for removal and replacement (event-028).
- On 24 Sep the tenant said no replacement had arrived and there was no packaging at the property (event-030).
- On 25 Sep the tenant answered a maintenance follow-up with 'Yes, the job is completed' and asked whether a planned washing-machine change is still happening (event-031). It is unclear what 'the job' means, and it contradicts event-030.
- Landlord complaint about slow response (event-029).
- No provider is assigned in the case, no invoice or quote amounts are recorded, and no money mentions exist. The landlord appears to be arranging the supplier and installers directly.
- Property: 8 Brackenmere Walk, Vellumford, ZZ1 1ZZ (index)
- Request: The washer-dryer displays error E13. The tenant has tried draining the water, but the appliance still does not work. (request)

Not known:
- Whether the old machine was repaired, replaced or neither.
- Who the supplier and installers are, and the delivery or installation date.
- Which 'other email' about a planned washing-machine change the tenant received, and who sent it.
- Who pays for the replacement and removal, and whether there is a quote. The landlord's own statement (event-029) suggests they arranged it themselves.
- Which maintenance follow-up the tenant was replying to.
- Whether the machine was repaired or replaced
- Delivery or installation date and who the installers are
- Which email the tenant received about the planned change

Tried:
- Asked the tenant for the appliance details several times (events 2, 12), and they were eventually supplied to the landlord (event-17).
- Passed on the appointment (event-19) and asked the tenant for the outcome (event-22).
- Measured the space and relayed it to the landlord (events 24-26).
- Phoned the tenant about delivery on 24 Sep (event-30).
- Agent proposed ESCALATE

Options:
- Recommended: Contact the landlord for the supplier or installer details and delivery date, and acknowledge their delay complaint. Then answer the tenant's question and correct the record so the job stays open until installation is confirmed.
- Phone the tenant to clarify what they meant by 'completed' and which email they received. Then reconcile with the landlord's arrangements.
- If the landlord wants the agency to take on the removal and replacement, get a written quote and landlord approval before instructing anyone.

Recommended: Recommended: Contact the landlord for the supplier or installer details and delivery date, and acknowledge their delay complaint. Then answer the tenant's question and correct the record so the job stays open until installation is confirmed.

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Landlord complaint about slow response (event-029)
