"""File helpers shared by several modules (kept apart so imports do not form a cycle)."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path


def atomic_write_bytes(path: Path, data: bytes) -> None:
    """Write to a temp file in the same folder, then rename, so a reader never sees half a file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=str(path.parent), prefix=".tmp-", suffix=path.suffix)
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def atomic_write(path: Path, text: str) -> None:
    atomic_write_bytes(path, text.encode("utf-8"))
