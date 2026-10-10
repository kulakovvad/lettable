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
- **Confidence:** 0.75
- **Decided by:** model
- **As of:** 2025-09-16T08:33:00+00:00
- **Evidence cited:** event-006, event-011, event-012, event-017, event-020, event-022, event-023

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
    "confidence": 0.75,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-16T08:33:00+00:00",
    "evidence_refs": [
      "event-006",
      "event-011",
      "event-012",
      "event-017",
      "event-020",
      "event-022",
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

The landlord approved the lock repair (event-006) and then told us to use his own contractor, Dorian Wren, and to stand down Peregrine Keyworks (event-011, event-012, event-017). Dorian visited and said a new lock was needed (event-020). The tenant says he is due today after 10:00 (event-023). No attendance or repair is confirmed yet, so this is not a completion and we cannot close it. The tenant replied after our last message (event-022) and said she will update us, so we are not overdue on anyone and a chase would be wrong. Escalation is not needed now. The door can still be locked by hand per event-001, and no one has reported that it cannot be secured, so P0 and P1 do not apply. Priority is P2 because security is a concern and a visit is due today. The decision would change if the tenant reports the door cannot be secured (P0/P1) or the visit does not happen. In that case the next step is to ask for the outcome or escalate to a person to reassign. I did not contact Dorian because no direct contact details for him are in the case. The landlord's earlier complaint about coordination (event-011) was already answered in event-015.

## Actions taken

- **COMMITTED**: Follow-up at 2025-09-16T16:33:00+00:00, waiting on tenant: Tenant (event-023) says the landlord's contractor Dorian Wren is due today after 10:00 and she will update us. Check late afternoon whether he attended and whether the lock was replaced and works. If there is no update, ask the tenant for the outcome. `followup-1`. Recorded in the local outbox (no external delivery connected).

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Broken bedroom blind letting in light (event-021)
- Door glazing the landlord previously said would be addressed (event-021)
- Hot water too hot, per the tenant (event-021); ask for severity and check for a scald risk
- Tenant's question about who is handling these matters is still unanswered (event-021)
