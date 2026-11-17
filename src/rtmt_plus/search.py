"""Streaming search for CUCM/RTMT text traces, with no external dependencies."""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
import gzip
import json
import re
from typing import Iterator

# Generic timestamps; exact formats vary by CUCM release.
TIMESTAMP = re.compile(
    r"(?P<ts>\d{4}[-/]\d{2}[-/]\d{2}[ T]\d{2}:\d{2}:\d{2}(?:[.,]\d{1,6})?)"
)
CALL_ID = re.compile(r"(?i)\b(?:call[-_ ]?id|globalcallid|callidentifier)\s*[:=]\s*([\w.@-]+)")
SUPPORTED_SUFFIXES = (".log", ".txt", ".trace", ".out", ".gz")

@dataclass(frozen=True)
class Match:
    path: str
    line: int
    timestamp: str | None
    call_id: str | None
    text: str

    def to_dict(self) -> dict:
        return asdict(self)

def parse_timestamp(line: str) -> datetime | None:
    match = TIMESTAMP.search(line)
    if not match:
        return None
    raw = match.group("ts").replace("/", "-").replace(",", ".").replace("T", " ")
    try:
        return datetime.fromisoformat(raw)
    except ValueError:
        return None

def parse_call_id(line: str) -> str | None:
    match = CALL_ID.search(line)
    return match.group(1) if match else None

def iter_files(paths: list[str | Path]) -> Iterator[Path]:
    """Yield candidate files in deterministic order; skip symlinks."""
    seen: set[Path] = set()
    for item in paths:
        root = Path(item).expanduser()
        if root.is_symlink():
            continue
        if root.is_file():
            candidates = [root]
        elif root.is_dir():
            candidates = sorted(p for p in root.rglob("*") if p.is_file() and not p.is_symlink())
        else:
            raise FileNotFoundError(f"Path not found: {root}")
        for path in candidates:
            if path.suffix.lower() not in SUPPORTED_SUFFIXES:
                continue
            resolved = path.resolve()
            if resolved not in seen:
                seen.add(resolved)
                yield path

def search(
    paths: list[str | Path],
    query: str,
    *,
    regex: bool = False,
    ignore_case: bool = True,
    since: datetime | None = None,
    until: datetime | None = None,
    call_id: str | None = None,
    limit: int | None = 1000,
) -> Iterator[Match]:
    if not query:
        raise ValueError("Query cannot be empty")
    if limit is not None and limit < 1:
        raise ValueError("Limit must be >= 1")
    flags = re.IGNORECASE if ignore_case else 0
    pattern = re.compile(query if regex else re.escape(query), flags)
    count = 0
    for path in iter_files(paths):
        opener = gzip.open if path.suffix.lower() == ".gz" else open
        try:
            with opener(path, "rt", encoding="utf-8", errors="replace") as stream:
                for line_number, line in enumerate(stream, start=1):
                    if not pattern.search(line):
                        continue
                    timestamp = parse_timestamp(line)
                    if since is not None and (timestamp is None or timestamp < since):
                        continue
                    if until is not None and (timestamp is None or timestamp > until):
                        continue
                    identifier = parse_call_id(line)
                    if call_id is not None and identifier != call_id:
                        continue
                    yield Match(str(path), line_number, timestamp.isoformat(sep=" ") if timestamp else None, identifier, line.rstrip("\r\n"))
                    count += 1
                    if limit is not None and count >= limit:
                        return
        except (OSError, EOFError) as exc:
            raise OSError(f"Could not read {path}: {exc}") from exc

def to_json_lines(matches: Iterator[Match]) -> Iterator[str]:
    for match in matches:
        yield json.dumps(match.to_dict(), ensure_ascii=False)
