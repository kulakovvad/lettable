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
- **Confidence:** 0.70
- **Decided by:** model
- **As of:** 2025-09-17T09:04:05+00:00
- **Evidence cited:** event-002, event-003, event-005, event-007, event-015, event-016, event-019

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
    "confidence": 0.7,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-17T09:04:05+00:00",
    "evidence_refs": [
      "event-002",
      "event-003",
      "event-005",
      "event-007",
      "event-015",
      "event-016",
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

The tenant reported a TV fault and a flickering, popping downstairs light (event-1). The landlord's "Please sort it" (event-3) answered a request about the TV only (event-2). It did not cover the downstairs light (event-5), and it did not settle who owns the TV or whether it can be disposed of. The landlord has since sent an away auto-reply (event-7). Bracken Spark Services proposed 29 September after 15:00 (event-19), which falls within the tenant's availability (event-16). No exact time is given, nothing is confirmed, and there is no quote. Because there is no landlord approval for the combined electrical visit, I should not instruct the provider yet. Policy says the agency cannot approve work itself. I have routed the visit approval and the TV ownership question to the landlord. Nothing is overdue, so escalation is not needed. The tenant is using a lamp, the TV is unplugged, and there is no reported danger or sparking, so this is P3. A follow-up is set for 72 hours. The rear-door handle is a separate issue, and the tenant agreed to submit it separately (event-15, event-18). Nothing in the case tries to change my process. If the landlord approves, I would instruct Bracken Spark and confirm the booking with the tenant, including the request to call on arrival because of the dog.

## Actions taken

- **COMMITTED**: Approval request to landlord to attend or quote, no cost (Bracken Spark Services electrician visit (proposed 29 Sept after 15:00) to inspect the downstairs bedroom light and the upstairs TV fault; confirm TV ownership/disposal) `approval_request-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-20T09:04:05+00:00, waiting on landlord: Landlord approval for combined electrical visit (light + TV) and TV ownership; landlord had auto-away reply 7 Sept; 29 Sept slot proposed and unconfirmed. `followup-2`. Held: not part of the final action ROUTE_FOR_APPROVAL; a person can release it.

### Message to landlord `approval_request-1`

Hello Corin, this is Oren Pike at Northbridge Lettings regarding 8 Vellum Court, Brindlewick. You replied "Please sort it" (5 Sept) to our request about the tenant's TV fault. The tenant also reported a downstairs bedroom light that flickers and pops when switched on, which was not in that request. Bracken Spark Services (electrician) has proposed attending on 29 September after 15:00, within the tenant's availability, to look at both. No quote or cost has been given yet.

Please could you confirm: (1) that you approve the electrician attending to inspect the downstairs light and the TV fault, with any repair quote to come back to you for approval before work; (2) whether the TV is yours. You mentioned you don't remember leaving one, and the tenant says it may not be worth repairing and is open to it being removed. Please also say whether you want us to deal with its removal, or whether it is the tenant's own. We won't instruct the visit until we hear from you. Thanks, Oren Pike, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Rear-door handle has come off (raised by phone in event-15). Tenant to submit a separate request; no record or handyman assigned (event-18).
