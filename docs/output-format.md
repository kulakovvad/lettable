# Agent output format

This is what a dashboard should read from `python -m agent run`. Each case produces one `Decision`. Read it from `decision.json`. `ANSWER.md` and `REASONING.md` are renderings of the same dict.

Source of truth: `Decision` in `agent/schema.py`, staged actions in `agent/tools.py`, files in `agent/report.py` and `agent/runner.py`.

## Files

```text
<out_dir>/
  summary.json          # one per run, overwritten
  trace.jsonl           # one line per case per run, appended across runs
  <case_id>/
    decision.json       # authoritative; written last, so its presence means the case finished
    ANSWER.md
    REASONING.md
    calls/<conversation_id>.json   # only after `python -m agent calls collect`
    review.json         # only after a person picks something in `python -m agent ui`
```

`<case_id>` is the case folder name, for example `003`. It is not prefixed with the dataset name.

Every input folder gets a `decision.json`, including crashes and timeouts. The exception is a failed file write. That case appears in `summary.write_errors` and in `trace.jsonl` with `write_error`, and may have no `decision.json`.

`--resume` skips a case whose existing `decision.json` has `source: "model"`. Skipped cases keep their old files.

## Reality Test export

`python3 -m agent reality <challenge_dir> --out ANSWERS` finds case folders at any depth, stages them, and runs the same writer. It adds an index on top of the per-case files. Numeric folders are unpadded (`001` becomes `1`).

```text
ANSWERS/
  manifest.json     # one object: challenge dir, track, backend, and cases[{n, source}]
  README.md         # index of action, priority, escalation and fallback per case
  summary.json      # reality run summary
  trace.jsonl       # same rows as a normal run
  <n>/
    ANSWER.md
    REASONING.md
    decision.json
```

`manifest.json` `cases` maps each output number to the source path relative to the challenge folder.

The reality `summary.json` records `total`, `written`, `missing` (numbers with no `decision.json`), `by_action`, `fallbacks`, `escalated`, `passes` (one object per pass: `written`, `skipped`, `by_action`, `fallbacks`, `seconds`), `seconds`, `track`, `backend`, `stt`, `finished_at` and `reconciled`. `reconciled` is true when `missing` is empty. A later pass resumes only cases whose `source` is not `model`, so fallbacks are retried and finished model decisions are kept.

## Run summary

`summary.json`, also printed to stdout:

```json
{
  "total": 1,
  "written": 1,
  "skipped": 0,
  "by_action": {"WAIT": 1},
  "fallbacks": {},
  "write_errors": [],
  "seconds": 0.47,
  "reconciled": true
}
```

| Field | Meaning |
|---|---|
| `total` | Case folders found |
| `written` | Cases decided this run |
| `skipped` | Cases skipped by `--resume` |
| `by_action` | Count of final `action` |
| `fallbacks` | Count of `cause` among `source: "fallback"` cases |
| `write_errors` | Case ids whose files failed to write |
| `seconds` | Wall time for the run |
| `reconciled` | `written + skipped == total` and no write errors. The CLI exits 1 when false |

`trace.jsonl` rows:

```json
{"case_id": "003", "seconds": 0.47, "source": "model", "action": "WAIT", "cause": null, "gate_notes": [], "write_error": null}
```

## Decision

All keys are always present. Timestamps are ISO-8601 strings with an offset.

### Core fields

These are filled by every path: the tool loop, the single-call backends and the fallback.

