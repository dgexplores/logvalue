.PHONY: demo test

demo:
	PYTHONPATH=src python3 -m logvalue analyze examples/incidents.jsonl --output results/demo_metrics.csv
	PYTHONPATH=src python3 -m logvalue redundancy examples/incidents.jsonl --output results/redundancy.json
	PYTHONPATH=src python3 -m logvalue parse examples/application.log --output results/templates.json
	PYTHONPATH=src python3 -m logvalue scan-python examples/problematic_logging.py --output results/static_findings.json
	PYTHONPATH=src python3 -m logvalue report examples/incidents.jsonl --output results/report.md

test:
	PYTHONPATH=src python3 -m pytest -q
