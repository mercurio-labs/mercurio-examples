"""
Compare Python-authored Pilot examples against the original Pilot sources.

Run the build scripts first, then run this verifier with a Mercurio Python
install that includes the native PyO3 extension.
"""

from __future__ import annotations

from pathlib import Path

from mercurio.authoring import ModelBuilder
from mercurio.semantic import compare_semantic_snapshots


ROOT = Path(__file__).resolve().parents[2]
EXAMPLE_ROOT = Path(__file__).resolve().parent
PILOT_ROOT = ROOT / "external" / "SysML-v2-Pilot-Implementation" / "sysml" / "src"

SAMPLES = [
    (
        "Metadata Example-1",
        PILOT_ROOT / "training" / "39. Metadata" / "Metadata Example-1.sysml",
        EXAMPLE_ROOT / "output" / "metadata-example-1.sysml",
    ),
    (
        "State Definition Example-1",
        PILOT_ROOT / "training" / "23. State Definitions" / "State Definition Example-1.sysml",
        EXAMPLE_ROOT / "output" / "state-definition-example-1.sysml",
    ),
]


def compile_source(path: Path):
    source = path.read_text(encoding="utf-8")
    return ModelBuilder.from_files({"model.sysml": source}, validate=True).compile()


def main() -> None:
    failures = 0
    for name, original, generated in SAMPLES:
        original_model = compile_source(original)
        generated_model = compile_source(generated)
        differences = compare_semantic_snapshots(original_model, generated_model)
        if differences:
            failures += 1
            print(f"{name}: {len(differences)} semantic differences")
            for diff in differences[:20]:
                print(f"  {diff.key} {diff.field}: {diff.left!r} != {diff.right!r}")
            if len(differences) > 20:
                print(f"  ... {len(differences) - 20} more")
        else:
            print(f"{name}: semantic snapshot match")

    if failures:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
