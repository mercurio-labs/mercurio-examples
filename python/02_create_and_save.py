from __future__ import annotations

import argparse
import tempfile
from pathlib import Path

import mercurio
from mercurio import model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=None)
    args = parser.parse_args()

    output_dir = args.out or Path(tempfile.mkdtemp(prefix="mercurio-python-example-"))
    project = mercurio.create(output_dir, package="SavedVehicle", stdlib=False)

    project.add(
        model.part_def("Battery")
        .with_attr(model.attr("capacity_kwh").typed("ScalarValues::Real").expression("80.0"))
    )
    project.add(
        model.part_def("Vehicle")
        .with_part(model.part("battery").typed("Battery"))
        .with_attr(model.attr("range_km").typed("ScalarValues::Real").expression("480.0"))
    )
    project.save()

    print(f"saved project sources to {output_dir}")
    for path in sorted(output_dir.rglob("*.sysml")):
        print(path)


if __name__ == "__main__":
    main()
