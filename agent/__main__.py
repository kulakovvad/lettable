"""python3 -m agent run|replay INPUT_DIR OUT_DIR [options]  |  calls collect OUT_DIR  |  export OUT_DIR"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path

from agent.config import Config
from agent.runner import run_all


def _voice_setup(args) -> int:
    from agent.voice_setup import create_agent, import_twilio_number

    steps = (["create the phone agent (prompt, first message, data collection)"] if args.create_agent else []) + (
        ["import Twilio number %s" % args.import_number] if args.import_number else [])
    if not steps:
        print("nothing to do: pass --create-agent and/or --import-number")
        return 2
    print("Will " + " and ".join(steps) + " on the ElevenLabs account." + ("" if args.yes else " Dry run: add --yes to do it."))
    if not args.yes:
        return 0
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        print("ELEVENLABS_API_KEY is not set", file=sys.stderr)
        return 2
    if args.create_agent:
        print("ELEVENLABS_AGENT_ID=%s" % create_agent(key))
    if args.import_number:
        sid, token = os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN")
        if not (sid and token):
            print("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are required", file=sys.stderr)
            return 2
        print("ELEVENLABS_PHONE_NUMBER_ID=%s" % import_twilio_number(key, args.import_number, sid, token))
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="agent")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="decide the next step for every case folder in INPUT_DIR")
    r.add_argument("input_dir")
    r.add_argument("out_dir")
    r.add_argument("--backend", default=os.environ.get("LETTABLE_BACKEND", "fake"),
                   help="fake (default, free); claude/anthropic, openai or auto run the tool loop; "
                        "anthropic-single is one call without tools; or module:Class")
    r.add_argument("--config", help="JSON file overriding Config values")
    r.add_argument("--now", help="treat this ISO time as 'now' (implies --as-of now)")
    r.add_argument("--as-of", choices=["last_event", "now", "later"], help="when waits are judged (default: config)")
    r.add_argument("--timeout", type=float, help="seconds allowed per case")
    r.add_argument("--deadline", type=float, help="seconds allowed for the whole run")
    r.add_argument("--concurrency", type=int)
    r.add_argument("--resume", action="store_true", help="skip cases already decided by the model")
    r.add_argument("--stt", choices=["off", "fake", "elevenlabs"],
                   help="transcribe audio files in cases (paid with elevenlabs; default: config or LETTABLE_STT)")
    r.add_argument("--calls", choices=["dry_run", "elevenlabs"], default=os.environ.get("LETTABLE_CALLS"),
                   help="dry_run (default) records calls and dials nothing; elevenlabs places them")
    c = sub.add_parser("calls", help="bring the results of placed phone calls back")
    c.add_argument("action", choices=["collect"])
    c.add_argument("out_dir")
    c.add_argument("--backend", choices=["dry_run", "elevenlabs"], default=os.environ.get("LETTABLE_CALLS", "dry_run"))
    rp = sub.add_parser("replay", help="cut finished cases at chosen points and compare with what happened next")
    rp.add_argument("input_dir")
    rp.add_argument("out_dir")
    rp.add_argument("--backend", default=os.environ.get("LETTABLE_BACKEND", "fake"))
    rp.add_argument("--points", type=int, default=3, help="decision points per case")
    rp.add_argument("--max-calls", type=int, help="cap on points run (default 30 for a paid backend)")
    rp.add_argument("--timeout", type=float)
    rp.add_argument("--concurrency", type=int)
    rp.add_argument("--config")
    ex = sub.add_parser("export", help="copy a run's results into ANSWERS/<n>/ for the submission")
    ex.add_argument("out_dir")
    ex.add_argument("--to", default="ANSWERS", help="destination folder (default: ANSWERS)")
    ex.add_argument("--force", action="store_true", help="overwrite ANSWERS/<n> folders that came from another run")
    vs = sub.add_parser("voice-setup", help="create the ElevenLabs phone agent and/or import a Twilio number")
    vs.add_argument("--create-agent", action="store_true")
    vs.add_argument("--import-number", metavar="E164", help="Twilio number to import (uses TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN)")
    vs.add_argument("--yes", action="store_true", help="actually call the API; without it only describe")
    args = p.parse_args(argv)
    if args.cmd == "voice-setup":
        return _voice_setup(args)
    if args.cmd == "export":
        from agent.export import ExportError, export

        try:
            print(json.dumps(export(Path(args.out_dir), Path(args.to), args.force), indent=2))
        except ExportError as exc:
            print("export refused: %s" % exc, file=sys.stderr)
            return 2
        return 0

    if args.cmd == "calls":
        from agent.calls import collect
        from agent.voice import make_dialer

        if not Path(args.out_dir).is_dir():
            print("output directory not found: %s" % args.out_dir, file=sys.stderr)
            return 2
        ccfg = dataclasses.replace(Config(), call_backend=args.backend)
        result = collect(Path(args.out_dir), lambda: make_dialer(args.backend, ccfg))
        print(json.dumps(result, indent=2))
        return 1 if result["errors"] else 0
    if not Path(args.input_dir).is_dir():
        print("input directory not found: %s" % args.input_dir, file=sys.stderr)
        return 2
    if args.cmd == "replay":
        from agent.replay import replay

        rcfg = Config.load(Path(args.config) if args.config else None)
        rover = {k: v for k, v in (("case_timeout_s", args.timeout), ("concurrency", args.concurrency)) if v is not None}
        rcfg = dataclasses.replace(rcfg, **rover)
        cap = args.max_calls if args.max_calls is not None else (None if args.backend == "fake" else 30)
        print(json.dumps(replay(Path(args.input_dir), Path(args.out_dir), rcfg, args.backend, args.points, cap), indent=2))
        return 0
    if args.stt:
        os.environ["LETTABLE_STT"] = args.stt  # an explicit flag (even 'off') beats the environment
    cfg = Config.load(Path(args.config) if args.config else None)
    as_of = args.as_of or ("now" if args.now else None)
    overrides = {k: v for k, v in (("case_timeout_s", args.timeout), ("run_deadline_s", args.deadline),
                                   ("concurrency", args.concurrency), ("as_of", as_of),
                                   ("stt_backend", args.stt), ("call_backend", args.calls)) if v is not None}
    cfg = dataclasses.replace(cfg, **overrides)

    summary = run_all(Path(args.input_dir), Path(args.out_dir), cfg, args.backend, args.now, args.resume)
    print(json.dumps(summary, indent=2))
    return 0 if summary["reconciled"] else 1


if __name__ == "__main__":
    sys.exit(main())
