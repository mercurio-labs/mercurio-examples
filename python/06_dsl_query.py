from __future__ import annotations

import mercurio

from _common import fixture


def main() -> None:
    project = mercurio.project(fixture("vehicle-basic"))
    result = project.query("model.parts().count()")

    print("DSL result:")
    print(result)


if __name__ == "__main__":
    main()
