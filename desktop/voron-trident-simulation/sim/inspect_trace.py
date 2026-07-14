"""Inspect raw trace structure to find correct subject IDs."""
import os, json
from pathlib import Path
WORKSPACE = str(Path(__file__).resolve().parent.parent)
_dev_exe = Path(WORKSPACE).parent.parent.parent / "mercurio-product/target/debug/mercurio-console-api.exe"
if _dev_exe.exists():
    os.environ.setdefault("MERCURIO_EXE", str(_dev_exe))

import mercurio

with mercurio.open(WORKSPACE) as model:
    trace = model.run_analysis("PrintSequence")
    print(f"status={trace.status}  duration={trace.duration}  timeline_entries={len(trace._timeline)}")
    print()
    for i, entry in enumerate(trace._timeline):
        print(f"--- entry {i}  t={entry.get('t')} ---")
        print(f"  states keys: {list(entry.get('states', {}).keys())}")
        print(f"  states:      {entry.get('states')}")
        print(f"  values keys: {list(entry.get('values', {}).keys())[:8]}")
        print(f"  events:      {entry.get('events')}")
