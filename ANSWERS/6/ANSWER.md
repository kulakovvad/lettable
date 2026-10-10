# Case 6

**Decision:** Ask the tenant for more information
**Priority:** P3

## Details

### Case

- **Id:** 6
- **Raised by:** Landlord
- **Request:** The landlord asked for the current solar generation readings for the property.

### Property

- **Address:** 14 Brindlefern Walk, Larkmere, ZZ1 1ZZ

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Timeline

- **Events:** 17, first 2025-09-03T09:10:00+00:00, last 2025-09-18T17:42:00+00:00
- **Channels:** Call 1, Note 4, Update 5, Email 6, SMS 1

### Decision

- **Action:** Ask the tenant for more information
- **Priority:** P3
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-18T17:42:00+00:00
- **Evidence cited:** event-001, event-016, event-017, event-015

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "6",
    "title": null,
    "source_role": "Landlord",
    "status": null,
    "request": "The landlord asked for the current solar generation readings for the property."
  },
  "property": {
    "address": "14 Brindlefern Walk, Larkmere, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "14 Brindlefern Walk, Larkmere, ZZ1 1ZZ",
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
      "ref": null,
      "covers": "unknown"
    },
    "payments": [],
    "deposit": []
  },
  "appointments": [],
  "timeline": {
    "events": 17,
    "first": "2025-09-03T09:10:00+00:00",
    "last": "2025-09-18T17:42:00+00:00",
    "waiting_on": null,
    "channels": {
      "Call": 1,
      "Note": 4,
      "Update": 5,
      "Email": 6,
      "SMS": 1
    }
  },
  "attachments": [],
  "decision": {
    "action": "ASK_TENANT",
    "priority": "P3",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-18T17:42:00+00:00",
    "evidence_refs": [
      "event-001",
      "event-016",
      "event-017",
      "event-015"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The landlord asked for the current solar generation readings for the property.
17 events reviewed, decision as of 2025-09-18T17:42:00+00:00.

## Decision

The landlord (event-001) only asked for the current solar readings. This is an information request with no fault, no contractor and no spend. We have asked the tenant four times (events 6, 10, 13, 16) and found no reading in the case. The tenant replied in event-17 saying the readings were supplied about two weeks earlier by his wife by phone and email. He gave no figures or image. That claim is unverified: nothing in this case's correspondence shows it (events 9, 12 and 15 record no reply). I am not chasing, because the tenant has now replied. I am not escalating, because there is no danger, dispute or authority issue; this is a single missing fact the tenant holds. I staged a polite request for the figure or a photo, and for the approximate date of the wife's contact so the office can check other inboxes and call logs. The landlord has not been updated and has had no reading since 3 Sept. Follow-up is set for 72 hours. If office records show the readings were received, pass them to the landlord instead.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P3) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-21T17:42:00+00:00, waiting on tenant: Awaiting solar reading/photo from tenant; also check office records for earlier phone/email from tenant's wife and update landlord. `followup-2`. Held: not part of the final action ASK_TENANT; a person can release it.

### Message to tenant `message-1`

Dear Ivo, thank you for your reply, and apologies for the repeated messages. We cannot see the readings against this request, so they may have been filed elsewhere. Could you please reply with the current kWh figure from the generation meter or inverter display, or a photo of the screen? If your wife can also tell us roughly when she phoned or emailed, we will check our records. Kind regards, Maya Chen, Northbridge Lettings

## Inconsistencies and mismatches

- **document consistency** (flag): landlord name differs between documents: 'Edwin Vale' vs 'Edwin' (similarity 0.663). [event-001, event-005, event-006, event-013]
- **document consistency** (flag): tenant name differs between documents: 'Ivo Mercer' vs 'Ivo' (similarity 0.673). [event-004, event-006, event-010, event-013, event-014, event-016, event-017]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
