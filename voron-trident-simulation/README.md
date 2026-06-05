# Voron Trident 350 + Indx — Concurrent Simulation Example

This example demonstrates **Phase 4** of the Mercurio simulation stack:
concurrent multi-part simulation with cross-machine coordination.

## What it shows

Three state machines run simultaneously on a shared time axis:

| Machine | Subject | Behaviour |
|---|---|---|
| `VoronLifecycle` | `individual.printer` | Idle → Homing → Heating → Printing → ToolChange |
| `BedLifecycle` | `individual.bed` | Cold → Heating (Rate 2.3 °C/s) → Ready |
| `HotendLifecycle` | `individual.hotend` | Cold → Heating (Rate 5.0 °C/s) → Ready |

### Cross-machine coordination

When `BedLifecycle` reaches `Ready`, it fires an `Assign` effect that writes
`printer.bed_temperature = 110.0` into the shared execution context.

The printer machine is sitting in `Heating` with a `Change` guard:
```
when printer.bed_temperature >= 105
```

That guard evaluates against the same shared context, fires immediately, and
transitions the printer to `Printing` — without any explicit event.  This is
the cross-part guard pattern.

### Rate effects

While `individual.bed` is in `Heating`, a `Rate` effect advances
`bed.temperature` at **2.3 °C/s** and emits a trace sample every
`RATE_SAMPLE_INTERVAL_S` (1 second).  The trace therefore captures the full
thermal curve, not just the endpoints.

## Running

```
cargo run -p mercurio-voron-trident-simulation-example
```

Expected output (abbreviated):

```
t (s)  Printer             Bed                 Hotend              Bed °C   Hotend °C
──────────────────────────────────────────────────────────────────────────────────────
0.0    Idle                Cold                Cold                  22.0°      22.0°
1.0    Homing              Heating             Heating               24.3°      27.0°
2.0    Homing              Heating             Heating               26.6°      32.0°
3.5    Heating             Heating             Heating               29.0°      37.5°
...
38.3   Heating             Ready               Heating              110.0°     182.0°
38.3   Printing            Ready               Heating              110.0°     182.0°   ← cross-part Change fires
...
46.1   Printing            Ready               Ready                110.0°     250.0°
51.1   ToolChange          Ready               Ready                110.0°     250.0°
54.1   Printing2           Ready               Ready                110.0°     250.0°
```

The printer transitions to `Printing` the instant the bed crosses 105 °C —
driven by the simulation model, not a hardcoded timestamp.

## File layout

```
model/
  voron-trident-350.sysml   Structural SysML model and PrintSequence analysis case
sim/
  voron.sim3d.json          Project-owned 3D scene and visual binding config
assets/
  voron-trident-350.glb     Project-owned static printer geometry
src/
  main.rs                   Rust example — compiles SysML, patches executable semantics, runs concurrent sim
```

## Connecting to the visualisation

The `sim/voron.sim3d.json` config maps trace channels to project-owned 3D scene
objects and visual properties. The Mercurio product provides the generic
primitive renderer; the Voron-specific scene description lives with this
example project.

```tsx
import { SimulationPanel } from '@mercurio/workbench-ui';

// Compile the SysML source in WASM and run the simulation:
<SimulationPanel
  sources={[{ path: 'voron.sysml', content: sysmlSource }]}
  concurrent
/>
```

The `SimulationPanel` with `concurrent` prop opens the multi-subject picker,
compiles the source via WASM, runs `runConcurrentSimulation`, and renders the
result through the project `*.sim3d.json` config when the workspace contains
one.

## Key simulation concepts demonstrated

| Concept | Where |
|---|---|
| Concurrent state machines | Authored `state lifecycle` blocks in `voron-trident-350.sysml` |
| Rate effects | Overlayed `heating_ready` effects arrays for bed and hotend |
| Cross-machine Assign | Overlayed bed `heating_ready` writes `printer.bed_temperature` |
| Change guard (cross-part) | Overlayed printer `heating_printing` guard reads `printer.bed_temperature` |
| Shared execution context | Single `BTreeMap<(subject_id, feature), Value>` across all machines |

## Analysis case scenario

The state-machine topology is compiled from `voron-trident-350.sysml`. The
executable run is sourced from `analysis.PrintSequence`, a
`SysML::Systems::AnalysisCaseDefinition` KIR element appended by the Rust
example for the scenario metadata that is not yet lowerable from authored
SysML. It declares the simulation subjects, initial values, objective channels,
compiled initial states, and injected `start` event. The Rust example extracts
that analysis case into a `ConcurrentSimulationScenario` immediately before
calling the engine.
