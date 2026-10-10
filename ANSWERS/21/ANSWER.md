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
- **Evidence cited:** event-001, event-017, event-018, event-019, event-020

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
      "event-001",
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

The tenant reported no hot water on 6 May (event-001). On 13 May they said it was still not fixed (event-017). The landlord said on 15 May, from a text from his plumber, that the plumber fixed it on 14 May (event-018). That is a second-hand claim with no report, invoice or description of the checks, so it is not proof. Our voicemail and email asking the tenant to confirm (events 019, 020) are unanswered after 1.3 days. The tenant is the only party who can confirm the outcome, so I am asking for confirmation, plus details of the letterbox fault. A call was blocked because only one written message has gone unanswered. Escalation is not needed: no danger is reported, the landlord and tenant accounts differ only because we lack confirmation, and the tenant is reachable. One caveat on priority: the household has a non-English speaker and birds, and there is no hot water in May. These facts are not verified as a safety risk, so P2 applies rather than P1. Closing is not possible. The tenant has not confirmed the fix, a letterbox query is unanswered, and the invoice position and the plumber's work are unknown. If the tenant says it is still broken, I will go back to the landlord and offer an agency contractor. If there is no reply in 24 hours, I will place a call.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-05-17T16:05:00+00:00, waiting on tenant: Tenant has not confirmed hot water restored after landlord's claimed fix on 14 May; if no reply, place a call (two unanswered written messages) and tell the landlord if still broken. `followup-2`. Held: not part of the final action ASK_TENANT; a person can release it.

### Message to tenant `message-1`

Dear Iris, the landlord has told us his plumber attended on 14 May and fixed the hot water. We have not seen any report from the plumber, and we want to hear from you before treating this as done. Please reply to confirm: (1) Is the boiler powered on and is hot water working at the taps and shower now? (2) Did anyone attend the property, and if so, when? If there is still no hot water, tell us and we will go back to the landlord straight away. You also mentioned a faulty letterbox on 13 May. We will log it as a separate request. Please send a short description of the fault and any photo. Kind regards, Maya Chen, Northbridge Lettings

## What was blocked or failed

- Tool gate refused `place_call`: only 1 unanswered written message(s) to the tenant so far; a call is for when 2 go unanswered, written contact bounces, or the matter is urgent

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Faulty letterbox reported by the tenant on 13 May (event-017); needs its own maintenance request
