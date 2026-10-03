"""Generate Phase 9 DSS example input and output files."""

from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.dss.service import PROJECT_ROOT, get_service


PHASE9_EXAMPLE_DIR = PROJECT_ROOT / "phase_9_decision_support_system" / "examples"
OUTPUT_EXAMPLE_DIR = PROJECT_ROOT / "outputs" / "dss" / "examples"
SUMMARY_JSON = PROJECT_ROOT / "outputs" / "dss" / "phase9_dss_summary.json"


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    PHASE9_EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_EXAMPLE_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_JSON.parent.mkdir(parents=True, exist_ok=True)

    service = get_service()
    example_input = service.default_input
    prediction = service.predict(example_input)
    report = service.export_markdown_report(prediction)

    for directory in [PHASE9_EXAMPLE_DIR, OUTPUT_EXAMPLE_DIR]:
        write_json(directory / "example_input.json", example_input)
        write_json(directory / "example_prediction_output.json", prediction)
        (directory / "example_prediction_report.md").write_text(report, encoding="utf-8")

    summary = {
        "phase": "9",
        "status": "complete",
        "example_input": str((OUTPUT_EXAMPLE_DIR / "example_input.json").relative_to(PROJECT_ROOT)),
        "example_prediction_output": str((OUTPUT_EXAMPLE_DIR / "example_prediction_output.json").relative_to(PROJECT_ROOT)),
        "example_prediction_report": str((OUTPUT_EXAMPLE_DIR / "example_prediction_report.md").relative_to(PROJECT_ROOT)),
        "phase9_example_input": str((PHASE9_EXAMPLE_DIR / "example_input.json").relative_to(PROJECT_ROOT)),
        "phase9_example_prediction_output": str(
            (PHASE9_EXAMPLE_DIR / "example_prediction_output.json").relative_to(PROJECT_ROOT)
        ),
        "phase9_example_prediction_report": str(
            (PHASE9_EXAMPLE_DIR / "example_prediction_report.md").relative_to(PROJECT_ROOT)
        ),
        "api_module": "src.dss.api:app",
        "dashboard_script": "src/dss/dashboard.py",
        "api_docs_url": "http://127.0.0.1:8000/docs",
        "dashboard_url": "http://127.0.0.1:8501",
    }
    write_json(SUMMARY_JSON, summary)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
