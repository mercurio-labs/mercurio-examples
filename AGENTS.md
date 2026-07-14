# mercurio-examples — Agent Orientation

Worked examples and integration test projects. Each subdirectory is self-contained and demonstrates a specific Mercurio capability. Examples are consumers of the Mercurio APIs — they must not introduce workarounds that paper over core bugs.

Examples are physically grouped by launch environment: `python/` (run with Python), `rust/` (run with Cargo), `desktop/` (opened in the desktop/workbench shell).

---

## Examples

Some examples span environments and appear in more than one table.

### Python

Run directly with Python against the SDK in `mercurio-host-adapters/python`.

| Directory | What it demonstrates |
|-----------|----------------------|
| `python/facade-tour/` | First-release Python facade tour: create/open/project, fluent declarations, compile snapshots, queries, analysis handles |
| `python/stdlib-authoring/` | `ModelBuilder` typed declarations, ISQ quantity kinds, SI units, generated SysML output |
| `python/pilot-authoring/` | Pilot-shaped authoring with metadata annotations, nested parts, states, transitions, semantic equivalence checks |
| `python/edit-existing/` | Descriptor-backed project editing: transactions, preview, apply, semantic queries, optional writeback |
| `python/model-graph-analysis/` | Compile SysML, extract the semantic graph, score candidates, D3 visualization |
| `python/simulation-*` | Small Python simulation fixtures: state-machine traces, objective channels, activity readiness, variants, trace overlays |
| `desktop/voron-trident-simulation/` | Python runtime model access, simulation execution, state timelines, trace channel reads |

### Rust

Compiled and run with Cargo from `mercurio-examples/`.

| Directory | What it demonstrates |
|-----------|----------------------|
| `rust/simple-language/` | Minimal custom language service: parses a line-oriented language into KIR |
| `rust/sysml-environment/` | Using the packaged SysML environment with the latest metamodel |

### Desktop UI

Opened as projects in the Mercurio desktop/workbench shell (`.project.json`
descriptors, plus `mercurio.extensions.json` where the project registers
local extensions).

| Directory | What it demonstrates |
|-----------|----------------------|
| `desktop/project-plugin-pacti-analysis/` | Project-local capability plugin: process-backed, static web view, Python wrapper |
| `desktop/structural-connectivity/` | NetworkX-backed structural connectivity analysis with table artifact output |
| `desktop/voron-trident-simulation/` | 3D printer simulation with registered replay view — primary integration test for the simulation engine |
| `desktop/vehicle-mass-compliance/` | Small analysis fixture for model/query/result/view and verification workflows |
| `python/model-graph-analysis/` | Descriptor-backed SysML model with graph-analysis assets and generated report output |

### Planned Examples (Not Yet Implemented)

The goal is one example per integration surface. The canonical
surface-by-surface coverage matrix lives in [README.md](README.md#coverage-matrix);
these directories are reserved but empty — do not reference them as runnable.

| Directory (planned) | Environment | Surface |
|-----------|-------------|---------|
| `python/capability-provider/` | Python | Standalone `mercurio_capability` process-provider SDK |
| `python/lab-notebook/` | Python | Lab kernel mode, `LabModel`, cell reports |
| `python/native-core/` | Python | Native PyO3 in-process mode (`mercurio._core`) |
| `python/rest-api-tour/` | Python (HTTP) | `mercurio-console-api` REST surface |
| `python/mcp-agent-session/` | Python (MCP) | MCP toolset, autonomy levels, change-task lifecycle |
| `rust/authoring/` | Rust | Native authoring builder (`AuthoringProject`) — mirrors `python/stdlib-authoring` + `python/pilot-authoring` |
| `rust/edit-existing/` | Rust | Native project editing + semantic mutation check/apply — mirrors `python/edit-existing` |
| `rust/graph-analysis/` | Rust | `mercurio_core::Graph` topology walk + report — mirrors `python/model-graph-analysis` |
| `rust/trade-study/` | Rust | `CoreSemanticVariantService` variant preview — mirrors facade-tour trade study |
| `rust/runtime-simulation/` | Rust | Deterministic runtime + simulation engine, native |
| `rust/query-dsl/` | Rust | Rhai query DSL in-process (`mercurio-query-dsl`) |
| `rust/model-store/` | Rust | `pkg:` addresses, `.mruntime` bundle, `LayeredRuntime` |
| `desktop/wasm-plugin-capability/` | Rust + desktop | WASM plugin ABI build + project-local registration |
| `browser/wasm-embedding/` | Browser | `mercurio-wasm` bindings: compile, lint, render, query |
| `desktop/ai-workbench/` | Desktop UI | AI ask/assessment/mutation-agent (needs configured provider) |
| `desktop/views-catalog/` | Desktop UI | View kind catalog — gated on `docs/visualization-plan.md` |

---

## The Voron Example

`desktop/voron-trident-simulation/` is the canonical integration target for the simulation pipeline. It is the verification script at the end of `../docs/archive/completed/codex-python-simulation-api.md`.

After implementing simulation API changes, verify with:

```python
import mercurio

with mercurio.open("mercurio-examples/desktop/voron-trident-simulation") as model:
    parts = model.parts()
    assert any(p.name == "bed" for p in parts)

    cases = model.analysis_cases()
    assert any(c.label == "PrintSequence" for c in cases)

    trace = model.run_analysis("PrintSequence")
    assert trace.status == "completed"

    bed_temp = trace.channel("bed.temperature")
    assert len(bed_temp.times) > 0
    assert bed_temp.values[0] == 22.0

    bed_states = trace.states("bed")
    assert "Cold" in bed_states.states[0]

print("all assertions passed")
```

---

## Build & Run

```powershell
cargo test                                             # all Rust examples
cargo run -p mercurio-simple-language --example compile
cargo run -p mercurio-sysml-environment-example
python mercurio-examples/python/model-graph-analysis/analyze_model_d3.py
```

---

## Key Constraint

If an example breaks after a core change, fix the core or update the example to match the new API — do not add core workarounds to preserve old example behaviour.
