"""
Satellite system — Python stdlib authoring example.

Builds a three-subsystem satellite model whose attributes are typed to ISQ
quantity-kind value types and SI units from the SysML standard library, then
prints the generated SysML source and writes it to ./output/. The adjacent
.project.json opens the generated output as a descriptor-backed Mercurio
project.
"""

from __future__ import annotations

from mercurio.authoring import (
    AttributeUsage,
    ModelBuilder,
    PartDefinition,
    PartUsage,
)
from mercurio.stdlib import StdlibRef, isq, scalar_values, si

# ---------------------------------------------------------------------------
# Subsystem definitions
# ---------------------------------------------------------------------------

structure = (
    PartDefinition("Structure")
    .with_attr(AttributeUsage("dry_mass").typed(isq.mass))
    .with_attr(AttributeUsage("length").typed(isq.length))
    .with_attr(AttributeUsage("width").typed(isq.length))
    .with_attr(AttributeUsage("height").typed(isq.length))
)

power_system = (
    PartDefinition("PowerSystem")
    .with_attr(AttributeUsage("mass").typed(isq.mass))
    .with_attr(AttributeUsage("solar_array_area").typed(isq.area))
    .with_attr(AttributeUsage("peak_power").typed(isq.power))
    .with_attr(AttributeUsage("battery_capacity").typed(isq.energy))
    .with_attr(AttributeUsage("bus_voltage").typed(isq.electric_potential))
)

thermal = (
    PartDefinition("ThermalControl")
    .with_attr(AttributeUsage("mass").typed(isq.mass))
    .with_attr(AttributeUsage("temp_min").typed(isq.thermodynamic_temperature))
    .with_attr(AttributeUsage("temp_max").typed(isq.thermodynamic_temperature))
    .with_attr(AttributeUsage("heat_dissipation").typed(isq.power))
)

# ---------------------------------------------------------------------------
# Top-level spacecraft
# ---------------------------------------------------------------------------

satellite = (
    PartDefinition("Satellite")
    .with_attr(AttributeUsage("total_mass").typed(isq.mass))
    .with_attr(AttributeUsage("orbit_altitude").typed(isq.length))
    .with_attr(AttributeUsage("design_life").typed(isq.duration))
    .with_attr(AttributeUsage("name").typed(scalar_values.string))
    .with_part(PartUsage("structure").typed(structure))
    .with_part(PartUsage("power").typed(power_system))
    .with_part(PartUsage("thermal").typed(thermal))
)

# ---------------------------------------------------------------------------
# Build and emit
# ---------------------------------------------------------------------------

builder = (
    ModelBuilder()
    .in_package("SatelliteModel")
    .add(structure)
    .add(power_system)
    .add(thermal)
    .add(satellite)
)

print("=== Generated SysML ===")
for filename, source in builder.to_sysml().items():
    print(f"-- {filename} --")
    print(source)

builder.save("output")
print("\nSaved to ./output/")
