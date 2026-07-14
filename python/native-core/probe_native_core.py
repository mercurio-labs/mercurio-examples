from __future__ import annotations

import json
import tempfile
from pathlib import Path

from mercurio_ex_support import configure_imports

configure_imports()

import mercurio  # noqa: E402
from mercurio import model  # noqa: E402


def native_core_available() -> bool:
    try:
        from mercurio._core import PyWorkspace  # noqa: F401
    except (ImportError, AttributeError):
        return False
    return True


def write_project(root: Path) -> None:
    project = mercurio.create(package="NativeProbe", stdlib=False)
    project.add(
        model.part_def("ProbeAssembly")
        .with_part(model.part("sensor"))
        .with_attr(model.attr("massKg").typed("ScalarValues::Real").expression("1.0"))
    )
    project.add(model.part("baseline").typed("ProbeAssembly"))
    project.save(root)
    (root / ".project.json").write_text(
        json.dumps(
            {
                "schema": "dev.mercurio.project.v2",
                "version": 2,
                "name": "native-core-probe",
                "model": {"entrypoints": ["model.sysml"]},
                "dependencies": [
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
    if not native_core_available():
        print("native core unavailable in this Python environment; skipped")
        return

    with tempfile.TemporaryDirectory(prefix="mercurio-native-") as temp:
        root = Path(temp)
        write_project(root)
        opened = mercurio.open(str(root), executable=None)
        parts = opened.parts()
        assert any(part.name == "baseline" for part in parts)

    print("native core probe example passed")


if __name__ == "__main__":
    main()
