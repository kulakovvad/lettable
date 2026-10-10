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
- **Confidence:** 0.75
- **Decided by:** model
- **As of:** 2025-09-25T12:06:33+00:00
- **Evidence cited:** event-003, event-006, event-008, event-019, event-022, event-023, event-025

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
    "confidence": 0.75,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-25T12:06:33+00:00",
    "evidence_refs": [
      "event-003",
      "event-006",
      "event-008",
      "event-019",
      "event-022",
      "event-023",
      "event-025"
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

Keypath Repairs (Edrin Moss) says verbally that the work was completed on 19 Sept (events 23, 25) and promises an invoice (26 Sept, or "later today" in event 25). This is only a claim: the file has no appointment, attendance record, visit notes or invoice. The tenant said they would be at work and asked for management keys (events 8, 19), and Edrin said in event 22 that they had not collected the keys and had not found the tenant in, so how access happened is unexplained. The landlord approved our own provider with no spending limit (event 3), and no quote or amount exists. The provider changed from Hearthline to Keypath (events 12-18), and the case shows no landlord approval for Keypath specifically. That is only a note for the person to check. I cannot close: there is no verified completion, no invoice position, and the key position is unknown. The tenant is the party who can confirm attendance and whether the locks and keys now work. I have staged that question, and it also asks for details of the bathroom mould mentioned in event 6, which is not yet established as a health-impact case. Escalation is not needed yet. I would escalate if the tenant says the work was not done, because that would conflict with the provider's claim, or if the mould affects health. The invoice should be checked against the landlord's approval when it arrives. Waiting on the invoice alone is not enough, as the tenant's confirmation is also needed. No instructions in the case try to alter my process.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-27T12:06:33+00:00, waiting on tenant: Tenant confirmation of attendance and fix; Keypath invoice promised for 25/26 Sept `followup-2`. Held: not part of the final action ASK_TENANT; a person can release it.

### Message to tenant `message-1`

Hi Perrin, this is Ilyra Venn at Northbridge Lettings with an update on the window lock work at Unit 2, 18 Brindlewick Mews. The contractor, Keypath Repairs, has told us the work was completed on Friday 19 September. We have no visit record or invoice yet, so we want to check with you before treating it as done. Could you tell us: 1) Did anyone attend, and did you let them in or did they use management keys? 2) Do the bathroom and bedroom window locks now work (bathroom opens, bedroom secures)? 3) Have you been given a key for the kitchen window and any other missing keys? If anything is still not working, please tell us what. You also mentioned mould in the bathroom on our call. Could you send a photo and tell us roughly how large the area is and whether it is spreading? Thank you.

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Bathroom mould reported in event 6 needs separate assessment
