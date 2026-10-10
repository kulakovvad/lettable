# Case 12

**Decision:** Ask the tenant for more information
**Priority:** P2

## Details

### Case

- **Id:** 12
- **Raised by:** Tenant
- **Request:** The bathroom window will not open, the bedroom window will not secure, and keys are missing. Please look into the locks.

### Property

- **Address:** Unit 2, 18 Brindlewick Mews, Orellin ZZ1 1ZZ

### Agency

- **Name:** Ilyra Venn (Property Manager, Northbridge Lettings)

### Money

- **Landlord approval:** for the visit, no amount [event-003]

### Appointments

- Offers Thursday 18 September between 08:30 and 10:30 as a possible visit time. [event-017]
- Passes on Perrin’s Thursday 08:30–10:30 availability and asks Edrin to confirm a visit time. [event-018]

### Timeline

- **Events:** 25, first 2025-09-04T08:08:44+00:00, last 2025-09-25T12:06:33+00:00
- **Channels:** Portal 1, Email 17, Call 5, Update 1, Note 1

### Decision

- **Action:** Ask the tenant for more information
- **Priority:** P2
- **Confidence:** 0.70
- **Decided by:** model
- **As of:** 2025-09-25T12:06:33+00:00
- **Evidence cited:** event-006, event-022, event-023, event-024, event-025, event-003

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "12",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The bathroom window will not open, the bedroom window will not secure, and keys are missing. Please look into the locks."
  },
  "property": {
    "address": "Unit 2, 18 Brindlewick Mews, Orellin ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "Unit 2, 18 Brindlewick Mews, Orellin ZZ1 1ZZ",
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
    "name": "Ilyra Venn (Property Manager, Northbridge Lettings)",
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
      "ref": "event-003",
      "covers": "visit"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Offers Thursday 18 September between 08:30 and 10:30 as a possible visit time.",
      "ref": "event-017"
    },
    {
      "when_text": "Passes on Perrin’s Thursday 08:30–10:30 availability and asks Edrin to confirm a visit time.",
      "ref": "event-018"
    }
  ],
  "timeline": {
    "events": 25,
    "first": "2025-09-04T08:08:44+00:00",
    "last": "2025-09-25T12:06:33+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 17,
      "Call": 5,
      "Update": 1,
      "Note": 1
    }
  },
  "attachments": [],
  "decision": {
    "action": "ASK_TENANT",
    "priority": "P2",
    "confidence": 0.7,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-25T12:06:33+00:00",
    "evidence_refs": [
      "event-006",
      "event-022",
      "event-023",
      "event-024",
      "event-025",
      "event-003"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The bathroom window will not open, the bedroom window will not secure, and keys are missing. Please look into the locks.
25 events reviewed, decision as of 2025-09-25T12:06:33+00:00.

## Decision

Edrin Moss (Keypath Repairs) said by phone that the work was completed on 19 Sept (event-23) and again on 25 Sept (event-25). These are only verbal claims. The file has no appointment, attendance record, visit notes or invoice (event-24). Edrin said on 17 Sept that they had tried three times, had not found Perrin in, and had not collected management keys (event-22). That conflicts with a 19 Sept completion unless keys were collected later, and nothing records that. Because of this I cannot report the work as done or close. The tenant is the one party who can confirm whether anyone attended and whether the locks and keys now work, so I asked Perrin (message-1). Tenant also reported mould in the bathroom (event-6) with no stated health impact or vulnerable occupant, so I asked about extent and health in the same message and did not escalate. If Perrin reports spreading mould or health effects, escalate as P1. Landlord approval (event-3) covers using our own provider but states no amount, and Keypath's assignment is shown only by the reassignment (events 12-15). When the promised invoice arrives it must be checked for property, provider and amount. Any amount must then go to the landlord for approval because none is approved. Escalation is not needed yet: no danger is reported, there is no invoice or dispute, and the tenant has not yet been asked. Waiting alone would leave the unverified completion claim untested. Follow-up is set for 48 hours. Keys are also unresolved, including whether any were held by the contractor.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-27T12:06:33+00:00, waiting on tenant: Await tenant confirmation of whether work was done, and the invoice Edrin promised for 25/26 Sept. Check the invoice against the property, provider, and approval (no amount approved in event-3). `followup-2`. Held: not part of the final action ASK_TENANT; a person can release it.

### Message to tenant `message-1`

Hello Perrin, the contractor (Keypath Repairs) has told us the lock work at Unit 2, 18 Brindlewick Mews was completed on Friday 19 September. We have no visit record, so we would like to check with you. Did anyone attend on or around that date, and did you let them in or did they use management keys? Does the bedroom window now lock, does the bathroom window open and lock, and have you been given keys, including for the kitchen window? If anything is still not working, please tell us what. You also mentioned mould in the bathroom. Could you tell us roughly how much there is and whether it is spreading or affecting anyone's health? Kind regards, Ilyra Venn, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Bathroom mould reported by tenant (event-6): assess for health impact
