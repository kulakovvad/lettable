# Case 16

**Decision:** Escalate to a person
**Priority:** P1

## Details

### Case

- **Id:** 16
- **Raised by:** Tenant
- **Request:** The smoke alarm has come away from the ceiling and needs attention.

### Property

- **Address:** 26 Tallowmere Close, Fenbarrow, ZZ1 1ZZ

### Agency

- **Name:** Maya Chen (Property Manager, Northbridge Lettings)

### Timeline

- **Events:** 17, first 2025-08-07T09:58:12+00:00, last 2025-09-22T08:48:00+00:00
- **Channels:** Portal 1, Email 9, Call 4, Note 2, Update 1

### Decision

- **Action:** Escalate to a person
- **Priority:** P1
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-22T08:48:00+00:00
- **Evidence cited:** event-001, event-004, event-007, event-010, event-012, event-013, event-014, event-015, event-016

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "16",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The smoke alarm has come away from the ceiling and needs attention."
  },
  "property": {
    "address": "26 Tallowmere Close, Fenbarrow, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "26 Tallowmere Close, Fenbarrow, ZZ1 1ZZ",
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
    "first": "2025-08-07T09:58:12+00:00",
    "last": "2025-09-22T08:48:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 9,
      "Call": 4,
      "Note": 2,
      "Update": 1
    }
  },
  "attachments": [],
  "decision": {
    "action": "ESCALATE",
    "priority": "P1",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-22T08:48:00+00:00",
    "evidence_refs": [
      "event-001",
      "event-004",
      "event-007",
      "event-010",
      "event-012",
      "event-013",
      "event-014",
      "event-015",
      "event-016"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The smoke alarm has come away from the ceiling and needs attention.
17 events reviewed, decision as of 2025-09-22T08:48:00+00:00.

## Decision

The smoke alarm has been unmounted for about 6 weeks (event-001, event-010). The landlord said he would use his own electrician but never named one, and no work is confirmed (event-004, event-007). The tenant was hospitalised and is vulnerable, and asked us to stop contacting them (event-012, event-013, event-014). On 20 Sep an unverified visitor came to the door and the tenant feared a scam (event-015, event-016). The visitor's link to the alarm job is unknown. Several policy reasons to escalate apply: a vulnerable occupant, a possible complaint about our contact, a possible security issue, and no clear contractor we can use. A plain chase or WAIT would not address those, and contacting the tenant would breach their request. I have also staged a request to the landlord for the contractor's identity and whether he sent the 20 Sep visitor. A chase was blocked because the landlord replied at event-007. No danger has been reported by code, so this is P1 rather than P0: there is no working-alarm status and the occupant is vulnerable. No money or approval is involved. The tenant's current alarm cover is unknown. If the landlord identifies the fitter and a visit is booked with the tenant's agreement, this could return to routine handling.

## Actions taken

- **COMMITTED**: Escalation ticket P1 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Message to landlord (request_info, P1) `message-2`. Held: not part of the final action ESCALATE; a person can release it.

### Message to landlord `message-2`

Dear Ronan, following up on the smoke alarm at 26 Tallowmere Close (NBL-016). We last heard on 12 August that your electrician would finish by the following weekend. The tenant says a fitter attended but could not refit the alarm because the box had no bracket, so it is still not mounted. Could you please tell us the name and company of the electrician or fitter, when they will return to fit the alarm, and whether you or they sent anyone to the property on Saturday 20 September? Kind regards, Maya Chen, Northbridge Lettings

## Handover for the person taking over

Smoke alarm at 26 Tallowmere Close has been unmounted since 7 Aug (about 6 weeks). The tenant, Elise Rowan, is a recently hospitalised, vulnerable occupant who asked us on 11 Aug to leave them alone. On 20 Sep an unannounced, unverified visitor knocked, and the tenant feared a scam. The landlord has given no contractor details since 12 Aug. A person needs to decide how to handle contact and the safety and security concerns.

Respond by 2025-09-22T12:48:00+00:00 (P1, route property_manager).

Known:
- Tenant reported the alarm off the ceiling on 7 Aug (event-001); no photos supplied.
- Landlord said he would use his own electrician (event-004). He said on 12 Aug the work would be done by the following weekend (event-007). He gave no name, scope or appointment.
- A fitter attended around 31 Aug-2 Sep, removed the bracket and could not refit the alarm because the box had no bracket. The alarm remains unmounted (event-010).
- Tenant was admitted to hospital on 5 Sep and discharged by 11 Sep. They said the alarm was still unfinished and that they would arrange it and report back (events 11-13).
- Tenant asked us to leave them alone because repeated calls and emails were upsetting. A pause was recorded (event-013, event-014).
- On 20 Sep an unannounced person said they were there to check something. The tenant did not admit them. Identity, organisation and authority are unverified, and it is unknown whether they relate to the alarm job (event-015, event-016).
- The tenant had earlier raised the knock with another agency contact, who passed it to a building-management contact (event-016).
- No completion evidence is on file. There is no assigned provider, no quote and no approval amount.
- Property: 26 Tallowmere Close, Fenbarrow, ZZ1 1ZZ (index)
- Request: The smoke alarm has come away from the ceiling and needs attention. (request)

Not known:
- Who the fitter and the electrician are, and whether the Saturday visitor was sent by the landlord or the fitter
- Whether the alarm has been mounted or tested; the tenant may have another working alarm
- The tenant's current health and whether any vulnerable-occupant arrangements are needed
- Whether the 'building-management contact' referral was actioned
- Whether the earlier contact was a complaint about our contact
- Fitter and electrician identity
- Whether the 20 Sep visitor was connected to the job
- Whether the alarm is now fitted

Tried:
- Acknowledged the request and asked the landlord, who chose his own contractor (events 2-7)
- Chased the tenant by email and calls (events 8-11)
- Paused tenant contact on request (event-014)
- I have not messaged the tenant, in line with their request. I am staging a short request to the landlord for contractor details.
- Agent proposed ESCALATE

Options:
- Recommended: Ask the landlord for the fitter's name and company and whether he sent anyone on 20 Sep. Share the answer with the tenant only through a single gentle message or a channel they accept.
- Have the manager decide whether a one-off welfare and safety contact with the tenant is justified. It would cover temporary alarm cover and advice not to admit unverified visitors. Consider offering an agency-arranged, landlord-approved provider.
- Log the unverified visitor as a possible security incident and pass it to the building-management contact. Review whether tenant contact breached their request and whether it needs the complaints route.

Recommended: Recommended: Ask the landlord for the fitter's name and company and whether he sent anyone on 20 Sep. Share the answer with the tenant only through a single gentle message or a channel they accept.

## What was blocked or failed

- Tool gate refused `send_message`: the landlord replied at event-007 after our last message event-005

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Unannounced visitor on 20 Sep and the referral to a building-management contact
- Tenant's complaint about repeated contact while ill
