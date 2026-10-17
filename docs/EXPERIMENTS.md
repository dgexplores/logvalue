# Experimental Design

Five experiments. Each states its question, method, output, and failure mode.

---

## E0 — Template mining accuracy

**Question:** can templates be extracted accurately enough that everything
downstream is trustworthy?

**Method:** Drain++ (He et al., ICSE 2020) with parameter masking. Evaluate
against LogHub's ground-truth `HDFS_templates.csv`.

**Output:** extraction accuracy, plus the confusion breakdown for missed
splits and over-merges.

**Failure mode:** below 95%, all downstream metrics are uninterpretable. This
is the Phase 0 gate — the experiment exists to be able to fail early.

---

## E1 — Per-template discriminative power

**Question:** which log templates actually carry information about failures?

**Method.** Per template *t*, over labelled events:

- **AUC** — primary. `P(score(faulty, t) > score(normal, t))`, correct under
  class imbalance where accuracy does not.
- **Mutual information** `I(t; fault)` — reported in nats, directly interpretable.
- **χ²** — classical, familiar to reviewers, gives a p-value.

Reported alongside: firing frequency, to distinguish *rare and informative* from
*constant and uninformative*.

**Output:**

- Distribution of per-template AUC (expect a large mass near 0.5)
- Templates ranked by information content
- **A measured count of diagnostically worthless log lines in a real system**

That last figure does not exist in the literature. It is the first concrete
result this project intends to produce.

**Discipline:** every number carries its extraction-accuracy context. A
discriminative-power figure computed on templates mined at 88% accuracy is not
the same claim as one computed at 97%, and must not be presented as if it were.

---

## E2 — The redundancy gap

**Question:** can a model achieve high accuracy using only templates that are
individually worthless?

**Method.**

1. Train on **all** templates → `A_all`
2. Train on **only** templates with per-template AUC < 0.55 → `A_worthless`
3. Report `A_all − A_worthless` with a confidence interval

**Interpretation.**

| Result | Meaning |
|---|---|
| `A_worthless` ≈ `A_all` | Signal lives in combination and ordering, not individual lines. Per-feature metrics are the only lens that exposes this. |
| `A_worthless` ≪ `A_all` | A minority of templates carry the signal; the rest are deletable with evidence. |

**Why this matters.** Aggregate accuracy flatters useless logs — a model can hit
99% while every individual feature is noise. Prior work reports aggregate
metrics and is structurally blind to it. This is the experiment that justifies
the ML framing over a linter framing.

**Guard:** feature selection must use **training data only**. Selecting
templates by AUC on the full dataset is leakage and would inflate `A_worthless`.

---

## E3 — Static-analysis correlation

**Question:** does a static analyzer's score predict a log's runtime value?

This tests the field's unvalidated core assumption: that source anti-patterns
correspond to production log quality.

**Method.**

1. 20 AST-based anti-pattern rules covering:
   - LCAnalyzer's 6 classes (Duplicated logs, Temporal inconsistency, Wrong
     verbosity level, Nullable object, Malformed output, Explicit cast)
   - Atlan's L-series categories (format, level, traceback, security,
     performance, config, print)
   - Defects4Log's 7 defect classes (readability, variable issues, level
     misuse, semantic inconsistency, sensitive-data leak, insufficient
     information, performance)
2. Run over the same systems
3. Correlate static score with E1's runtime discriminative power (Spearman —
   scores are ordinal, not Gaussian)
4. Separately: precision/recall against `Defects4Log`'s 164 verified defects

**Output:** correlation with confidence interval; comparison of measured
precision against the field's claimed ~60%.

**Both outcomes are publishable.** A weak correlation is evidence that twenty
tools generate false signal at scale. A strong correlation empirically validates
an assumption nobody has tested.

---

## E4 — Paired-run validation *(external ground truth)*

**Question:** do the per-template findings hold against controlled,
paired-run failure data?

**Method.** The `dessertlab/Fault-Injection-Dataset` OpenStack campaigns provide
911 tests across three workloads (Nova 439, Cinder 269, Neutron 203), each with:

- `round_1` — faulty
- `round_2` — fault-free
- `Fault_Type`, `Component`, `Class`, `Function`, `Fault_Point`
- Zipkin trace JSON and a `trigger_log` fault-activation timestamp

Same test, run with and without a fault. This is a controlled experiment the
project does not have to construct.

**Analysis.**

1. Per-template AUC for discriminating `round_1` from `round_2`
2. Per-fault-type: which templates gain information specifically
3. Recovery of the spurious/missing anomaly labels from `LCS_with_VMM.tsv`,
   which separates anomalies that were logged but not real from anomalies that
   were real but not logged

**Output:** precision/recall against externally-defined ground truth — the
measurement the entire log-analysis field lacks.

---

## ML rigor checklist

Applied to every experiment. These are the first things an ML reviewer probes.

| Commitment | Rationale |
|---|---|
| **Temporal splits, never random** | Log data is sequential. Random splits leak future information backwards. Train on earlier time, test on later. |
| **PR-AUC, never accuracy** | Faults are 1–5% of events. Accuracy is meaningless under imbalance. |
| **Trivial baseline always reported** | An always-normal classifier. If the model does not beat it, say so. |
| **Fixed seeds; variance across seeds reported** | Single-run numbers are not results. |
| **Held-out test set untouched** | Touched once, at final evaluation. |
| **Feature selection inside the fold** | Selecting features on the full dataset is leakage. |
| **Causal language avoided** | Correlation is reported as correlation. MTTR-style claims would be confounded by severity and are out of scope. |
| **Extraction accuracy reported with every metric** | Downstream numbers inherit template-mining error. |

---

## Deliberate scope exclusions

Stated so omissions read as decisions rather than gaps.

- **Deep sequence models.** Frequency baseline → gradient boosting →
  permutation importance is sufficient and interpretable. A sequence model is
  optional stretch work only.
- **Cost optimisation.** Storage-cost estimation is secondary to diagnostic
  value. Not this project's thesis.
- **Multi-logger library comparison.** pin/winston/zap/slog are equivalent once
  structured. Not a research question.
- **Real-time / streaming.** Batch analysis only.