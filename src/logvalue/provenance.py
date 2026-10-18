"""Run metadata for traceable, reproducible batch executions."""

from __future__ import annotations

import hashlib
import json
import os
import platform
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Iterable

from . import __version__


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: object) -> None:
    """Write complete JSON or leave the existing artifact untouched."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as file:
        json.dump(payload, file, indent=2, sort_keys=True)
        file.write("\n")
        temporary = Path(file.name)
    os.replace(temporary, path)


def atomic_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as file:
        file.write(content)
        temporary = Path(file.name)
    os.replace(temporary, path)


def write_run_metadata(path: Path, command: str, input_path: Path | None, outputs: Iterable[Path]) -> None:
    """Record code/runtime/input identities without copying sensitive log content."""
    artifacts = [output for output in outputs if output.exists()]
    payload = {
        "schema_version": 1,
        "created_at": datetime.now(UTC).isoformat(),
        "command": command,
        "logvalue_version": __version__,
        "python": platform.python_version(),
        "input": None if input_path is None else {"path": str(input_path), "sha256": sha256(input_path)},
        "outputs": [{"path": str(output), "sha256": sha256(output)} for output in artifacts],
    }
    atomic_json(path, payload)
