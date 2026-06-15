"""
Pilot State Definition Example-1 recreated with Python authoring.

This mirrors:
external/SysML-v2-Pilot-Implementation/sysml/src/training/23. State Definitions/State Definition Example-1.sysml
"""

from __future__ import annotations

from pathlib import Path

from mercurio.authoring import (
    AttributeDefinition,
    ModelBuilder,
    StateDefinition,
    StateUsage,
    TransitionUsage,
)


vehicle_states = (
    StateDefinition("VehicleStates")
    .with_state(TransitionUsage("start").initial().then("off"))
    .with_state(StateUsage("off"))
    .with_state(
        TransitionUsage("off_to_starting")
        .first("off")
        .accept("VehicleStartSignal")
        .then("starting")
    )
    .with_state(StateUsage("starting"))
    .with_state(
        TransitionUsage("starting_to_on")
        .first("starting")
        .accept("VehicleOnSignal")
        .then("on")
    )
    .with_state(StateUsage("on"))
    .with_state(
        TransitionUsage("on_to_off")
        .first("on")
        .accept("VehicleOffSignal")
        .then("off")
    )
)

builder = (
    ModelBuilder()
    .in_package("State Definition Example-1", stdlib_imports=False)
    .add(AttributeDefinition("VehicleStartSignal"))
    .add(AttributeDefinition("VehicleOnSignal"))
    .add(AttributeDefinition("VehicleOffSignal"))
    .add(vehicle_states)
)

print("=== Generated SysML ===")
for filename, source in builder.to_sysml().items():
    print(f"-- {filename} --")
    print(source)

builder.save("output")
Path("output/model.sysml").replace("output/state-definition-example-1.sysml")
print("\nSaved to ./output/")
