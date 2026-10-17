# Build Plan

Phased, gated, sequenced by risk rather than by feature. Each phase has a
**gate** — a measurement that either justifies proceeding or kills the phase.

---

## Phase 0 — Corpus acquisition *(gate)*

**Duration:** ~1 week
**Goal:** prove the datasets parse and templates extract before anything is built on them.

### Deliverables

- `scripts/download_data.py` — fetches datasets, verifies SHA256 against a
  committed manifest, extracts to `data/` (gitignored)
- `src/logvalue/parsing/formats.py` — readers for HDFS, OpenStack, Hadoop,
  Apache formats
- `src/logvalue/parsing/drain.py` — Drain++ template mining

### Why Drain++

He et al., *"Drain: An Online Log Parsing Approach with Fixed Depth Tree"*
(ICSE 2020) is the standard published algorithm for log template mining, with
loghub-2.0 (ISSTA 2024) benchmarking it as the community baseline. Implementing
it is genuine engineering — per-dataset formats are incompatible — and it is the
correct citation rather than an ad-hoc regex.

Parameter masking (UUIDs, IPs, hex, numbers, quoted strings, URLs, paths) is
part of the implementation, not an afterthought; without it, extraction accuracy
collapses.

### Gate

> **Template extraction accuracy > 95% against LogHub's ground-truth
> `HDFS_templates.csv`.**

If this fails, stop. Every downstream metric inherits template mining error, and
the project's core measurement becomes uninterpretable.

This gate is deliberately first and deliberately cheap. It costs one week to
learn whether the project is viable, rather than six.

---

## Phase 1 — Feature extraction

**Duration:** ~1 week
**Goal:** represent every template as a numeric feature vector.

### Per-template features

| Feature | Rationale |
|---|---|
| frequency (log scale) | rare vs constant |
| burstiness (coefficient of variation) | periodic vs spiky |
| temporal position (mean normalized index) | where in the request lifecycle it fires |
| co-occurrence degree | how many other templates co-occur |
| sequence entropy | how predictable its neighbours are |
| novelty (first-seen offset) | config-dependent vs eternal |
| level (INFO/WARN/ERROR) | severity prior |
| service / component | context |

**Discipline:** a feature that cannot be justified mechanistically is dropped.
Feature-count inflation is the default failure mode of log-ML papers, and a
reviewer will ask "why this feature" for every column.

### Gate

Feature matrix builds over ≥5M lines without memory pressure, and every feature
has a stated justification.

---

## Phase 2 — Per-template discriminative power *(the first real result)*

**Duration:** ~2 weeks
**Gate:** a discriminable signal exists.

Measure, per template, against labelled failure events:

- **AUC** — primary. Handles imbalance correctly.
- **Mutual information** with the fault label — interpretable in nats.
- **χ²** — classical, familiar to reviewers.

### Output

- Distribution of per-template AUC across templates (expect most near 0.5)
- Templates ranked by information content
- A measured count of **diagnostically worthless log lines in a real system**

That last number does not currently exist anywhere in the literature. Producing
it is the first publishable artifact of this project.

---

## Phase 3 — The redundancy gap

**Duration:** ~1 week
**Gate:** effect survives stratification.

### Experiment

1. Train classifier on **all** templates → accuracy *A_all*
2. Train classifier using **only** templates with per-template AUC < 0.55 — the
   "worthless" set → accuracy *A_worthless*
3. If *A_worthless* ≈ *A_all*, redundancy is the norm and per-feature metrics
   are the only lens that exposes it.

### Why this is the contribution

Aggregate accuracy flatters worthless logs. A model can reach 99% while every
individual feature is noise, because the signal lives in their *combination and
ordering*. Every prior tool reports aggregate metrics and is structurally blind
to this.

This is the experiment that only makes sense under an ML framing, and it is the
reason the project is framed as feature analysis rather than as a linter.

---

## Phase 4 — Static-analysis correlation

**Duration:** ~2 weeks
**Goal:** test the field's unvalidated assumption.

1. Implement 20 static anti-pattern rules (AST-based, not regex) covering
   LCAnalyzer's 6 classes, Atlan's L-series categories, and Defects4Log's 7
   defect classes
2. Run them over the same systems
3. Correlate static score with Phase 2's runtime discriminative power
4. Report precision/recall against `Defects4Log`'s 164 verified defects

### Expected outcomes — both publishable

| Outcome | Meaning |
|---|---|
| Weak/negative correlation | Static analyzers generate false signal at scale. Justifies deletion-first thinking. |
| Strong correlation | Empirically validates the field's core assumption, which has never been done. |

Either result is worth publishing. A correlation of *r* with a confidence
interval is the deliverable.

---

## Phase 5 — Paired-run validation

**Duration:** ~1 week

