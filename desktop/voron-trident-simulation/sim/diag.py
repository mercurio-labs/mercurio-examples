"""Step-by-step diagnostic."""
import os, sys
from pathlib import Path
WORKSPACE = str(Path(__file__).resolve().parent.parent)
_dev_exe = Path(WORKSPACE).parent.parent.parent / "mercurio-product/target/debug/mercurio-console-api.exe"
if _dev_exe.exists():
    os.environ.setdefault("MERCURIO_EXE", str(_dev_exe))

from mercurio.backend import Mercurio
from mercurio.process import launch_backend

print("1. launching backend...")
backend = Mercurio.launch(timeout=30)
print(f"   ok - {backend.client.base_url}")

print("2. health check...")
print("  ", backend.health())

print("3. opening workspace (mode=compiled)...")
ws = backend.open_workspace(WORKSPACE, mode="compiled")
print(f"   workspace_id={ws.workspace_id!r}")

print("5. list_analysis_cases...")
cases = ws.list_analysis_cases()
print(f"   {cases}")

print("6. run_analysis PrintSequence...")
trace = ws.run_analysis("PrintSequence")
print(f"   status={trace.status} duration={trace.duration:.1f}s channels={len(trace.channels)}")

print("7. graph (scope=None, server default)...")
g = ws.graph()
print(f"   nodes={len(g.get('nodes', []))}")

print("8. graph scope=l2...")
g2 = ws.graph(scope="l2")
print(f"   nodes={len(g2.get('nodes', []))}")

print("\nALL STEPS PASSED")
backend.close()
