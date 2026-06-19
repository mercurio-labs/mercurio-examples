from __future__ import annotations

from pathlib import Path

from mercurio.authoring import AttributeUsage, ModelBuilder, PartDefinition, PartUsage


def main() -> None:
    output_dir = Path(__file__).resolve().parent / "model"
    output_file = output_dir / "created-model.sysml"

    builder = (
        ModelBuilder(validate_each_mutation=False)
        .in_package("CreatedModel", stdlib_imports=False)
        .add(PartDefinition("MissionComputer"))
        .add(
            PartDefinition("Spacecraft")
            .with_part(PartUsage("computer").typed("MissionComputer"))
            .with_attr(AttributeUsage("mass").typed("MassValue"))
        )
    )

    files = builder.to_sysml()
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file.write_text(files["model.sysml"], encoding="utf-8")

    print(f"Wrote {output_file}")


if __name__ == "__main__":
    main()
