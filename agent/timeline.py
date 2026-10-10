"""Turn a case folder (index.md, history.md, attachments/) into a Case.

Loading never raises on bad content: problems become warnings. The summary and
outcome sections of index.md are dropped on purpose, so a recorded ending can
never reach the model.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from agent.config import Config

_EVENT_RE = re.compile(
    r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC\s*[\u2014-]+\s*event (\d+)\s*$", re.M
)
_META_RE = re.compile(r"^- \*\*(Channel|From|To):\*\*\s*(.*)$")
_ANCHOR_RE = re.compile(r"^<a id=.*</a>\s*$")
_WAIT_RE = re.compile(r"waiting for\s+(landlord|provider|tenant)", re.I)
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Who counts as a reply from the party we wait on.
_ROLES = {
    "landlord": {"landlord", "owner"},
    "provider": {"contractor", "provider", "supplier"},
    "tenant": {"tenant", "resident"},
}


@dataclass(frozen=True)
class Event:
    index: int
    ts: Optional[datetime]
    channel: str
    sender: str
    recipient: str
    body: str


@dataclass(frozen=True)
class Attachment:
    name: str
    text: Optional[str]  # None when the file is missing or unreadable


@dataclass(frozen=True)
class WaitState:
    party: str  # landlord | provider | tenant
    since: datetime
    event_index: int


@dataclass(frozen=True)
class Case:
    case_id: str
    title: str
    source_role: str
    property: str
    request: str
    events: Tuple[Event, ...]
    attachments: Tuple[Attachment, ...]
    warnings: Tuple[str, ...]

    def cut(self, n: int) -> "Case":
        """The case as it stood after the first n events (for replay tests)."""
        return replace(self, events=self.events[:n])

    def last_ts(self) -> Optional[datetime]:
        for e in reversed(self.events):
            if e.ts:
                return e.ts
        return None

    def waiting(self) -> Optional[WaitState]:
        """Who we are waiting on, from the latest status line, unless they replied since."""
        for i in range(len(self.events) - 1, -1, -1):
            e = self.events[i]
            m = _WAIT_RE.search(e.body)
            if not m or e.ts is None:
                continue
            party = m.group(1).lower()
            roles = _ROLES[party]
            if any(
                any(role in later.sender.lower() for role in roles) for later in self.events[i + 1:]
            ):
                return None
            return WaitState(party=party, since=e.ts, event_index=e.index)
        return None


def _read_capped(path: Path, cap: int) -> str:
    with open(path, "rb") as fh:
        return fh.read(cap).decode("utf-8", errors="replace")


def parse_history(text: str) -> Tuple[List[Event], List[str]]:
    warnings: List[str] = []
    matches = list(_EVENT_RE.finditer(text))
    if not matches:
        if text.strip():
            warnings.append("history.md has no recognisable events; kept as one note")
            return [Event(1, None, "Note", "unknown", "unknown", text.strip())], warnings
        return [], warnings
    events: List[Event] = []
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        meta = {"Channel": "", "From": "", "To": ""}
        body_lines: List[str] = []
        for line in text[m.end():end].splitlines():
            if _ANCHOR_RE.match(line):
                continue
            mm = _META_RE.match(line)
            if mm and not any(x.strip() for x in body_lines):
                meta[mm.group(1)] = mm.group(2).strip()
            else:
                body_lines.append(line)
        try:
            ts: Optional[datetime] = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S").replace(
                tzinfo=timezone.utc
            )
        except ValueError:
            ts = None
            warnings.append("event %s has an unreadable time" % m.group(2))
        events.append(
            Event(
                index=int(m.group(2)),
                ts=ts,
                channel=meta["Channel"] or "Note",
                sender=meta["From"] or "unknown",
                recipient=meta["To"] or "unknown",
                body="\n".join(body_lines).strip(),
            )
        )
    return events, warnings


def parse_index(text: str) -> Tuple[str, str, str, str, List[str]]:
    """Return title, source role, property, request, attachment names. Skips summary and outcome."""
    title = ""
    m = re.search(r"^# Case [^:\n]*:\s*(.+)$", text, re.M)
    if m:
        title = m.group(1).strip()
    role = prop = ""
    for key, var in (("Source role", "role"), ("Property", "prop")):
        mm = re.search(r"^- \*\*%s:\*\*\s*(.+)$" % key, text, re.M)
        if mm:
            if var == "role":
                role = mm.group(1).strip()
            else:
                prop = mm.group(1).strip()
    sections = re.split(r"^## ", text, flags=re.M)
    request = ""
    names: List[str] = []
    for sec in sections[1:]:
        head, _, body = sec.partition("\n")
        head = head.strip().lower()
        if head == "initial request":
            request = body.strip()
        elif head == "attachments":
            names = [Path(link).name for _, link in _LINK_RE.findall(body)]
    return title, role, prop, request, names


def _read_pdf_text(path: Path, limit: int) -> Optional[str]:
    try:
        import pypdf  # optional dependency

        reader = pypdf.PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages[:10])
        return text.strip()[:limit] or None
    except Exception:
        return None


def load_case(folder: Path, cfg: Optional[Config] = None) -> Case:
    cfg = cfg or Config()
    folder = Path(folder)
    warnings: List[str] = []
    title = role = prop = request = ""
    index_names: List[str] = []
    events: List[Event] = []

    idx = folder / "index.md"
    if idx.is_file():
        try:
            title, role, prop, request, index_names = parse_index(_read_capped(idx, cfg.max_file_bytes))
        except Exception as exc:
            warnings.append("index.md unreadable: %s" % exc)
    else:
        warnings.append("index.md missing")

    hist = folder / "history.md"
    if hist.is_file():
        try:
            events, w = parse_history(_read_capped(hist, cfg.max_file_bytes))
            warnings.extend(w)
        except Exception as exc:
            warnings.append("history.md unreadable: %s" % exc)
    else:
        warnings.append("history.md missing")

    attachments: List[Attachment] = []
    seen = set()
    adir = folder / "attachments"
    if adir.is_dir():
        for f in sorted(adir.iterdir()):
            if f.is_symlink() or not f.is_file():
                continue
            seen.add(f.name)
            text = _read_pdf_text(f, cfg.pdf_chars) if f.suffix.lower() == ".pdf" else None
            attachments.append(Attachment(f.name, text))
    for name in index_names:
        if name not in seen:
            attachments.append(Attachment(name, None))

    return Case(
        case_id=folder.name,
        title=title,
        source_role=role,
        property=prop,
        request=request,
        events=tuple(events),
        attachments=tuple(attachments),
        warnings=tuple(warnings),
    )


def render_case(case: Case, max_chars: int, body_cap: int = 1500) -> str:
    """Plain text for the model. Keeps the first events and as many of the latest as fit."""
    head = [
        "Case %s: %s" % (case.case_id, case.title or "(no title)"),
        "Raised by: %s" % (case.source_role or "unknown"),
        "Property: %s" % (case.property or "unknown"),
        "Initial request: %s" % (case.request or "(none)"),
    ]
    if case.attachments:
        head.append("Attachments:")
        for a in case.attachments:
            if a.text:
                head.append("- %s (text): %s" % (a.name, a.text))
            else:
                head.append("- %s (content not available)" % a.name)

    def fmt(e: Event) -> str:
        when = e.ts.strftime("%Y-%m-%d %H:%M") if e.ts else "unknown time"
        body = e.body if len(e.body) <= body_cap else e.body[:body_cap] + " [cut]"
        return "[#%d %s %s, %s -> %s] %s" % (e.index, when, e.channel, e.sender, e.recipient, body)

    lines = [fmt(e) for e in case.events]
    used = sum(len(x) + 1 for x in head)
    budget = max_chars - used
    if sum(len(x) + 1 for x in lines) > budget:
        first = lines[:3]
        rest = lines[3:]
        budget -= sum(len(x) + 1 for x in first) + 60
        tail: List[str] = []
        for x in reversed(rest):
            if budget - len(x) - 1 < 0:
                break
            tail.append(x)
            budget -= len(x) + 1
        tail.reverse()
        omitted = len(rest) - len(tail)
        lines = first + ["[... %d events omitted ...]" % omitted] + tail
    return "\n".join(head + ["", "Events, oldest first:"] + lines)
