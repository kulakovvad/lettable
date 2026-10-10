# Reasoning for case 23

- Decided by: the model, checked by code
- Events seen: 23
- Model: claude-sonnet-5-5, 3 turn(s), 59389 tokens
- Evidence cited: event-005, event-008, event-009, event-012, event-016, event-017, event-018, event-019, event-020, event-022, event-023, invoice-NBL-CFM-250210-A.pdf, invoice-NBL-CFM-250210-B.pdf
- Model confidence: 0.80

## 1. Decision and next action

- **Final action:** Escalate to a person (ESCALATE)
- **Priority:** P2
- **As of:** 2025-02-12T16:35:00+00:00
- **Request received:** The radiators have stopped heating intermittently. Hot water is still available. Please arrange an inspection.

## 2. Why

Two Copper Finch invoices dated 10 Feb (event-017, event-018) overlap: A is £138 for diagnosis, B is £372 for actuator replacement plus diagnosis. Both give a service date of 5 Feb. Both name the right property, customer and provider, so there is no address or provider mismatch. The landlord authorised diagnosis only, up to £180 inc VAT (event-005), and explicitly declined to authorise remedial work or more spend (event-012). The £372 estimate came after the visit (event-009). The provider's visit report (event-008) mentions no remedial work, and on 7 Feb she still had to check parts (event-016). The file has no completion evidence (event-019), and the tenant does not know whether the actuator was replaced (event-020). The provider has been asked twice for clarification and gave only a holding reply (event-022). This is a duplicate or overlapping invoice case with a charge disputed in effect, which policy sends to a person. ROUTE_FOR_APPROVAL would be wrong, because it would imply the work is validly claimed. ASK_PROVIDER has already been tried twice (event-015, event-021). WAIT is not enough, because a person needs to decide how to handle the invoices and the unresolved heating fault. The landlord was asked at event-023 and is not yet overdue. Nothing is payable, and the case can't close. I did not read the claim in invoice B as proof of completion. Priority is P2 because there is no reported danger and no gas concern, but a child lives at the property, the heating is intermittent, and the tenant is using a portable heater. Neither invoice contains any instruction to change process. A person should decide the invoice handling and the next heating step if the landlord's answer changes things.

Facts the decision rests on:

- Landlord authorised diagnosis only, up to £180 inc VAT (event-005); the £138 diagnostic quote is within that (event-007).
- £372 estimate was sent at 14:54 on 5 Feb, after the visit, asking for written authorisation (event-009). Landlord did not authorise remedial work (event-012).
- Provider's 5 Feb visit report mentions no remedial work (event-008). On 7 Feb she still had to check parts and estimate details (event-016).
- Invoice B (£372) describes actuator replacement as done on 5 Feb. Its wording overlaps invoice A, and neither says whether it credits or supersedes the other (event-017, event-018, invoice PDFs).
- Provider replied on 12 Feb that she is still checking records and gave no completion evidence, revised invoice or parts confirmation (event-022).
- Tenant doesn't know if the actuator was replaced and has seen no contractor since 5 Feb. Heating is working intermittently with one radiator cooler (event-020).
- A child lives at the property (event-001). The tenant is using a portable heater plugged into a wall socket (event-011). No leak, smell or hazard has been reported.
- I asked the landlord on 12 Feb how to proceed (event-023). No reply yet, and it is not overdue. Invoice, address and customer details match the job and the assigned provider. No payment is recorded.
- Property: 7 Larkspur Fold, Orvane Heath, ZZ1 1ZZ (index)
- Request: The radiators have stopped heating intermittently. Hot water is still available. Please arrange an inspection. (request)

Evidence cited by the model: event-005, event-008, event-009, event-012, event-016, event-017, event-018, event-019, event-020, event-022, event-023, invoice-NBL-CFM-250210-A.pdf, invoice-NBL-CFM-250210-B.pdf

## 3. Missing information and conflicting facts

Not known:

- Whether the actuator was replaced
- Whether invoice B supersedes A
- Whether the diagnosis is credited
- The landlord's decision

### Inconsistencies and mismatches

- **amount** (info): The provider gave different quotes: GBP 138.00 (event-007); GBP 372.00 (event-009). [event-007, event-009]

Checked: addresses, invoice amounts against quotes and approval, completion against later reports, contact details; document consistency check unavailable.

## Document consistency check

