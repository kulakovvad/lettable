from __future__ import annotations

from pathlib import Path

INDEX = """# Case {cid}: {title}

## Case details

- **Source role:** Tenant
- **Status:** Completed
- **Property:** Flat 1, 2 Test Road

## Initial request

{request}

## Overview

OVERVIEW-SECRET the work was finished and everyone was happy.

## Outcome

OUTCOME-SECRET the landlord paid the contractor.

## Attachments

No attachments are required or available for this case.
"""

EVENT = """<a id="event-{n:03d}"></a>
## {ts} UTC — event {n:03d}

- **Channel:** {channel}
- **From:** {sender}
- **To:** {to}

{body}

"""


def make_case(root: Path, cid: str, events, title="Dishwasher repair", request="Dishwasher leaks.") -> Path:
    """events: list of (ts, channel, sender, to, body)."""
    folder = Path(root) / cid
    folder.mkdir(parents=True)
    (folder / "index.md").write_text(INDEX.format(cid=cid, title=title, request=request), encoding="utf-8")
    text = "# Case %s history\n\nTotal events: %d\n\n" % (cid, len(events))
    for n, (ts, channel, sender, to, body) in enumerate(events, 1):
        text += EVENT.format(n=n, ts=ts, channel=channel, sender=sender, to=to, body=body)
    (folder / "history.md").write_text(text, encoding="utf-8")
    return folder


WAITING_LANDLORD = [
    ("2026-01-01 09:00:00", "Note", "Agency / system", "Not specified", "Request: dishwasher leaks."),
    ("2026-01-01 09:05:00", "Email", "Agency / system", "Landlord", "Can you approve a repair?"),
    ("2026-01-01 09:06:00", "Update", "Agency / system", "Not specified", "Waiting for Landlord (0 days)"),
]
