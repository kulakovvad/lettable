# Case 1

**Decision:** Escalate to a person
**Priority:** P2

## Details

### Case

- **Id:** 1
- **Raised by:** Tenant
- **Request:** The tenant reports a continuing leak behind the shower and moisture coming through the bathroom wall covering. A previous tightening of the pipe did not hold, and the visible wall deterioration has worsened.

### Property

- **Address:** 4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ
- **References:** reference NBL-001-Q1 [bathroom-works-quotation.pdf]

### Tenant

- **Phones:** 07700 900184 [event-012]

### Agency

- **Name:** Mira Sallow (Property Manager, Northbridge Lettings)

### Money

- **Quotes:** GBP 2370.00 (VAT unknown, provider) [event-016]; GBP 474.00 (VAT unknown, provider) [event-016]; GBP 2844.00 (VAT unknown, provider) [event-016]; GBP 1270.00 (VAT unknown, provider) [event-021]; GBP 1170.00 (VAT unknown, provider) [event-021]; GBP 2370.00 (VAT unknown, attachment) [bathroom-works-quotation.pdf]; GBP 474.00 (VAT unknown, attachment) [bathroom-works-quotation.pdf]; GBP 2844.00 (VAT unknown, attachment) [bathroom-works-quotation.pdf]
- **Landlord approval:** GBP 1270.00 [event-023]
- **Deposit:** He said a 50% deposit would be required if the landlord wished to proceed. [event-021]; The message did not state a revised subtotal or total, clarify how the commission is applied, or specify the deposit calculation basis. [event-021]

### Timeline

- **Events:** 23, first 2025-09-04T08:10:00+00:00, last 2025-09-23T16:12:00+00:00
- **Channels:** Email 17, Call 3, SMS 1, Note 1, Document 1

### Attachments

- bathroom-works-quotation.pdf (pdf, content read)

### Decision

- **Action:** Escalate to a person
- **Priority:** P2
- **Confidence:** 0.80
- **Decided by:** model
- **As of:** 2025-09-23T16:12:00+00:00
- **Evidence cited:** event-005, event-016, event-021, event-023, bathroom-works-quotation.pdf

### Case card (machine-readable)

```json
{
  "schema": "case-card/1",
  "case": {
    "id": "1",
    "title": null,
    "source_role": "Tenant",
    "status": null,
    "request": "The tenant reports a continuing leak behind the shower and moisture coming through the bathroom wall covering. A previous tightening of the pipe did not hold, and the visible wall deterioration has worsened."
  },
  "property": {
    "address": "4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ",
    "address_variants": [
      {
        "value": "4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ",
        "refs": [
          "index"
        ]
      }
    ],
    "references": [
      {
        "kind": "reference",
        "value": "NBL-001-Q1",
        "refs": [
          "bathroom-works-quotation.pdf"
        ]
      }
    ]
  },
  "tenant": {
    "name": null,
    "names": [],
    "phones": [
      {
        "value": "07700 900184",
        "refs": [
          "event-012"
        ]
      }
    ],
    "emails": []
  },
  "landlord": {
    "name": null,
    "names": [],
    "phones": [],
    "emails": []
  },
  "agency": {
    "name": "Mira Sallow (Property Manager, Northbridge Lettings)",
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
        "amount_gbp": 2370.0,
        "vat": "unknown",
        "from": "provider",
        "ref": "event-016"
      },
      {
        "amount_gbp": 474.0,
        "vat": "unknown",
        "from": "provider",
        "ref": "event-016"
      },
      {
        "amount_gbp": 2844.0,
        "vat": "unknown",
        "from": "provider",
        "ref": "event-016"
      },
      {
        "amount_gbp": 1270.0,
        "vat": "unknown",
        "from": "provider",
        "ref": "event-021"
      },
      {
        "amount_gbp": 1170.0,
        "vat": "unknown",
        "from": "provider",
        "ref": "event-021"
      },
      {
        "amount_gbp": 2370.0,
        "vat": "unknown",
        "from": "attachment",
        "ref": "bathroom-works-quotation.pdf"
      },
      {
        "amount_gbp": 474.0,
        "vat": "unknown",
        "from": "attachment",
        "ref": "bathroom-works-quotation.pdf"
      },
      {
        "amount_gbp": 2844.0,
        "vat": "unknown",
        "from": "attachment",
        "ref": "bathroom-works-quotation.pdf"
      }
    ],
    "invoices": [],
    "approval": {
      "amount_gbp": 1270.0,
      "ref": "event-023",
      "covers": "amount"
    },
    "payments": [],
    "deposit": [
      {
        "text": "He said a 50% deposit would be required if the landlord wished to proceed.",
        "amount_gbp": null,
        "ref": "event-021"
      },
      {
        "text": "The message did not state a revised subtotal or total, clarify how the commission is applied, or specify the deposit calculation basis.",
        "amount_gbp": null,
        "ref": "event-021"
      }
    ]
  },
  "appointments": [],
  "timeline": {
    "events": 23,
    "first": "2025-09-04T08:10:00+00:00",
    "last": "2025-09-23T16:12:00+00:00",
    "waiting_on": null,
    "channels": {
      "Email": 17,
      "Call": 3,
      "SMS": 1,
      "Note": 1,
      "Document": 1
    }
  },
  "attachments": [
    {
      "name": "bathroom-works-quotation.pdf",
      "available": true,
      "kind": "pdf"
    }
  ],
  "decision": {
    "action": "ESCALATE",
    "priority": "P2",
    "confidence": 0.8,
    "decided_by": "model",
    "cause": null,
    "as_of": "2025-09-23T16:12:00+00:00",
    "evidence_refs": [
      "event-005",
      "event-016",
      "event-021",
      "event-023",
      "bathroom-works-quotation.pdf"
    ]
  },
  "calls": [],
  "warnings": []
}
```

