"""Test-only backend that fails on purpose, chosen by the case id."""

from __future__ import annotations

import os
import time

from agent.llm import FakeBackend


class ChaosBackend(FakeBackend):
    def propose(self, case, now, cfg):
        cid = case.case_id
        if cid.startswith("crash"):
            os._exit(13)
        if cid.startswith("hang"):
            time.sleep(60)
        if cid.startswith("raise"):
            raise RuntimeError("model exploded")
        if cid.startswith("junk"):
            return {"action": "DELETE_EVERYTHING", "reason": "x", "confidence": 1}
        return super().propose(case, now, cfg)


class FlakyBackend(FakeBackend):
    """Fails the first time it sees a case whose title says FLAKY, then works (state in LETTABLE_FLAKY_DIR)."""

    def propose(self, case, now, cfg):
        if "FLAKY" in case.title:
            marker = os.path.join(os.environ["LETTABLE_FLAKY_DIR"], "seen-%s" % case.case_id)
            if not os.path.exists(marker):
                open(marker, "w").close()
                raise RuntimeError("transient failure")
        return super().propose(case, now, cfg)
