# lettable

Decides the next step on property-management cases. The model proposes an action; plain code checks it; anything that fails or cannot be approved becomes an escalation to a person. Design: [docs/design.md](docs/design.md) (once merged).

Status: core loop only. The real task output format and tools are not known yet, so actions are recorded, not executed.

## Run

Needs Python 3.9+. The default setup has no dependencies.

```
python3 -m agent run "<cases folder>" out/            # fake backend: free, offline
python3 -m unittest discover -s tests -t .               # tests
```

Each case folder holds `index.md`, `history.md` and optional `attachments/`. For every case the run writes `out/<case>/ANSWER.md`, `REASONING.md` and `decision.json`, plus `out/trace.jsonl` and `out/summary.json`.

Useful options: `--timeout` (seconds per case), `--deadline` (whole run), `--concurrency`, `--resume` (skip cases the model already decided), `--now <ISO time>` (replay as of a past moment), `--config file.json` (override any value in `agent/config.py`).

### Real model (tool loop)

Claude is the main driver; OpenAI is a fallback. The clients use the standard library, so no SDK is needed (`pip install pypdf` to read PDF attachments).

```
cp .env.example .env             # set ANTHROPIC_API_KEY (or OPENAI_API_KEY), then export it
python3 -m agent run "<cases folder>" out/ --backend claude     # or: openai, auto
```

`claude`/`anthropic`, `openai` and `auto` run the bounded tool loop (`agent/loop.py`). `anthropic-single` is the original one-call backend. Model names come from `ANTHROPIC_MODEL` / `OPENAI_MODEL` or `agent/config.py`. The real model is only used when you ask for it by name; a key in the environment never turns on spending by itself.

### Replay (testing without an answer key)

```
python3 -m agent replay "<cases folder>" out-replay/ --points 4
python3 -m agent replay "<cases folder>" out-replay/ --points 2 --backend claude   # tool loop, capped at 30 points
```

Cuts each finished case at a few points, shows the agent only the events up to that point (clock set to when the next event happened), and compares its proposed action with what the agency actually did next. Writes `rows.jsonl`, `summary.json` and `report.md` (with the disagreements to read by hand). The "what happened next" label is a rough rule on the next event, so treat the numbers as agreement, not accuracy. Attachments are left out of a cut case, because they cannot be tied to a point in time. A paid backend is capped at 30 points unless you pass `--max-calls`.

### Voice

Audio files in a case can be transcribed (`--stt elevenlabs`), and the agent can phone a provider, landlord or tenant (`--calls elevenlabs`; `dry_run` by default). Both are off unless asked for. See [docs/voice.md](docs/voice.md).

## How it stays reliable

- Every case runs in its own process with a hard time limit. A crash, hang, model error or malformed answer produces a fallback escalation, so outputs always equal inputs (`summary.json` checks this).
- Gates can only make a decision stricter (wait or escalate), never looser.
- The recorded summary and outcome in `index.md` are never loaded, so a case's ending cannot leak into the decision.
- Results are written atomically; `decision.json` is written last and marks a case as finished.

## Layout

- `agent/timeline.py`: parse a case into events and a waiting state
- `agent/llm.py`: backends (`fake`, `claude`/`anthropic`, `openai`, `auto`, `anthropic-single`, or `module:Class`)
- `agent/gates.py`: code checks on a proposal
- `agent/fallback.py`: escalation when anything fails
- `agent/runner.py`: isolation, time limits, concurrency, resume
- `agent/report.py`: atomic output files
- `agent/replay.py`: cut-and-compare check on finished cases
- `agent/chat.py`: Claude/OpenAI tool-calling clients
- `agent/loop.py`: bounded tool loop, final gates, commit or hold staged actions
- `agent/tools.py`: read tools and gated action tools
- `agent/policy.py`: trusted operating policy for the model
- `tests/`: unit and failure-injection tests

## Known limits

- Actions are staged and committed to a local outbox only; no external messaging, CRM or ticketing system is connected.
- PDFs are read only when `pypdf` is installed; scanned or image-only files are listed as "content not available".
- Thresholds in `agent/config.py` are starting values, not tuned.
- The real model path has not been run end to end.
