from __future__ import annotations

from pathlib import Path
import sys

PYTHON_EXAMPLES = Path(__file__).resolve().parents[1]
if str(PYTHON_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(PYTHON_EXAMPLES))

from simulation_support import configure_imports, first_channel, project_dir

configure_imports()

import mercurio


PROJECT = project_dir(__file__)


def main() -> None:
    with mercurio.open(str(PROJECT)) as model:
        spec = model.analysis_case_spec("HeatProfile")
        print(f"readiness: {spec.readiness}")
        print("expected artifacts:")
        for artifact in spec.expected_artifacts:
            print(f"  {artifact.kind} {artifact.schema}")

        report = model.run_analysis_report(
            spec.case_ref.element_id,
            run_id="python.simulation.constraints-channels",
        )
        trace = report.simulation_trace()
        temperature = first_channel(trace, ["temperature"])

        print(f"run status: {report.status}")
        print(f"trace status: {trace.status}")
        print(f"temperature samples: {len(temperature.values)}")
        print(f"temperature: {temperature.values[0]} -> {temperature.values[-1]}")

        assert report.status == "passed"
        assert trace.status == "completed"
        assert len(temperature.values) >= 1
        assert temperature.values[-1] >= temperature.values[0]


if __name__ == "__main__":
    main()
