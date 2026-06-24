from __future__ import annotations

import mercurio
from mercurio import model

from _common import print_sources


def main() -> None:
    base = mercurio.create(package="BatteryStudy", stdlib=False)
    base.add(
        model.part_def("Vehicle")
        .with_attr(model.attr("battery_capacity_kwh").typed("ScalarValues::Real").expression("80.0"))
        .with_attr(model.attr("range_km").typed("ScalarValues::Real").expression("480.0"))
    )

    study = base.trade_study("battery-sizing")
    city = study.variant("city")
    long_range = study.variant("long-range")

    city.edit("BatteryStudy.Vehicle.battery_capacity_kwh").set_value("55.0")
    city.edit("BatteryStudy.Vehicle.range_km").set_value("330.0")
    long_range.edit("BatteryStudy.Vehicle.battery_capacity_kwh").set_value("110.0")
    long_range.edit("BatteryStudy.Vehicle.range_km").set_value("660.0")

    print("base:")
    print_sources(base.to_sysml())
    print("city variant:")
    print_sources(city.to_sysml())
    print("long-range variant:")
    print_sources(long_range.to_sysml())


if __name__ == "__main__":
    main()
