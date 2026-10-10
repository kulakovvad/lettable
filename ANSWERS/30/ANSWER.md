# Case 30

**Decision:** Ask the tenant for more information
**Priority:** P2

## Details

### Case

- **Id:** 30
- **Raised by:** Tenant
- **Request:** The smoke alarm on the upstairs landing kept beeping despite attempts to stop it. The tenant removed it, and a small opening remains in the ceiling where it was fitted.

### Property

- **Address:** 8 Brindlefern Walk, Oakhollow, ZZ1 1ZZ

### Agency

- **Name:** Ivo Merrick (Property Manager, Northbridge Lettings)

### Timeline

- **Events:** 15, first 2025-08-20T18:02:51+00:00, last 2025-09-06T18:42:00+00:00
- **Channels:** Portal 1, Note 5, Email 9

### Decision

- **Action:** Ask the tenant for more information
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-06T18:42:00+00:00
- **Evidence cited:** event-001, event-007, event-009, event-012, event-014

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "30",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The smoke alarm on the upstairs landing kept beeping despite attempts to stop it. The tenant removed it, and a small opening remains in the ceiling where it was fitted."
  },
  "property": {
    "address": "8 Brindlefern Walk, Oakhollow, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "8 Brindlefern Walk, Oakhollow, ZZ1 1ZZ",
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
    "name": "Ivo Merrick (Property Manager, Northbridge Lettings)",
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
    "events": 15,
    "first": "2025-08-20T18:02:51+00:00",
    "last": "2025-09-06T18:42:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Note": 5,
      "Email": 9
    }
  },
  "attachments": [],
  "decision": {
    "action": "ASK_TENANT",
    "priority": "P2",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-06T18:42:00+00:00",
    "evidence_refs": [
      "event-001",
      "event-007",
      "event-009",
      "event-012",
      "event-014"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The smoke alarm on the upstairs landing kept beeping despite attempts to stop it. The tenant removed it, and a small opening remains in the ceiling where it was fitted.
15 events reviewed, decision as of 2025-09-06T18:42:00+00:00.

## Decision

The landlord said he would do the work himself (event-7, event-10). On 6 Sept he claimed it was completed on 31 August (event-12) and added details about the sockets and a dehumidifier (event-14). This is only a claim. It gives no description of the alarm replacement, no contractor or certificate, and no evidence that the ceiling opening was closed. The tenant removed the alarm (event-1) and has not been heard from since 20 Aug. We told her we would check back on completion (event-9), so that promise is still open. I cannot close on the landlord's word alone. The tenant is the party who can confirm that a working alarm is fitted and the sockets are fixed, so I asked her (message-1). The property and landlord match the job, and no provider or invoice is involved, so there is no money or mismatch issue. I did not escalate because nothing shows danger or a dispute. A missing smoke alarm is a compliance concern, but the landlord reports it fixed, and the tenant never reported an immediate risk. The recorded alarm detail is still unverified. If the tenant says the alarm is still missing, or the sockets are still loose, or there is damp, I would escalate. The kitchen socket issue after boiler work in February and the dehumidifier/bathroom damp are possible separate issues to follow up.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-09T18:42:00+00:00, waiting on tenant: Tenant confirmation of landlord's completion claim (alarm, ceiling, sockets, dehumidifier) `followup-2`. Held: not part of the final action ASK_TENANT; a person can release it.

### Message to tenant `message-1`

Dear Nessa, the landlord has told us he completed the work at 8 Brindlefern Walk on 31 August. Before we update our record, please could you confirm the following: (1) Is a working smoke alarm now fitted on the upstairs landing, and is the opening in the ceiling closed? (2) Have the loose plug sockets been fixed, including the kitchen and back bedroom, or are any still coming away from the wall? (3) Did you receive a portable dehumidifier for the bathroom, and is there any damp or mould there? If any alarm is missing or a socket is still loose, please tell us and we will follow it up. Kind regards, Ivo Merrick, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Loose plug sockets (kitchen and back bedroom) reported alongside the alarm
- Possible bathroom damp, with a dehumidifier supplied by the landlord on 6 August
