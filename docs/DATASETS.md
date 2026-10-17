# Datasets

All datasets are **publicly available**. Nothing proprietary is required. This
project is reproducible end-to-end by a third party from public sources alone —
which is the point: a research artefact nobody else can run is not an artefact.

Datasets are **downloaded, never committed**. Integrity is enforced by a
SHA256 manifest in `scripts/download_data.py`.

---

## Key find: controlled paired-run experiments

The two `dessertlab` repositories are what make this project viable. They
provide controlled experiments with ground truth — not datasets someone else
already mined.

### `dessertlab/Fault-Injection-Dataset`

**911 tests** across three fault-injection campaigns on OpenStack:

| Workload | Tests |
|---|---|
| Nova (compute) | 439 |
| Cinder (storage) | 269 |
| Neutron (network) | 203 |

Per test:

| Field | Value |
|---|---|
| `Fault_Type` | injected fault category |
| `Component` / `Class` / `Function` | **source location of the mutated statement** |
| `Fault_Point` | **the exact mutated statement** |
| `Round_1` | faulty run |
| `Round_2` | fault-free run |
| `logs/round_N/` | raw logs per subsystem, plus `trigger_log` with fault-activation timestamp |
| `trace_Test_*` | Zipkin trace JSON |

**Same test, run with and without a fault.** This is a paired design. Per-template
discriminative power can be measured against a controlled contrast rather than
inferred.

### `dessertlab/Failure-Dataset-OpenStack`

15 labelled failure modes across DEPL / NET / STO campaigns (instance, volume,
SSH, cleanup, network, no-failure).

Its `LCS_with_VMM.tsv` separates **spurious anomalies** (logged but not real) from
**missing anomalies** (real but not logged).

That distinction is this project's entire thesis, and it exists as a public
benchmark. It is the only external ground truth available for the
precision/recall claim.

---

## LogHub

`logpai/loghub` — ISSRE 2023. 19 real-world datasets, 77 GB total, 90,000+
downloads across 450+ organisations. The community benchmark idiom for log
analytics.

Labelled datasets used by this project:

| Dataset | Lines | Time span | Ground truth |
|---|---|---|---|
| `HDFS_v1` | 11,175,629 | 38.7 h | ✅ per-trace normal/anomaly + anomaly type |
| `HDFS_v3` TraceBench | 14,778,079 | ~180 h | ✅ normal/failure traces, 17 injected faults |
| `OpenStack` | 207,820 | — | ✅ normal + fault injection |
| `Hadoop` | 394,308 | — | ✅ |

Supporting datasets (unlabelled; used for scale, cardinality and cost analysis):

| Dataset | Lines | Size |
|---|---|---|
| `Spark` | 33,236,604 | 2.75 GiB |
| `HDFS_v2` | 71,118,073 | 16.06 GiB |
| `OpenSSH` | 655,146 | 70 MB |
| `Linux` | 25,567 | 2.25 MB |
| `Apache` | 56,481 | 4.9 MB |

**Planned headline scale: ~27M lines across 6 datasets, 1,822 paired runs.**

### Ground-truth templates

`HDFS_v1` ships `HDFS_templates.csv` — human-verified event templates. This is
what makes the Phase 0 gate measurable (E0) rather than a matter of opinion.

---

## `Defects4Log`

164 developer-verified real-world logging defects across 7 classes (readability,
variable issues, logging level misuse, semantic inconsistency, sensitive-data
leak, insufficient information, performance).

Used as the ground truth for E3's static-rule precision measurement — the
comparison point against the field's claimed ~60% precision.

---

## Licensing and citation obligations

**These are conditions of use, not courtesies.**

LogHub requires that any usage or distribution reference the loghub repository
URL **and** cite the LogHub paper.

| Requirement | Handling |
|---|---|
| Cite LogHub | `CITATION.cff` + README citation section |
| Reference repo URL | `CITATION.cff` |
| Cite the ISSRE'23 paper | `CITATION.cff`, README, `docs/RESULTS.md` |
| Desktoplab citation | `CITATION.cff` |
| SHA256 integrity | manifest in `scripts/download_data.py` |
| No redistribution of raw logs | downloaded on demand, `data/` gitignored |

Datasets are fetched at runtime and never committed. Nobody's licensing
conditions are violated by this repository.

---

## Integrity

Every dataset is verified against a committed SHA256 manifest at download time.
A mismatch is a hard failure, not a warning.

Rationale: silently-corrupted data producing a plausible-looking metric is the
worst failure mode this project has, and it is the one nobody notices.

---

## Disk requirements

| Scope | Download |
|---|---|
| Minimum viable (OpenStack + HDFS_v1) | ~250 MB |
| Full labelled set | ~1.5 GB |
| Including `Spark` for scale figures | ~4.3 GB |
| Everything in LogHub | 77 GB |

Phase 0 runs on the minimum scope. Large downloads are opt-in and only added
once a result justifies them.