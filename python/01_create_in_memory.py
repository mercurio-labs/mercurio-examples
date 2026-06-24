from __future__ import annotations

import mercurio
from mercurio import model

from _common import print_sources


def main() -> None:
    project = mercurio.create(package="VehicleExample", stdlib=False)

    project.add(
        model.part_def("Engine")
        .with_attr(model.attr("power_kw").typed("ScalarValues::Real").expression("150.0"))
    )
    project.add(
        model.part_def("Wheel")
        .with_attr(model.attr("diameter_mm").typed("ScalarValues::Real").expression("600.0"))
    )
    project.add(
        model.part_def("Vehicle")
        .with_attr(model.attr("mass_kg").typed("ScalarValues::Real").expression("1200.0"))
        .with_part(model.part("engine").typed("Engine"))
        .with_part(model.part("frontLeft").typed("Wheel"))
        .with_part(model.part("frontRight").typed("Wheel"))
        .with_part(model.part("rearLeft").typed("Wheel"))
        .with_part(model.part("rearRight").typed("Wheel"))
    )
    project.add(model.part("baselineVehicle").typed("Vehicle"))

    print_sources(project.to_sysml())


if __name__ == "__main__":
    main()
