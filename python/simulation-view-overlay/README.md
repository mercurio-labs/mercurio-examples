# Python Simulation - View Overlay

Runs the small thermal-channel simulation and projects selected trace data into
a portable overlay JSON artifact. This is the Python-side smoke shape for future
trace-backed diagram overlays; today it verifies state timelines, channels, and
part-tree projection without depending on the larger Voron fixture.

```powershell
python mercurio-examples/python/simulation-view-overlay/render_trace_overlay.py
python mercurio-examples/python/simulation-view-overlay/render_trace_overlay.py --write
```
