"""python3 -m agent run INPUT_DIR OUT_DIR [options]"""

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
                   help="fake (default, free); claude/anthropic, openai or auto run the tool loop; "
                        "anthropic-single is one call without tools; or module:Class")
    r.add_argument("--config", help="JSON file overriding Config values")
    r.add_argument("--now", help="treat this ISO time as 'now' (for replays)")
    r.add_argument("--timeout", type=float, help="seconds allowed per case")
    r.add_argument("--deadline", type=float, help="seconds allowed for the whole run")
    r.add_argument("--concurrency", type=int)
    r.add_argument("--resume", action="store_true", help="skip cases already decided by the model")
    rp = sub.add_parser("replay", help="cut public cases mid-history so there is a real decision to make")
    rp.add_argument("cases_dir")
    rp.add_argument("replay_dir")
    rp.add_argument("--points", type=int, default=2, help="decision points per case")
    rp.add_argument("--only", nargs="*", help="case folder names to include")
    cp = sub.add_parser("compare", help="agent decision vs what the agency did next, for a replay run")
    cp.add_argument("replay_dir")
    cp.add_argument("out_dir")
    args = p.parse_args(argv)

    if args.cmd in ("replay", "compare"):
        from agent import replay

        rows = (replay.build(Path(args.cases_dir), Path(args.replay_dir), args.points, args.only)
                if args.cmd == "replay" else replay.compare(Path(args.replay_dir), Path(args.out_dir)))
        print(json.dumps(rows, indent=2))
        return 0
    if not Path(args.input_dir).is_dir():
        print("input directory not found: %s" % args.input_dir, file=sys.stderr)
        return 2
    cfg = Config.load(Path(args.config) if args.config else None)
    overrides = {k: v for k, v in (("case_timeout_s", args.timeout), ("run_deadline_s", args.deadline),
                                   ("concurrency", args.concurrency)) if v is not None}
    cfg = dataclasses.replace(cfg, **overrides)

    summary = run_all(Path(args.input_dir), Path(args.out_dir), cfg, args.backend, args.now, args.resume)
    print(json.dumps(summary, indent=2))
    return 0 if summary["reconciled"] else 1


if __name__ == "__main__":
    sys.exit(main())
