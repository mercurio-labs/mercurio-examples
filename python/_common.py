from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent
FIXTURES = ROOT / "fixtures"


def fixture(name: str) -> Path:
    return FIXTURES / name


def print_sources(files: dict[str, str]) -> None:
    for filename, source in files.items():
        print(f"-- {filename} --")
        print(source.rstrip())
        print()
