"""python3 -m lettable run INPUT_DIR OUT_DIR [options]"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import sys
from pathlib import Path

from lettable.config import Config
from lettable.runner import run_all


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="lettable")
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
    args = p.parse_args(argv)

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
