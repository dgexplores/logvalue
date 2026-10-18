"""E2: compare all template features with individually weak features only."""

from __future__ import annotations

from dataclasses import dataclass

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score

from ..features.extract import FeatureMatrix


@dataclass(frozen=True)
class RedundancyResult:
    all_pr_auc: float
    weak_only_pr_auc: float
    weak_template_count: int
    train_events: int
    test_events: int


def _template_auc(column: list[int], labels: list[int]) -> float:
    positives = sum(labels)
    negatives = len(labels) - positives
    if not positives or not negatives:
        return 0.5
    wins = ties = 0
    for score, label in zip(column, labels):
        if label:
            for other_score, other_label in zip(column, labels):
                if not other_label:
                    wins += score > other_score
                    ties += score == other_score
    return (wins + 0.5 * ties) / (positives * negatives)


def _pr_auc(train_x: list[list[int]], train_y: list[int], test_x: list[list[int]], test_y: list[int]) -> float:
    if len(set(train_y)) < 2 or len(set(test_y)) < 2:
        raise ValueError("temporal train and test folds each need normal and faulty events")
    model = LogisticRegression(random_state=42, max_iter=500, class_weight="balanced")
    model.fit(train_x, train_y)
    return float(average_precision_score(test_y, model.predict_proba(test_x)[:, 1]))


def run_redundancy_experiment(matrix: FeatureMatrix, weak_auc_threshold: float = 0.55) -> RedundancyResult:
    """Use an earlier/later 70/30 split; feature selection sees training only."""
    boundary = max(1, int(len(matrix.rows) * 0.7))
    train_x, test_x = matrix.rows[:boundary], matrix.rows[boundary:]
    train_y, test_y = matrix.labels[:boundary], matrix.labels[boundary:]
    if not test_x:
        raise ValueError("at least four event windows are required")
    columns = list(zip(*train_x))
    weak_indices = [index for index, column in enumerate(columns) if abs(_template_auc(list(column), train_y) - 0.5) < weak_auc_threshold - 0.5]
    if not weak_indices:
        raise ValueError("no weak templates found in the training split")
    weak_train = [[row[index] for index in weak_indices] for row in train_x]
    weak_test = [[row[index] for index in weak_indices] for row in test_x]
    return RedundancyResult(
        all_pr_auc=_pr_auc(train_x, train_y, test_x, test_y),
        weak_only_pr_auc=_pr_auc(weak_train, train_y, weak_test, test_y),
        weak_template_count=len(weak_indices),
        train_events=len(train_y),
        test_events=len(test_y),
    )
