"""Strict, small readers for common plain-text log formats."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_LEVEL = re.compile(r"\b(TRACE|DEBUG|INFO|WARN|WARNING|ERROR|FATAL|CRITICAL)\b", re.I)


@dataclass(frozen=True)
class ParsedLine:
    line_number: int
    message: str
    level: str | None
    raw: str


def parse_line(raw: str, line_number: int) -> ParsedLine | None:
    """Extract severity and message without assuming a vendor-specific prefix."""
    text = raw.strip()
    if not text:
        return None
    match = _LEVEL.search(text)
    if not match:
        return ParsedLine(line_number, text, None, raw.rstrip("\n"))
    return ParsedLine(line_number, text[match.end():].lstrip(" :-"), match.group(1).upper(), raw.rstrip("\n"))


def read_text_log(path: Path) -> list[ParsedLine]:
    """Read a UTF-8 text log, retaining unrecognised lines for auditability."""
    parsed: list[ParsedLine] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
        line = parse_line(raw, number)
        if line is not None:
            parsed.append(line)
    return parsed
