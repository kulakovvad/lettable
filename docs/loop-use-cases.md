# The agent loop, with operational examples

This guide separates what the runtime implements today from the business behaviour the prompt requests. The runtime exists; document extraction, property records, job records, payment verification and notifications still need real tool adapters. The examples below are illustrative, not executed case results.

## 1. Receive and claim the request

The server supplies the trusted user identity, conversation and request ID. The runtime validates input and claims the request so a repeated request ID cannot start the same workflow again. It loads that conversation's saved history.

Example: “Check whether these employment documents agree before we continue with this application.” The agent needs accessible documents and a clear application reference. An uploaded name is not authorization to access another person's records.

Handles: repeated submissions, follow-up answers, separate customers and conversations. Record-level access still belongs in each adapter. Input larger than the configured limit is rejected, not automatically chunked.

## 2. Understand the outcome and constraints

The model determines what must be established, which entities are involved and what constitutes completion. It separates the requested check from any subsequent action.

Example: checking document consistency does not itself authorize approving a tenant or sending money. “Job address” could mean an employer's office or the physical work site; the agent should establish its meaning before comparing it with a payslip field.

Handles: multiple tasks, unclear instructions, new user intent, urgent cases and requests outside its capabilities.

## 3. Gather evidence

The model selects available authorized read tools. For documents, an adapter should supply extracted fields, document/page references and extraction uncertainty. The agent reads the relevant authoritative records where available and asks a targeted question only when evidence cannot resolve an essential unknown.

Example: obtain the job record, payslip, application and an authorized record linking a name variant. Do not guess the job ID or substitute a similarly named person's record.

Handles: missing documents, absent IDs, unreadable scans, missing pages, ambiguous dates, not-found records and access denial. Text extraction/OCR is not currently implemented.

## 4. Compare and decide

Preserve original values; normalize cosmetic differences only. Compare corresponding roles, dates and references. Record each required comparison as match, supported equivalent, mismatch, missing or unverifiable.

Example: “Alex Morgan” and “Alexander Morgan” require evidence linking the names. “18 Cedar Rd” and “18 Cedar Road” may be equivalent if unit and postcode agree. “Flat 2” and “Flat 7” are materially different. A payslip from a payroll company may be consistent with a job at a different company only if that relationship is supported.

Handles: name variants, changed names, employer versus payroll provider, home versus work addresses, stale records, pay-period differences, amount discrepancies, duplicates and conflicting sources. Matching text does not establish document authenticity or eligibility.

## 5. Choose the next safe action

If the check is complete, report its findings. If a user can resolve an essential gap, ask for that detail. If the decision requires expertise or an unresolved material conflict remains, hand it to a human. Otherwise choose the smallest useful action permitted by configured policy and tools.

Example: record a discrepancy or request supporting evidence, if those tools exist. Do not correct a payslip, accuse the applicant of fraud, decline their application or release a payment merely because a mismatch was found.

Handles: routine resolutions, clarification, safe non-action, human judgement and independent progress on unblocked tasks.

## 6. Pause for approval and execute

A tool configured to require approval interrupts the SDK run. The runtime saves the pending action and exposes its exact arguments. Explicit approval resumes that action; denial must be respected. Approvals expire. For permitted actions, the adapter enforces authorization and executes the operation.

Example: the agent can prepare a document request; sending it may require approval under the configured policy. It must not describe the request as sent while approval is pending.

Handles: approved and denied actions, expired approval and resumable workflows. Approval is implemented; business tools and their approval policies are not supplied by default.

## 7. Observe, verify and recover

The result feeds back to the model. It checks whether the relevant state actually changed. Replay-safe reads can use bounded retries. An uncertain write must be reconciled before a retry. Partial progress is retained and explained.

Example: creating a review task needs a task ID or an authorized read confirming its existence. If creation times out, check whether the task already exists before creating another. If one document is readable and another is unavailable, report the verified findings and the remaining gap.

Handles: temporary outages, invalid arguments, permanent failures, duplicate actions, uncertain writes, partial success and stale state. The runtime caps time, model turns, tokens, tool calls and repeated identical calls; it does not implement service-specific reconciliation automatically.

## 8. Return a disposition and preserve context

The model returns a validated reply with `status`, `message` and structured `triage`. The runtime persists successful conversation history and outcomes. A user answer starts a new request with history; an approval resumes the saved SDK run.

- `completed`: the requested check or action is fully satisfied by evidence. A check can complete with a reported mismatch if its scope was only to identify differences.
- `needs_input`: an essential user answer is needed to continue.
- `escalated`: a human must resolve the blocker or handle an unsupported or uncertain action.
- `awaiting_approval`: the runtime is paused before a protected action.
- `cancelled`: the local run stopped; remote effects may still need checking.

A final message should state verified findings, unresolved parts and the next useful step. An escalation message is not proof that a human has been notified. Current runtime failures produce a generic escalation and do not persist a detailed intermediate business handover; durable case records and receipts are needed for robust crash/failure recovery.

## Worked example: job record and payslip

Illustrative inputs:

- Job record: Alexander Morgan; employee E-104; employer Cedar Maintenance Ltd; work site Flat 2, 18 Cedar Road, AB1 2CD; employment starts 1 September 2026.
- September payslip: Alex Morgan; employee E-104; employer Cedar Maintenance Ltd; employer office 80 Market Street; employee home Flat 7, 18 Cedar Rd, AB1 2CD; pay period September 2026.
- Application: Alexander Morgan; home Flat 2, 18 Cedar Road, AB1 2CD.

The agent should make these separate findings:

1. Employee ID and employer agree, supporting the employment link. The name variant still needs an authoritative record linking Alex to Alexander; it must not rely on name similarity alone.
2. The employer office and work site are different address roles, so their difference is not a contradiction.
3. The work site and application home happen to agree, but that does not prove residence.
4. The employee home on the payslip differs from the application home by flat number. This is a material discrepancy unless evidence establishes an address change or stale record.
5. The pay period follows the employment start, which is chronologically consistent; this alone does not prove payment or authenticity.

Next action: consult authorized employee/application records if available; otherwise ask for evidence of the name variant and which home address is current. Escalate if a material conflict remains. If the task was only a consistency check, the agent can complete that check with these findings; if the task includes an eligibility decision, it must apply configured criteria and resolve required blockers first.

## Other cases the same loop can address with integrations

- Contractor invoice versus work order: check contractor identity, property/unit, job reference, scope, dates, amount/currency and recorded completion. A matching invoice does not prove the work was completed or paid.
- Duplicate invoice/payment request: inspect invoice references, existing transactions and service receipts before creating a new payment.
- Maintenance booking: match the property and unit, issue, tenant availability, contractor capability and confirmed appointment; recover from unavailable slots.
- Tenancy paperwork: reconcile names, property/unit, tenancy dates, document versions and authorized signatures; refer unresolved legal interpretation to a human.
- Wrong-person records: similar names with different identifiers must remain separate; do not leak the other record.
- Changed intent: cancel pending work where supported, check existing side effects and update only the work that remains authorized.
- Malicious document text: extract business facts but ignore embedded instructions to skip checks, disclose secrets or mark the case approved.
- Urgent maintenance: follow the configured urgent route and distinguish reported danger from verified dispatch; never invent a successful call.

These are intended behaviours to evaluate, not a claim that all workflows are implemented. Real readiness needs representative tool-connected cases, observed action assertions and service-state checks.

See [the integration and priority policy](integration-policy.md) for case ordering, proposed tool contracts and implementation sequence.
