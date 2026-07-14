# Python Simulation - State Machine

Small descriptor-backed simulation fixture for a single executable state
machine. The script opens the project through `mercurio.open()`, inspects the
analysis spec, runs the case, and asserts that the trace visits the expected
states.

```powershell
python mercurio-examples/python/simulation-state-machine/run_state_machine.py
```

