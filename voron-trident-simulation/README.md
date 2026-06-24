# Voron Trident 350 Simulation Project

This folder is a pure Mercurio simulation project. It contains the authored
SysML model, the project-owned 3D scene configuration, a GLB asset used by the
generic workbench renderer, and Python scripts that exercise the simulation
interface.

## Running

Open this folder in the Mercurio workbench and choose
**View -> Voron Print Sequence**. The core project descriptor identifies the
SysML entrypoint; `mercurio.extensions.json` registers `sim/launch.py` as a
`python_process` view with `protocol: "legacy_process"` and `kind:
"simulation"`, so it appears as a normal registered project view.

The workbench:

1. Compiles `model/voron-trident-350.sysml`.
2. Discovers the authored `PrintSequence` analysis case.
3. Extracts the analysis-case subjects and initial assumptions.
4. Runs the concurrent simulation engine.
5. Launches the Python replay window.

For a headless check:

```powershell
cd mercurio-examples
python .\voron-trident-simulation\sim\test_api.py
```

## File Layout

```text
model/
  voron-trident-350.sysml   Structural SysML model and PrintSequence analysis case
sim/
  demo_qt.py                Native PyQt replay dashboard
  test_api.py               Headless Python API verifier
  voron.sim3d.json          Project-owned 3D scene and visual binding config
  launch.py                 Registered simulation view launcher
assets/
  voron-trident-350.glb     Project-owned static printer geometry
```

## What It Shows

Six state machines are authored in the SysML source and executed from one
analysis case:

| Machine | Subject | Composition Level | Behaviour |
|---|---|---|---|
| `VoronLifecycle` | `printer` | Top-level printer context | Idle -> Homing -> Heating -> Printing -> ToolChange |
| `Motion lifecycle` | `motion` | Direct subsystem | Parked -> Homing -> Ready -> Rastering -> Complete |
| `BedLifecycle` | `bed` | Direct subsystem | Cold -> Heating -> Ready |
| `HotendLifecycle` | `hotend` | Direct subsystem | Cold -> Heating -> Ready |
| `FilamentDrive lifecycle` | `extruder` | Nested toolchanger subsystem type | Idle -> Priming -> Extruding -> Retracting |
| `Toolchanger lifecycle` | `toolchanger` | Direct subsystem with nested `extruder` part | T0Loaded -> Changing -> T1Loaded |

`PrintSequence` declares all six subjects and initial value assumptions. The
simulation extractor injects the conventional `start` event for machines that
declare a `start` transition, so the scenario can run from authored SysML
without a project-local Rust bridge.

## Visualization

`sim/demo_qt.py` runs the analysis through the Python API and opens a native Qt
window. The main replay panel shows all state machines in one animated view and
normalizes the relevant parametric values in the same timeline:

- `bed.temperature`
- `hotend.temperature`
- `motion.position_x`
- `motion.position_y`
- `extruder.filamentUsed`
- `toolchanger.changeProgress`

The same window also includes a transition log, analysis-case summary, model
parts table, and a 3D final-state schematic coloured by subsystem state.

`sim/voron.sim3d.json` remains the declarative scene-binding example for the
generic renderer. The Python dashboard is the integration test for direct
simulation harnessing from Python.
