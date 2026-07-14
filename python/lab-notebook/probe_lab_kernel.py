from __future__ import annotations

import os

from mercurio_ex_support import configure_imports

configure_imports()

import mercurio  # noqa: E402
from mercurio.lab import parameter_sweep  # noqa: E402


def main() -> None:
    if os.environ.get("MERCURIO_LAB_KERNEL") != "1":
        print("not running inside Mercurio Lab kernel; skipped")
        return

    model = mercurio.open()
    variants = parameter_sweep(model, "massMargin", [0.1, 0.2, 0.3])
    assert len(variants) == 3
    assert variants[0].params["massMargin"] == 0.1

    if model.workspace:
        legality = model.can_type_usage("PartUsage", "PartDefinition")
        assert legality.get("allowed") is True

    print(f"lab model={model.label} variants={len(variants)}")
    print("lab notebook probe example passed")


if __name__ == "__main__":
    main()
