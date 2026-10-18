# Why LogValue exists

Most logging tools inspect source code. They can point out a string
interpolation or a missing field, but they cannot tell whether that log line
was useful when a system failed. LogValue makes the missing measurement
concrete: for labelled incident windows, it ranks each parameter-masked log
template by its association with failures.

The project is designed as an honest research-engineering artifact. You can run
the full synthetic demonstration locally, inspect every intermediate output,
and replace the example input with a labelled public dataset. It also makes a
useful portfolio story: data ingestion discipline, interpretable feature
engineering, leakage-aware temporal evaluation, static AST analysis, and
reproducible reporting in one small project.

The important constraint is just as valuable as the metrics: a template with
low association is only uninformative for the observed labels. It is not an
automatic deletion candidate, and correlation is not causation.
