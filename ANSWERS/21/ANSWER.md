# Case 21

**Decision:** Ask the tenant for more information
**Priority:** P2

## Details

### Case

- **Id:** 21
- **Raised by:** Tenant
- **Request:** The tenant reports that the shower and hot water are not working. They have checked the boiler switch and report that the boiler has no power.

### Property

- **Address:** 17 Wrenfold Quay, Larkhollow, ZZ1 1ZZ

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Timeline

- **Events:** 21, first 2025-05-06T08:14:00+00:00, last 2025-05-16T16:05:00+00:00
- **Channels:** Portal 1, Email 9, Call 8, Note 1, Update 2

### Decision

- **Action:** Ask the tenant for more information
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-05-16T16:05:00+00:00
- **Evidence cited:** event-012, event-017, event-018, event-019, event-020

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "21",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The tenant reports that the shower and hot water are not working. They have checked the boiler switch and report that the boiler has no power."
  },
  "property": {
    "address": "17 Wrenfold Quay, Larkhollow, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "17 Wrenfold Quay, Larkhollow, ZZ1 1ZZ",
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
    "events": 21,
    "first": "2025-05-06T08:14:00+00:00",
    "last": "2025-05-16T16:05:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 9,
      "Call": 8,
      "Note": 1,
      "Update": 2
    }
  },
  "attachments": [],
  "decision": {
    "action": "ASK_TENANT",
    "priority": "P2",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-05-16T16:05:00+00:00",
    "evidence_refs": [
      "event-012",
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

Initial request: The tenant reports that the shower and hot water are not working. They have checked the boiler switch and report that the boiler has no power.
21 events reviewed, decision as of 2025-05-16T16:05:00+00:00.

## Decision

The landlord said by phone (event-018) that his plumber fixed the fault on 14 May. That is hearsay: it rests on a text, with no report, invoice or description of work. The tenant's last word was "Nothing done" (event-012), and she repeated that there was no hot water on 13 May (event-017). My voicemail and email asking for confirmation (event-019, event-020) have had no reply, and they are only about a day old. The tenant has not confirmed the fix, so I cannot close the case. I also cannot chase the landlord, because he answered at event-018 and asked only to be told if the problem persists. Escalation is not needed yet because the tenant is reachable and the email chase is not overdue. The failed voicemail should not be repeated, so I sent a short yes/no email that also asks for details of the letterbox fault she raised at event-017. No danger is reported. Hot water has been out for about 10 days, so this is P2. There is a possible vulnerable-occupant angle: a household member does not speak English and small birds are kept at the property (event-001, event-003). Nothing says anyone is vulnerable, so I did not raise the priority. I scheduled a 24-hour follow-up. If the tenant says it is still not working, or does not reply, I would go back to the landlord for the plumber's report and consider sending our own contractor, which he offered at event-015. Maya's earlier remark that a call-out might be chargeable (event-004) is not relevant now.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-05-17T16:05:00+00:00, waiting on tenant: Await tenant confirmation that hot water is restored; if none, try another channel or go back to landlord for the plumber's report. `followup-2`. Held: not part of the final action ASK_TENANT; a person can release it.

### Message to tenant `message-1`

Hello Iris, the landlord has told us his plumber attended on 14 May and fixed the hot water. We have not yet heard from you, so we cannot treat it as resolved. Please reply with a simple yes or no: is the boiler now on and is hot water working at the taps and shower? If it is still not working, please say so and we will go back to the landlord straight away. Separately, you mentioned the letterbox is not working. We will log that as its own request. Please tell us what is wrong with it (for example broken flap, jammed, or cannot be locked) and whether it affects the security of the front door. Kind regards, Maya Chen, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Letterbox not working (event-017) - needs its own maintenance request
