from __future__ import annotations

import sys
from pathlib import Path
_SDK = Path(__file__).resolve().parents[2] / "mercurio-host-adapters" / "python"
if (_SDK / "mercurio").is_dir():
    sys.path.insert(0, str(_SDK))
import mercurio

PROJECT = Path(__file__).resolve().parent
DOC = "Updated by transaction_query_writeback.py"


def main() -> None:
    write = "--write" in sys.argv
    project = mercurio.open_project(PROJECT, validate=False)
    before = project.compile()
    print(f"Initial compile ok: {len(before.refs())} elements")
    transaction = (
        project.transaction("python outside-in source writeback")
        .rename("SensorSystem.SensorArray.pressure_sensor", "ambient_pressure_sensor")
        .set_attribute("SensorSystem.SensorArray", "doc", DOC)
        .set_attribute("SensorSystem.PressureSensor", "doc", DOC)
    )
    preview = transaction.preview()
    ops = preview["operations"]
    edits = sum(len(op.get("change_set", {}).get("actions", [])) for op in ops)
    print(f"Transaction preview: {preview['status']} ({len(ops)} op, {edits} edits)")
    transaction.apply()
    after = project.compile()
    print(f"Post-edit compile ok: {len(after.refs())} elements")
    packages = (
        after.query.elements()
        .where_metatype_is("KerML.Package")
        .order_by("qualified_name")
        .select(["qualified_name", "kind", "metatype_chain", "model_layer"])
    )
    for row in packages:
        chain = " > ".join(row["metatype_chain"])
        print(f"{row['qualified_name']} | {row['kind']} | {chain} | {row['model_layer']}")
    if write:
        for name, source in project.to_sysml().items():
            (PROJECT / name).write_text(source, encoding="utf-8")
            print(f"Wrote {name}")


if __name__ == "__main__":
    main()
