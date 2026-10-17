# Threats to Validity

Published rather than buried. A limitations section that exists is evidence of
methodological rigour; its absence is evidence of inexperience.

---

## 1. Fault injection ≠ production failure distribution

**Threat:** the primary ground truth comes from injected faults. Production
failures have different frequency, duration, blast radius, and interleaving.

**Consequence:** conclusions about which log templates matter may not transfer
to organically-occurring failures.

**Mitigation:** report every fault-injection result as scoped to
fault-injection. Where a claim would generalise, say what would have to be true
for it to hold.

**Residual risk:** real. No public dataset carries organic production failures
with per-template annotations.

---

## 2. System-level sample size is small

**Threat:** line-level *n* is enormous (~27M). System-level *n* — the number of
distinct real systems — is **3 to 4** (OpenStack, HDFS, Hadoop).

**Consequence:** any claim of the form *"per-template AUC averages 0.52"* is a
statement about three systems, not about software in general. Per-template
*correlations* across those systems are likewise n=3.

**Mitigation:** never conflate line-level and system-level *n*. Report both.
Any cross-system generalisation is labelled an extrapolation, not a finding.

**Residual risk:** the single most important limitation in this project. It
bounds every claim made.

---

## 3. Template mining error propagates

**Threat:** if template extraction merges two distinct events or splits one in
two, every downstream metric is affected — discriminative power, redundancy,
correlation.

**Consequence:** a spurious AUC can be created by a mis-merge that happens to
correlate with a fault label.

**Mitigation:** the Phase 0 gate (>95% extraction accuracy) exists for this
reason. Extraction accuracy is **reported alongside every downstream metric**,
never as a footnote. Ground-truth template datasets permit direct measurement of
this error rather than estimation.

**Residual risk:** moderate, and bounded by gating rather than eliminated.

---

## 4. Source–log version mismatch

**Threat:** log datasets were captured at specific versions of HDFS, OpenStack,
and Hadoop. Analysing a different checkout introduces code that did not produce
the logs.

**Consequence:** static-analysis findings (E3) may reference code that never ran.

**Mitigation:** pin the exact upstream revision for each dataset. Restrict
correlation analysis to matched source–log pairs. Document any unavoidable
mismatch explicitly and exclude those sites from correlation rather than
reporting them with a caveat.

---

## 5. Defect-detection claims are not utility claims

**Threat:** low per-template AUC means a template is uninformative **about the
labelled fault set** — not that it is worthless in general.

**Consequence:** over-claiming deletion candidates. A template with AUC ≈ 0.5
against six fault classes may still be essential for an unlabelled failure mode.

**Mitigation:** every deletion candidate is scoped to *"uninformative about the
observed failure distribution."* No template is recommended for deletion solely
on this evidence. Human approval required; no automatic deletion, ever.

**This is the most likely way the project's conclusions could be misused**, and
the constraint is stated in every output.

---

## 6. Class imbalance

**Threat:** faults are 1–5% of events.

**Consequence:** accuracy is meaningless. A trivial always-normal classifier can
score 99%.

**Mitigation:** PR-AUC as the primary metric. The trivial baseline is reported
alongside every result, and it is stated plainly whether the model beats it.

---

## 7. Correlation is not causation

**Threat:** any relationship found between static log quality and runtime
diagnostic value is correlational.

**Mitigation:** causal language is prohibited. The project reports correlation
with confidence intervals and does not make intervention claims.

**Explicitly out of scope:** MTTR-based arguments. "Incidents with logs resolve
faster" is confounded by severity — sicker incidents produce both longer MTTR
*and* more logging. That analysis is excluded rather than reported misleadingly.

---

## 8. Unmeasured confounders in the correlation

**Threat:** templates with high information content may correlate with static
anti-patterns because both reflect system architecture — a legacy, tightly
coupled subsystem may emit both noisy logs *and* concentrated failures.

**Consequence:** the E3 correlation may reflect a shared cause rather than a
direct relationship.

**Mitigation:** report as association. Where possible, stratify by system to
check whether the relationship holds within systems rather than only between
them.

---

## 9. Dataset bias

**Threat:** LogHub systems are large, older, well-documented infrastructure —
HDFS, OpenStack, Hadoop. They do not resemble microservices, serverless, or
AI/ML pipelines.

**Consequence:** findings may not generalise to the systems people actually
maintain today.

**Mitigation:** stated explicitly. Extending coverage to contemporary
architectures is listed as future work, not quietly omitted.

---

## Summary

| # | Threat | Severity | Status |
|---|---|---|---|
| 2 | System-level n is 3–4 | **Highest** | Accepted, bounded, always reported |
| 5 | Defect ≠ uselessness | **Highest** | Constraint in every output |
| 1 | Fault injection ≠ production | High | Scoped in every claim |
| 4 | Source–log version mismatch | High | Pinned, mismatches excluded |
| 3 | Template mining error | High | Gated at >95%, reported inline |
| 6 | Class imbalance | Medium | PR-AUC + trivial baseline |
| 8 | Unmeasured confounders | Medium | Reported as association |
| 9 | Dataset bias | Medium | Stated, listed as future work |
| 7 | Correlation ≠ causation | — | Language enforced |