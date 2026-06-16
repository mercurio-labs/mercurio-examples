"""
Pilot Metadata Example-1 recreated with Python authoring.

This mirrors:
external/SysML-v2-Pilot-Implementation/sysml/src/training/39. Metadata/Metadata Example-1.sysml
"""

from __future__ import annotations

from pathlib import Path

from mercurio.authoring import (
    MetadataDefinition,
    MetadataUsage,
    ModelBuilder,
    PartUsage,
)


metadata_security = (
    MetadataDefinition("SecurityFeature")
    .annotates("SysML::PartDefinition")
    .annotates("SysML::PartUsage")
)

vehicle = (
    PartUsage("vehicle")
    .with_part(
        PartUsage("interior")
        .with_part(PartUsage("alarm"))
        .with_part(PartUsage("seatBelt").multiplicity("2"))
        .with_part(PartUsage("frontSeat").multiplicity("2"))
        .with_part(PartUsage("driverAirBag"))
    )
    .with_part(
        PartUsage("bodyAssy")
        .with_part(PartUsage("body"))
        .with_part(PartUsage("bumper"))
        .with_part(PartUsage("keylessEntry"))
    )
)

builder = (
    ModelBuilder(validate_each_mutation=False)
    .in_package("Metadata Example-1", stdlib_imports=False)
    .add(MetadataDefinition("SafetyFeature"))
    .add(metadata_security)
    .add(
        MetadataUsage("SafetyFeature").about(
            [
                "vehicle::interior::seatBelt",
                "vehicle::interior::driverAirBag",
                "vehicle::bodyAssy::bumper",
            ]
        )
    )
    .add(
        MetadataUsage("SecurityFeature").about(
            [
                "vehicle::interior::alarm",
                "vehicle::bodyAssy::keylessEntry",
            ]
        )
    )
    .add(vehicle)
)

print("=== Generated SysML ===")
for filename, source in builder.to_sysml().items():
    print(f"-- {filename} --")
    print(source)

builder.save("output")
Path("output/model.sysml").replace("output/metadata-example-1.sysml")
print("\nSaved to ./output/")
