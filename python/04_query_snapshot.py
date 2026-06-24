from __future__ import annotations

import mercurio

from _common import fixture


def main() -> None:
    snapshot = mercurio.project(fixture("vehicle-basic")).compile()

    vehicle = snapshot.part_def("Vehicle")
    print(f"vehicle: {vehicle.qualified_name}")
    print("children:")
    for child in vehicle.children():
        print(f"  {child.kind} {child.qualified_name}")

    wheels = [
        ref
        for ref in snapshot.query.part_usages()
        if ref.type_name() == "VehicleExample.Wheel" or ref.type_name() == "Wheel"
    ]
    print(f"wheel usages: {len(wheels)}")


if __name__ == "__main__":
    main()
