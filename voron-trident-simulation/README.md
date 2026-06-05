# Voron Trident 350 Simulation Project

This folder is a pure Mercurio simulation project. It contains the authored
SysML model, the project-owned 3D scene configuration, and the GLB asset used
by the generic workbench renderer. It does not build or ship a project-local
Rust executable.

## Running

Open this folder in the Mercurio workbench and choose **View -> Simulate**.
The workbench:

1. Compiles `model/voron-trident-350.sysml`.
2. Discovers the authored `PrintSequence` analysis case.
3. Extracts the analysis-case subjects and initial assumptions.
4. Runs the concurrent simulation engine.
5. Renders `sim/voron.sim3d.json` with `assets/voron-trident-350.glb`.

## File Layout

```text
model/
  voron-trident-350.sysml   Structural SysML model and PrintSequence analysis case
sim/
  voron.sim3d.json          Project-owned 3D scene and visual binding config
assets/
  voron-trident-350.glb     Project-owned static printer geometry
```

## What It Shows

Three state machines are authored in the SysML source:

| Machine | Subject | Behaviour |
|---|---|---|
| `VoronLifecycle` | `printer` | Idle -> Homing -> Heating -> Printing -> ToolChange |
| `BedLifecycle` | `bed` | Cold -> Heating -> Ready |
| `HotendLifecycle` | `hotend` | Cold -> Heating -> Ready |

The `PrintSequence` analysis case declares the simulation subjects and initial
temperature assumptions. The simulation extractor injects the conventional
`start` event for machines that declare a `start` transition, so the scenario
can run from the authored model without a project-local Rust bridge.

## Visualization

`sim/voron.sim3d.json` maps simulation trace channels to scene properties. The
static printer frame is loaded from `assets/voron-trident-350.glb`; trace-driven
overlays such as the heated bed and active toolhead remain declarative scene
objects in the JSON config.

The Mercurio product provides the renderer runtime. This project only carries
model data, scene config, and assets, so it can be managed separately from the
product repository.
