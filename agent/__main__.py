"""python3 -m agent run|replay INPUT_DIR OUT_DIR [options]  |  calls collect OUT_DIR  |  export OUT_DIR  |  ui OUT_DIR  |  reality CHALLENGE_DIR --out ANSWERS  |  doctor  |  grade OUT_DIR EVAL_DIR [--judge claude]"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path
from typing import Optional

from agent.config import Config
from agent.runner import run_all


def _voice_setup(args) -> int:
    from agent.voice_setup import create_agent, import_twilio_number, update_agent

    agent_id = os.environ.get("ELEVENLABS_AGENT_ID")
    if args.create_agent and args.update_agent:
        print("--create-agent and --update-agent cannot be used together: update would patch the old agent, not the new one. "
              "Create first, set ELEVENLABS_AGENT_ID to the printed id, then update.", file=sys.stderr)
        return 2
    if args.update_agent and not agent_id:
        print("ELEVENLABS_AGENT_ID is not set: nothing to update", file=sys.stderr)
        return 2
    steps = (["create the phone agent (prompt, first message, voice, data collection)"] if args.create_agent else []) + (
        ["update the existing phone agent %s with the current prompt, first message, voice and data collection" % agent_id]
        if args.update_agent else []) + (["import Twilio number %s" % args.import_number] if args.import_number else [])
    if not steps:
        print("nothing to do: pass --create-agent, --update-agent and/or --import-number")
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
    if args.update_agent:
        update_agent(key, agent_id)
        print("updated agent %s" % agent_id)
    if args.import_number:
        sid, token = os.environ.get("TWILIO_ACCOUNT_SID"), os.environ.get("TWILIO_AUTH_TOKEN")
        if not (sid and token):
            print("TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN are required", file=sys.stderr)
            return 2
        print("ELEVENLABS_PHONE_NUMBER_ID=%s" % import_twilio_number(key, args.import_number, sid, token))
    return 0


REALITY_CONFIG = Path(__file__).resolve().parent.parent / "reality.json"


def _reality_config(path: Optional[str]) -> Config:
    if path:
        return Config.load(Path(path))
    return Config.load(REALITY_CONFIG if REALITY_CONFIG.is_file() else None)


def _reality(args) -> int:
    from agent.reality import run_reality

    if not Path(args.challenge_dir).is_dir():
        print("challenge directory not found: %s" % args.challenge_dir, file=sys.stderr)
        return 2
    cfg = _reality_config(args.config)
    overrides = {k: v for k, v in (("run_deadline_s", args.deadline), ("case_timeout_s", args.timeout),
                                   ("concurrency", args.concurrency), ("call_backend", args.calls)) if v is not None}
    cfg = dataclasses.replace(cfg, **overrides)
    try:
        summary = run_reality(Path(args.challenge_dir), Path(args.out), cfg, args.backend, args.track, args.resume,
                              args.stt, args.now, log=lambda m: print(m, file=sys.stderr))
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2))
    return 0 if summary["reconciled"] else 1


def _doctor(args) -> int:
    from agent.doctor import report, run_checks

    try:
        cfg = _reality_config(args.config)
    except Exception as exc:
        print("FAIL config             %s: %s" % (args.config or REALITY_CONFIG, exc))
        return 1
    checks = run_checks(args.backend, cfg, Path(args.out), live=args.live,
                        challenge_dir=Path(args.challenge_dir) if args.challenge_dir else None, track=args.track)
    print(report(checks))
    return 1 if any(c.status == "fail" for c in checks) else 0

def _grade(args) -> int:
    from agent.grade import grade
    from agent.llm import make_backend

    for d in (args.out_dir, args.eval_dir):
        if not Path(d).is_dir():
            print("directory not found: %s" % d, file=sys.stderr)
            return 2
    judge = None
    if args.judge:
        judge = make_backend(args.judge, Config.load(Path(args.config) if args.config else None))
    print(json.dumps(grade(Path(args.out_dir), Path(args.eval_dir), judge), indent=2))
    return 0


def _voice_test(args) -> int:
    from agent import voice_simulate as vs

    chosen = [s for s in vs.SCENARIOS if args.only in (None, s.name)]
    if not chosen:
        print("unknown scenario %r; choose from: %s" % (args.only, ", ".join(s.name for s in vs.SCENARIOS)), file=sys.stderr)
        return 2
    if not args.live:
        for s in chosen:
            print("%-17s %s" % (s.name, s.description))
            print("    would send: %s" % json.dumps(s.body(), ensure_ascii=False)[:300])
        print("Not run. Add --live to run these against ELEVENLABS_AGENT_ID (uses ElevenLabs credits, never dials).")
        return 0
    key, agent_id = os.environ.get("ELEVENLABS_API_KEY"), os.environ.get("ELEVENLABS_AGENT_ID")
    if not (key and agent_id):
        print("ELEVENLABS_API_KEY and ELEVENLABS_AGENT_ID are required for --live", file=sys.stderr)
        return 2
    results = [vs.run_scenario(s, agent_id, key, attempts=args.attempts) for s in chosen]
    print(vs.table(results))
    vs.save(results, Path(args.out))
    print("transcripts saved in %s/" % args.out)
    return 0 if all(r.passed for r in results) else 1


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
    g = sub.add_parser("grade", help="grade a run's decisions against an eval set's <id>.expected.json rubrics")
    g.add_argument("out_dir")
    g.add_argument("eval_dir")
    g.add_argument("--judge", help="also score the reasoning with a model: claude, openai, or module:Class")
    g.add_argument("--config")
    ex = sub.add_parser("export", help="copy a run's results into ANSWERS/<n>/ for the submission")
    ex.add_argument("out_dir")
    ex.add_argument("--to", default="ANSWERS", help="destination folder (default: ANSWERS)")
    ex.add_argument("--force", action="store_true", help="overwrite ANSWERS/<n> folders that came from another run")
    ex.add_argument("--skip-incomplete", action="store_true", help="export the finished cases and list those missing ANSWER.md or REASONING.md")
    vs = sub.add_parser("voice-setup", help="create or update the ElevenLabs phone agent and/or import a Twilio number")
    vs.add_argument("--create-agent", action="store_true")
    vs.add_argument("--update-agent", action="store_true", help="apply the current configuration to ELEVENLABS_AGENT_ID")
    vs.add_argument("--import-number", metavar="E164", help="Twilio number to import (uses TWILIO_ACCOUNT_SID / TWILIO_AUTH_TOKEN)")
    vs.add_argument("--yes", action="store_true", help="actually call the API; without it only describe")
    vt = sub.add_parser("voice-test", help="test the phone agent with simulated callers (no phone; --live uses ElevenLabs credits)")
    vt.add_argument("--only", metavar="NAME", help="run one scenario")
    vt.add_argument("--live", action="store_true", help="run against ELEVENLABS_AGENT_ID; without it only list the scenarios")
    vt.add_argument("--attempts", type=int, default=1, help="tries per scenario (the simulated caller is an LLM)")
    vt.add_argument("--out", default="out-voice-test", help="where to save the transcripts")
    ui = sub.add_parser("ui", help="open a local page over a run's results (read-only, except a person's choice in review.json)")
    ui.add_argument("out_dir")
    ui.add_argument("--port", type=int, default=8765)
    ui.add_argument("--open", action="store_true", help="open the page in a browser")
    rl = sub.add_parser("reality", help="find every case under CHALLENGE_DIR at any depth and write ANSWERS/<n>/")
    rl.add_argument("challenge_dir")
    rl.add_argument("--out", default="ANSWERS")
    rl.add_argument("--track", help="track folder to run when the drop is split by track (default: %r; 'all' for every track)"
                    % "Property Management")
    rl.add_argument("--backend", default="claude", help="claude (default), openai, auto, fake, or module:Class")
    rl.add_argument("--config", help="JSON file overriding Config values (default: reality.json at the repo root)")
    rl.add_argument("--deadline", type=float, help="seconds allowed for the whole run, including passes over fallbacks")
    rl.add_argument("--timeout", type=float, help="seconds allowed per case")
    rl.add_argument("--concurrency", type=int)
    rl.add_argument("--resume", action="store_true", help="keep cases already decided by the model; redo only fallbacks")
    rl.add_argument("--stt", choices=["off", "fake", "elevenlabs"], help="default: elevenlabs when cases have audio and the key is set")
    rl.add_argument("--calls", choices=["dry_run", "elevenlabs"], help="phone calls (default dry_run: nothing is dialled)")
    rl.add_argument("--now", help="treat this ISO time as 'now'")
    dr = sub.add_parser("doctor", help="preflight: keys present, pypdf, output dir writable, optional live model call")
    dr.add_argument("challenge_dir", nargs="?", help="also check that cases can be found here")
    dr.add_argument("--backend", default="claude")
    dr.add_argument("--out", default="ANSWERS")
    dr.add_argument("--track")
    dr.add_argument("--config", help="JSON file overriding Config values (default: reality.json at the repo root)")
    dr.add_argument("--live", action="store_true", help="make one tiny model call to check the key and model name")
    args = p.parse_args(argv)
    if args.cmd == "voice-setup":
        return _voice_setup(args)
    if args.cmd == "voice-test":
        return _voice_test(args)
    if args.cmd == "ui":
        from agent.ui import serve

        if not Path(args.out_dir).is_dir():
            print("output directory not found: %s" % args.out_dir, file=sys.stderr)
            return 2
        serve(Path(args.out_dir), args.port, args.open)
        return 0
    if args.cmd == "export":
        from agent.export import ExportError, export

        try:
            print(json.dumps(export(Path(args.out_dir), Path(args.to), args.force, args.skip_incomplete), indent=2))
        except ExportError as exc:
            print("export refused: %s" % exc, file=sys.stderr)
            return 2
        return 0
    if args.cmd == "reality":
        return _reality(args)
    if args.cmd == "doctor":
        return _doctor(args)
    if args.cmd == "grade":
        return _grade(args)

    if args.cmd == "calls":
        from agent.calls import collect
        from agent.voice import make_dialer

        if not Path(args.out_dir).is_dir():
            print("output directory not found: %s" % args.out_dir, file=sys.stderr)
            return 2
        ccfg = dataclasses.replace(Config(), call_backend=args.backend)
        result = collect(Path(args.out_dir), lambda: make_dialer(args.backend, ccfg), skip_dry_run=args.backend != "dry_run")
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
