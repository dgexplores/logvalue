from logvalue.analysis import Event, score_templates
from logvalue.cli import main
from logvalue.correlation import spearman_correlation
from logvalue.evaluate.redundancy import run_redundancy_experiment
from logvalue.features.extract import build_feature_matrix
from logvalue.masking import mask_parameters
from logvalue.parsing.drain import DrainMiner
from logvalue.static.python_rules import scan_python
from pathlib import Path
import json
import pytest


def test_masking_collapses_runtime_values():
    assert mask_parameters("failed user 42 at 10.1.2.3") == "failed user <NUM> at <IP>"
    assert mask_parameters("completed in 18ms") == "completed in <NUM>ms"


def test_fault_specific_template_ranks_first():
    metrics = score_templates([
        Event("INFO healthy request 1", 0),
        Event("INFO healthy request 2", 0),
        Event("ERROR disk unavailable on 10.0.0.1", 1),
        Event("ERROR disk unavailable on 10.0.0.2", 1),
    ])
    assert metrics[0].template == "ERROR disk unavailable on <IP>"
    assert metrics[0].auc == 1.0
    assert metrics[0].fault_frequency == 2


def test_rejects_non_binary_labels():
    try:
        score_templates([Event("hello", 2)])
    except ValueError as error:
        assert "labels" in str(error)
    else:
        raise AssertionError("expected a validation error")


def test_feature_matrix_groups_multiple_lines_in_one_incident():
    matrix = build_feature_matrix([
        Event("INFO start", 0, "incident-a"),
        Event("INFO done", 0, "incident-a"),
        Event("ERROR failed", 1, "incident-b"),
    ])
    assert matrix.event_ids == ["incident-a", "incident-b"]
    assert matrix.rows[0].count(1) == 2


def test_drain_miner_groups_masked_values():
    miner = DrainMiner()
    miner.add("request for user 10 failed")
    miner.add("request for user 11 failed")
    assert miner.results()[0].count == 2


def test_redundancy_experiment_has_temporal_split():
    events = []
    for number in range(10):
        label = int(number in {2, 4, 6, 8})
        event_id = str(number)
        events.append(Event("DEBUG heartbeat", label, event_id))
        events.append(Event("ERROR database failed" if label else "INFO request complete", label, event_id))
    result = run_redundancy_experiment(build_feature_matrix(events))
    assert result.train_events == 7
    assert result.test_events == 3


def test_static_scanner_finds_example_issues():
    findings = scan_python(Path("examples/problematic_logging.py"))
    assert {finding.rule for finding in findings} == {"print-instead-of-logger", "concatenated-log-message"}


def test_spearman_correlation_tracks_rank_order():
    assert spearman_correlation([1, 2, 3], [10, 20, 30]) == pytest.approx(1.0)


def test_cli_writes_run_metadata(tmp_path):
    output = tmp_path / "metrics.csv"
    metadata = tmp_path / "run.json"
    exit_code = main([
        "analyze", "examples/incidents.jsonl", "--output", str(output),
        "--run-metadata", str(metadata),
    ])
    payload = json.loads(metadata.read_text())
    assert exit_code == 0
    assert payload["schema_version"] == 1
    assert payload["outputs"][0]["sha256"]


def test_cli_returns_nonzero_for_bad_input(tmp_path):
    invalid = tmp_path / "invalid.jsonl"
    invalid.write_text("not json\n")
    assert main(["analyze", str(invalid), "--output", str(tmp_path / "metrics.csv")]) == 2
