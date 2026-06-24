from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import mercurio

from _common import fixture


def main() -> None:
    work_dir = Path(tempfile.mkdtemp(prefix="mercurio-python-edit-")) / "vehicle-basic"
    shutil.copytree(fixture("vehicle-basic"), work_dir)

    project = mercurio.project(work_dir)
    before = project.to_sysml()

    snapshot = project.compile()
    engine = snapshot.part_usage("engine")
    project.edit(engine).rename("motor")
    project.save()

    after = project.to_sysml()
    print(f"edited copy: {work_dir}")
    for filename in sorted(after):
        changed = before.get(filename) != after[filename]
        status = "changed" if changed else "unchanged"
        print(f"{status}: {filename}")


if __name__ == "__main__":
    main()
