"""Test-only backend that fails on purpose, chosen by the case id."""

from __future__ import annotations

import os
import time

from lettable.llm import FakeBackend


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
