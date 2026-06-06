"""
Verification script for the mercurio Python simulation API.
Runs against the Voron Trident 350 example workspace.

STATUS:
  PASS  mercurio.open() / backend launch
  PASS  model.parts()              -- 17 parts returned
  PASS  model.analysis_cases()     -- PrintSequence found
  PASS  model.run_analysis()       -- completed
  PASS  trace.states()             -- state sequences tracked
  PASS  trace.channels / trace.channel()
        bed and hotend temperatures are integrated from textual state
        do actions compiled into KIR do_behavior.
"""

import os
from pathlib import Path
WORKSPACE = str(Path(__file__).resolve().parent.parent)
_dev_exe = Path(WORKSPACE).parent.parent / "mercurio-product/target/debug/mercurio-console-api.exe"
if _dev_exe.exists():
    os.environ.setdefault("MERCURIO_EXE", str(_dev_exe))

import mercurio

def section(label):
    print(f"\n{'=' * 55}")
    print(f"  {label}")
    print('=' * 55)

print(f"mercurio {mercurio.__version__}  |  {WORKSPACE}")

with mercurio.open(WORKSPACE) as model:

    # ── Parts ─────────────────────────────────────────────────────────────────
    section("Parts")
    parts = model.parts()
    print(f"  total: {len(parts)}")
    for p in parts:
        indent = "  " + ("  " * p.depth)
        print(f"{indent}{p.name} : {p.kind}")

    assert len(parts) > 0,                               "expected parts"
    assert any(p.name == "bed" for p in parts),          "expected 'bed'"
    assert any(p.name == "hotend" for p in parts),       "expected 'hotend'"
    assert any(p.name == "motion" for p in parts),       "expected 'motion'"
    assert any(p.name == "toolchanger" for p in parts),  "expected 'toolchanger'"
    assert any(p.name == "electronics" for p in parts),  "expected 'electronics'"
    print("  PASS: all part assertions")

    # ── Attribute access ───────────────────────────────────────────────────────
    section("Part attribute access")
    bed = next(p for p in parts if p.name == "bed")
    print(f"  bed.attrs() = {bed.attrs()}")
    heat_rate = bed.attr("heatRate") or bed.attr("heat_rate")
    print(f"  bed.attr('heatRate') = {heat_rate}")
    print("  PASS: attr access works (values depend on KIR property inclusion)")

    # ── Analysis cases ────────────────────────────────────────────────────────
    section("Analysis Cases")
    cases = model.analysis_cases()
    print(f"  found {len(cases)}:")
    for c in cases:
        print(f"    [{c.id}]  label={c.label!r}  subjects={c.subject_count}")

    assert len(cases) >= 1,                                   "expected at least one"
    assert any(c.label == "PrintSequence" for c in cases),    "expected PrintSequence"
    print_seq = next(c for c in cases if c.label == "PrintSequence")
    assert print_seq.subject_count == 3,                      f"expected 3 subjects, got {print_seq.subject_count}"
    print("  PASS: all analysis case assertions")

    # ── Run simulation ────────────────────────────────────────────────────────
    section("Simulation: PrintSequence")
    trace = model.run_analysis("PrintSequence")
    print(f"  status   : {trace.status}")
    print(f"  scenario : {trace.scenario_id}")
    print(f"  duration : {trace.duration:.1f} s")
    print(f"  channels : {len(trace.channels)}")
    print(f"  timeline : {len(trace._timeline)} entries")
    for ch in trace.channels:
        print(f"    {ch.id}  source={ch.source}")

    assert trace.status == "completed",     f"expected completed, got {trace.status!r}"
    assert trace.duration > 40.0,           f"expected >40s (bed heat time), got {trace.duration}"
    print("  PASS: trace status and duration")

    # ── State sequences ───────────────────────────────────────────────────────
    section("States: bed")
    bed_states = trace.states("bed")
    print(f"  {len(bed_states.times)} state entries")
    for t, s in zip(bed_states.times, bed_states.states):
        print(f"    t={t:6.1f}s  {s}")

    assert len(bed_states.times) > 0,           "expected bed state entries"
    all_bed = [s for ss in bed_states.states for s in ss]
    assert any("Cold" in s for s in all_bed),   f"expected Cold in bed states, got {all_bed}"
    assert any("Heating" in s for s in all_bed), f"expected Heating in bed states, got {all_bed}"
    print("  PASS: bed states (Cold -> Heating sequence found)")

    section("States: hotend")
    hotend_states = trace.states("hotend")
    all_hotend = [s for ss in hotend_states.states for s in ss]
    print(f"  sequence: {hotend_states.states}")
    assert len(hotend_states.times) > 0,             "expected hotend state entries"
    assert any("Heating" in s for s in all_hotend),  f"expected Heating in hotend states"
    print("  PASS: hotend states")

    section("States: printer")
    printer_states = trace.states("printer")
    all_printer = [s for ss in printer_states.states for s in ss]
    print(f"  sequence: {printer_states.states}")
    assert len(printer_states.times) > 0,  "expected printer state entries"
    print("  PASS: printer states")

    # ── Known gap: channels ───────────────────────────────────────────────────
    section("Rate channels")
    print(f"  channels={len(trace.channels)}")
    assert len(trace.channels) > 0, "expected rate channels"
    bed_ch = trace.channel("bed.temperature")
    print(f"  bed.temperature: {len(bed_ch.times)} samples")
    print(f"  first: t={bed_ch.times[0]}, temp={bed_ch.values[0]}")
    print(f"  last:  t={bed_ch.times[-1]:.1f}, temp={bed_ch.values[-1]:.1f}")
    assert len(bed_ch.times) > 10, "expected sampled bed temperature channel"
    assert bed_ch.values[-1] >= 110.0, "expected bed to reach target temperature"
    print("  PASS: rate channels present and extractable")

section("ALL PASSING ASSERTIONS OK")
