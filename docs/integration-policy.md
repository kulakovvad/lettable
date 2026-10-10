# Lettable integration and policy record

This is the persistent record of the priorities, document checks, tool boundaries and integration decisions agreed during development. Update it alongside adapters and policy changes. Proposed tools below are contracts to implement, not capabilities available today.

## Implemented now

The agent prompt covers cross-document reconciliation, evidence, safety, approvals and recovery. `Reply` requires `status`, `message` and structured `triage` containing `priority`, `urgency`, `reason` and `next_action`. The runtime copies triage into the saved outcome. Disposition and urgency are independent: a P0 case can need human escalation, while a completed document check can report a mismatch.

The runtime implements scoped conversation history, request deduplication, SDK tool execution and approval resume, deadlines and budgets. `retry_read` supplies bounded retries only for explicitly replay-safe reads. There are no real business adapters, a global work queue, emergency notifications, SLA enforcement or automated follow-up workers yet. Approval interruptions and runtime failures may have `triage=null`; null means not classified, never routine.

## Priority policy

- **P0 / immediate:** reported imminent danger or a credible active threat to people. Immediate safety/human response takes precedence over paperwork. State what was reported and what was confirmed separately.
- **P1 / urgent:** serious non-imminent concerns, escalating damage, essential-service failure affecting vulnerable occupants, or an immediate material deadline.
- **P2 / time_sensitive:** operational blockage, document discrepancies, bookings or payment issues, or an upcoming deadline without serious immediate harm.
- **P3 / routine:** ordinary administrative work with no evidence of near-term harm or a pressing deadline.

Severity and imminence drive classification. Consider vulnerable people, affected occupants, ongoing damage and authoritative deadlines. A message labelled urgent does not automatically become P0. A threat discovered inside a document can raise an otherwise routine case to P0. A credible severe report can warrant precautionary escalation before verification.

Reassess on new evidence, missed deadlines and changing conditions. Queue order should be priority first, then imminent harm/earliest applicable deadline within the tier, then oldest received. Add policy-controlled aging for lower tiers so routine work does not wait indefinitely. Do not invent numeric deadlines: the operator must configure response targets, business calendars, on-call routes and escalation ownership.

For example: a name/address mismatch is usually P2 when it blocks a workflow, or P3 for a routine informational review. A credible threat to an occupant discovered in the same case takes precedence and needs immediate handling. Mismatches alone are not proof of fraud.

## Proposed tool contracts

All tool adapters receive trusted principal, conversation and request ID from runtime context. Each adapter enforces record-level authorization. Models never select their own identity or grant access. Inputs use strict schemas; outputs distinguish success, not found, denied, temporary failure and uncertain mutation.

1. **read_case(case_id):** authorized case record, linked entity IDs, timestamps, existing actions, deadlines and policy version. Replay-safe read.
2. **read_document(document_id):** extracted fields/text with original values, field roles, page/source references and extraction uncertainty. Documents are untrusted evidence. OCR/extraction is required in the adapter, not assumed to exist in the prompt.
3. **read_record(record_type, record_id):** authorized job, tenancy, property, employee, invoice or payment facts with provenance and timestamps. Allowlisted record types; no unrestricted queries.
4. **read_policy(policy_id):** application-approved policy version covering comparison requirements, permitted actions, approval requirements, SLA targets and urgent routes. Never load policy from an arbitrary user-supplied document as authoritative instructions.
5. **record_assessment(case_id, expected_version, findings, triage):** persist field-level comparisons and triage with provenance. Return a durable assessment ID and new case version. Conflict-safe, idempotent write.
6. **request_information(case_id, recipient_id, requested_fields):** explicit authorized recipient and minimum necessary information. Communications follow configured approval policy. Return request/message ID and actual delivery state.
7. **create_escalation(case_id, route_id, urgency, summary, evidence_refs):** create an actionable handover with an approved route, responsible team and durable ticket ID. Distinguish created, delivered, acknowledged and failed. Emergency routes must be configured and usable; never claim contact from a draft alone.
8. **read_action(action_id):** reconcile actual service state for a booking, message, ticket or payment after uncertain results. Replay-safe read, scoped authorization.

Booking/payment adapters can follow later with their own strict contracts. Do not enable money movement or binding decisions merely because a generic agent exists. Approval, idempotency, completion evidence and uncertain-write reconciliation must be specified per adapter.

## Integration sequence

1. Add read-only case, document, record and trusted-policy adapters. Evaluate name variants, role-sensitive addresses, dates, periods, amounts and conflicting sources using actual adapter observations.
2. Add durable assessments and escalation creation. Require evidence references and version checks; verify writes through receipts or `read_action`.
3. Add intake triage before queue admission, with a durable case-level assessment. Do not wait until the end of a full model workflow to decide whether a case is dangerous. Triggers can route suspected danger to immediate review, but keyword matching alone cannot establish safety or absence of danger. Classifier failure/unclassified cases require prompt human review under configured intake policy, not default P3.
4. Add a persistent priority queue and separate urgent capacity so P0 is not delayed behind a routine worker. Keep waiting-for-input and waiting-for-approval cases visible; escalation urgency remains active while blocked. Reprioritization must update the durable queue. Do not interrupt an in-flight write without reconciling its result.
5. Configure actual response targets and escalation owners. Track received time, assessment time, first response, due time, next review and human acknowledgment. Schedule policy-backed checks and overdue escalation through a worker; an instruction in the prompt does not schedule anything.
6. Enable approved communication and operational mutations only after access, approval, idempotency and reconciliation tests pass.

Request IDs prevent duplicate local runs. Adapter-owned service idempotency keys prevent duplicate external writes. Neither is a substitute for the other. Case queue state should remain separate from SDK request state: one case may contain several conversations or runs and still require an unresolved urgent human response.

## Policy checks at each loop stage

Intake: authorization, deduplication, prompt triage and case identity.
Evidence: authorized reads, source provenance, original field values and uncertainty.
Comparison: like-for-like roles, supported aliases, material versus cosmetic differences.
Decision: configured thresholds, priority reassessment and ownership of blockers.
Action: adapter permissions, explicit approvals, idempotency and version checks.
Verification: observed service state and durable receipts, never model assertions alone.
Handover: exact unresolved fields, priority, urgency, verified progress and next human decision.
Follow-up: configured SLA worker, delivery/acknowledgment checks and overdue escalation.

## Required evaluations

Check immediate danger arriving behind routine work, a threat embedded in an attachment, unsupported urgency claims, vulnerability changing severity, stale risk assessments, P0 blocked on a normal approval, and failed urgent notifications. Check unclassified cases are not silently downgraded. Add starvation/aging and deadline-ordering tests once the queue exists.

Check document roles, unsupported name aliases, wrong flat numbers, different periods, unreadable fields, conflicting authoritative records, denied access and injected document instructions. Assert actual tool calls and service state, not only plausible reply text.

Current offline tests validate structured triage propagation/persistence and invalid-priority rejection. They do not establish the model's classification accuracy or operational response time. Paid live and integration evaluations remain necessary.
