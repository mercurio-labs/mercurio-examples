from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Iterable


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def use_local_sdk() -> None:
    sdk = repo_root() / "mercurio-host-adapters" / "python"
    if sdk.exists() and str(sdk) not in sys.path:
        sys.path.insert(0, str(sdk))


def use_dev_console_api() -> None:
    exe = repo_root() / "mercurio-product" / "target" / "debug" / "mercurio-console-api.exe"
    if exe.exists():
        os.environ.setdefault("MERCURIO_EXE", str(exe))


def configure_imports() -> None:
    use_local_sdk()
    use_dev_console_api()


def project_dir(file: str) -> Path:
    return Path(file).resolve().parent


def compact_state_sequence(state_data) -> list[str]:
    compact: list[str] = []
    for active in state_data.states:
        label = active[-1] if active else "?"
        label = label.rsplit(".", 1)[-1]
        if not compact or compact[-1] != label:
            compact.append(label)
    return compact


def first_state_data(trace, candidates: Iterable[str]):
    errors: list[str] = []
    for candidate in candidates:
        if not candidate:
            continue
        try:
            data = trace.states(candidate)
        except Exception as exc:  # API supports multiple backend id shapes.
            errors.append(f"{candidate}: {exc}")
            continue
        if data.times:
            return data
    raise AssertionError("no state data found for candidates: " + "; ".join(errors))


def assert_state_seen(state_data, expected: str) -> None:
    if not any(any(expected in state for state in active) for active in state_data.states):
        raise AssertionError(f"expected state {expected!r}, got {state_data.states!r}")


def first_channel(trace, needles: Iterable[str]):
    wanted = [needle.lower() for needle in needles]
    for channel in trace.channels:
        lowered = channel.id.lower()
        if any(needle in lowered for needle in wanted):
            return trace.channel(channel.id)
    raise AssertionError(f"no channel matched {list(needles)!r}")

