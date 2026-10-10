# Case 4

**Decision:** Wait, nothing to do yet
**Priority:** P2

## Details

### Case

- **Id:** 4
- **Raised by:** Tenant
- **Request:** The tenant reports that the front-door lock feels loose and works intermittently. The door sometimes catches before closing, although the tenant says it can currently be locked by hand. A newly cut spare key does not work. The tenant is concerned about the effect on the property's security.

### Property

- **Address:** 18 Larkspur Quay, Morrowfen, ZZ1 1ZZ

### Agency

- **Name:** Mira Sol (Property Manager, Northbridge Lettings)

### Appointments

- Apologises for the failed coordination around the earlier Saturday visit and provides the tenant's current availability: that day, 4 September, and 8 and 9 Sept [event-015]
- The tenant reports a later visit by Dorian Wren, separate from the earlier Saturday visit reported by the landlord. [event-020]

### Timeline

- **Events:** 23, first 2025-08-27T10:05:00+00:00, last 2025-09-16T08:33:00+00:00
- **Channels:** Portal 1, Email 13, Call 5, Note 4

### Decision

- **Action:** Wait, nothing to do yet
- **Priority:** P2
- **Confidence:** 0.70
- **Decided by:** model
- **As of:** 2025-09-16T08:33:00+00:00
- **Evidence cited:** event-006, event-011, event-016, event-017, event-020, event-023

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "4",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The tenant reports that the front-door lock feels loose and works intermittently. The door sometimes catches before closing, although the tenant says it can currently be locked by hand. A newly cut spare key does not work. The tenant is concerned about the effect on the property's security."
  },
  "property": {
    "address": "18 Larkspur Quay, Morrowfen, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "18 Larkspur Quay, Morrowfen, ZZ1 1ZZ",
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
    "name": "Mira Sol (Property Manager, Northbridge Lettings)",
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
    "payments": [],
    "deposit": []
  },
  "appointments": [
    {
      "when_text": "Apologises for the failed coordination around the earlier Saturday visit and provides the tenant's current availability: that day, 4 September, and 8 and 9 Sept",
      "ref": "event-015"
    },
    {
      "when_text": "The tenant reports a later visit by Dorian Wren, separate from the earlier Saturday visit reported by the landlord.",
      "ref": "event-020"
    }
  ],
  "timeline": {
    "events": 23,
    "first": "2025-08-27T10:05:00+00:00",
    "last": "2025-09-16T08:33:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 13,
      "Call": 5,
      "Note": 4
    }
  },
  "attachments": [],
  "decision": {
    "action": "WAIT",
    "priority": "P2",
    "confidence": 0.7,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-16T08:33:00+00:00",
    "evidence_refs": [
      "event-006",
      "event-011",
      "event-016",
      "event-017",
      "event-020",
      "event-023"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The tenant reports that the front-door lock feels loose and works intermittently. The door sometimes catches before closing, although the tenant says it can currently be locked by hand. A newly cut spare key does not work. The tenant is concerned about the effect on the property's security.
23 events reviewed, decision as of 2025-09-16T08:33:00+00:00.

## Decision

The landlord approved the lock repair or replacement (event-006). He then told us to use his own contractor, Dorian Wren, and not to instruct anyone else (event-011, event-016). Our selected locksmith was stood down (event-017). On 9 September the tenant said Dorian attended, agreed a new lock was needed and would return the following week, and that the lock was now worse (event-020). On 16 September the tenant says he is due today after 10:00 and she will update us (event-023). Nothing is overdue, because the visit is today and she has promised an update. A chase to the landlord or contractor would be premature, and instructing another provider would breach the landlord's instruction. Escalation is not needed, because the case is progressing and the tenant is contactable. Nothing in the case shows completion: there is no confirmation of attendance, a new lock, a working spare key or an invoice position. Closing is therefore not possible, and the case-4 completion signal at event-023 is not a completion. Priority is P2, not P0. The tenant earlier said the door could be locked by hand (event-001), but event-020 says it is now worse, and we do not know whether the door can still be secured. A lock affecting security can be P1 under policy. If the tenant reports the door cannot be secured, or the contractor does not attend today, re-judge as P1 and escalate. A follow-up is set for this afternoon to ask the tenant for the outcome.

## Actions taken

- **COMMITTED**: Follow-up at 2025-09-16T14:33:00+00:00, waiting on tenant: Tenant (event-023) says Dorian Wren is due today after 10:00 and she will update us. Check whether he attended and whether the lock was replaced and works, including spare key. If there is no update, ask her this evening. `followup-1`. Recorded in the local outbox (no external delivery connected).

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Broken bedroom blind letting in light (event-021)
- Door glazing the landlord previously said would be addressed (event-021)
- Hot water reported as too hot (event-021). This may be a safety concern and needs its own request. Ownership and status were not confirmed to the tenant.
- Landlord's complaint about contractor coordination (event-011), already noted
- Skirting-board paint touch-ups agreed at the tenant's expense (event-005, event-011)
