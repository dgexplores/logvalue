# Results

## Status: no public-dataset result yet

The repository deliberately makes **no empirical claim** about LogHub,
OpenStack, Hadoop, static-analysis tools, or production logging. The demo data
is synthetic and exists solely to make every command inspectable in minutes.

## Reproducible synthetic smoke test

```bash
python3 -m pip install -e '.[dev]'
make demo
```

This writes `results/report.md`, `results/demo_metrics.csv`,
`results/redundancy.json`, `results/templates.json`, and
`results/static_findings.json`.

Expected properties of the synthetic input:

| Check | Expected behaviour |
|---|---|
| Fault-specific database template | highest positive association |
| Common heartbeat template | AUC near 0.5 and MI near 0 |
| Weak-only model | lower PR-AUC than all-template model |
| Python source scanner | identifies `print` and concatenated logging |

These are software regression checks, not research findings.

## Publication gate

Before publishing a real result, record the exact archive URL, publisher
checksum, upstream revision, parser configuration, extraction accuracy, event
windowing procedure, temporal split, seed, and environment. If ground-truth
template accuracy is below 95%, stop before reporting downstream metrics, as
specified in [`PLAN.md`](PLAN.md).
