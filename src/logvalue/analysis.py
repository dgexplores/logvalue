"""Per-template association metrics without hidden model dependencies."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable

from .templates import template_for


@dataclass(frozen=True)
class Event:
    """One labelled observation; label 1 denotes a faulty event."""

    message: str
    label: int
    event_id: str = ""


@dataclass(frozen=True)
class TemplateMetric:
    template: str
    frequency: int
    fault_frequency: int
    auc: float
    mutual_information: float
    chi_square: float


def _binary_auc(scores: list[int], labels: list[int]) -> float:
    positives = sum(labels)
    negatives = len(labels) - positives
    if not positives or not negatives:
        return 0.5
    wins = ties = 0
    for score, label in zip(scores, labels):
        if label != 1:
            continue
        for other_score, other_label in zip(scores, labels):
            if other_label != 0:
                continue
            if score > other_score:
                wins += 1
            elif score == other_score:
                ties += 1
    return (wins + 0.5 * ties) / (positives * negatives)


def _mutual_information(present: list[int], labels: list[int]) -> float:
    total = len(labels)
    joint = Counter(zip(present, labels))
    px = Counter(present)
    py = Counter(labels)
    return sum(
        (count / total) * math.log((count * total) / (px[x] * py[y]))
        for (x, y), count in joint.items()
        if count
    )


def _chi_square(present: list[int], labels: list[int]) -> float:
    a = sum(x == 1 and y == 1 for x, y in zip(present, labels))
    b = sum(x == 1 and y == 0 for x, y in zip(present, labels))
    c = sum(x == 0 and y == 1 for x, y in zip(present, labels))
    d = sum(x == 0 and y == 0 for x, y in zip(present, labels))
    denominator = (a + b) * (c + d) * (a + c) * (b + d)
    return 0.0 if not denominator else len(labels) * (a * d - b * c) ** 2 / denominator


def score_templates(events: Iterable[Event]) -> list[TemplateMetric]:
    """Score presence of each template against binary event labels.

    Each input row is one labelled event/window. For raw line-level data, callers
    should first aggregate messages into incident or trace windows.
    """
    raw_rows = list(events)
    if not raw_rows:
        raise ValueError("at least one event is required")
    grouped: dict[str, list[Event]] = defaultdict(list)
    for index, event in enumerate(raw_rows):
        grouped[event.event_id or f"row-{index}"].append(event)
    rows = [grouped[event_id] for event_id in sorted(grouped)]
    labels = [int(group[0].label) for group in rows]
    if any(label not in (0, 1) for label in labels):
        raise ValueError("labels must be 0 (normal) or 1 (faulty)")
    if any(any(event.label != group[0].label for event in group) for group in rows):
        raise ValueError("each event_id must have one binary label")
    templates = [set(template_for(event.message) for event in group) for group in rows]
    metrics: list[TemplateMetric] = []
    for candidate in sorted(set().union(*templates)):
        present = [int(candidate in event_templates) for event_templates in templates]
        metrics.append(TemplateMetric(
            template=candidate,
            frequency=sum(present),
            fault_frequency=sum(x and y for x, y in zip(present, labels)),
            auc=_binary_auc(present, labels),
            mutual_information=_mutual_information(present, labels),
            chi_square=_chi_square(present, labels),
        ))
    return sorted(metrics, key=lambda metric: (-metric.mutual_information, -metric.auc, metric.template))
