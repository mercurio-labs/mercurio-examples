from __future__ import annotations

import mercurio

from _common import fixture


def main() -> None:
    project = mercurio.project(fixture("vehicle-basic"))
    snapshot = project.compile()

    print(f"source files: {', '.join(project.to_sysml())}")
    print(f"revision: {snapshot.revision}")
    print("part definitions:")
    for ref in snapshot.query.part_defs():
        print(f"  {ref.qualified_name}")


if __name__ == "__main__":
    main()
