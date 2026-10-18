"""Command-line interface for an auditable, small-scale log-value analysis."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path

from .analysis import Event, score_templates
from .evaluate.redundancy import run_redundancy_experiment
from .features.extract import build_feature_matrix
from .parsing.drain import DrainMiner
from .parsing.formats import read_text_log
from .report import write_report
from .provenance import atomic_json, atomic_text, write_run_metadata
from .static.python_rules import findings_as_dicts, scan_python


def _read_events(path: Path) -> list[Event]:
    if not path.is_file():
        raise ValueError(f"input file does not exist: {path}")
    if path.suffix == ".jsonl":
        rows = []
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip():
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError as error:
                    raise ValueError(f"invalid JSON on line {number}") from error
    elif path.suffix == ".csv":
        with path.open(newline="") as file:
            rows = list(csv.DictReader(file))
    else:
        raise ValueError("input must be .jsonl or .csv")
    try:
        events = [Event(message=row["message"], label=int(row["label"]), event_id=str(row.get("id", ""))) for row in rows]
    except (KeyError, TypeError, ValueError) as error:
        raise ValueError("every row needs message and binary label columns") from error
    if not events:
        raise ValueError("input contains no events")
    if any(not isinstance(event.message, str) or not event.message.strip() for event in events):
        raise ValueError("every message must be a non-empty string")
    return events


def _write_metrics(path: Path, metrics: list) -> None:
    with io.StringIO(newline="") as file:
        writer = csv.DictWriter(file, fieldnames=["template", "frequency", "fault_frequency", "auc", "mutual_information", "chi_square"])
        writer.writeheader()
        writer.writerows(metric.__dict__ for metric in metrics)
        content = file.getvalue()
    atomic_text(path, content)


def _write_json(path: Path, data: object) -> None:
    atomic_json(path, data)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Measure per-template association with labelled failures.")
    parser.add_argument("--version", action="version", version="%(prog)s 0.1.0")
    subcommands = parser.add_subparsers(dest="command", required=True)
    analyze = subcommands.add_parser("analyze", help="score JSONL or CSV labelled events")
    analyze.add_argument("input", type=Path)
    analyze.add_argument("--output", type=Path, required=True)
    redundancy = subcommands.add_parser("redundancy", help="run E2 using a temporal split")
    redundancy.add_argument("input", type=Path)
    redundancy.add_argument("--output", type=Path, required=True)
    parse = subcommands.add_parser("parse", help="mine templates from a plain-text log")
    parse.add_argument("input", type=Path)
    parse.add_argument("--output", type=Path, required=True)
    scan = subcommands.add_parser("scan-python", help="run conservative Python logging checks")
    scan.add_argument("input", type=Path)
    scan.add_argument("--output", type=Path, required=True)
    report = subcommands.add_parser("report", help="write a Markdown report from labelled events")
    report.add_argument("input", type=Path)
    report.add_argument("--output", type=Path, required=True)
    for command in (analyze, redundancy, parse, scan, report):
        command.add_argument("--run-metadata", type=Path, help="write hashes and runtime metadata for this run")
    args = parser.parse_args(argv)
    try:
        if args.command == "parse":
            miner = DrainMiner()
            for line in read_text_log(args.input):
                miner.add(line.message)
            results = [result.__dict__ for result in miner.results()]
            _write_json(args.output, results)
            message = f"mined {len(results)} templates → {args.output}"
        elif args.command == "scan-python":
            findings = findings_as_dicts(scan_python(args.input))
            _write_json(args.output, findings)
            message = f"found {len(findings)} static findings → {args.output}"
        else:
            events = _read_events(args.input)
            metrics = score_templates(events)
            if args.command == "analyze":
                _write_metrics(args.output, metrics)
                message = f"scored {len(metrics)} templates → {args.output}"
            elif args.command == "redundancy":
                result = run_redundancy_experiment(build_feature_matrix(events))
                _write_json(args.output, result.__dict__)
                message = f"completed temporal redundancy experiment → {args.output}"
            else:
                write_report(args.output, metrics, str(args.input))
                message = f"wrote report → {args.output}"
        if args.run_metadata:
            write_run_metadata(args.run_metadata, args.command, args.input, [args.output])
        print(message)
        return 0
    except (OSError, UnicodeError, ValueError) as error:
        print(f"logvalue: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