Use the 911 OpenStack fault-injection tests (`round_1` faulty / `round_2`
fault-free) to validate per-template discriminative power against known fault
locations, and measure recovery of the spurious/missing anomaly labels in
`LCS_with_VMM.tsv`.

This is the only external ground truth available for the precision/recall claim.

---

## Phase 6 — Reporting

**Duration:** ~1 week

- `docs/RESULTS.md` — tables, figures, the finding
- `docs/THREATS.md` — limitations, published rather than buried
- `docs/BLOG.md` — the narrative for a general technical audience
- `make demo` — one command, number in ten minutes, on a public dataset

---

## Milestone summary

| Phase | Duration | Output | Gate |
|---|---|---|---|
| 0 Corpus | 1 wk | Drain++ + readers | **>95% template accuracy — hard stop** |
| 1 Features | 1 wk | Feature matrix | Justified features, ≥5M lines |
| 2 Discriminative | 2 wk | **First real result** | Signal exists |
| 3 Redundancy | 1 wk | Aggregate-vs-per-feature gap | Survives stratification |
| 4 Static | 2 wk | The correlation result | CI computed, stated |
| 5 Validation | 1 wk | Precision/recall | Recovers known spurious set |
| 6 Reporting | 1 wk | RESULTS + blog | — |

**~9 weeks complete.**

**Phases 0–2 alone (~4 weeks) produce one defensible finding** and are a
complete portfolio project on their own. Every subsequent phase is additive, so
the project can be stopped at any gate without finishing half of anything.

---

## Architecture

```
logvalue/
  Makefile                  make demo / results / figures / test
  pyproject.toml            Python 3.10+ floor
  CITATION.cff              dataset + tool citations (licence compliance)
  docs/                     PLAN, EXPERIMENTS, DATASETS, THREATS, RESULTS, BLOG
  src/logvalue/
    config.py               paths, constants, seeds
    parsing/
      drain.py              Drain++ template mining
      formats.py            per-dataset readers
      mask.py               parameter masking patterns
    features/extract.py     per-template feature vectors
    analysis/
      discriminative.py     AUC, mutual information, chi-squared
      redundancy.py         pairwise MI matrix, clustering
      cost.py               cardinality, bytes, storage-cost estimate
    models/
      baseline.py           frequency-only
      gbdt.py               HistGradientBoostingClassifier
      importance.py         permutation importance per template
    static/                 20 AST anti-pattern rules
    evaluate/               e0..e5 experiment entry points
  scripts/download_data.py  checksums + extraction
  tests/  figures/  data/
```

Interfaces are defined once and implemented once. No speculative backends: Phase
0 supports exactly the datasets in Phase 0.

---

## Commit strategy

Ten substantive commits forming a research trajectory. History is part of the
artefact — a reviewer reads `git log` before reading the code.

```
 1  chore: scaffold, CI, tooling
 2  feat: Drain++ template mining + accuracy eval on LogHub ground truth
 3  feat: multi-format readers (HDFS, OpenStack, Hadoop)
 4  feat: per-template feature extraction
 5  feat: per-template discriminative power (AUC / MI / chi-squared)
 6  exp: redundancy gap — aggregate vs per-feature accuracy
 7  exp: fault-injection paired-run validation (911 tests)
 8  feat: static-analyzer correlation — testing the field's assumption
 9  docs: results, method, threats to validity
10  docs: blog post
```

Not fifty chore commits — that reads as thrash.

---

## Tooling

- Python 3.10+ floor (3.14 locally; recruiters run older)
- `numpy`, `pandas`, `scikit-learn`, `scipy`, `matplotlib`, `tqdm`, `pytest`
- Datasets via `scripts/download_data.py` with SHA256 manifest — data is never
  committed, only its manifest
- GitHub Actions: tests, lint, coverage badge from day one
- Fixed seeds throughout; multiple seeds with reported variance

---

## Risks

| # | Risk | Severity | Mitigation |
|---|---|---|---|
| 1 | Template extraction accuracy too low | **Fatal** | Phase 0 gate, week 1 |
| 2 | No discriminative signal in public logs | **Fatal** | Phase 2 gate before Phase 3–4 investment |
| 3 | Source version ≠ log version | High | Pin versions, document mismatch, restrict correlation to matched pairs |
| 4 | Fault injection ≠ production distribution | High | Published in THREATS.md, stated in every result |
| 5 | Template parsing errors propagate | High | Report extraction accuracy alongside every downstream metric |
| 6 | System-level n is small (3–4) | Medium | Never conflate system-level n with line-level n |
| 7 | Class imbalance hides failure | Medium | PR-AUC always, plus trivial baseline |

Risks 1 and 2 are the fatal ones and both have early, cheap gates. That is the
entire purpose of the gate structure.