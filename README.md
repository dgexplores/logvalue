# logvalue

**Do your log statements actually carry information?**

A feature-analysis harness that measures the diagnostic value of individual log
templates against real failure ground truth — and tests whether the entire
static log-analysis field is measuring anything real.

> **Status: design phase.** No implementation yet. See [`docs/PLAN.md`](docs/PLAN.md).
> No results are published here because none exist yet. That is deliberate — this
> repository will only ever report numbers it has actually measured.

---

## The problem

More than twenty tools will tell you your logging is bad. Among them:

| Tool | What it does |
|---|---|
| Atlan `application-sdk-conformance` | L001–L020, AST-based, 100 tests, SARIF |
| `eslint-plugin-observability` | Interpolated-message rule |
| `eslint-plugin-llm-core` | Static message + structured metadata |
| `unfault.dev` | `missing_structured_logging` for Python/Rust/TS, with auto-patch |
| `thai-lint` | `print`/`console` + `if verbose:` guards |
| SonarQube 10.5 | 15 new .NET logging rules (syntax, placeholder, performance) |

**Every one of them is static.** None has runtime access. They cannot know
whether a log line ever fired, was ever searched, or ever helped a human
resolve an incident.

They all rest on one assumption:

> Anti-patterns in source code correspond to bad logs in production.

**This assumption has never been empirically validated.** In nine years of
research, LCAnalyzer reported 95% recall at **60% precision** — meaning four in
ten findings are noise — and nobody has published a correlation between static
scores and runtime diagnostic value.

This project measures it.

---

## The question

For each log template, how much information does it actually carry about system
failures — and do the tools that flag it agree with that answer?

Three findings, each of which is publishable regardless of outcome:

1. **Per-template discriminative power.** A template with AUC ≈ 0.5 fires
   identically whether or not the system is broken. It carries zero
   diagnostic information. Nobody has counted how many exist in a real system.
2. **The redundancy gap.** A classifier can reach high accuracy using only
   templates that are individually worthless, because the signal lives in their
   combination and ordering. Aggregate accuracy flatters useless logs. Prior
   work reports aggregate metrics and is structurally blind to this.
3. **Static-analysis correlation.** Does a linter's score predict a log's
   runtime value? If not, twenty tools are generating false signal at scale.

A negative result is a valid result. "Static analysis does not predict runtime
log utility" is more useful to the field than another linter.

---

## Approach in one diagram

```
   source code                          production logs
   ────────────                         ───────────────
        │                                     │
   static rules                        template mining (Drain++)
   (20 anti-patterns)                  911 paired faulty/fault-free runs
        │                                     │
   score per log site                  per-template AUC / MI / χ²
        │                                     │
        │           discriminative power       │
        ├──────────────►  per template  ◄──────┘
        │                     │
        │                     ▼
        │              redundancy analysis
        │            (MI matrix → clustering)
        │                     │
        │                     ▼
        └────────►  correlation: does static  ──► THE FINDING
                     analysis predict runtime?
```

---

## Why this is an ML problem, not a lint problem

Log templates are **features**. Discriminative power is **information gain,
AUC, χ²**. Redundancy is **mutual information between features**. Template
mining is a clustering problem with a published algorithm (Drain, ICSE'20).

This is textbook feature analysis applied at industrial scale, to a domain where
it has never been applied. The ML pipeline produces the research finding rather
than decorating it.

Model stack is deliberately conventional — frequency baseline → gradient
boosting → permutation importance. Permutation importance is the seam that
converts a trained model back into *"which log line actually mattered."*

Deep sequence models are explicitly **out of scope** unless time permits. A clean
feature analysis beats a sloppy transformer.

---

## Datasets

All public, all with verifiable provenance. Full inventory in
[`docs/DATASETS.md`](docs/DATASETS.md).

| Dataset | Scale | Ground truth |
|---|---|---|
| **OpenStack fault-injection** (dessertlab) | **911 tests × 2 paired rounds** | ✅ fault type, source location, trigger timestamp |
| **OpenStack failure analysis** (dessertlab) | 15 fault classes | ✅ **explicitly labels spurious vs missing anomalies** |
| `HDFS_v1` (LogHub) | 11.2M lines | ✅ normal/anomaly + type |
| `HDFS_v3` TraceBench (LogHub) | 14.8M lines | ✅ normal/failure traces |
| `Hadoop` (LogHub) | 394k lines | ✅ |
| `Defects4Log` | 164 developer-verified defects | ✅ |

The two `dessertlab` repositories are the key find: a **controlled paired-run
experiment** with known fault locations, and a dataset that already
distinguishes *spurious* anomalies (logged but not real) from *missing* ones
(real but not logged). That distinction is this project's entire thesis, and it
exists only as a public benchmark.

---

## Methodology commitments

These are the things an ML reviewer probes first. They are non-negotiable here.

- **Temporal splits, never random splits.** Log data is sequential. Train on
  earlier time, test on later. Random splits leak.
- **PR-AUC, never accuracy.** Faults are rare. Always report a trivial
  always-normal baseline and state plainly whether the model beats it.
- **Fixed seeds**, multiple seeds, variance reported.
- **Held-out test set** untouched until final evaluation.
- **No causal claims** from correlational evidence.
- **Threats to validity published, not buried** — see
  [`docs/THREATS.md`](docs/THREATS.md).

---

## Documentation

| Document | Contents |
|---|---|
| [`docs/PLAN.md`](docs/PLAN.md) | Build plan, architecture, milestones, gates |
| [`docs/EXPERIMENTS.md`](docs/EXPERIMENTS.md) | E0–E4 experimental design |
| [`docs/DATASETS.md`](docs/DATASETS.md) | Dataset inventory, licensing, integrity |
| [`docs/THREATS.md`](docs/THREATS.md) | Threats to validity |

## Citation

This project uses the **LogHub** datasets. Usage requires citing the LogHub
paper; see [`CITATION.cff`](CITATION.cff) and [`docs/DATASETS.md`](docs/DATASETS.md).

## License

MIT — see [`LICENSE`](LICENSE).