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
- At most `max_calls_per_case` calls in a case's whole history (earlier calls are counted from their call records) and `max_calls_per_run` per run.
- Live calls only between `call_hours` (default 08:00 to 21:00 UK time); otherwise the call is held and a person is told.
- A hazard case is not phoned except to give the tenant safety advice; it escalates.
- The number comes from the case, never from the model. Quoted lines, lines pointing to someone else ("ring our accounts desk") and premium-rate or non-geographic numbers are skipped.
- The phone agent speaks for the agency named in the case, not for a name the model supplies.
- One call per case, party, purpose and number in each round: rewording the objective does not dial again. The ledger (`~/.cache/lettable/calls.json`, or `LETTABLE_CALL_LEDGER`) stops the same call being dialled twice, across runs and processes.
- If a request may have gone through (timeout, dropped connection, 5xx) the call stays `pending` in the ledger and is never retried automatically. A person checks ElevenLabs, then removes the entry. A clear refusal (4xx) is not recorded and can be retried.
- A call that cannot be placed (failed or held) never loses the decision: the action is marked `call_failed` or `held_for_review` and a person is told through an escalation ticket.
- Call records and transcripts are third-party speech: labelled untrusted, and amounts or numbers spoken in them do not count as facts of the case.
- The phone agent has no authority: it cannot approve spend or promise prices, dates or compensation, and hands anything unusual to a colleague.

Results come back by themselves: at the start of the next live run (`--calls elevenlabs`), calls placed earlier are fetched and their records added to the case (turn this off with `collect_calls: false`). You can also do it by hand:

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

### Changing what the agent says

The wording, the voice settings and the extracted fields live in `agent/voice_prompt.py`. After editing them, apply them to the agent you already created (its phone numbers and name are kept):

```
python3 -m agent voice-setup --update-agent          # describes the change; needs ELEVENLABS_AGENT_ID
python3 -m agent voice-setup --update-agent --yes    # sends it
```

Create and update send the same configuration. `--create-agent` and `--update-agent` cannot be combined (update would patch the old agent): create, set `ELEVENLABS_AGENT_ID` to the printed id, then update. An update changes only the fields it sends; on a live check the voice id, tools and built-in settings were left as they were.

## What the phone agent says

- **Opening:** one short statement and then it waits, for example: "Hello, this is an automated assistant calling for Northbridge Lettings about the dishwasher repair. This call is recorded." It does not ask the person to confirm who they are. The job comes from the call's `job` fact (cut to 80 characters at a word), else "a maintenance job"; the objective is an instruction and is never read out as the topic. The agency name comes from the case (a sender's name or a sign-off such as "Kind regards, Northbridge Lettings"), else "the letting agency".
- **During the call:** one or two short sentences per turn, one question at a time, it stops when interrupted, and it offers a colleague's callback if the person cannot talk. It writes plain words only (no bracketed tags such as `[sad]`).
- **Voice:** a non-expressive English model (`eleven_flash_v2`, expressive mode off). The expressive models read stage directions aloud.
- **Limits:** a call ends by itself after 3 minutes (the agent says "A colleague will follow up. Goodbye."), and the phone stops ringing after 30 seconds (`call_ring_timeout_s`).
- **Voicemail:** if a machine answers, the standard message plays: only the agency name and the job, no objective, price or personal detail. The outcome is `no_answer`.
- **Someone phones the number back:** every field has a spoken default ("the letting agency", "a maintenance job"), and the agent says this is an automated line that cannot take requests and asks them to contact the agency.
- **Dates:** `confirmed_date` is what was said ("Tuesday morning"). `confirmed_date_iso` is filled only when an exact calendar date was given, and is empty otherwise: a relative day is never turned into a date.
- **Outcome after the call** (one of): `confirmed`, `declined`, `no_answer` (nobody picked up or only voicemail), `callback_requested`, `needs_human`, `unclear` (a person answered but gave no usable answer). A call that a person answered is never `no_answer`.

## What a live call needs

| Piece | Why | Variables |
|---|---|---|
| ElevenLabs account on a plan that includes phone calls | runs the voice agent (speech-to-text, the language model, text-to-speech, turn-taking) | `ELEVENLABS_API_KEY`, `ELEVENLABS_AGENT_ID` |
| A Twilio account and a Twilio phone number | the telephone line: ElevenLabs places the call through it | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN` (used once, by `voice-setup --import-number`) |
| The number imported into ElevenLabs | gives the agent a line to dial from | `ELEVENLABS_PHONE_NUMBER_ID` (printed by `voice-setup`) |

Notes:
- A Twilio **trial** account can only call numbers you have verified in Twilio, and plays a short trial message before the call connects. That is enough for a demo to your own phone.
- ElevenLabs accepts a purchased Twilio number (inbound and outbound) or a verified caller ID (outbound only).
- Prefer a Twilio API key (SID and secret) over the account token if you have one.
- No Twilio? A SIP trunk from another carrier also works with ElevenLabs, but this repo's `voice-setup` only imports Twilio numbers.

## Demo call

Use a phone you control and say so to whoever answers. Keep the number out of every committed file (`DEMO_CALL_NUMBER` in your own `.env` is a reminder, the code does not read it), build a case whose provider's phone number is that number, run with `--calls elevenlabs`, then `calls collect`. Synthetic case numbers (07700 900xxx) are unreachable test numbers.

## Not done

- Inbound calls (a tenant phoning the agency) are not handled.
- Text-to-speech replies and voicemail drops are not used.
- The live path (real STT, real call) has only been tested against mocked HTTP.
- Calling hours and the run cap are checked in the runner and again inside the dialer; dry runs skip the hours check, so they do not rehearse an out-of-hours hold.
- Voicemail uses ElevenLabs' built-in detection only; Twilio's own machine detection is not turned on.
- `calls collect` rewrites `decision.json` without a lock, so run it when no `run` is writing the same output folder.
