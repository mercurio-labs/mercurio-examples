from __future__ import annotations

import json
import sys
from pathlib import Path

PYTHON_EXAMPLES = Path(__file__).resolve().parents[1]
if str(PYTHON_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(PYTHON_EXAMPLES))

from simulation_support import compact_state_sequence, configure_imports, first_channel, first_state_data, repo_root

configure_imports()

import mercurio


PROJECT = repo_root() / "mercurio-examples" / "python" / "simulation-constraints-channels"
OUTPUT = Path(__file__).resolve().parent / "output" / "trace-overlay.json"


def main() -> None:
    with mercurio.open(str(PROJECT)) as model:
        spec = model.analysis_case_spec("HeatProfile")
        report = model.run_analysis_report(
            spec.case_ref.element_id,
            run_id="python.simulation.view-overlay",
        )
        trace = report.simulation_trace()

        chamber_states = first_state_data(trace, ["chamber"])
        temperature = first_channel(trace, ["temperature"])

        parts = model.parts()

    overlay = {
        "schema": "dev.mercurio.example.trace-overlay.v1",
        "sourceProject": str(PROJECT),
        "runId": report.run_id,
        "scenarioId": trace.scenario_id,
        "status": trace.status,
        "stateSequences": {
            "chamber": compact_state_sequence(chamber_states),
        },
        "channels": {
            "temperature": {
                "samples": len(temperature.values),
                "first": temperature.values[0],
                "last": temperature.values[-1],
            },
        },
        "partCount": len(parts),
    }

    print(json.dumps(overlay, indent=2))
    if "--write" in sys.argv:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_text(json.dumps(overlay, indent=2) + "\n", encoding="utf-8")
        print(f"wrote {OUTPUT}")

    assert trace.status == "completed"
    assert overlay["channels"]["temperature"]["last"] >= overlay["channels"]["temperature"]["first"]
    assert overlay["partCount"] >= 1


if __name__ == "__main__":
    main()
