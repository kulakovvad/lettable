# Case 7

**Decision:** Send for landlord approval
**Priority:** P3

## Details

### Case

- **Id:** 7
- **Raised by:** Tenant
- **Request:** The tenant reports that a Samsung television in an upstairs bedroom has an electrical fault and trips a fuse when plugged in; it is currently unplugged. They also report a downstairs bedroom light that flickers and makes a popping sound when switched on. Please arrange any property access in advance

### Property

- **Address:** 8 Vellum Court, Brindlewick, ZZ1 1ZZ

### Agency

- **Name:** Oren Pike (Maintenance Coordinator, Northbridge Lettings)

### Appointments

- Provided availability for an electrical visit: 23 September after 15:00, 24 September after 15:00, 25 September after 12:30, 29 September after 15:00, 30 Septem [event-016]
- Proposed attending on 29 September after 15:00. [event-019]

### Timeline

- **Events:** 19, first 2025-09-04T13:05:32+00:00, last 2025-09-17T09:04:05+00:00
- **Channels:** Portal 1, Email 10, Note 3, Update 2, SMS 2, Call 1

### Decision

- **Action:** Send for landlord approval
- **Priority:** P3
- **Confidence:** 0.72
- **Decided by:** model
- **As of:** 2025-09-17T09:04:05+00:00
- **Evidence cited:** event-001, event-002, event-003, event-004, event-005, event-007, event-015, event-016, event-018, event-019

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "7",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The tenant reports that a Samsung television in an upstairs bedroom has an electrical fault and trips a fuse when plugged in; it is currently unplugged. They also report a downstairs bedroom light that flickers and makes a popping sound when switched on. Please arrange any property access in advance"
  },
  "property": {
    "address": "8 Vellum Court, Brindlewick, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "8 Vellum Court, Brindlewick, ZZ1 1ZZ",
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
    "name": "Oren Pike (Maintenance Coordinator, Northbridge Lettings)",
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
      "when_text": "Provided availability for an electrical visit: 23 September after 15:00, 24 September after 15:00, 25 September after 12:30, 29 September after 15:00, 30 Septem",
      "ref": "event-016"
    },
    {
      "when_text": "Proposed attending on 29 September after 15:00.",
      "ref": "event-019"
    }
  ],
  "timeline": {
    "events": 19,
    "first": "2025-09-04T13:05:32+00:00",
    "last": "2025-09-17T09:04:05+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 10,
      "Note": 3,
      "Update": 2,
      "SMS": 2,
      "Call": 1
    }
  },
  "attachments": [],
  "decision": {
    "action": "ROUTE_FOR_APPROVAL",
    "priority": "P3",
    "confidence": 0.72,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-17T09:04:05+00:00",
    "evidence_refs": [
      "event-001",
      "event-002",
      "event-003",
      "event-004",
      "event-005",
      "event-007",
      "event-015",
      "event-016",
      "event-018",
      "event-019"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The tenant reports that a Samsung television in an upstairs bedroom has an electrical fault and trips a fuse when plugged in; it is currently unplugged. They also report a downstairs bedroom light that flickers and makes a popping sound when switched on. Please arrange any property access in advance because a dog is at the property.
19 events reviewed, decision as of 2025-09-17T09:04:05+00:00.

## Decision

The electrician (Rian Sol, Bracken Spark Services) proposed 29 September after 15:00 (event-019). That date is within the tenant's availability (event-016). The landlord's only written approval is "Please sort it" (event-003). It answered a request about the TV alone (event-002) and did not cover the downstairs light, which the tenant raised (event-001) and we added to the record (event-005). The landlord is also unsure the TV is theirs, and the tenant is open to it being discarded (event-015). No instruction on disposal or repair was ever given, and no spending limit was set (event-004). The landlord's last reply was an out-of-office message (event-007). I did not instruct or confirm the appointment, because the approval does not clearly cover the combined scope. I did not escalate, because the landlord is the right party to decide and is reachable. I did not wait, because the proposed slot needs a decision. No quote exists, so no amount is routed. Priority is P3: the TV is unplugged, the tenant is using a lamp and can manage without the light (event-015), and no hazard is reported beyond the tenant-reported light flicker and pop. Unrelated issue: the rear-door handle came off. It was raised on the call only, and the tenant has agreed to submit it as a separate request (events 015 and 018). The case should not close until that is done. What would change the decision: if the landlord approves the scope, we instruct Bracken Spark and confirm the slot with the tenant. If the light worsens, for example visible sparking or burning smells, treat it as P0.

## Actions taken

- **COMMITTED**: Approval request to landlord to attend or quote, no cost (Bracken Spark Services electrician visit at 8 Vellum Court: downstairs bedroom light (flickering/popping) plus tenant-reported TV fault; proposed slot 29 September after 15:00) `approval_request-1`. Recorded in the local outbox (no external delivery connected).

### Message to landlord `approval_request-1`

Hi Corin, Bracken Spark Services (electrician) has proposed attending 8 Vellum Court on 29 September after 15:00, which fits the tenant's availability. Two points need your decision before we confirm. (1) Your earlier "Please sort it" covered the TV only. The tenant also reported a downstairs bedroom light that flickers and pops when switched on. Please confirm you approve the electrician attending for the light as well. No quote or cost has been received yet, and we will come back to you for approval of any quote. (2) You said you don't remember leaving a TV. The tenant now believes the TV's main board has failed and is open to it being removed or discarded. Please tell us whether the TV is yours and whether you want it repaired, left, or removed, or whether the electrician should only look at the light and the circuit. Thanks, Oren Pike, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Rear-door handle has come off: the tenant should submit a separate request; no handyman is assigned (events 015 and 018)
