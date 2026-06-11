"""
Electric drive system — minimal Python authoring example.

Builds a three-component drive system (battery, motor, controller) whose
attributes are typed to ISQ quantities and SI units from the SysML stdlib.
Prints the generated SysML source and writes it to ./output/.
"""

from __future__ import annotations

from mercurio.authoring import (
    AttributeUsage,
    ConnectionDefinition,
    ConnectionUsage,
    ModelBuilder,
    PartDefinition,
    PartUsage,
    PortDefinition,
    PortUsage,
)
from mercurio.stdlib import isq, si

# ---------------------------------------------------------------------------
# Ports
# ---------------------------------------------------------------------------

electrical_port = PortDefinition("ElectricalPort").with_attr(
    AttributeUsage("voltage").typed(isq.electric_potential),
).with_attr(
    AttributeUsage("current").typed(isq.electric_current),
)

mechanical_port = PortDefinition("MechanicalPort").with_attr(
    AttributeUsage("torque").typed(isq.torque),
    ).with_attr(
    AttributeUsage("angular_velocity").typed(isq.angular_velocity),
)

# ---------------------------------------------------------------------------
# Components
# ---------------------------------------------------------------------------

battery = (
    PartDefinition("Battery")
    .with_attr(AttributeUsage("mass").typed(isq.mass))
    .with_attr(AttributeUsage("capacity").typed(isq.energy))
    .with_attr(AttributeUsage("nominal_voltage").typed(isq.electric_potential))
    .with_port(PortUsage("output").typed(electrical_port))
)

motor = (
    PartDefinition("Motor")
    .with_attr(AttributeUsage("mass").typed(isq.mass))
    .with_attr(AttributeUsage("rated_power").typed(isq.power))
    .with_attr(AttributeUsage("efficiency").typed(si.one))
    .with_port(PortUsage("electrical_in").typed(electrical_port).direction("in"))
    .with_port(PortUsage("shaft_out").typed(mechanical_port).direction("out"))
)

controller = (
    PartDefinition("MotorController")
    .with_attr(AttributeUsage("mass").typed(isq.mass))
    .with_attr(AttributeUsage("switching_frequency").typed(isq.frequency))
    .with_port(PortUsage("power_in").typed(electrical_port).direction("in"))
    .with_port(PortUsage("drive_out").typed(electrical_port).direction("out"))
)

# ---------------------------------------------------------------------------
# Top-level system
# ---------------------------------------------------------------------------

drive_system = (
    PartDefinition("ElectricDriveSystem")
    .with_attr(AttributeUsage("total_mass").typed(isq.mass))
    .with_attr(AttributeUsage("peak_power").typed(isq.power))
    .with_part(PartUsage("battery").typed(battery))
    .with_part(PartUsage("controller").typed(controller))
    .with_part(PartUsage("motor").typed(motor))
    .with_part(
        ConnectionUsage("power_link")
        .typed(ConnectionDefinition("PowerLink"))
        .end("battery::output")
        .end("controller::power_in")
    )
    .with_part(
        ConnectionUsage("drive_link")
        .typed(ConnectionDefinition("DriveLink"))
        .end("controller::drive_out")
        .end("motor::electrical_in")
    )
)

# ---------------------------------------------------------------------------
# Build and emit
# ---------------------------------------------------------------------------

builder = (
    ModelBuilder()
    .in_package("ElectricDriveSystem")
    .add(electrical_port)
    .add(mechanical_port)
    .add(battery)
    .add(motor)
    .add(controller)
    .add(drive_system)
)

print("=== Generated SysML ===")
for filename, source in builder.to_sysml().items():
    print(f"-- {filename} --")
    print(source)

builder.save("output")
print("Saved to ./output/")
