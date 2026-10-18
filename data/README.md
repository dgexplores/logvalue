# Data directory

**Empty by design.** Datasets are downloaded on demand and never committed.

Provenance references can be listed with:

```bash
python3 scripts/download_data.py --list
```

For reproducibility, download only an artifact that publishes a SHA-256, then
pass that URL and checksum to `scripts/download_data.py`. A mismatch is a hard
failure. The repository intentionally does not invent checksums for sources
that do not publish one.

## Licensing

Datasets here are third-party and remain under their original licences. They are
not redistributed by this repository. LogHub's terms require citing the LogHub
paper for any usage — see `../CITATION.cff` and `../docs/DATASETS.md`.

Full inventory, provenance and integrity policy: `../docs/DATASETS.md`.
