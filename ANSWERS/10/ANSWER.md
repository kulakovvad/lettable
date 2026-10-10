# Case 10

**Decision:** Ask the provider for more information
**Priority:** P2

## Details

### Case

- **Id:** 10
- **Raised by:** Tenant
- **Request:** Tenant reports peeling laminate on kitchen cabinets, with sharp edges that have caused cuts, and several cabinet doors that do not close properly. Two dogs are at the property, so access needs to be arranged in advance.

### Property

- **Address:** 42 Brackenveil Row, Oakhollow, ZZ1 1ZZ

### Agency

- **Name:** Nia Calder (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 4850.00 (VAT excl, provider) [event-024]; GBP 3800.00 (VAT excl, provider) [event-024]; GBP 230.00 (VAT excl, provider) [event-024]; GBP 380.00 (VAT excl, provider) [event-024]

### Timeline

- **Events:** 26, first 2025-09-04T12:08:49+00:00, last 2025-09-24T14:36:22+00:00
- **Channels:** Portal 1, Email 16, Update 2, Call 4, Note 3

### Decision

- **Action:** Ask the provider for more information
- **Priority:** P2
- **Confidence:** 0.70
- **Decided by:** model
- **As of:** 2025-09-24T14:36:22+00:00
- **Evidence cited:** event-006, event-016, event-024, event-025, event-022, event-023, event-021

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "10",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "Tenant reports peeling laminate on kitchen cabinets, with sharp edges that have caused cuts, and several cabinet doors that do not close properly. Two dogs are at the property, so access needs to be arranged in advance."
  },
  "property": {
    "address": "42 Brackenveil Row, Oakhollow, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "42 Brackenveil Row, Oakhollow, ZZ1 1ZZ",
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
    "name": "Nia Calder (Property Manager, Northbridge Lettings)",
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
    "quotes": [
      {
        "amount_gbp": 4850.0,
        "vat": "excl",
        "from": "provider",
        "ref": "event-024"
      },
      {
        "amount_gbp": 3800.0,
        "vat": "excl",
        "from": "provider",
        "ref": "event-024"
      },
      {
        "amount_gbp": 230.0,
        "vat": "excl",
        "from": "provider",
        "ref": "event-024"
      },
      {
        "amount_gbp": 380.0,
        "vat": "excl",
        "from": "provider",
        "ref": "event-024"
      }
    ],
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
    "events": 26,
    "first": "2025-09-04T12:08:49+00:00",
    "last": "2025-09-24T14:36:22+00:00",
    "waiting_on": null,
    "channels": {
      "Portal": 1,
      "Email": 16,
      "Update": 2,
      "Call": 4,
      "Note": 3
    }
  },
  "attachments": [],
  "decision": {
    "action": "ASK_PROVIDER",
    "priority": "P2",
    "confidence": 0.7,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-24T14:36:22+00:00",
    "evidence_refs": [
      "event-006",
      "event-016",
      "event-024",
      "event-025",
      "event-022",
      "event-023",
      "event-021"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: Tenant reports peeling laminate on kitchen cabinets, with sharp edges that have caused cuts, and several cabinet doors that do not close properly. Two dogs are at the property, so access needs to be arranged in advance.
26 events reviewed, decision as of 2025-09-24T14:36:22+00:00.

## Decision

The only landlord approval on record is for the original laminate-repair scope (event-6). The landlord later asked for two estimates, a full kitchen and cupboards and doors only (event-16), and that did not approve replacement. The contractor's full-kitchen figures (event-24) total £4,850 + £3,800 + £230 plus VAT, with a £380 electrical estimate. All are far above the £300 threshold and no approval covers them. Nia has already forwarded these to the landlord (event-25), so a second route_for_approval would be a duplicate, and the landlord's reply is not overdue because we only wrote minutes ago. The cupboards-and-doors-only estimate is missing from event-24, and only the contractor holds it, so I asked Kellan for it (message-1). I also asked what the electrical item covers, and told him not to order or start work. I offered to arrange a site visit if he needs one. The tenant's offered dates (event-10) have passed (event-21). No hazard keywords were flagged. The cuts from sharp edges (event-1) are a minor injury risk with no imminent danger, so P2 applies and escalation is not needed. Unresolved: the commission basis, any cap and the VAT total from the call in event-22/23 are unsettled. The commission instruction in event-23 was given without any documented basis, so a person should review it if it affects the quoted price. A follow-up is set for 72 hours. A decision on the quote should wait for the landlord's reply and the second estimate.

## Actions taken

- **COMMITTED**: Message to provider (request_info, P2) `message-1`. Recorded in the local outbox (no external delivery connected).
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-27T14:36:22+00:00, waiting on provider: Cupboards-and-doors-only estimate outstanding; landlord decision on full-kitchen quote (event-25) also awaited. `followup-2`. Held: not part of the final action ASK_PROVIDER; a person can release it.

### Message to provider `message-1`

Hello Kellan, thank you for the full-kitchen figures (your email of 24 September). The landlord has asked for two estimates, and we have only received the first. Could you please send the estimate for replacing the cupboards and doors only, keeping the existing appliances, worktops and flooring? An itemised breakdown like the one you sent would be ideal, stating clearly whether each figure is plus VAT. Please also confirm what the electrical item of £380 plus VAT covers and what needs checking. Please note that nothing in the full-kitchen quote has been approved by the landlord yet, so please do not order materials or start any work. The tenant's earlier visit dates have passed, so please also tell us if you need a site visit to firm up the figures and we will arrange new access with the tenant, who has two dogs to secure. Kind regards, Nia Calder, Northbridge Lettings

## Inconsistencies and mismatches

None found.

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.

## Separate issues to raise as new requests

- Contractor's query about the 15% commission basis, cap and VAT treatment (event-22) needs a person to confirm the commercial terms
