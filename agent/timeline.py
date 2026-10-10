"""Turn a case folder (index.md, history.md, attachments/) into a Case.

Loading never raises on bad content: problems become warnings. Overview, outcome,
summary, resolution and the history link are dropped, as are Status, Completed
and Updated lines, so a recorded ending cannot reach the model.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from agent.config import Config
from agent.stt import AUDIO_SUFFIXES, Transcriber, case_keyterms, transcript_for

_EVENT_RE = re.compile(
    r"^## (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}) UTC\s*[\u2014-]+\s*event (\d+)\s*$", re.M
)
_META_RE = re.compile(r"^- \*\*(Channel|From|To):\*\*\s*(.*)$")
_ANCHOR_RE = re.compile(r"^<a id=.*</a>\s*$")
# Hold wording varies: "Waiting for Provider", "Awaiting TT response", "await T reply", "waiting for contractor".
_WAIT_RE = re.compile(
    r"\b(?:waiting (?:for|on)|awaiting|await)\s+(?:a |an |the )?(?:(?:response|reply|update) from (?:the )?)?"
    r"(landlord|LL|provider|contractor|tenant|TT|T)\b",
    re.I,
)
_WAIT_PARTY = {"ll": "landlord", "contractor": "provider", "tt": "tenant", "t": "tenant"}
_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
# Recorded endings. A Reality Test case may add Question, Task or other sections; those stay.
_DROP_HEADS = {"overview", "outcome", "summary", "resolution", "history"}
_EXPLICIT_HEADS = {
    "question", "questions", "task", "tasks", "decision point", "decision points",
    "instructions", "instruction",
}
_DROP_BULLETS = re.compile(r"^- \*\*(?:Status|Completed|Updated):\*\*.*(?:\n|$)", re.I | re.M)
_TEXT_ATTACHMENTS = {".txt", ".csv", ".json", ".eml", ".md"}
_IMAGE_TYPES = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif", ".webp": "image/webp"}
IMAGE_MAX_BYTES = 1_500_000
MAX_IMAGES = 4
# Headings that are not the public "UTC — event N" form.
_GENERIC_HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)
_DATE_IN = re.compile(r"(\d{4}-\d{2}-\d{2}(?:[ T]\d{2}:\d{2}(?::\d{2})?)?)")
_EVENTISH = re.compile(r"\b(events?|e-?mails?|calls?|sms|texts?|notes?|messages?|updates?|letters?)\b", re.I)
_EVENT_NUM = re.compile(r"\bevent\s+(\d+)\b", re.I)

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
    index_notes: str = ""  # kept index sections other than the initial request
    explicit_question: bool = False

    def cut(self, n: int) -> "Case":
        """The case as it stood after the first n events (for replay tests).

        Attachments are dropped: they cannot be tied to a point in time, and a
        later invoice or report would reveal what happened next.
        """
        return replace(self, events=self.events[:n], attachments=())

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
            party = _WAIT_PARTY.get(party, party)
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


def _parse_ts(value: str) -> Optional[datetime]:
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _generic_history(text: str) -> Optional[Tuple[List[Event], List[str]]]:
    """Other heading styles, used only when the standard 'UTC — event N' form is absent."""
    marks = list(_GENERIC_HEADING.finditer(text))
    chosen = []
    for i, m in enumerate(marks):
        title = m.group(1).strip()
        if not (_DATE_IN.search(title) or _EVENTISH.search(title)):
            continue
        if i == 0 and re.search(r"\bhistory\b", title, re.I) and not _DATE_IN.search(title):
            continue
        chosen.append(m)
    if not chosen:
        return None
    events: List[Event] = []
    warnings = ["history.md did not use the standard event headings; parsed with the generic fallback"]
    for i, m in enumerate(chosen):
        at = next(n for n, mark in enumerate(marks) if mark is m)
        nxt = marks[at + 1].start() if at + 1 < len(marks) else len(text)
        title = m.group(1).strip()
        meta = {"Channel": "", "From": "", "To": ""}
        body_lines: List[str] = []
        for line in text[m.end():nxt].splitlines():
            if _ANCHOR_RE.match(line):
                continue
            mm = _META_RE.match(line)
            if mm and not any(x.strip() for x in body_lines):
                meta[mm.group(1)] = mm.group(2).strip()
            else:
                body_lines.append(line)
        stamp = _DATE_IN.search(title)
        ts = _parse_ts(stamp.group(1).replace("T", " ")) if stamp else None
        if stamp and ts is None:
            warnings.append("event heading has an unreadable time: %s" % title[:80])
        num = _EVENT_NUM.search(title)
        channel = meta["Channel"] or ("Email" if re.search(r"e-?mail", title, re.I) else
                                       "Call" if re.search(r"\bcall\b", title, re.I) else "Note")
        events.append(Event(
            index=int(num.group(1)) if num else i + 1,
            ts=ts,
            channel=channel,
            sender=meta["From"] or "unknown",
            recipient=meta["To"] or "unknown",
            body="\n".join(body_lines).strip() or title,
        ))
    return events, warnings


def parse_history(text: str) -> Tuple[List[Event], List[str]]:
    warnings: List[str] = []
    matches = list(_EVENT_RE.finditer(text))
    if not matches:
        generic = _generic_history(text)
        if generic is not None:
            return generic
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


def _heading_key(head: str) -> str:
    return re.sub(r"\s+", " ", head.strip().lower()).rstrip(":.").strip()


def _dropped_heading(key: str) -> bool:
    return key.split(" ", 1)[0] in _DROP_HEADS


def redact_index(text: str) -> str:
    """Index text safe to show the model: drop recorded endings and status lines."""
    parts: List[str] = []
    for i, chunk in enumerate(re.split(r"(?=^## )", text, flags=re.M)):
        if i == 0:
            parts.append(_DROP_BULLETS.sub("", chunk))
            continue
        head = chunk.split("\n", 1)[0]
        if _dropped_heading(_heading_key(head[3:])):
            continue
        parts.append(_DROP_BULLETS.sub("", chunk))
    return "".join(parts)


def parse_index(text: str) -> Tuple[str, str, str, str, List[str], str, bool]:
    """Title, role, property, request, attachment names, kept notes, explicit-question flag.

    Every section is kept except Overview, Outcome, Summary, Resolution and the History link.
    Status, Completed and Updated bullets are dropped so a recorded ending cannot leak.
    """
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
    notes: List[str] = []
    explicit = False
    for sec in sections[1:]:
        head, _, body = sec.partition("\n")
        raw_head = head.strip()
        key = _heading_key(raw_head)
        if _dropped_heading(key):
            continue
        body = _DROP_BULLETS.sub("", body).strip()
        if key == "initial request":
            request = body
        elif key == "attachments":
            names = [Path(link).name for _, link in _LINK_RE.findall(body)]
        elif body:
            notes.append("## %s\n\n%s" % (raw_head, body))
        if key in _EXPLICIT_HEADS:
            explicit = True
    note_text = "\n\n".join(notes)
    if not explicit and re.search(r"\?", "\n".join((title, request))):
        explicit = True
    return title, role, prop, request, names, note_text, explicit


def _read_pdf_text(path: Path, limit: int) -> Optional[str]:
    try:
        import pypdf  # optional dependency

        reader = pypdf.PdfReader(str(path))
        text = "\n".join((page.extract_text() or "") for page in reader.pages[:10])
        return text.strip()[:limit] or None
    except Exception:
        return None


def load_case(folder: Path, cfg: Optional[Config] = None, transcriber: Optional[Transcriber] = None) -> Case:
    """Load a case. Audio files are transcribed only when a transcriber is given."""
    cfg = cfg or Config()
    folder = Path(folder)
    warnings: List[str] = []
    title = role = prop = request = ""
    index_names: List[str] = []
    index_notes = ""
    explicit_question = False
    events: List[Event] = []

    idx = folder / "index.md"
    if idx.is_file():
        try:
            title, role, prop, request, index_names, index_notes, explicit_question = parse_index(
                _read_capped(idx, cfg.max_file_bytes))
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
    files = [f for d in (folder / "attachments", folder) if d.is_dir() for f in sorted(d.iterdir())]
    keyterms: Optional[List[str]] = None
    for f in files:
        if f.is_symlink() or not f.is_file() or f.name in seen:
            continue
        suffix = f.suffix.lower()
        if f.parent == folder and suffix not in AUDIO_SUFFIXES:
            continue  # the case's own files (index.md, history.md, ...); only audio is also read from the top level
        if suffix == ".pdf":
            text = _read_pdf_text(f, cfg.pdf_chars)
        elif suffix in _TEXT_ATTACHMENTS:
            try:
                text = _read_capped(f, cfg.max_file_bytes).strip()[:cfg.attachment_chars] or None
            except Exception:
                text = None
        elif suffix in AUDIO_SUFFIXES:
            text = None
            if transcriber is not None:
                if keyterms is None:
                    keyterms = case_keyterms(prop, title, [e.body for e in events])
                text = transcript_for(f, transcriber, cfg, keyterms)
        else:
            text = None
        seen.add(f.name)
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
        index_notes=index_notes,
        explicit_question=explicit_question,
    )


def render_case(case: Case, max_chars: int, body_cap: int = 1500) -> str:
    """Plain text for the model. Keeps the first events and as many of the latest as fit."""
    head = [
        "Case %s: %s" % (case.case_id, case.title or "(no title)"),
        "Raised by: %s" % (case.source_role or "unknown"),
        "Property: %s" % (case.property or "unknown"),
        "Initial request: %s" % (case.request or "(none)"),
    ]
    if case.index_notes:
        head += ["", case.index_notes]
    if case.attachments:
        head.append("Attachments:")
        for a in case.attachments:
            if a.text:
                head.append("- %s (text): %s" % (a.name, a.text))
            elif Path(a.name).suffix.lower() in _IMAGE_TYPES:
                head.append("- %s (image)" % a.name)
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


def case_images(folder: Path, max_bytes: int = IMAGE_MAX_BYTES, limit: int = MAX_IMAGES) -> List[Dict[str, str]]:
    """PNG/JPG/GIF/WEBP files as size-capped base64 blocks for Claude. Never raises."""
    found: List[Dict[str, str]] = []
    try:
        paths = sorted(p for p in Path(folder).rglob("*") if p.is_file() and not p.is_symlink())
    except OSError:
        return found
    for path in paths:
        media = _IMAGE_TYPES.get(path.suffix.lower())
        if not media:
            continue
        try:
            if path.stat().st_size <= 0 or path.stat().st_size > max_bytes:
                continue
            data = base64.standard_b64encode(path.read_bytes()).decode("ascii")
        except OSError:
            continue
        found.append({"name": path.name, "media_type": media, "data": data})
        if len(found) >= limit:
            break
    return found
