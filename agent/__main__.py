"""python3 -m agent run|replay INPUT_DIR OUT_DIR [options]"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path

from agent.config import Config
from agent.runner import run_all


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="agent")
    sub = p.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="decide the next step for every case folder in INPUT_DIR")
    r.add_argument("input_dir")
    r.add_argument("out_dir")
    r.add_argument("--backend", default=os.environ.get("LETTABLE_BACKEND", "fake"),
                   help="fake (default, free) or anthropic")
    r.add_argument("--config", help="JSON file overriding Config values")
    r.add_argument("--now", help="treat this ISO time as 'now' (for replays)")
    r.add_argument("--timeout", type=float, help="seconds allowed per case")
    r.add_argument("--deadline", type=float, help="seconds allowed for the whole run")
    r.add_argument("--concurrency", type=int)
    r.add_argument("--resume", action="store_true", help="skip cases already decided by the model")
    rp = sub.add_parser("replay", help="cut finished cases at chosen points and compare with what happened next")
    rp.add_argument("input_dir")
    rp.add_argument("out_dir")
    rp.add_argument("--backend", default=os.environ.get("LETTABLE_BACKEND", "fake"))
    rp.add_argument("--points", type=int, default=3, help="decision points per case")
    rp.add_argument("--max-calls", type=int, help="cap on points run (default 30 for a paid backend)")
    rp.add_argument("--timeout", type=float)
    rp.add_argument("--concurrency", type=int)
    rp.add_argument("--config")
    args = p.parse_args(argv)

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
    cfg = Config.load(Path(args.config) if args.config else None)
    overrides = {k: v for k, v in (("case_timeout_s", args.timeout), ("run_deadline_s", args.deadline),
                                   ("concurrency", args.concurrency)) if v is not None}
    cfg = dataclasses.replace(cfg, **overrides)

    summary = run_all(Path(args.input_dir), Path(args.out_dir), cfg, args.backend, args.now, args.resume)
    print(json.dumps(summary, indent=2))
    return 0 if summary["reconciled"] else 1


if __name__ == "__main__":
    sys.exit(main())
