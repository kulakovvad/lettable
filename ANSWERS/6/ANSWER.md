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
- **Evidence cited:** event-001, event-016, event-017, event-005

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
      "event-005"
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

The landlord (event-001) only wants the current solar generation readings. It is an information request with no fault, deadline or contractor, so no approval or provider is involved. We have asked the tenant four times (events 6, 10, 13, 16). In event-17 he says the readings were supplied about two weeks ago by his wife, by phone and email. No figures or image are in the case, and nothing in the request shows a reading received. That is a claim I cannot verify, and it is not a safety or fraud issue. The tenant has just replied, so chasing again or waiting is not appropriate. Escalating is not needed yet. I have asked him to resend the figure or a photo and to say when and from which address his wife emailed, so that staff can trace the earlier message. The case should not close and the landlord should not be told it is done, as no reading is in the case. If a reading turns up in another mailbox or call log, we can pass it to Edwin. If there is still no reading after this reply, a person should check the office inbox and call log. Event-005 also marked approval as given without any landlord approval message; this is moot because no work is being instructed.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P3) `message-1`. Recorded in the local outbox (no external delivery connected).

### Message to tenant `message-1`

Dear Ivo, thank you for your reply, and apologies for the repeated messages. We cannot see the readings against this request, so they may have been logged elsewhere. Could you or your wife resend the current kWh figure from the generation meter or inverter display, or a photo of the screen? If you can, please also tell us roughly what date and which email address your wife used, so we can trace the earlier message. Kind regards, Maya Chen, Northbridge Lettings

## Inconsistencies and mismatches

- **document consistency** (flag): landlord name differs between documents: 'Edwin Vale' vs 'Edwin' (similarity 0.663). [event-001, event-005, event-006, event-013]
- **document consistency** (flag): tenant name differs between documents: 'Ivo Mercer' vs 'Ivo' (similarity 0.673). [event-004, event-006, event-010, event-013, event-014, event-016, event-017]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
