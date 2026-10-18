"""Convert event-level log messages into an interpretable sparse matrix."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from ..analysis import Event
from ..templates import template_for


@dataclass(frozen=True)
class FeatureMatrix:
    event_ids: list[str]
    labels: list[int]
    templates: list[str]
    rows: list[list[int]]


def build_feature_matrix(events: Iterable[Event]) -> FeatureMatrix:
    """Create a binary template-presence matrix, grouped by `event_id`."""
    grouped: dict[str, list[Event]] = defaultdict(list)
    for index, event in enumerate(events):
        grouped[event.event_id or f"row-{index}"].append(event)
    event_ids = sorted(grouped)
    labels: list[int] = []
    template_sets: list[set[str]] = []
    for event_id in event_ids:
        group = grouped[event_id]
        group_labels = {event.label for event in group}
        if len(group_labels) != 1:
            raise ValueError(f"event {event_id!r} contains conflicting labels")
        labels.append(group[0].label)
        template_sets.append({template_for(event.message) for event in group})
    templates = sorted(set().union(*template_sets)) if template_sets else []
    rows = [[int(template in present) for template in templates] for present in template_sets]
    return FeatureMatrix(event_ids, labels, templates, rows)


def template_summary(matrix: FeatureMatrix) -> dict[str, int]:
    """Frequency by event window, not raw line count."""
    return dict(zip(matrix.templates, map(sum, zip(*matrix.rows)))) if matrix.rows else {}
