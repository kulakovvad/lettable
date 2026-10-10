# Case 8

**Decision:** Escalate to a person
**Priority:** P0

## Details

### Case

- **Id:** 8
- **Raised by:** Tenant
- **Request:** Water is entering the flat below from an unidentified source. Please help coordinate an inspection and next steps.

### Property

- **Address:** Flat 3, 8 Tallowmere Row, Ossin Vale, ZZ1 1ZZ

### Agency

- **Name:** Arlen Quist (Property Manager, Northbridge Lettings)

### Timeline

- **Events:** 24, first 2025-06-18T08:12:00+00:00, last 2025-06-18T12:55:00+00:00
- **Channels:** Portal 2, Call 16, SMS 3, Email 2, Update 1

### Decision

- **Action:** Escalate to a person
- **Priority:** P0
- **Confidence:** 0.93
- **Decided by:** model
- **As of:** 2025-06-18T12:55:00+00:00
- **Evidence cited:** event-002, event-012, event-017, event-018, event-019, event-020, event-022, event-023, event-024

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "8",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "Water is entering the flat below from an unidentified source. Please help coordinate an inspection and next steps."
  },
  "property": {
    "address": "Flat 3, 8 Tallowmere Row, Ossin Vale, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "Flat 3, 8 Tallowmere Row, Ossin Vale, ZZ1 1ZZ",
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
    "name": "Arlen Quist (Property Manager, Northbridge Lettings)",
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
    "events": 24,
    "first": "2025-06-18T08:12:00+00:00",
    "last": "2025-06-18T12:55:00+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 2,
      "Call": 16,
      "SMS": 3,
      "Email": 2,
      "Update": 1
    }
  },
  "attachments": [],
  "decision": {
    "action": "ESCALATE",
    "priority": "P0",
    "confidence": 0.93,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-06-18T12:55:00+00:00",
    "evidence_refs": [
      "event-002",
      "event-012",
      "event-017",
      "event-018",
      "event-019",
      "event-020",
      "event-022",
      "event-023",
      "event-024"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Water is entering the flat below from an unidentified source. Please help coordinate an inspection and next steps.
24 events reviewed, decision as of 2025-06-18T12:55:00+00:00.

## Decision

Water is actively dripping through a wet ceiling light fitting in Flat 2, and the ceiling bulge is reportedly growing (event-002, event-012, event-017, event-023). Electrical safety is unverified: the wall switch being off proves nothing, and the electrician said the fitting is not considered safe (event-018). This is water near electrics with a ceiling bulge, so it is P0 even though urgent_by_code is false. The source is probably Flat 3, but nobody has entered it. Yara refuses entry until after 17:30 (event-009, event-020). Niko has not authorised entry (event-006, event-011, event-019). The duty manager found no delegated authority to override the refusal and pointed to the director and emergency services (event-022). Plumbing attendance found no source or isolation point (event-016, event-021). A person must decide on emergency access and the response, so waiting, asking or chasing would not do. The agency cannot authorise entry, and Vellum Electrical's attendance (due 12:30-13:15) is not yet confirmed. The Flat 2 tenant has already been given safety advice (event-003, event-015). The tenant-name flag is two different tenants in two flats, not a conflict. This decision would change if the electrician confirms the circuit is isolated, if Yara consents, or if the director authorises access.

## Actions taken

- **COMMITTED**: Escalation ticket P0 to on_call_emergency `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Active water ingress through the ceiling light fitting in Flat 2 (Bevin Orlo), with the ceiling bulge reportedly enlarging. Electrical safety is not established. The source is probably Flat 3, but nobody has entered it, and the Flat 3 tenant (Yara Mallow) refuses entry until she is home after 17:30. The landlord has not authorised entry, and the agency has no verified emergency-entry authority. A human decision is needed now on access and on the emergency response.

Respond by 2025-06-18T13:55:00+00:00 (P0, route on_call_emergency).

Conflicts:
- tenant_name: Yara Mallow (event-001, event-020) vs Bevin Orlo (event-002, event-003, event-015, event-017, event-023)

Known:
- Flat 2 ceiling light fitting is dripping, and the drip is faster with a new brown patch (event-002, event-12). The bulge beside the fitting has grown (event-017, event-023).
- Bevin's wall switch is off, but the fitting's supply status is unknown. Runa Elt (Vellum Electrical) said the fitting is not considered safe on switch position alone (event-018).
- Vellum Electrical is due 12:30-13:15 subject to access, but no attendance or arrival is recorded as of 12:55 (event-014, event-018).
- Bevin has left the bedroom and is keeping others out. No sparks, smoke or fallen material has been seen (event-004, event-012, event-023). Bevin has not touched the consumer unit.
- Brindle Flow Plumbing (Daro Fen) and the building manager (Selka Venn) attended Flat 2 and the common riser. No source was found, no isolation point was confirmed, and no valve was operated (event-016, event-021). Daro needs Flat 3 access to trace the source (event-008).
- Yara (Flat 3) refuses entry and asks that no key be used. She cannot return before 17:30 and can take a call around noon. She wants the plumber's name and the proposed work in writing before reconsidering (event-009, event-020).
- Niko Pell (landlord) is away and has no key. He has not authorised entry, forced entry or unaccompanied entry (event-006, event-011, event-019). The tenancy clauses (access by arrangement, emergency repairs) are unchecked, and the full agreement has not been reviewed (event-019, event-022).
- The duty manager found no delegated authority to override the refusal. The escalation route is to obtain the full agreement and a decision from the agency director, and to call emergency services if there is immediate danger to life or property (event-022).
- Bevin asked that details be kept within the maintenance team (event-007). No cost or quote is in the case, so there is no spend approval issue yet.
- The document check flagged tenant names Yara Mallow and Bevin Orlo. These are two different tenants (Flat 3 and Flat 2), not a mismatch.
- Property: Flat 3, 8 Tallowmere Row, Ossin Vale, ZZ1 1ZZ (index)
- Request: Water is entering the flat below from an unidentified source. Please help coordinate an inspection and next steps. (request)

Not known:
- The source of the water, and whether it is Flat 3 at all.
- Whether the Flat 2 light circuit is live or isolated.
- Whether Vellum Electrical has arrived, and what it found.
- What the full tenancy agreement says about emergency access.
- Whether the water can be isolated at a valve, and which valve serves Flat 3.
- The condition of the ceiling void, and the collapse risk from the bulge.
- Source of the leak
- Whether the Flat 2 fitting circuit is isolated

Tried:
- Safety instructions were given to Bevin: stay out of the bedroom, do not touch the fitting or switches, do not operate the consumer unit, and call 999 for sparks, smoke, falling material or immediate danger (event-003, event-015, event-017).
- Selka was asked about a water isolation point. The riser labels are incomplete and nothing is confirmed (event-005, event-010).
- Plumber Daro attended and found no source. Electrician Runa was booked for 12:30-13:15 (event-014).
- Yara and Niko were each asked about access. Yara refused and Niko did not authorise entry (event-009, event-011, event-019, event-020).
- The duty manager was consulted. No authority was found, and the director route was advised (event-022).
- Agent proposed ESCALATE

Options:
- Recommended: Call the agency director now with the full tenancy wording for a decision on emergency access. Meanwhile, call Yara at her noon break window, or ask her again now, to consent to a supervised entry (Selka present, Daro attending). Give her the plumber's name and scope in writing as she asked, and update Niko before any non-routine access, as he asked (event-006).
- Confirm that Vellum Electrical has attended and tested or isolated the Flat 2 fitting and circuit. If access to isolate cannot be achieved, or if the bulge worsens or sparks, smoke or sagging appear, advise Bevin to leave the flat and call 999 or the fire service. Follow the responding authority's direction on entry.
- Ask Selka and Daro whether the building supply can be shut off safely at a common stopcock for the whole block as a stopgap. Do this only on a person's decision and with neighbours informed. Keep Bevin's details within the maintenance team.

Recommended: Recommended: Call the agency director now with the full tenancy wording for a decision on emergency access. Meanwhile, call Yara at her noon break window, or ask her again now, to consent to a supervised entry (Selka present, Daro attending). Give her the plumber's name and scope in writing as she asked, and update Niko before any non-routine access, as he asked (event-006).

## Inconsistencies and mismatches

- **document consistency** (flag): tenant name differs between documents: 'Yara Mallow' vs 'Bevin Orlo' (similarity 0.017). [event-001, event-002, event-003, event-015, event-017, event-020, event-023]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
