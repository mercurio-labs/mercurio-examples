from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

PYTHON_EXAMPLES = Path(__file__).resolve().parents[1]
if str(PYTHON_EXAMPLES) not in sys.path:
    sys.path.insert(0, str(PYTHON_EXAMPLES))

from simulation_support import configure_imports, first_channel

configure_imports()

import mercurio


SOURCE_PROJECT = PYTHON_EXAMPLES / "simulation-constraints-channels"


def run_case(project: Path, run_id: str) -> float:
    with mercurio.open(str(project)) as model:
        spec = model.analysis_case_spec("HeatProfile")
        report = model.run_analysis_report(spec.case_ref.element_id, run_id=run_id)
        trace = report.simulation_trace()
        return float(first_channel(trace, ["temperature"]).values[-1])


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="mercurio-sim-study-") as raw_tmp:
        tmp = Path(raw_tmp)
        baseline = tmp / "baseline"
        higher_target = tmp / "higher-target"
        shutil.copytree(SOURCE_PROJECT, baseline)
        shutil.copytree(SOURCE_PROJECT, higher_target)

        source_path = higher_target / "model" / "thermal-chamber.sysml"
        source = source_path.read_text(encoding="utf-8")
        source_path.write_text(
            source.replace(
                "attribute targetTemperature : Real = 80.0;",
                "attribute targetTemperature : Real = 95.0;",
            ),
            encoding="utf-8",
        )

        baseline_final = run_case(baseline, "python.simulation.variant.baseline")
        higher_final = run_case(higher_target, "python.simulation.variant.higher-target")

        print(f"baseline final temperature: {baseline_final}")
        print(f"higher-target final temperature: {higher_final}")

        assert higher_final >= baseline_final


if __name__ == "__main__":
    main()
