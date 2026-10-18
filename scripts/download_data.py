#!/usr/bin/env python3
"""Download a user-selected dataset artifact with mandatory SHA-256 validation.

Dataset hosts and licences change. This utility deliberately requires the
artifact URL and publisher checksum supplied by the researcher at run time;
it never treats an unverified URL as a reproducible dataset.
"""

from __future__ import annotations

import argparse
import hashlib
import shutil
import urllib.request
from pathlib import Path


CATALOG = {
    "loghub": "https://github.com/logpai/loghub",
    "openstack-fault-injection": "https://github.com/dessertlab/Fault-Injection-Dataset",
    "openstack-failure": "https://github.com/dessertlab/Failure-Dataset-OpenStack",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Download and verify an external log dataset artifact.")
    parser.add_argument("--list", action="store_true", help="show dataset provenance URLs")
    parser.add_argument("--url", help="publisher artifact URL")
    parser.add_argument("--sha256", dest="expected_sha", help="publisher-provided SHA-256")
    parser.add_argument("--output", type=Path, help="target archive path")
    args = parser.parse_args()
    if args.list:
        for name, url in CATALOG.items():
            print(f"{name}: {url}")
        return 0
    if not (args.url and args.expected_sha and args.output):
        parser.error("use --list, or provide --url, --sha256, and --output")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".part")
    with urllib.request.urlopen(args.url) as response, temporary.open("wb") as destination:
        shutil.copyfileobj(response, destination)
    actual = sha256(temporary)
    if actual.lower() != args.expected_sha.lower():
        temporary.unlink(missing_ok=True)
        raise SystemExit(f"SHA-256 mismatch: expected {args.expected_sha}, got {actual}")
    temporary.replace(args.output)
    print(f"verified {args.output} ({actual})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
