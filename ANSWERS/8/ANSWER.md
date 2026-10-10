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
- **Confidence:** 0.90
- **Decided by:** model
- **As of:** 2025-06-18T12:55:00+00:00
- **Evidence cited:** event-002, event-012, event-016, event-017, event-018, event-019, event-020, event-022, event-023, event-024

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
    "confidence": 0.9,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-06-18T12:55:00+00:00",
    "evidence_refs": [
      "event-002",
      "event-012",
      "event-016",
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

Active water is coming through a ceiling light fitting in Flat 2, with a bulge that is getting larger (event-002, event-012, event-017, event-023). Electrical isolation is unverified. A wall switch being off proves nothing, and the electrician considers the fitting unsafe (event-018). Water near electrics is P0 under the safety policy, and a reported danger is treated as real until verified. The code did not flag urgent_by_code, but the case itself reports the danger. Plumber and building manager visits found no source and no isolation point (event-016, event-021). Flat 3 is the suspected but unconfirmed source. Yara refuses entry (event-009, event-020), Niko has not authorised it (event-011, event-019), and the duty manager found no documented agency authority to override her refusal (event-022). That is a conflict over access, and a decision on emergency action and possible emergency services needs a person. Waiting or asking would not resolve it, because nobody we can reach can authorise entry without the full tenancy agreement and a director decision. We cannot instruct further work because there is no landlord approval or quote. The tenant name mismatch flagged by the check is just two different flats' tenants. The case contains no instructions trying to change our process. The electrician's arrival and findings in the 12:30-13:15 window are unknown and could change the picture. I have staged a P0 handover to on_call_emergency with options. Event-024 is our own internal summary and adds no new facts.

## Actions taken

- **COMMITTED**: Escalation ticket P0 to on_call_emergency `escalation-1`. Recorded in the local outbox (no external delivery connected).

## Handover for the person taking over

Active water ingress through the ceiling light fitting in Flat 2 (water near electrics), with an enlarging ceiling bulge. Electrical safety is unverified. Source is unidentified and the suspected source flat (Flat 3) is inaccessible: the tenant refuses entry, the landlord has not authorised it, and no agency entry authority is documented. A decision on emergency action is needed now.

Respond by 2025-06-18T13:55:00+00:00 (P0, route on_call_emergency).

Conflicts:
- tenant_name: Yara Mallow (event-001, event-020) vs Bevin Orlo (event-002, event-003, event-015, event-017, event-012, event-023)

Known:
- Flat 2 (Bevin Orlo): water dripping from the bedroom ceiling light fitting, dripping faster with a new brown patch (event-002, event-012). A bulge appeared (event-017) and appears larger at 12:38 (event-023). No sparks, smoke or fallen material reported. Bevin is outside the bedroom and has been told not to touch the fitting or the consumer unit (event-003, event-004).
- The wall switch being off does not prove the fitting is isolated. Runa Elt (Vellum Electrical) considers the fitting not safe on that basis. Attendance window 12:30-13:15 subject to access (event-014, event-018). Nothing in the case confirms she has arrived; the window is open at 12:55.
- Daro Fen (Brindle Flow Plumbing) and Selka Venn (building manager) attended Flat 2 and the common riser. No source or confirmed isolation point was found, no valve was operated, and Flat 3 was inaccessible (event-016, event-021).
- Yara Mallow (Flat 3 tenant) does not consent to entry before she returns (about 17:30) and asked that no key be used (event-009, event-020). She has asked for the plumber's name and proposed work in writing, and Daro's name has been given (event-020).
- Niko Pell (landlord, Flat 3) is away, has no key, has not authorised entry, and does not authorise forced or unaccompanied entry. He asked to be updated before any non-routine access (event-006, event-011, event-019).
- Duty Manager Devra Senn found no documented delegated authority to override the refusal. The full tenancy wording has not been checked. The route is the full agreement plus a decision from the agency director, and emergency services if there is immediate danger to life or property (event-022).
- The tenant name mismatch flagged by the document check is not a data error. Yara Mallow is the Flat 3 tenant and Bevin Orlo is the Flat 2 tenant.
- Property: Flat 3, 8 Tallowmere Row, Ossin Vale, ZZ1 1ZZ (index)
- Request: Water is entering the flat below from an unidentified source. Please help coordinate an inspection and next steps. (request)

Not known:
- Whether the Flat 2 light circuit is isolated or live.
- Whether Vellum Electrical has arrived and what they found.
- The source of the water, and whether Flat 3 is it.
- Whether the full tenancy agreement permits emergency entry after the tenant refused.
- Whether the ceiling is at risk of collapse.
- Whether Yara can be reached by phone around noon, as she offered in event-009, to reconsider consent.
- Whether the circuit is isolated
- Whether the electrician has arrived and what was found

Tried:
- Safety instructions given to Bevin by phone (event-003, event-015, event-017).
- Building manager asked about an isolation point; none confirmed (event-005, event-010, event-021).
- Plumber attended Flat 2 and the riser; no source found (event-016).
- Electrician booked for 12:30-13:15 (event-014, event-018).
- Landlord contacted three times; he has not authorised entry (event-006, event-011, event-019).
- Tenant of Flat 3 asked for consent twice and declined (event-009, event-020).
- Duty Manager asked about emergency access authority; none documented (event-022).
- Agent proposed ESCALATE

Options:
- Recommended: Decide now whether to call emergency services or the fire service for the water and electrical risk, given the enlarging bulge and unverified circuit. Tell Bevin to leave the room and to call 999 if there are sparks, smoke or sagging or falling material. Ask the electrician to isolate the circuit on arrival.
- Obtain the full tenancy agreement and an urgent agency director decision on emergency entry to Flat 3. Update Niko before any non-routine access, as he asked. Do not enter without a documented authority.
- Phone Yara again (she offered a call at about noon) with Daro's name and the written scope of work, to ask her to consent to a supervised, accompanied attendance or to reconsider before 17:30. Keep Niko updated.

Recommended: Recommended: Decide now whether to call emergency services or the fire service for the water and electrical risk, given the enlarging bulge and unverified circuit. Tell Bevin to leave the room and to call 999 if there are sparks, smoke or sagging or falling material. Ask the electrician to isolate the circuit on arrival.

## Inconsistencies and mismatches

- **document consistency** (flag): tenant name differs between documents: 'Yara Mallow' vs 'Bevin Orlo' (similarity 0.017). [event-001, event-002, event-003, event-012, event-015, event-017, event-020, event-023]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
