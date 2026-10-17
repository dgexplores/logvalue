# Data directory

**Empty by design.** Datasets are downloaded on demand and never committed.

Fetched via:

```bash
python3 scripts/download_data.py --list     # show available datasets
python3 scripts/download_data.py --minimal  # OpenStack + HDFS_v1  (~250 MB)
python3 scripts/download_data.py --all      # full labelled set      (~1.5 GB)
```

Every download is verified against a SHA256 manifest. A mismatch is a hard
failure.

## Licensing

Datasets here are third-party and remain under their original licences. They are
not redistributed by this repository. LogHub's terms require citing the LogHub
paper for any usage — see `../CITATION.cff` and `../docs/DATASETS.md`.

Full inventory, provenance and integrity policy: `../docs/DATASETS.md`.