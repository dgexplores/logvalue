"""E3 correlation helpers with no causal interpretation."""

from __future__ import annotations

import math


def _ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index
        while end + 1 < len(ordered) and ordered[end + 1][1] == ordered[index][1]:
            end += 1
        rank = (index + end + 2) / 2
        for position in range(index, end + 1):
            ranks[ordered[position][0]] = rank
        index = end + 1
    return ranks


def spearman_correlation(static_scores: list[float], runtime_scores: list[float]) -> float:
    """Return Spearman's rho; require at least two aligned, varying observations."""
    if len(static_scores) != len(runtime_scores) or len(static_scores) < 2:
        raise ValueError("scores must be aligned and contain at least two observations")
    left, right = _ranks(static_scores), _ranks(runtime_scores)
    left_mean, right_mean = sum(left) / len(left), sum(right) / len(right)
    numerator = sum((x - left_mean) * (y - right_mean) for x, y in zip(left, right))
    left_scale = math.sqrt(sum((x - left_mean) ** 2 for x in left))
    right_scale = math.sqrt(sum((y - right_mean) ** 2 for y in right))
    if not left_scale or not right_scale:
        raise ValueError("Spearman correlation is undefined for constant scores")
    return numerator / (left_scale * right_scale)
