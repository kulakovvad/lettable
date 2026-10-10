"""Retries belong around a replay-safe operation, never around an entire agent run."""
import asyncio
import random


class TransientReadError(Exception):
    """Adapters raise this only for a known transient, replay-safe read failure."""


async def retry_read(operation, *, attempts=3, timeout_seconds=5, base_delay=0.1):
    if attempts < 1 or timeout_seconds <= 0 or base_delay < 0:
        raise ValueError("Invalid retry policy")
    for attempt in range(attempts):
        try:
            return await asyncio.wait_for(operation(), timeout_seconds)
        except (TransientReadError, TimeoutError):
            if attempt == attempts - 1:
                raise
            await asyncio.sleep(base_delay * 2**attempt * random.uniform(0.75, 1.25))
