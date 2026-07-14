# Mercurio Python API Examples

This folder is the Python-first progression for the public Mercurio facade:

```python
import mercurio
from mercurio import model
```

The scripts here avoid project-local desktop plugins and custom native binding
code. They are intended to be run directly with Python from the repository root.
Additional Python examples in sibling folders cover authoring, graph analysis,
capability providers, and simulation harnessing.

## Setup

Install the local SDK from the repository root:

```powershell
python -m pip install -e mercurio-host-adapters/python
```

Some examples require the native Mercurio extension or a Mercurio sidecar
because opening, compiling, querying, and analysis execution need the runtime.

Run a starter example:

```powershell
python mercurio-examples/python/facade-tour/01_create_in_memory.py
```

## Starter Progression

| Script | Demonstrates |
| --- | --- |
| `01_create_in_memory.py` | `mercurio.create(package=...)`, fluent declarations from `mercurio.model`, nested parts, attributes, typed usages, and `to_sysml()` without touching disk. |
| `02_create_and_save.py` | File-backed project creation, generated SysML output, and `Project.save()`. |
| `03_open_existing_project.py` | `mercurio.project(path)`, descriptor-backed project loading, `Project.compile()`, immutable snapshot revisions, and part-definition queries. |
| `04_query_snapshot.py` | `CompiledModel.part_def()`, semantic refs, containment traversal, part-usage filtering, and type-name inspection. |
| `05_edit_existing_project.py` | Safe copy-edit workflow, `Project.edit(ref)`, source-backed rename, `save()`, and changed-file detection. |
| `06_dsl_query.py` | Mercurio DSL query execution through `Project.query()` and shared session/cell plumbing. |
| `07_analysis_case.py` | `mercurio.open(path)`, runtime model context management, analysis handle lookup, spec inspection, expected artifacts, readiness, and `AnalysisHandle.run()`. |
| `08_trade_study_variants.py` | `Project.trade_study()`, low-cost variants, variant edits, and separate rendered SysML overlays. |

The `fixtures/` directory contains small descriptor-backed SysML projects used
by these scripts.

## Expanded Python API Coverage

The Python examples are split across the examples tree by scenario:

| API area | Example | What to look for |
| --- | --- | --- |
| Public facade | `python/*.py` | `open`, `create`, `project`, fluent declaration factories, source save, compile snapshots, semantic refs, DSL query, analysis handles, and variants. |
| Stdlib-aware authoring | `../stdlib-authoring/build_model.py` | `ModelBuilder`, ISQ quantity kinds, SI units, scalar value refs, typed attributes, and generated descriptor-backed output. |
| Pilot-style authoring | `../pilot-authoring/build_metadata_example.py` and `../pilot-authoring/build_state_definition_example.py` | Metadata definitions/usages, multi-target annotations, nested part trees, multiplicities, state definitions, transition shorthand, generated SysML, and save output. |
| Semantic equivalence | `../pilot-authoring/verify_equivalence.py` | `compare_semantic_snapshots()` over compiled Pilot source and generated Python-authored source. |
| Existing project mutation | `../edit-existing/edit_model.py` | `ModelBuilder.from_project()`, add-to-container mutations, stdlib refs, rename, diff, and source writeback. |
| Transaction preview/writeback | `../edit-existing/transaction_query_writeback.py` | `Project.transaction()`, semantic transaction preview, apply, query chaining, metatype filters, model-layer projection, and optional `--write`. |
| Graph analysis and sidecar control | `../model-graph-analysis/analyze_model_d3.py` | `Mercurio.launch()`, `Mercurio.connect()`, project graph reads, model topology analysis, and report generation outside desktop. |
| Runtime simulation API | `../voron-trident-simulation/sim/test_api.py` | Runtime parts, analysis-case discovery, `run_analysis()`, `SimulationTrace`, state timelines, channel reads, and assertion-friendly trace checks. |
| Native replay dashboard | `../voron-trident-simulation/sim/demo_qt.py` | Python-driven analysis execution with a native Qt visualization over the same trace data. |
| Process capability SDK | `../structural-connectivity/plugins/structural-connectivity/analyze_connectivity.py` | `mercurio_capability`, `CapabilityRequest`, findings, table artifacts, evidence graph, and stdin/stdout provider behavior. |
| Project-local capability wrapper | `../project-plugin-pacti-analysis/plugins/pacti-contract-analysis/analyze_pacti.py` | Stable JSON DTO boundary for a replaceable Python analysis adapter. |

## API Surface Checklist

Use this checklist when adding or reviewing Python examples:

| Python API surface | Covered by |
| --- | --- |
| In-memory source authoring | `01_create_in_memory.py` |
| File-backed source authoring and save | `02_create_and_save.py`, `../stdlib-authoring/` |
| Descriptor-backed open and compile | `03_open_existing_project.py`, `../edit-existing/` |
| Immutable semantic refs and query helpers | `04_query_snapshot.py`, `transaction_query_writeback.py` |
| Source edits through refs | `05_edit_existing_project.py`, `edit_model.py` |
| Transaction preview and apply | `transaction_query_writeback.py` |
| DSL query cells | `06_dsl_query.py` |
| Analysis spec and run reports | `07_analysis_case.py`, `voron-trident-simulation/sim/test_api.py` |
| Trade-study variants | `08_trade_study_variants.py` |
| Stdlib references | `../stdlib-authoring/`, `../edit-existing/` |
| Metadata, state, and transition authoring | `../pilot-authoring/` |
| Semantic snapshot comparison | `../pilot-authoring/verify_equivalence.py` |
| Graph, search, and backend escape hatches | `model-graph-analysis/` |
| Simulation traces and channels | `voron-trident-simulation/sim/test_api.py` |
| Process-backed capability authoring | `structural-connectivity/`, `project-plugin-pacti-analysis/` |

For complete API signatures, see
[`../../mercurio-host-adapters/python/API.md`](../../mercurio-host-adapters/python/API.md).
