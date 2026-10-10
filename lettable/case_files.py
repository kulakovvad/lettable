"""Read the actual public case format without leaking summaries or future events."""
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

from pypdf import PdfReader

from .case_contracts import CaseFailure, CasePolicy, CaseSnapshot, Document, Event


EVENT = re.compile(r"^## (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d UTC) [—-] event (\d+)\s*$", re.M)
ATTACHMENT = re.compile(r"\]\((attachments/[^)]+)\)")


def safe_path(root: Path, relative: str) -> Path:
    path = (root / unquote(relative)).resolve()
    if not path.is_relative_to(root.resolve()):
        raise CaseFailure("unsafe_file_reference")
    return path


def read_text(path: Path, max_bytes=2_000_000):
    if path.stat().st_size > max_bytes:
        raise CaseFailure("file_size_limit")
    return path.read_text(encoding="utf-8")


def sections(text):
    result = {}
    matches = list(re.finditer(r"^## (.+)$", text, re.M))
    for i, match in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        result[match.group(1).strip()] = text[match.end():end].strip()
    return result


def metadata(text, name):
    match = re.search(rf"^- \*\*{name}:\*\* (.+)$", text, re.M)
    return match.group(1).strip() if match else "Not specified"


def load_case(folder: Path, policy: CasePolicy, *, through_event: int | None = None,
              as_of: datetime | None = None) -> CaseSnapshot:
    folder = folder.resolve()
    index = sections(read_text(safe_path(folder, "index.md")))
    initial = index.get("Initial request", "")
    if not initial:
        raise CaseFailure("missing_initial_request")
    text = read_text(safe_path(folder, "history.md"))
    headings = list(EVENT.finditer(text))
    if not headings:
        raise CaseFailure("invalid_history")
    events = []
    for i, heading in enumerate(headings):
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        body = re.sub(r'<a id="event-\d+"></a>\s*', "", text[heading.end():end]).strip()
        events.append(Event(id=f"event-{int(heading.group(2)):03d}",
            at=datetime.strptime(heading.group(1), "%Y-%m-%d %H:%M:%S UTC").replace(tzinfo=timezone.utc),
            channel=metadata(body, "Channel"), sender=metadata(body, "From"),
            recipient=metadata(body, "To"), text=body, source=f"history.md#{int(heading.group(2)):03d}"))
    if len({e.id for e in events}) != len(events):
        raise CaseFailure("duplicate_event_id")
    if through_event is not None:
        if through_event < 1 or f"event-{through_event:03d}" not in {e.id for e in events}:
            raise CaseFailure("invalid_cutoff")
        events = [e for e in events if int(e.id.removeprefix("event-")) <= through_event]
    if as_of is not None:
        if as_of.tzinfo is None:
            raise CaseFailure("timezone_required")
        events = [e for e in events if e.at <= as_of]
    if not events:
        raise CaseFailure("empty_snapshot")
    events.sort(key=lambda e: (e.at, e.id))
    # Evaluation time defaults to the last visible event, never the host's clock.
    at = as_of or events[-1].at
    missing, documents, references = [], [], {}
    for event in events:
        if re.search(r"\bunavailable\b|\bnot available\b", event.text, re.I):
            missing.append(f"{event.id}: referenced content unavailable; do not infer its contents")
        for relative in ATTACHMENT.findall(event.text):
            references.setdefault(relative, event.id)
    # Index attachment lists have no availability date. Never expose them at a cutoff.
    for relative, available_from in references.items():
        path = safe_path(folder, relative)
        if not path.is_file():
            missing.append(f"{relative}: referenced at {available_from} but file missing")
            continue
        if path.stat().st_size > 20_000_000:
            raise CaseFailure("file_size_limit")
        if path.suffix.lower() != ".pdf":
            missing.append(f"{relative}: unsupported attachment type")
            continue
        try:
            reader = PdfReader(path, strict=True)
            if reader.is_encrypted:
                missing.append(f"{relative}: encrypted PDF")
                continue
            if len(reader.pages) > policy.max_pdf_pages:
                raise CaseFailure("pdf_page_limit")
            pages = [page.extract_text() or "" for page in reader.pages]
        except CaseFailure:
            raise
        except Exception:
            missing.append(f"{relative}: unreadable PDF")
            continue
        if any(not page.strip() for page in pages):
            missing.append(f"{relative}: one or more pages need OCR; text extraction is incomplete")
        documents.append(Document(source=relative, available_from=available_from, pages=pages))
    property_value = metadata(index.get("Case details", ""), "Property")
    snapshot = CaseSnapshot(case_id=f"{folder.parent.name}/{folder.name}", initial_request=initial,
        property=None if property_value == "Not specified" else property_value,
        as_of=at, events=events, documents=documents, missing=missing, fingerprint="")
    serialized = snapshot.model_dump_json()
    if len(serialized) > policy.max_input_chars:
        raise CaseFailure("input_size_limit")
    snapshot.fingerprint = hashlib.sha256(serialized.encode()).hexdigest()
    return snapshot


def source_fingerprint(folder: Path, config: dict):
    """Bind replay to bytes and configuration, including attachments not yet visible."""
    digest = hashlib.sha256(json.dumps(config, sort_keys=True).encode())
    root = folder.resolve()
    files = sorted([root / "index.md", root / "history.md", *root.glob("attachments/*")])
    if len(files) > 100:
        raise CaseFailure("file_count_limit")
    total = 0
    for path in files:
        if not path.resolve().is_relative_to(root) or not path.is_file():
            raise CaseFailure("invalid_case_file")
        size = path.stat().st_size
        total += size
        if total > 50_000_000 or size > 20_000_000:
            raise CaseFailure("file_size_limit")
        digest.update(str(path.relative_to(root)).encode())
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(65536), b""):
                digest.update(chunk)
    return digest.hexdigest()