| Field | Type | Meaning |
|---|---|---|
| `case_id` | string | Case folder name |
| `action` | enum | Final action after code gates. `WAIT`, `CHASE_LANDLORD`, `CHASE_PROVIDER`, `ASK_TENANT`, `ASK_PROVIDER`, `ASK_LANDLORD`, `ROUTE_FOR_APPROVAL`, `INSTRUCT_PROVIDER`, `SEND_REMINDER`, `CLOSE`, `ESCALATE` |
| `reason` | string | Model reason. Gate changes are appended as ` [gate: ...]`. Fallback reasons start `Automatic escalation:` |
| `source` | `model` \| `fallback` | `fallback` means the worker crashed, timed out, errored or never started, and plain code wrote the escalation |
| `message` | string | Body of the staged action that matches the final action. Empty unless the final action is `CHASE_LANDLORD`, `CHASE_PROVIDER`, `ASK_TENANT`, `ASK_PROVIDER`, `ASK_LANDLORD`, `INSTRUCT_PROVIDER` or `SEND_REMINDER`. For `ROUTE_FOR_APPROVAL`, read the body from `actions` |
| `unknowns` | string[] | Open questions |
| `options` | string[] | Choices for a person. Always filled on `ESCALATE` |
| `confidence` | number 0–1 or null | Model's confidence. `null` on fallback |
| `hazard` | boolean | Code found an open hazard phrase. Forces `ESCALATE` |
| `waiting_on` | `landlord` \| `provider` \| `tenant` \| null | From the latest hold line, unless that party replied since |
| `waiting_days` | number or null | Days since that hold, as of the decision time |
| `events_seen` | integer | Events visible to the agent |
| `gate_notes` | string[] | Each final gate change, in plain English |
| `proposed_action` | enum or null | What the model asked for, only when the gates changed it |
| `cause` | string or null | Why the run did not finish normally. See below |
| `idempotency_key` | string | 16 hex chars from case id, events seen, action and message |
| `decided_at` | string | Time the gates judged against. In the tool loop this is the decision time (`as_of`). On fallback it is the wall clock or `--now` |
| `warnings` | string[] | Input problems, such as a missing `index.md` or unreadable event time |
| `answer` | string | Direct answer when the case asks an explicit question. Empty on fallback, on the single-call backends, and when the case does not ask one. When non-empty, `ANSWER.md` starts with an `## Answer` section |

### Tool-loop fields

These are filled only by the `claude`, `anthropic`, `openai` and `auto` backends. With `fake`, `anthropic-single` and on fallback, they keep the empty defaults shown in the fallback example.

| Field | Type | Meaning |
|---|---|---|
| `priority` | `P0`–`P3` or null | Model priority. A hazard raises P2 or P3 to P1. Null outside the tool loop |
| `title` | string | Case title from `index.md` |
| `request` | string | Initial request |
| `as_of` | string | Decision time. `--as-of last_event` (default): the case's latest event; `now`: the wall clock or `--now` (an explicit `--now` implies this); `later`: whichever is later |
| `model` | string | Model name |
| `steps` | integer | Model turns used, max `loop_max_steps` (12) |
| `tokens` | integer | Tokens across all turns |
| `evidence_refs` | string[] | `event-NNN` or attachment names cited in `submit_decision` |
| `unrelated_issues` | string[] | Separate issues the model says need their own request |
| `actions` | object[] | Everything staged, with its final state |
| `blocked` | object[] | Tool calls a code gate refused, with the reason given to the model |
| `trace` | object[] | Every model note and tool call, in order |
| `consistency` | object or null | Document consistency report (see below). Null unless `consistency_check` is on |

### Consistency report

