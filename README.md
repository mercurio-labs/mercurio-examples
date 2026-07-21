# Mercurio Examples

Runnable examples for the main Mercurio integration surfaces, physically
grouped by the environment they are launched from:

- `python/` — scripts run directly with Python against the Python SDK.
- `rust/` — raw Rust examples compiled and run with Cargo.
- `desktop/` — projects opened in the Mercurio desktop/workbench shell.

## Core Python API Examples

Use this section when validating the stable Python SDK: model opening,
creation, navigation, typed/fluent authoring, compile snapshots, and
source-backed edits. Install the local SDK from the repository root if needed:

```powershell
python -m pip install -e mercurio-host-adapters
```

Advanced REST, Lab, capability, simulation, DSL, view, and native probes live
under [Backburner Python Examples](#backburner-python-examples). They are useful
integration coverage, but they are not the stable Python interface.

| Directory | Run | Stable Python API coverage |
| --- | --- | --- |
| `python/facade-tour/` | `python mercurio-examples/python/facade-tour/01_create_in_memory.py` | Stable facade progression in scripts 01-05: `mercurio.create`, `mercurio.project`, `mercurio.open`, fluent declarations, source save, compile snapshots, semantic refs, navigation, and source edits. Scripts 06-08 are backburner DSL/analysis/variant coverage. |
| `python/stdlib-authoring/` | `cd mercurio-examples/python/stdlib-authoring; python build_model.py` | `ModelBuilder`, typed declarations, ISQ quantity kinds, SI units, scalar value refs, generated SysML, and descriptor-backed output. |
| `python/pilot-authoring/` | `cd mercurio-examples/python/pilot-authoring; python build_metadata_example.py` | Pilot-shaped authoring with metadata annotations, multi-target metadata usage, nested parts, states, transitions, generated SysML, and semantic equivalence checks. |
| `python/semantic-construction-typed/` | `python mercurio-examples/python/semantic-construction-typed/build_typed_model.py` | Semantic construction using typed elements, fluent declarations, compile snapshots, descriptor-backed open, and semantic legality checks. |

## Backburner Python Examples

These examples remain runnable integration coverage, but they intentionally do
not define the stable Python interface.

| Directory | Run | Backburner coverage |
| --- | --- | --- |
| `python/model-graph-analysis/` | `python mercurio-examples/python/model-graph-analysis/analyze_model_d3.py` | Backend launch/connect, graph extraction, model topology analysis, candidate scoring, and portable D3 report generation. |
| `python/edit-existing/` | `cd mercurio-examples/python/edit-existing; python transaction_query_writeback.py` | Descriptor-backed project editing, transactions, preview, apply, semantic queries, metatype traversal, and optional writeback with `--write`. |
| `python/capability-provider/` | `python mercurio-examples/python/capability-provider/test_provider.py` | Standalone process-backed capability provider, `CapabilityRunner`, request/response DTOs, findings, artifacts, evidence graph, and local ABI verification. |
| `python/rest-api-tour/` | `python mercurio-examples/python/rest-api-tour/run_rest_api_tour.py` | Plain-HTTP `mercurio-console-api` tour: health/version, workspace open, scoped files, session cell run, semantic legality, and cleanup. |
| `python/native-core/` | `python mercurio-examples/python/native-core/probe_native_core.py` | In-process PyO3 native core probe with descriptor-backed open when `mercurio._core` is installed; clean skip in source-only Python environments. |
| `python/lab-notebook/` | `python mercurio-examples/python/lab-notebook/probe_lab_kernel.py` | Lab kernel mode probe, `LabModel`, parameter sweep handles, and semantic helper delegation when a Lab workspace is active. |
| `python/simulation-state-machine/` | `python mercurio-examples/python/simulation-state-machine/run_state_machine.py` | Small descriptor-backed state-machine simulation and Python state timeline assertions. |
| `python/simulation-constraints-channels/` | `python mercurio-examples/python/simulation-constraints-channels/run_constraints_channels.py` | Objective projection and trace channel reads without relying on state `do_behavior`. |
| `python/simulation-activity-readiness/` | `python mercurio-examples/python/simulation-activity-readiness/inspect_activity_readiness.py` | Activity dynamic-behavior projection where supported, with readiness diagnostics otherwise. |
| `python/simulation-variant-trade-study/` | `python mercurio-examples/python/simulation-variant-trade-study/run_variant_trade_study.py` | Temporary simulation variants, parameter edits, repeated runs, and trace comparison. |
| `python/simulation-view-overlay/` | `python mercurio-examples/python/simulation-view-overlay/render_trace_overlay.py` | Trace-to-overlay JSON shape and part-tree projection over the small thermal model. |
| `desktop/voron-trident-simulation/` | `cd mercurio-examples; python .\desktop\voron-trident-simulation\sim\test_api.py` | Python runtime model access, part discovery, analysis-case discovery, simulation execution, state timelines, and trace channel reads. |

See [`python/facade-tour/README.md`](python/facade-tour/README.md) for the
expanded Python API map and script-by-script progression.
See [`EXAMPLES_DESCRIPTOR.md`](EXAMPLES_DESCRIPTOR.md) for the example coverage
contract and the stable/backburner matrix.

### Planned Python Examples

Not yet implemented. These fill the Python-launched coverage gaps listed in
[Coverage Matrix](#coverage-matrix).

| Directory (planned) | Will demonstrate |
| --- | --- |
| `python/mcp-agent-session/` | MCP client session against the console-api MCP endpoint: tool discovery, autonomy levels (L0-L3), `create_model`, `query_model`, `check_changes`/`apply_changes`, and the task lifecycle. |

## Desktop Projects

Use this section for examples that are meant to be opened as Mercurio desktop
or workbench projects. These folders contain `.project.json` descriptors and,
where needed, `mercurio.extensions.json` project-local extension manifests.

| Directory | Open or run in desktop | What it demonstrates |
| --- | --- | --- |
| `desktop/project-plugin-pacti-analysis/` | Open the folder in the workbench. | Project-local process-backed capability, neutral JSON DTO boundary, declared plugin permissions, and static report view. |
| `desktop/structural-connectivity/` | Open the folder in the workbench and run the Structural Connectivity capability. | NetworkX-backed static analysis over the compiled graph, connectivity findings, table artifact output, and project-local plugin registration. |
| `desktop/voron-trident-simulation/` | Open the folder and choose `View -> Voron Print Sequence`. | Descriptor-backed simulation project, registered Python replay view, concurrent state-machine execution, and project-owned 3D scene assets. |
| `desktop/vehicle-mass-compliance/` | Open the folder and run the documented Analysis dock queries. | Small analysis fixture for model/query/result/view and analysis/calculation/constraint/verification/evidence workflows. |
| `python/model-graph-analysis/` | Open the folder when inspecting the descriptor-backed model; run the Python script for the D3 report. | Descriptor-backed SysML model with graph-analysis assets and generated report output. |

Python authoring examples such as `python/stdlib-authoring/` and
`python/pilot-authoring/` generate output that can also be opened in desktop
after the Python script has produced the referenced `output/*.sysml` files.

### Planned Desktop Examples

| Directory (planned) | Will demonstrate |
| --- | --- |
| `desktop/wasm-plugin-capability/` | Project-local WASM plugin registration and execution: the WASM plugin ABI (`memory`, `mercurio_alloc`, service `(i32,i32)->i64`) as the counterpart to the process-backed capabilities in `desktop/project-plugin-pacti-analysis/` and `desktop/structural-connectivity/`. The plugin itself is a Rust wasm32 crate inside the project; cross-listed under Raw Rust Examples. |
| `desktop/ai-workbench/` | AI workbench flows: ask, semantic assessment, and agent-driven semantic mutation check/apply against a small model. Requires a configured AI provider; scope tracks `docs/action-space-plan.md`. |
| `desktop/views-catalog/` | The diagram/table/view kind catalog rendered over a small model. Gated on the visualization plan (`docs/visualization-plan.md`); do not start until the view contract lands. |

## Raw Rust Examples

Use this section when validating Mercurio as a Rust library dependency or when
working on language-service integration without Python or desktop involved.

Run from `mercurio-examples/`:

```powershell
cargo test
cargo run -p mercurio-simple-language --example compile
cargo run -p mercurio-sysml-environment-example
```

| Directory | What it demonstrates |
| --- | --- |
| `rust/simple-language/` | Minimal custom `LanguageService`, registration through `LanguageRegistry`, and direct KIR emission from a tiny non-SysML language. |
| `rust/sysml-environment/` | Native Rust use of the packaged SysML environment and latest metamodel to compile in-memory SysML source. |

### Planned Rust Examples

The Python examples are thin wrappers over native crates (via PyO3), so each
Python example should eventually have a Rust mirror that drives the same crate
directly. Mirrors reuse the same fixtures so outputs are comparable.

| Directory (planned) | Will demonstrate |
| --- | --- |
| `rust/authoring/` | The native authoring builder (`AuthoringProject` in `mercurio-sysml` — the same surface `mercurio._core.ModelBuilder` wraps): package/part/attribute/state declarations, per-mutation validation, and generated SysML writeback. Mirrors `python/stdlib-authoring/` and `python/pilot-authoring/`. |
| `rust/edit-existing/` | Opening an existing descriptor-backed project natively, mutating it through the authoring project, and semantic mutation check/apply via `mercurio-semantic-services`. Mirrors `python/edit-existing/`. |
| `rust/graph-analysis/` | Compile a fixture, build `mercurio_core::Graph`, walk topology and metamodel views, and emit a machine-readable report. Mirrors `python/model-graph-analysis/` without the D3 rendering. |
| `rust/trade-study/` | Variant preview and comparison through `CoreSemanticVariantService` (`mercurio-semantic-services`). Mirrors the trade-study script in `python/facade-tour/`. |
| `rust/runtime-simulation/` | The deterministic runtime and simulation engine driven directly from Rust: compile a model, run an analysis case, read state timelines and trace channels. Native counterpart to the Voron Python verification script. |
| `rust/query-dsl/` | The Rhai-backed query DSL (`mercurio-query-dsl`) evaluated in-process against a compiled model — the same DSL the Python `query()` helpers and desktop Analysis dock send over HTTP. Mirrors `python/facade-tour/06_dsl_query.py`. |
| `rust/model-store/` | The model store runtime: canonical `pkg:` stdlib address, loading the prebuilt `.mruntime` bundle, and `LayeredRuntime` base+overlay composition. |
| `desktop/wasm-plugin-capability/` | Building a wasm32 plugin that exports the WASM plugin ABI and invoking it through the plugin host. Physical home is under `desktop/`; listed here because the plugin crate is built with Cargo. |

## Browser (WASM) Examples

No examples exist yet for the browser embedding surface. `mercurio-wasm`
exposes compile, lint, format, diagram/table/view rendering, runtime queries,
and assessments to JavaScript.

| Directory (planned) | Will demonstrate |
| --- | --- |
| `browser/wasm-embedding/` | A minimal static page embedding `mercurio-wasm`: `compileSysml`, `lint`, `renderDiagram`, and `queryRuntime` running fully in the browser with no backend process. |

## Capability And Fixture Examples

Some examples intentionally bridge categories:

- `desktop/project-plugin-pacti-analysis/` and `desktop/structural-connectivity/`
  are desktop projects, but their capability providers are Python scripts that
  can be inspected or tested independently.
- `desktop/voron-trident-simulation/` is the canonical simulation integration
  target for both desktop replay and Python runtime verification.
- `desktop/vehicle-mass-compliance/` is intentionally small so it can be reused
  by desktop, Python, REST, and notebook workflows as the common analysis
  fixture.

## Coverage Matrix

The target is one example (or one clearly named section of an example) per
integration surface. "Existing" examples run today; "planned" directories are
listed in the per-environment tables above and do not exist yet.

| Surface / capability | Existing coverage | Planned |
| --- | --- | --- |
| Python facade: open, create, project, navigation | `python/facade-tour/` scripts 01-05, `python/semantic-construction-typed/` | — |
| Authoring builder: typed declarations, generated SysML (`AuthoringProject`; Python `ModelBuilder`) | `python/stdlib-authoring/`, `python/pilot-authoring/`, `python/semantic-construction-typed/` | `rust/authoring/` |
| Project editing: transactions, preview/apply, writeback | `python/edit-existing/` (backburner) | `rust/edit-existing/` |
| Trade studies and variants | `python/facade-tour/` script 08 (backburner) | `rust/trade-study/` |
| Semantic graph extraction and analysis | `python/model-graph-analysis/` (backburner) | `rust/graph-analysis/` |
| Simulation execution, state timelines, trace channels | `desktop/voron-trident-simulation/` (Python + desktop), `python/simulation-state-machine/`, `python/simulation-constraints-channels/` (backburner Python API) | `rust/runtime-simulation/` |
| Simulation readiness, variants, and trace overlays | `python/simulation-activity-readiness/`, `python/simulation-variant-trade-study/`, `python/simulation-view-overlay/` (backburner Python API) | deeper diagram overlay examples after `docs/visualization-plan.md` V-3 |
| Query DSL (Rhai) | `python/facade-tour/` script 06 (backburner) | `rust/query-dsl/` (in-process) |
| Process-backed capability SDK (stdin/stdout ABI) | `desktop/project-plugin-pacti-analysis/`, `desktop/structural-connectivity/`, `python/capability-provider/` (backburner) | deeper project-registration matrix coverage |
| WASM plugin ABI | — | `desktop/wasm-plugin-capability/` |
| Lab / notebook kernel mode | `python/lab-notebook/` (backburner probe) | richer notebook cell-report example |
| Native PyO3 in-process mode (`mercurio._core`) | `python/native-core/` (backburner probe) | deeper semantic workspace mutation example |
| REST API (`mercurio-console-api`) | `python/rest-api-tour/` (backburner) | mutation check/apply writeback flow |
| MCP tool surface | — | `python/mcp-agent-session/` |
| Browser WASM bindings | — | `browser/wasm-embedding/` |
| Model store runtime (`pkg:` addresses, `.mruntime`, `LayeredRuntime`) | — | `rust/model-store/` |
| Custom language services (non-SysML source → KIR) | `rust/simple-language/` | — |
| Packaged SysML environment from Rust | `rust/sysml-environment/` | — |
| Desktop registered views / simulation replay | `desktop/voron-trident-simulation/` | `desktop/views-catalog/` (gated) |
| Desktop analysis dock workflows | `desktop/vehicle-mass-compliance/` | — |
| AI workbench and semantic-mutation agent | — | `desktop/ai-workbench/` (needs configured provider) |

When a new integration surface ships, add a row here first, then the example.

## Maintenance Rule

If an example breaks after a core change, fix the core or update the example to
match the new API. Do not add local workarounds that preserve obsolete behavior.
