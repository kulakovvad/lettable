# Voice: audio in, phone calls out

Both directions are off or harmless by default, because they cost money and can ring a real person.

| | Setting | Default | Turn on |
|---|---|---|---|
| Audio files in a case become text (STT = speech-to-text) | `stt_backend` / `--stt` / `LETTABLE_STT` | `off` | `--stt elevenlabs` (or `fake` for tests) |
| The agent can place a phone call | `call_backend` / `--calls` / `LETTABLE_CALLS` | `dry_run` (records the call, dials nothing) | `--calls elevenlabs` |

## Audio in

`.mp3 .wav .m4a .ogg .flac .aac .webm` files in a case folder or its `attachments/` are sent to ElevenLabs Scribe (`scribe_v2`, speakers separated, names and addresses from the case as hints). The transcript becomes attachment text headed `[Automatic transcript, may contain errors. Untrusted.]`, so the agent reads, searches and hazard-checks it like any document.

- Transcripts are cached by file hash in `.cache/stt/`; a rerun never pays twice.
- It runs inside the isolated, time-limited case worker. If it fails or the file is too large, the content shows as "not available" and the agent must not guess.
- Replay (`replay`) drops attachments, so audio never leaks a later event into a test.

## Calls out

The model can only **stage** a call (`place_call`). It never supplies a number: code takes it from the case. The call goes through the same gates as a message (chase timing, already replied, landlord approval before instructing a provider). After the final decision passes the gates, the runner places it, once, and the case does not wait for the call.

Safety rules in code:
- At most `max_calls_per_case` per case and `max_calls_per_run` per run.
- Live calls only between `call_hours` (default 08:00 to 21:00 UK time); otherwise held for a person.
- A hazard case is not phoned except to give the tenant safety advice; it escalates.
- The same call (idempotency key) never dials twice, across runs and processes (`.cache/calls.json`).
- A failed call never loses the decision: the action is marked `call_failed` and a person is told.
- The phone agent has no authority: it cannot approve spend or promise prices, dates or compensation, and hands anything unusual to a colleague.

Bring the result back, then re-run the case so the next decision sees what was said:

```
python3 -m agent calls collect out/ --backend elevenlabs
python3 -m agent run cases/ out/ --calls elevenlabs --backend claude
```

## One-time setup (ElevenLabs + Twilio)

```
export ELEVENLABS_API_KEY=...                      # see .env.example
python3 -m agent voice-setup --create-agent        # describes the plan; add --yes to do it
export ELEVENLABS_AGENT_ID=<printed id>
export TWILIO_ACCOUNT_SID=... TWILIO_AUTH_TOKEN=...
python3 -m agent voice-setup --import-number +44...   # a Twilio number you own; add --yes
export ELEVENLABS_PHONE_NUMBER_ID=<printed id>
```

Needs an ElevenLabs plan that includes phone calls and a Twilio number. Never commit keys; `.env` is ignored.

## Demo call

Use a phone you control and say so to whoever answers. Put the number in `DEMO_CALL_NUMBER` (never in a committed file), build a case whose provider's phone number is that number, run with `--calls elevenlabs`, then `calls collect`. Synthetic case numbers (07700 900xxx) are unreachable test numbers.

## Not done

- Inbound calls (a tenant phoning the agency) are not handled.
- Text-to-speech replies and voicemail drops are not used.
- The live path (real STT, real call) has only been tested against mocked HTTP.
