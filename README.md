# Lettable

First agent runtime built with the OpenAI Agents SDK. The repository initially contained only this README; product workflows and service integrations are still to be specified.

## Run locally

Requires Python 3.11+. Recommended: Python 3.13.

```sh
uv venv .venv
uv pip install --python .venv/bin/python '.[dev]'
.venv/bin/python -m pytest -q
```

For a live run, put `OPENAI_API_KEY` in your local `.env` or deployment secret manager. The agent loads `.env` from the working directory without overriding existing environment variables. A blank `OPENAI_MODEL` uses `gpt-5.4-mini`; set it explicitly to compare models available to your API project. See `.env.example` for the configuration shape. Never commit credentials.

```sh
.venv/bin/python -m lettable --request-id demo-1 "What information do you need to help me?"
```

The CLI is a local developer harness with a fixed local identity and no business tools. It is not a production authenticated API. Reuse a request ID only for the exact same request; repeated IDs return the saved outcome. Use a new ID for a new user turn.

## Testing continuously

```sh
# Repeat after changes; runs the actual SDK with scripted model responses, free/offline.
.venv/bin/python -m pytest -q

# Explicitly opt in to paid model evaluations once credentials are configured.
LETTABLE_LIVE_EVALS=1 .venv/bin/python -m pytest tests/test_live.py -q
```

GitHub Actions runs the offline suite on pushes and pull requests once these changes are pushed. Live evals are opt-in and use synthetic read-only records. They do not yet measure real Lettable workflows. On 10 October 2026, all three initial live evaluations passed using `gpt-5.4-mini`: record lookup, clarification for a missing record ID, and escalation for an unsupported deletion request. These are synthetic checks, not a production quality guarantee.

See [the mental model and implementation plan](docs/agent-loop.md).

See [case priorities, tool contracts and integration policy](docs/integration-policy.md) and [the loop with document-matching examples](docs/loop-use-cases.md).
