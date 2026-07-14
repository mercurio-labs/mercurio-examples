"""
Load an existing SysML project, make edits, and save back.

This script demonstrates the Python authoring workflow for an existing model:

  1. Open the project through .project.json.
  2. Load descriptor-selected sources into a ModelBuilder via from_project().
  3. Apply mutations — add a new sensor definition, add a part to an existing
     definition, rename a usage.
  4. Print a diff of changed files and write the results back to disk.

Note on .project.json
---------------------
The .project.json file is used by the Mercurio desktop app to configure
the project (library selection, registered views, plugins).  The native
Python bindings read .project.json, including descriptor-selected source roots,
entrypoints, and dependencies. Use ModelBuilder.from_project() when editing a
descriptor-backed workspace.
"""

from __future__ import annotations

import difflib
from pathlib import Path

from mercurio.authoring import (
    AttributeUsage,
    ModelBuilder,
    PartDefinition,
    PartUsage,
)
from mercurio.stdlib import isq, scalar_values

# ---------------------------------------------------------------------------
# 1.  Open the descriptor-backed project
# ---------------------------------------------------------------------------

PROJECT_DIR = Path(__file__).parent

builder = ModelBuilder.from_project(PROJECT_DIR)
original_files = builder.to_sysml()
original_text = "\n".join(original_files.values())
print(f"Loaded {len(original_files)} descriptor-selected file(s): {list(original_files)}\n")

# ---------------------------------------------------------------------------
# 2.  Inspect what's already there
# ---------------------------------------------------------------------------

print("=== Original SysML ===")
for filename, source in builder.to_sysml().items():
    print(f"-- {filename} --")
    print(source)

# ---------------------------------------------------------------------------
# 3.  Apply mutations
# ---------------------------------------------------------------------------

# (a) Add a new sensor definition to the existing package.
humidity_sensor = (
    PartDefinition("HumiditySensor")
    .with_attr(AttributeUsage("mass").typed(isq.mass))
    .with_attr(AttributeUsage("sampling_rate").typed(isq.frequency))
    .with_attr(AttributeUsage("resolution").typed(scalar_values.real))
)
if "part def HumiditySensor" not in original_text:
    builder.add_to("SensorSystem", humidity_sensor)

# (b) Add the new sensor as a part inside SensorArray.
if "part humidity_sensor:" not in original_text:
    builder.add_to(
        "SensorSystem.SensorArray",
        PartUsage("humidity_sensor").typed(humidity_sensor),
    )

# (c) Add a power-budget attribute to SensorArray.
if "attribute power_budget:" not in original_text:
    builder.add_to(
        "SensorSystem.SensorArray",
        AttributeUsage("power_budget").typed(isq.power),
    )

# (d) Rename an existing usage for clarity.
if "temp_sensor" in original_text:
    builder.rename("SensorSystem.SensorArray.temp_sensor", "temperature_sensor")

# ---------------------------------------------------------------------------
# 4.  Show diff and write back
# ---------------------------------------------------------------------------

updated_files = builder.to_sysml()

print("\n=== Diff ===")
for filename, updated in updated_files.items():
    original = original_files.get(filename, "")
    diff = list(
        difflib.unified_diff(
            original.splitlines(keepends=True),
            updated.splitlines(keepends=True),
            fromfile=f"a/{filename}",
            tofile=f"b/{filename}",
        )
    )
    if diff:
        print("".join(diff))
    else:
        print(f"(no changes in {filename})")

print("\n=== Updated SysML ===")
for filename, source in updated_files.items():
    print(f"-- {filename} --")
    print(source)

# Write back to disk.
for filename, source in updated_files.items():
    out = PROJECT_DIR / filename
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(source, encoding="utf-8")
    print(f"Saved {out}")
