"""Small deterministic template miner suitable for a reproducible Phase-0 MVP."""

from __future__ import annotations

from collections import Counter

from .masking import mask_parameters


def template_for(message: str) -> str:
    """Return a stable, parameter-masked template for one log message."""
    return mask_parameters(message)


def mine_templates(messages: list[str]) -> Counter[str]:
    """Count canonical templates from raw log messages."""
    return Counter(template_for(message) for message in messages)
