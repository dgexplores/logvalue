"""Conservative normalisation of volatile values before template mining."""

from __future__ import annotations

import re

_RULES: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\b[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}\b"), "<UUID>"),
    (re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"), "<IP>"),
    (re.compile(r"\b0x[0-9a-fA-F]+\b"), "<HEX>"),
    (re.compile(r"https?://\S+"), "<URL>"),
    (re.compile(r"(?:^|\s)/[^\s]+"), " <PATH>"),
    (re.compile(r"(['\"]).*?\1"), "<STRING>"),
    (re.compile(r"\b\d+(?:\.\d+)?(?=[A-Za-z]+)"), "<NUM>"),
    (re.compile(r"\b\d+(?:\.\d+)?\b"), "<NUM>"),
)


def mask_parameters(message: str) -> str:
    """Replace common runtime values while preserving the event's wording."""
    masked = message.strip()
    for pattern, replacement in _RULES:
        masked = pattern.sub(replacement, masked)
    return re.sub(r"\s+", " ", masked)
