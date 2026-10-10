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
- **Confidence:** 0.75
- **Decided by:** model
- **As of:** 2025-09-06T18:42:00+00:00
- **Evidence cited:** event-001, event-005, event-007, event-012, event-014

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
    "confidence": 0.75,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-06T18:42:00+00:00",
    "evidence_refs": [
      "event-001",
      "event-005",
      "event-007",
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

The landlord said he would do the work himself (event-007, event-010). On 6 Sept he claimed completion on 31 August (event-012) and added details on the sockets and a dehumidifier (event-014). This is a claim, not proof. There is no invoice, photo or contractor detail, and no assigned provider. The claim is also thin: it says nothing about a replacement smoke alarm or closing the ceiling opening. Only one back-bedroom socket and one kitchen socket are mentioned, though the tenant reported several sockets (event-005). The dehumidifier suggests a possible damp issue in the bathroom that was never reported to us, so I need severity and health impact (damp_mould policy). The tenant has not been heard from since event-001. A working smoke alarm is a legal requirement, so I am not closing, and I am not escalating because nothing reports active danger and the tenant can supply the facts. I asked the tenant to confirm the alarm, ceiling, sockets and bathroom, and asked the landlord for detail and evidence. Follow-up in 72 hours. If the tenant says the alarm is missing, sockets are still loose or there is mould with health impact, escalate. The agency has not approved or instructed anything. The record update the landlord asked for should wait for confirmation.

## Actions taken

- **COMMITTED**: Message to tenant (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Message to landlord (request_info, P2) `message-2`. Held: not part of the final action ASK_TENANT; a person can release it.
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-09T18:42:00+00:00, waiting on tenant: Awaiting tenant confirmation of smoke alarm, sockets, bathroom damp; and landlord detail on the work done `followup-3`. Held: not part of the final action ASK_TENANT; a person can release it.

### Message to tenant `message-1`

Dear Nessa, the landlord has told us the work at 8 Brindlefern Walk was completed on 31 August. Before we update our record, could you please confirm: (1) Is a smoke alarm now fitted and working on the upstairs landing, and is the ceiling opening closed? (2) Have the loose plug sockets been fixed? If any are still coming away from the wall, please tell us which rooms. (3) The landlord says he gave you a dehumidifier for the bathroom. Is there damp or mould in the bathroom, and if so, how bad is it? Photos would help. Kind regards, Ivo Merrick, Northbridge Lettings

### Message to landlord `message-2`

Dear Tavian, thank you for the update. So we can record this correctly, could you confirm what was done on 31 August on the upstairs landing? Was a new smoke alarm fitted, and was the ceiling opening made good? Please also confirm whether all the loose sockets the tenant reported were dealt with. Your email mentions only one back-bedroom socket and one kitchen socket. If you have an invoice, photos or an electrician's confirmation, please send them. We have also asked the tenant to confirm. Kind regards, Ivo Merrick, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Plug sockets coming away from walls (electrical safety)
- Possible bathroom damp/dehumidifier issue
