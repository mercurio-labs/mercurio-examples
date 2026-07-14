from __future__ import annotations

from pathlib import Path
import sys

PYTHON_EXAMPLES = Path(__file__).resolve().parents[1]
if str(PYTHON_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(PYTHON_EXAMPLES))

from simulation_support import configure_imports, project_dir

configure_imports()

import mercurio


PROJECT = project_dir(__file__)


def main() -> None:
    with mercurio.open(str(PROJECT)) as model:
        spec = model.analysis_case_spec("Warmup")
        print(f"readiness: {spec.readiness}")
        print("dynamic bindings:")
        for binding in spec.dynamic_behavior_bindings:
            print(f"  {binding.subject.label} -> {binding.behavior.label} ({binding.kind})")
        print("readiness diagnostics:")
        for diagnostic in spec.readiness_diagnostics:
            print(f"  {diagnostic.severity}: {diagnostic.code}: {diagnostic.message}")

        report = model.run_analysis_report(
            spec.case_ref.element_id,
            run_id="python.simulation.activity-readiness",
        )
        print(f"run status: {report.status}")
        print("artifacts:")
        for artifact in report.artifacts:
            print(f"  {artifact.kind} {artifact.schema}")

        try:
            summary = report.activity_summary()
        except KeyError:
            assert spec.readiness in {"partial", "blocked", "ready"}
            assert report.diagnostics or spec.readiness_diagnostics
            print("activity summary not produced; diagnostics describe current support")
            return

        print(f"activity bindings: {summary.get('bindingCount', 0)}")
        assert summary.get("bindingCount", 0) >= 1


if __name__ == "__main__":
    main()