## What the system received

Initial request: The tenant reports a continuing leak behind the shower and moisture coming through the bathroom wall covering. A previous tightening of the pipe did not hold, and the visible wall deterioration has worsened.
23 events reviewed, decision as of 2025-09-23T16:12:00+00:00.

## Decision

The landlord's latest message (event-23) asks which quote we mean. Event-5 approved only an inspection and a quote, and nothing has been approved since. The code's "approval in force" of £1,270 (event-23) is wrong: event-23 is a question, not an approval. The quote PDF (bathroom-works-quotation.pdf, event-16) names 8 Wrenfold Mews, Brindlewick, not our job address at 4 Thistlewick Rise, Larkcombe. That is a property mismatch under verify_claims, so we cannot route it for approval or instruct on it. The price is also unclear. The PDF total is £2,844.00 (£2,370 plus £474 VAT), while Ewan's email (event-21) gives materials £1,270 and labour £1,170, mentions commission and a 50% deposit, and states no revised total. The quote is above the £300 limit and the agency cannot approve spend. I asked Ewan to confirm the address and send one itemised quote. I also staged a short note to Orin saying which quote exists, why it is on hold, and that nothing is approved. Escalation is not needed because Ewan can answer this directly. There is no reported danger or hazard keyword, although the leak is ongoing, so I set P2. A follow-up is set for 48 hours. If Ewan says the address is correct and sends a consistent itemised quote, route it to the landlord for approval. [gate: documents disagree on property_address ('4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ' vs '8 Wrenfold Mews, Brindlewick, ZZ1 1ZZ'); a person must confirm which is right]

## Actions taken

- **HELD_FOR_REVIEW**: Message to landlord (update, P2) `message-1`. Held: code gates changed the decision to ESCALATE.
- **HELD_FOR_REVIEW**: Follow-up at 2025-09-25T16:12:00+00:00, waiting on provider: Awaiting Hearthline confirmation of quote address and a single itemised quote `followup-2`. Held: code gates changed the decision to ESCALATE.
- **HELD_FOR_REVIEW**: Message to provider (request_info, P2) `message-3`. Held: code gates changed the decision to ESCALATE.
- **COMMITTED**: Escalation ticket P2 to property_manager `escalation-4`. Created automatically because the final decision is an escalation.

### Message to landlord `message-1`

Hi Orin, sorry for the confusion. The only quote we hold is Hearthline's dated 18 September, totalling £2,844.00 including VAT. The PDF carries a different property address from yours, and the contractor's later breakdown doesn't add up to that total. We have asked Hearthline to confirm the address and send one corrected, itemised quote. We will send it to you for a decision once we have it. Nothing has been approved or started.

