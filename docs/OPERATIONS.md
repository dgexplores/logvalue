# Operations guide

## Supported production workflow

LogValue is designed as a stateless batch job. A scheduler exports an approved,
labelled incident-window file, runs one CLI command in a restricted container,
and persists only the output artifacts and run metadata. It is not a log
collector, SIEM, hosted multi-tenant service, or automatic log-deletion tool.

## Input contract

Use UTF-8 JSONL or CSV. Every row needs:

| Field | Type | Requirement |
|---|---|---|
| `id` | string | incident/trace-window identifier; identical IDs form one window |
| `message` | string | non-empty raw log message |
| `label` | integer | `0` for normal, `1` for faulty |

Rows for the same `id` must have the same label. Labels should be assigned by
an approved incident process, not inferred by LogValue.

## Container run

```bash
docker build -t logvalue:0.1.0 .
docker run --rm \
  --read-only \
  --tmpfs /tmp \
  --user "$(id -u):$(id -g)" \
  --mount type=bind,src="$PWD/input",dst=/input,readonly \
  --mount type=bind,src="$PWD/output",dst=/output \
  logvalue:0.1.0 analyze /input/incidents.jsonl \
  --output /output/template_metrics.csv \
  --run-metadata /output/run.json
```

Use an image digest—not a floating tag—in a production scheduler. The output
directory is the only writable application mount. The `--user` override keeps
the process non-root while allowing a host-mounted output directory to be
written; in Kubernetes, set the equivalent `runAsUser` and `fsGroup` values.

## Data handling and access control

- Logs may contain secrets or personal data. Redact upstream and restrict input
  and output storage to the team approved for the data classification.
- Run metadata contains file paths and SHA-256 hashes, never copied log rows.
- Do not send raw production logs to issue trackers, CI logs, or this repository.
- Keep the container non-root, read-only, and without network access unless an
  explicitly reviewed data-fetch step needs it.

## Change management

Pin the package/image version, retain `run.json`, and review any change to
masking rules, parser configuration, labels, event windowing, or temporal split
as a methodology change. Results from different configurations are not directly
comparable.
