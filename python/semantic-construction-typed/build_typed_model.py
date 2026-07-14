from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from mercurio_ex_support import configure_imports

configure_imports()

import mercurio  # noqa: E402
from mercurio import model  # noqa: E402


def write_descriptor(root: Path) -> None:
    (root / ".project.json").write_text(
        json.dumps(
            {
                "schema": "dev.mercurio.project.v2",
                "version": 2,
                "name": "typed-semantic-construction",
                "model": {"entrypoints": ["model.sysml"]},
                "libraries": [
                    {
                        "id": "stdlib",
                        "role": "baseline",
                        "provider": {"kind": "bundled_stdlib"},
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def main() -> None:
    project = mercurio.create(package="TypedConstruction", stdlib=True)

    project.add(
        model.port_def("TelemetryPort")
        .with_attr(model.attr("bandwidth").typed("ScalarValues::Real").expression("250.0"))
    )
    project.add(
        model.part_def("Sensor")
        .with_attr(model.attr("sampleRate").typed("ScalarValues::Real").expression("10.0"))
        .with_port(model.port("telemetry").typed("TelemetryPort"))
    )
    project.add(
        model.part_def("Controller")
        .with_port(model.port("telemetryIn").typed("TelemetryPort"))
    )
    project.add(
        model.part_def("Instrument")
        .with_part(model.part("primarySensor").typed("Sensor"))
        .with_part(model.part("controller").typed("Controller"))
        .with_attr(model.attr("massKg").typed("ScalarValues::Real").expression("4.2"))
    )
    project.add(
        model.requirement_def("SamplingRequirement").doc(
            "The instrument publishes telemetry at the required sampling cadence."
        )
    )
    project.add(model.part("flightInstrument").typed("Instrument"))

    compiled = project.compile()
    refs = compiled.query.elements().select(["qualified_name", "metatype_name", "type"])
    names = {row["qualified_name"] for row in refs}
    assert "TypedConstruction.Sensor" in names
    assert "TypedConstruction.flightInstrument" in names

    sources = project.to_sysml()
    source = "\n".join(sources.values())
    assert "part def Sensor" in source
    assert "part flightInstrument:" in source and "Instrument;" in source
    assert "requirement def SamplingRequirement" in source

    with tempfile.TemporaryDirectory(prefix="mercurio-typed-") as temp:
        root = Path(temp)
        project.save(root)
        write_descriptor(root)
        opened = mercurio.open(str(root), executable=os.environ.get("MERCURIO_EXE"))
        try:
            legality = opened.can_type_usage("PartUsage", "PartDefinition")
            status = str(legality.get("status") or "").lower()
            assert legality.get("allowed") is True or status.startswith("allowed")
            parts = opened.parts()
            assert any(part.name == "flightInstrument" for part in parts)
        finally:
            close = getattr(opened, "close", None)
            if close is not None:
                close()

    print(f"compiled {len(refs)} semantic refs from {len(sources)} source file")
    print("typed semantic construction example passed")


if __name__ == "__main__":
    main()
