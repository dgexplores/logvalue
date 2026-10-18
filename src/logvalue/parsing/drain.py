"""Deterministic token-tree template miner inspired by Drain's fixed-depth idea.

This is intentionally a transparent baseline, not a claim of a benchmarked
Drain++ reproduction. `evaluate_templates` makes that distinction testable.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from ..masking import mask_parameters


def _tokens(message: str) -> tuple[str, ...]:
    return tuple(mask_parameters(message).split())


@dataclass(frozen=True)
class TemplateResult:
    template: str
    count: int


class DrainMiner:
    """Cluster messages by token count and fixed token positions."""

    def __init__(self, similarity_threshold: float = 0.6) -> None:
        if not 0 < similarity_threshold <= 1:
            raise ValueError("similarity_threshold must be in (0, 1]")
        self.similarity_threshold = similarity_threshold
        self._clusters: dict[int, list[tuple[list[str], int]]] = defaultdict(list)

    def add(self, message: str) -> str:
        tokens = list(_tokens(message))
        candidates = self._clusters[len(tokens)]
        for index, (template, count) in enumerate(candidates):
            equal = sum(a == b or a == "<*>" for a, b in zip(template, tokens))
            if equal / max(1, len(tokens)) >= self.similarity_threshold:
                merged = [a if a == b else "<*>" for a, b in zip(template, tokens)]
                candidates[index] = (merged, count + 1)
                return " ".join(merged)
        candidates.append((tokens, 1))
        return " ".join(tokens)

    def results(self) -> list[TemplateResult]:
        output = [TemplateResult(" ".join(template), count) for clusters in self._clusters.values() for template, count in clusters]
        return sorted(output, key=lambda item: (-item.count, item.template))


def evaluate_templates(predicted: list[str], expected: list[str]) -> float:
    """Return exact template agreement; inputs must be aligned event-for-event."""
    if len(predicted) != len(expected) or not expected:
        raise ValueError("predicted and expected templates must be non-empty and aligned")
    return sum(left == right for left, right in zip(predicted, expected)) / len(expected)
