"""Generate a provenance-first Markdown report from real command output."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from .analysis import TemplateMetric
from .evaluate.redundancy import RedundancyResult
from .provenance import atomic_text


def write_report(path: Path, metrics: list[TemplateMetric], source: str, redundancy: RedundancyResult | None = None) -> None:
    lines = [
        "# LogValue analysis report",
        "",
        f"Generated: {datetime.now(UTC).isoformat()}",
        "",
        f"Input: `{source}`",
        "",
        "> **Interpretation boundary:** metrics show association with this input's labelled failure distribution. They do not establish causation or justify automatic log deletion.",
        "",
        "## Per-template association",
        "",
        "| Template | Event frequency | Fault frequency | AUC | MI (nats) | χ² |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for metric in metrics:
        template = metric.template.replace("|", "\\|")
        lines.append(f"| `{template}` | {metric.frequency} | {metric.fault_frequency} | {metric.auc:.3f} | {metric.mutual_information:.4f} | {metric.chi_square:.3f} |")
    if redundancy is not None:
        lines.extend([
            "",
            "## Redundancy experiment (temporal split)",
            "",
            f"- Train/test windows: {redundancy.train_events}/{redundancy.test_events}",
            f"- PR-AUC, all templates: {redundancy.all_pr_auc:.3f}",
            f"- PR-AUC, weak-only templates: {redundancy.weak_only_pr_auc:.3f}",
            f"- Weak templates selected using training data only: {redundancy.weak_template_count}",
        ])
    atomic_text(path, "\n".join(lines) + "\n")