Document consistency check unavailable (ValueError: the extraction model did not call report_facts). Compare names and addresses yourself.

Input warnings:

- none

## 4. Actions taken, results and failures

EXECUTED means the action was committed. PROPOSED, NOT SENT means it was staged and then held because the final decision changed or a person must approve it first.

- **EXECUTED**: Escalation ticket P2 to property_manager `escalation-1`. Recorded in the local outbox (no external delivery connected).

What was tried before this decision:

- Asked the provider on 7 Feb and 11 Feb for a breakdown, credit position, job notes and parts records (event-015, event-021). Only a holding reply (event-022).
- Asked the tenant for a status update (event-013, event-020).
- Asked the landlord on 12 Feb to decide on the invoices and any further work (event-023).
- Agent proposed ESCALATE

Checks applied by code:

- none

Failures and refused actions:

- none

## 5. Handover to a person

- **Route:** property_manager, priority P2, respond by 2025-02-13T16:35:00+00:00
- **Summary:** Copper Finch Mechanical sent two overlapping invoices for 7 Larkspur Fold: A £138 (diagnosis) and B £372 (actuator supply/replacement, diagnosis, testing). Both give a service date of 5 Feb. The file has no evidence the actuator was replaced, and the landlord authorised diagnosis only. The invoices should not be paid or closed until a person rules on them. The heating fault is also still unresolved.

Options for the person:

- Recommended: Hold both invoices as unpayable. Tell the provider that only invoice A (£138, within the £180 authorisation) can be considered, once confirmed. Invoice B is disputed until she shows authorisation and completion evidence.
- Wait for the landlord's reply to event-023, then ask the provider for one corrected itemised invoice with job notes and a parts record. Route any actuator work to the landlord for written approval.
- Arrange an attendance to check the actuator and the heating, with the landlord's approval, to establish what was done. Review interim heating for the child in the household.

Recommended: Hold both invoices as unpayable. Tell the provider that only invoice A (£138, within the £180 authorisation) can be considered, once confirmed. Invoice B is disputed until she shows authorisation and completion evidence.

## Uncertainty

- Model confidence: 0.80
- Open questions: 4
- Code overrides: none
- Safety hazard flagged: no

## Logs and traces

- Full decision record: `decision.json` in this folder
- Run-level log: `../trace.jsonl` and `../manifest.json`
- Idempotency key: `f7cc54e713532e5f`

## Tool trace

Every tool call the agent made, in order, with the code's response.

0. `consistency_check(null)` -> `{"status": "unavailable", "checks": [], "dropped": 0, "error": "ValueError: the extraction model did not call report_facts"}`
1. `check_policy({"topic": "verify_claims,amounts,closing,escalation,chasing"})` -> `{"status": "ok"}`
2. `escalate_to_human({"priority": "P2", "route": "property_manager", "summary": "Copper Finch Mechanical sent two overlapping invoices for 7 Larkspur Fold: A £138 (diagnosis) and B £372 (actuator supply/replacement, diagnosis, testing). Both give a service date of 5 Feb. The file has no evidence the actuator was replaced, and the landlord authorised diagnosis only. The invoices should not be paid or closed until a person rules on them. The heating fault is also still unresolved.", "known": ["Landlord authorised diagnosis only, up to £180 inc VAT (event-005); the £138 diagnostic quote is within that (event-007).", "£372 estimate was sent at 14:54 on 5 Feb, after the visit, asking for written authorisation (event-009). Landlord did not authorise remedial work (event-012).", "Provider's 5 Feb visit report mention)` -> `{"status": "staged", "id": "escalation-1", "note": "Staged. Committed only if the final decision passes code checks."}`
3. `submit_decision({"action": "ESCALATE", "priority": "P2", "reason": "Two Copper Finch invoices dated 10 Feb (event-017, event-018) overlap: A is £138 for diagnosis, B is £372 for actuator replacement plus diagnosis. Both give a service date of 5 Feb. Both name the right property, customer and provider, so there is no address or provider mismatch. The landlord authorised diagnosis only, up to £180 inc VAT (event-005), and explicitly declined to authorise remedial work or more spend (event-012). The £372 estimate came after the visit (event-009). The provider's visit report (event-008) mentions no remedial work, and on 7 Feb she still had to check parts (event-016). The file has no completion evidence (event-019), and the tenant does not know whether the actuator was replaced (event-020). The provider has be)` -> `{"status": "accepted"}`
