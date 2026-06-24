"""
Verification script for the mercurio Python simulation API.

Runs the Voron Trident 350 PrintSequence analysis case and checks that Python
can discover structure, execute multiple concurrent state machines, and read
parametric channels for the replay dashboard.
"""

import os
import sys
from pathlib import Path

WORKSPACE = str(Path(__file__).resolve().parent.parent)
REPO_ROOT = Path(WORKSPACE).parent.parent

python_support = REPO_ROOT / "mercurio-host-adapters" / "python"
if python_support.exists() and str(python_support) not in sys.path:
    sys.path.insert(0, str(python_support))

dev_exe = REPO_ROOT / "mercurio-product/target/debug/mercurio-console-api.exe"
if dev_exe.exists():
    os.environ.setdefault("MERCURIO_EXE", str(dev_exe))

import mercurio

EXPECTED_SUBJECTS = [
    "printer",
    "motion",
    "bed",
    "hotend",
    "extruder",
    "toolchanger",
]


def section(label):
    print(f"\n{'=' * 55}")
    print(f"  {label}")
    print("=" * 55)


def flattened_states(trace, subject):
    states = trace.states(subject)
    return states, [state for active in states.states for state in active]


def active_state_sequence(states):
    sequence = [active[-1] if active else "?" for active in states.states]
    compact = []
    for state in sequence:
        if not compact or compact[-1] != state:
            compact.append(state)
    return compact


def channel(trace, channel_id):
    data = trace.channel(channel_id)
    assert len(data.times) > 0, f"expected samples for {channel_id}"
    assert len(data.times) == len(data.values), f"expected aligned samples for {channel_id}"
    return data


print(f"mercurio {mercurio.__version__}  |  {WORKSPACE}")

with mercurio.open(WORKSPACE) as model:
    section("Parts")
    parts = model.parts()
    print(f"  total: {len(parts)}")
    for part in parts:
        indent = "  " + ("  " * part.depth)
        print(f"{indent}{part.name} : {part.kind}")

    expected_parts = ["bed", "hotend", "motion", "toolchanger", "electronics", "extruder"]
    for name in expected_parts:
        assert any(part.name == name for part in parts), f"expected part {name!r}"
    print("  PASS: core composed parts found")

    section("Part attribute access")
    bed = next(part for part in parts if part.name == "bed")
    print(f"  bed.attrs() = {bed.attrs()}")
    print(f"  bed.attr('heatRate') = {bed.attr('heatRate') or bed.attr('heat_rate')}")
    print("  PASS: attr access works")

    section("Analysis Cases")
    cases = model.analysis_cases()
    for case in cases:
        print(f"    [{case.id}]  label={case.label!r}  subjects={case.subject_count}")

    print_seq = next((case for case in cases if case.label == "PrintSequence"), None)
    assert print_seq is not None, "expected PrintSequence analysis case"
    assert print_seq.subject_count == len(EXPECTED_SUBJECTS), (
        f"expected {len(EXPECTED_SUBJECTS)} subjects, got {print_seq.subject_count}"
    )
    print("  PASS: PrintSequence exposes all replay subjects")

    section("Simulation: PrintSequence")
    trace = model.run_analysis("PrintSequence")
    print(f"  status   : {trace.status}")
    print(f"  scenario : {trace.scenario_id}")
    print(f"  duration : {trace.duration:.1f} s")
    print(f"  channels : {len(trace.channels)}")
    print(f"  timeline : {len(trace._timeline)} entries")
    for ch in trace.channels:
        print(f"    {ch.id}  source={ch.source}")

    assert trace.status == "completed", f"expected completed, got {trace.status!r}"
    assert trace.duration > 40.0, f"expected bed heat time, got {trace.duration}"
    print("  PASS: trace status and duration")

    section("State sequences")
    expected_state_markers = {
        "printer": ["Idle", "Homing", "Heating"],
        "motion": ["Parked", "Homing", "Rastering", "Complete"],
        "bed": ["Cold", "Heating", "Ready"],
        "hotend": ["Cold", "Heating", "Ready"],
        "extruder": ["Idle", "Priming", "Extruding", "Retracting"],
        "toolchanger": ["T0Loaded", "Changing", "T1Loaded"],
    }
    for subject in EXPECTED_SUBJECTS:
        states, flat = flattened_states(trace, subject)
        print(f"  {subject}: {' -> '.join(active_state_sequence(states))}")
        assert len(states.times) > 0, f"expected state entries for {subject}"
        for expected in expected_state_markers[subject]:
            assert any(expected in state for state in flat), (
                f"expected {expected!r} in {subject} states, got {flat}"
            )
    print("  PASS: all authored state machines executed")

    section("Parametric channels")
    bed_temp = channel(trace, "bed.temperature")
    hotend_temp = channel(trace, "hotend.temperature")
    motion_x = channel(trace, "motion.position_x")
    motion_y = channel(trace, "motion.position_y")
    filament = channel(trace, "extruder.filamentUsed")
    change = channel(trace, "toolchanger.changeProgress")

    print(f"  bed.temperature:              {bed_temp.values[0]:.1f} -> {bed_temp.values[-1]:.1f}")
    print(f"  hotend.temperature:           {hotend_temp.values[0]:.1f} -> {hotend_temp.values[-1]:.1f}")
    print(f"  motion.position_x:            {motion_x.values[0]:.1f} -> {motion_x.values[-1]:.1f}")
    print(f"  motion.position_y:            {motion_y.values[0]:.1f} -> {motion_y.values[-1]:.1f}")
    print(f"  extruder.filamentUsed:        {filament.values[0]:.1f} -> {filament.values[-1]:.1f}")
    print(f"  toolchanger.changeProgress:   {change.values[0]:.1f} -> {change.values[-1]:.1f}")

    assert bed_temp.values[-1] >= 110.0, "expected bed to reach target temperature"
    assert hotend_temp.values[-1] >= 245.0, "expected hotend to reach target temperature"
    assert motion_x.values[-1] >= 120.0, "expected homing X travel"
    assert motion_y.values[-1] >= 180.0, "expected rastering Y travel"
    assert filament.values[-1] >= 10.0, "expected filament accumulation"
    assert change.values[-1] >= 1.0, "expected completed tool change progress"
    print("  PASS: replay channels present and advancing")

section("ALL PASSING ASSERTIONS OK")