Present when `consistency_check` is on (tool loop only). Design: [design.md](design.md#document-consistency-check-opt-in). Shape, with values based on public case 028 (refs illustrative):

```json
{"status": "ok", "model": "jev-1.13.0", "dropped": 0,
 "checks": [{"field": "property_address",
             "values": ["Flat 7, 87 Alder Lane, Bellmere, ZZ3 8ZZ", "Flat 7, 177 Alder Lane, Northbridge, ZZ6 5ZZ"],
             "refs": [["index", "event-001"], ["event-009"]],
             "score": 0.023, "confidence": 0.94, "tier": "escalate"}]}
```

| Field | Type | Meaning |
|---|---|---|
| `status` | `ok` \| `unavailable` | `unavailable`: extraction or Jev failed, or `TYPESAFE_API_KEY` is not set. The case continues |
| `error` | string | Only when `unavailable`, truncated to 300 characters |
| `model` | string | Jev model |
| `dropped` | integer | Extracted values not found in the source they cited |
| `checks` | object[] | Only fields whose values still differ after normalising. Empty means nothing differed |
| `checks[].field` | string | `tenant_name`, `landlord_name`, `property_address`, `tenant_phone`, `tenant_email`, `landlord_phone`, `landlord_email`, `reference_number` |
| `checks[].values` / `refs` | string[] / string[][] | Distinct values as written, and where each appears, in the same order |
| `checks[].score` | number | Jev similarity, 0 (different) to 1 (identical) |
| `checks[].confidence` | number | Jev confidence |
| `checks[].tier` | `pass` \| `flag` \| `escalate` | `escalate` adds a gate note and forces `ESCALATE` |

### Cause

| Value | Source | Meaning |
|---|---|---|
| null | model | Normal finish |
| `loop_no` | model | Loop hit its turn limit without `submit_decision`. Auto-escalated |
| `loop_token` | model | Loop exceeded its token budget. Auto-escalated |
| `timeout` | fallback | Case exceeded `case_timeout_s` (240 s) |
| `crash` | fallback | Worker exited without reporting |
| `error` | fallback | Worker raised, or returned an invalid decision |
| `deadline` | fallback | Run deadline passed before this case started |
| `spend_cap` | fallback | Run-wide `run_token_budget` was used up before this case started. No model call |
| `runner` | fallback | Worker process could not be started |

A fallback `reason` includes the exception type and message, truncated to 300 characters. Hide it from end users if that matters.

## Actions

Each item in `actions` is one staged side effect. Nothing is delivered. `committed` means recorded in the local outbox only.

Common keys:

| Field | Type | Meaning |
|---|---|---|
| `id` | string | `<kind>-<n>`, such as `message-1` |
| `kind` | `message` \| `call` \| `approval_request` \| `followup` \| `escalation` \| `closure` | |
| `idempotency_key` | string | 12 hex chars |
| `state` | `committed` \| `held_for_review` \| `call_failed` | Items are `staged` during the run. Finished output has only these. `call_failed` is only for a `call` the dialer could not place |
| `note` | string | Why it is in that state |

Only the staged item that matches the final action is `committed` (for example the chase message for `CHASE_LANDLORD`, the follow-up for `WAIT`, the closure for `CLOSE`). Escalations always commit. A `safety_advice` message commits only when it goes to the tenant and code found an open hazard. Everything else is `held_for_review`, including every message when the loop ran out of budget or the final action is `ESCALATE`. If the final action is `ESCALATE` and the model staged no escalation, code adds one with note `Created automatically because the final decision is an escalation.`

Per-kind keys:

| `kind` | Extra keys |
|---|---|
| `message` | `to` (`tenant`, `landlord`, `provider`), `purpose` (`chase`, `request_info`, `reminder`, `update`, `safety_advice`, `instruct_provider`), `priority`, `body`, `evidence_refs` |
| `call` | `to` (`tenant`, `landlord`, `provider`), `purpose` (`chase`, `request_info`, `instruct_provider`, `update`, `safety_advice`), `priority`, `number` (E.164, taken from the case, never from the model), `objective`, `facts` (short strings the caller may rely on), `body` (`Phone call: <objective>`), `evidence_refs`, and after placing: `call_status` (`pending` \| `dry_run` \| `started` \| `failed` \| `not_placed`), `conversation_id`, `call_detail`, and after `calls collect`: `call_result` (`status`, `success`, `summary`, `data`) |
| `approval_request` | `to` (`landlord`), `amount_gbp` (`null` asks approval for a provider to attend or quote, with no cost approved), `scope`, `body`, `evidence_refs`, `above_limit` (amount over `approval_limit_gbp`, default 300) |
| `followup` | `review_at`, `waiting_on` (`tenant`, `landlord`, `provider`, `internal`), `reason` |
| `escalation` | `priority`, `route` (`on_call_emergency`, `property_manager`, `accounts`, `complaints`), `summary`, `known`, `unknowns`, `tried`, `options`, `evidence_refs` |
| `closure` | `completion_refs` (events where a provider, tenant or landlord says the job is done), `invoice_status` (`sent_to_landlord`, `landlord_pays_directly`, `no_charge`), `invoice_refs`, `keys_status` (`returned`, `not_applicable`), `key_refs`, `reason` |

### Phone calls

A call is staged like a message and can stand in for it on `CHASE_*`, `ASK_TENANT`, `ASK_PROVIDER`, `ASK_LANDLORD` and `INSTRUCT_PROVIDER`. It follows the same commit rule. After the final checks the runner places each committed call once (`call_backend`: `dry_run` records it and dials nothing, `elevenlabs` places it). Nothing waits for the call to finish. A call to the tenant with purpose `safety_advice` commits on a code-found hazard, like safety advice by message.

- `call_status` `not_placed` with state `held_for_review`: the run's call limit (`max_calls_per_run`) was reached, or a live call fell outside UK calling hours (`call_hours`).
- `call_failed`: the dialer raised or returned `failed`. The decision stays; `blocked` gets a `call_failed` item and a ticket (or the existing escalation's `unknowns`) tells a person the call did not happen.
- The same `idempotency_key` found in an earlier `decision.json` is never dialled again; the earlier `conversation_id` is reused (note `Already placed by an earlier run.`).
- `python -m agent calls collect <out_dir>` fetches finished calls, writes `calls/<conversation_id>.json` (`transcript`, `summary`, `success`, `data`, `dry_run`), fills `call_result` and re-renders `ANSWER.md`. Calls still in progress are listed under `pending`. Re-running the case adds each finished, non-dry-run call as an automatic `Call` event from `Agency / system` (a record of our contact, not a reply, so a voicemail never clears the wait).

## Blocked calls

Despite the name, this section is about tool calls a gate refused (not phone calls).

Each item in `blocked` is a tool call a gate refused. The model saw the reason and could adapt. A non-empty list does not mean the case failed. Shape, with illustrative values:

```json
{"tool": "send_message", "status": "blocked", "code": "too_early", "why": "only 1.2 days since we wrote to the provider (event-004); policy is 3 days", "hint": "Schedule a follow-up and WAIT. Only an open hazard found by code allows an early chase."}
```

| `code` | Tool |
|---|---|
| `empty_message`, `unknown_party`, `unverified_detail`, `wrong_purpose`, `nothing_to_chase`, `already_replied`, `too_early`, `no_landlord_approval`, `no_appointment` | `send_message` |
| `amount_not_in_case`, `unknown_party`, `unverified_detail`, `already_approved` | `route_for_approval` |
| `no_confirmation`, `possibly_reopened`, `invoice_unknown`, `invoice_unverified`, `keys_unknown`, `keys_unverified` | `close_case` |
| `empty_objective`, `unknown_party`, `unverified_detail`, `no_hazard`, `hazard_escalate`, `call_limit`, `too_early`, `already_replied`, `nothing_to_chase`, `wrong_purpose`, `no_landlord_approval`, `no_number` | `place_call` |
| `call_failed` | added by the runner when a call could not be placed |
| `action_not_staged`, `staged_not_submitted` | `submit_decision` |

`staged_not_submitted` refuses the first `WAIT` while an outbound request (`request_info`, `chase`, `instruct_provider`, `reminder` or an approval request) is staged. Its hint names the action that would send it. A second `WAIT` is accepted and the request stays `held_for_review`.

## Trace

Each item in `trace` is a model note or a tool call:

```json
{"step": 1, "thought": "model text, up to 1500 chars"}
{"step": 2, "tool": "schedule_followup", "args": {"after_hours": 48}, "result": {"status": "staged", "id": "followup-1"}}
```

With the consistency check on, the trace starts with step 0: `{"step": 0, "tool": "consistency_check", "result": {"status": "ok", "checks": ["property_address:escalate"], "dropped": 0, "error": null}}`.

`result` is a summary. It keeps `status`, `code`, `why`, `hint`, `id`, `error` and `note`. Long lists and text become counts, such as `"events": "12 item(s)"`. Tool `status` values are `ok`, `staged`, `blocked`, `accepted`, `unavailable`, `error` and `skipped`.

## Suggested dashboard grouping

There is no status field. These groupings come from the fields above.

| Group | Rule |
|---|---|
| System failure | `source == "fallback"` |
| Agent ran out of budget | `cause` starts with `loop_` |
| Needs a person | `action == "ESCALATE"`, then sort by `priority` and `hazard` |
| Gates overrode the model | `proposed_action != null` |
| Waiting | `action == "WAIT"`. Next review is the `followup` action's `review_at` |
| Outbound queued | Any `actions[].state == "committed"` with `kind` `message`, `call` or `approval_request` |
| Call failed | Any `actions[].state == "call_failed"` |
| Held | Any `actions[].state == "held_for_review"` |

## Review

`python -m agent ui <out_dir>` writes `<case_id>/review.json` when a person picks an option, takes a case over or asks for a separate issue to become a new case. Entries are appended, never edited. `decision.json` is not changed and the agent does not read this file yet.

```json
{"case_id": "015", "entries": [
  {"choice": "option", "at": "2026-10-10T12:01:00+00:00", "option": 1, "option_text": "Ask Alder Homes to confirm attendance ..."},
  {"choice": "new_case", "at": "2026-10-10T12:02:00+00:00", "text": "Event-016: the door at Flat 10, 110 Meadow Row ..."},
  {"choice": "take_over", "at": "2026-10-10T12:03:00+00:00"}
]}
```

| Field | Meaning |
|---|---|
| `choice` | `option` (go with one of `options`), `take_over` (a person handles the case) or `new_case` (open a separate issue as its own case) |
| `at` | UTC time of the choice |
| `option`, `option_text` | Only for `option`: the 1-based number and the text as it was in `options` |
| `text` | Only for `new_case`: the separate issue, usually one of `unrelated_issues` |

The latest `option` or `take_over` entry is the current choice.

`text` and `option_text` are stored as given and are not scrubbed for phone numbers, names or secrets. Treat `review.json` like the case files it sits next to.

## Examples

These were produced by running PR 5's own code on public case 003 with the scripted test backends in `tests/`. No model was called.

### Tool loop, normal finish

`--backend tests.loop_backends:WaitChat`:

```json
{
  "case_id": "003",
  "action": "WAIT",
  "reason": "Scripted decision citing event-003.",
  "source": "model",
  "message": "",
  "unknowns": [],
  "options": [],
  "confidence": 0.9,
  "hazard": false,
  "waiting_on": null,
  "waiting_days": null,
  "events_seen": 23,
  "gate_notes": [],
  "proposed_action": null,
  "cause": null,
  "idempotency_key": "446696a191bfb8bb",
  "decided_at": "2025-09-05T12:34:00+00:00",
  "warnings": [],
  "priority": "P3",
  "title": "Checkout Cleaning Estimate and Invoice",
  "request": "Please provide an estimate to clean property as per check out to include the removal of dumped items left in the property and a carpet clean.",
  "as_of": "2025-09-05T12:34:00+00:00",
  "model": "scripted",
  "steps": 3,
  "tokens": 0,
  "evidence_refs": ["event-003"],
  "unrelated_issues": [],
  "actions": [
    {
      "id": "followup-1",
      "kind": "followup",
      "idempotency_key": "0d391678a092",
      "state": "committed",
      "review_at": "2025-09-07T12:34:00+00:00",
      "waiting_on": "landlord",
      "reason": "Asked today.",
      "note": "Recorded in the local outbox (no external delivery connected)."
    }
  ],
  "blocked": [],
  "trace": [
    {"step": 1, "tool": "case_facts", "args": {}, "result": {"status": "ok"}},
    {"step": 2, "tool": "schedule_followup", "args": {"after_hours": 48, "waiting_on": "landlord", "reason": "Asked today."}, "result": {"status": "staged", "id": "followup-1", "note": "Staged. Committed only if the final decision passes code checks."}},
    {"step": 3, "tool": "submit_decision", "args": {"action": "WAIT", "priority": "P3", "reason": "Scripted decision citing event-003.", "confidence": 0.9, "evidence_refs": ["event-003"], "unknowns": [], "options": [], "unrelated_issues": [], "amount_gbp": null}, "result": {"status": "accepted"}}
  ]
}
```

### Tool loop, no decision

`--backend tests.loop_backends:SilentChat` never calls `submit_decision`. The trace is cut to its first step here. The real trace has twelve `case_facts` calls. From the third on, each result is `{"status": "error", "error": "repeated identical call; use the earlier result or decide"}`.

```json
{
  "case_id": "003",
  "action": "ESCALATE",
  "reason": "The agent did not reach a decision (no decision within 12 turns). The investigation so far is in the trace.",
  "source": "model",
  "message": "",
  "unknowns": ["What the next step should be"],
  "options": ["Read the trace and decide the next step", "Re-run the case with a larger budget"],
  "confidence": 0.0,
  "hazard": false,
  "waiting_on": null,
  "waiting_days": null,
  "events_seen": 23,
  "gate_notes": [],
  "proposed_action": null,
  "cause": "loop_no",
  "idempotency_key": "9d949b1fc1453880",
  "decided_at": "2025-09-05T12:34:00+00:00",
  "warnings": [],
  "priority": "P2",
  "title": "Checkout Cleaning Estimate and Invoice",
  "request": "Please provide an estimate to clean property as per check out to include the removal of dumped items left in the property and a carpet clean.",
  "as_of": "2025-09-05T12:34:00+00:00",
  "model": "scripted",
  "steps": 12,
  "tokens": 0,
  "evidence_refs": [],
  "unrelated_issues": [],
  "actions": [
    {
      "id": "escalation-1",
      "kind": "escalation",
      "idempotency_key": "bba271f7a1b0",
      "state": "committed",
      "priority": "P2",
      "route": "property_manager",
      "summary": "The agent did not reach a decision (no decision within 12 turns). The investigation so far is in the trace.",
      "known": ["23 events reviewed"],
      "unknowns": ["What the next step should be"],
      "tried": ["Agent proposed ESCALATE"],
      "options": ["Read the trace and decide the next step", "Re-run the case with a larger budget"],
      "evidence_refs": [],
      "note": "Created automatically because the final decision is an escalation."
    }
  ],
  "blocked": [],
  "trace": [
    {"step": 1, "tool": "case_facts", "args": {}, "result": {"status": "ok"}}
  ]
}
```

### Fallback

`--backend tests.chaos_backend:ChaosBackend` on a folder named `raise-003`. The backend raises, so the runner writes the plain-code escalation. All tool-loop fields are empty.

```json
{
  "case_id": "raise-003",
  "action": "ESCALATE",
  "reason": "Automatic escalation: error. RuntimeError: model exploded Known: Case: Checkout Cleaning Estimate and Invoice; Request: Please provide an estimate to clean property as per check out to include the removal of dumped items left in the property and a carpet clean.; 23 events recorded.",
  "source": "fallback",
  "message": "",
  "unknowns": ["The system could not finish this case (error)."],
  "options": ["Take over the case and read the timeline", "Re-run the case once the cause is fixed"],
  "confidence": null,
  "hazard": false,
  "waiting_on": null,
  "waiting_days": null,
  "events_seen": 23,
  "gate_notes": [],
  "proposed_action": null,
  "cause": "error",
  "idempotency_key": "091cafc2057c9690",
  "decided_at": "2026-10-10T10:38:34.653839+00:00",
  "warnings": [],
  "priority": null,
  "title": "",
  "request": "",
  "as_of": "",
  "model": "",
  "steps": 0,
  "tokens": 0,
  "evidence_refs": [],
  "unrelated_issues": [],
  "actions": [],
  "blocked": [],
  "trace": []
}
```

## Replay output

`python -m agent replay` is an evaluation run, not case output. It writes to its own directory:

- `rows.jsonl`: one row per decision point, with `case_id`, `events_visible`, `now`, `proposed`, `model_proposed`, `real_next`, `real_next_text`, `result` (`agree`, `differ`, `escalated`, `unscored`, `fallback`), `gate_notes` and `reason`.
- `summary.json`: `points`, `results`, `agreement_rate`, `agree_or_escalated_rate`, `by_real_next`, `seconds` and `backend`.
- `report.md`: a readable version of the summary, with the disagreements listed.

`real_next` comes from a rule applied to the next event. Treat agreement rates as something to read, not an accuracy score.
