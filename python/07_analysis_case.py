from __future__ import annotations

import mercurio

from _common import fixture


def main() -> None:
    with mercurio.open(str(fixture("vehicle-analysis"))) as runtime_model:
        handle = runtime_model.analysis("VehicleMassComplianceAnalysis")
        spec = handle.spec()

        print(f"readiness: {spec.readiness}")
        print("expected artifacts:")
        for artifact in spec.expected_artifacts:
            print(f"  {artifact.kind} {artifact.schema}")

        if spec.readiness == "ready":
            report = handle.run(run_id="python-example.vehicle-mass")
            print(f"run status: {report.status}")
            if report.artifacts:
                print("artifacts:")
                for artifact in report.artifacts:
                    print(f"  {artifact.kind} {artifact.schema}")


if __name__ == "__main__":
    main()
