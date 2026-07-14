from __future__ import annotations

from pathlib import Path
import sys

PYTHON_EXAMPLES = Path(__file__).resolve().parents[1]
if str(PYTHON_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(PYTHON_EXAMPLES))

from simulation_support import (
    assert_state_seen,
    compact_state_sequence,
    configure_imports,
    first_state_data,
    project_dir,
)

configure_imports()

import mercurio


PROJECT = project_dir(__file__)


def main() -> None:
    with mercurio.open(str(PROJECT)) as model:
        spec = model.analysis_case_spec("PrintSequence")
        print(f"readiness: {spec.readiness}")
        print(f"dynamic bindings: {len(spec.dynamic_behavior_bindings)}")

        report = model.run_analysis_report(
            spec.case_ref.element_id,
            run_id="python.simulation.state-machine",
        )
        trace = report.simulation_trace()
        print(f"run status: {report.status}")
        print(f"trace status: {trace.status}")

        states = first_state_data(
            trace,
            [
                "printer",
                spec.subjects[0].label if spec.subjects else "",
                spec.subjects[0].element_id if spec.subjects else "",
            ],
        )
        print("state sequence:", " -> ".join(compact_state_sequence(states)))

        assert report.status == "passed"
        assert trace.status == "completed"
        assert_state_seen(states, "Idle")
        assert_state_seen(states, "Printing")


if __name__ == "__main__":
    main()