Mira Sallow, Northbridge Lettings

### Message to provider `message-3`

Hi Ewan, two points on your quotation NBL-001-Q1 dated 18 September 2025 before we can take it to the landlord.

1. The PDF shows the property as 8 Wrenfold Mews, Brindlewick, ZZ1 1ZZ. Our job is for 4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ (the shower leak you inspected). Please confirm which property the quote is for. If it is for Thistlewick Rise, please reissue it with the correct address.

2. The quote shows a subtotal of £2,370.00, VAT of £474.00 and a total of £2,844.00. Your breakdown by email gave materials £1,270 and labour £1,170, and did not state a revised total. Please send one itemised quote showing materials, labour, VAT and the total, and explain how the 10% commission and the 50% deposit are calculated. Please also confirm which figure is the current price.

We are not treating any quote as approved yet and nothing should be started. Thank you.

Mira Sallow, Northbridge Lettings

## Handover for the person taking over

The landlord's latest message (event-23) asks which quote we mean. Event-5 approved only an inspection and a quote, and nothing has been approved since. The code's "approval in force" of £1,270 (event-23) is wrong: event-23 is a question, not an approval. The quote PDF (bathroom-works-quotation.pdf, event-16) names 8 Wrenfold Mews, Brindlewick, not our job address at 4 Thistlewick Rise, Larkcombe. That is a property mismatch under verify_claims, so we cannot route it for approval or instruct on it. The price is also unclear. The PDF total is £2,844.00 (£2,370 plus £474 VAT), while Ewan's email (event-21) gives materials £1,270 and labour £1,170, mentions commission and a 50% deposit, and states no revised total. The quote is above the £300 limit and the agency cannot approve spend. I asked Ewan to confirm the address and send one itemised quote. I also staged a short note to Orin saying which quote exists, why it is on hold, and that nothing is approved. Escalation is not needed because Ewan can answer this directly. There is no reported danger or hazard keyword, although the leak is ongoing, so I set P2. A follow-up is set for 48 hours. If Ewan says the address is correct and sends a consistent itemised quote, route it to the landlord for approval. [gate: documents disagree on property_address ('4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ' vs '8 Wrenfold Mews, Brindlewick, ZZ1 1ZZ'); a person must confirm which is right]

Respond by 2025-09-24T16:12:00+00:00 (P2, route property_manager).

Conflicts:
- property_address: 4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ (index) vs 8 Wrenfold Mews, Brindlewick, ZZ1 1ZZ (bathroom-works-quotation.pdf)

Known:
- 23 events reviewed
- Property: 4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ (index)
- Request: The tenant reports a continuing leak behind the shower and moisture coming through the bathroom wall covering. A previous tightening of the pipe did not hold, and the visible wall deterioration has worsened. (request)

Not known:
- Whether the quote is really for 4 Thistlewick Rise
- Actual total and basis of commission and deposit
- Whether the landlord will approve
- Which conflicting value is right (see conflicts)

Tried:
- Agent proposed ASK_PROVIDER
- documents disagree on property_address ('4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ' vs '8 Wrenfold Mews, Brindlewick, ZZ1 1ZZ'); a person must confirm which is right

Options:
- Recommended: Review the timeline and decide the next step
- Contact the party we are waiting on directly

Recommended: Recommended: Review the timeline and decide the next step

## What was blocked or failed

- Tool gate refused `send_message`: amount GBP 2440.00 does not appear in the case
- Final code check: documents disagree on property_address ('4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ' vs '8 Wrenfold Mews, Brindlewick, ZZ1 1ZZ'); a person must confirm which is right

## Inconsistencies and mismatches

- **document consistency** (flag): property address differs between documents: '4 Thistlewick Rise, Larkcombe, ZZ1 1ZZ' vs '8 Wrenfold Mews, Brindlewick, ZZ1 1ZZ' (similarity 0.007). [bathroom-works-quotation.pdf, index]
- **amount** (info): The provider gave different quotes: GBP 2844.00 (event-016); GBP 1270.00 (event-021). [event-016, event-021]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check on.
