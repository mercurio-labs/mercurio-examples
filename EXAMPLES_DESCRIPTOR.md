# Mercurio Examples Descriptor

This descriptor is the human-readable contract for the examples tree. Core
examples are runnable evidence for stable public interfaces. Backburner examples
are runnable integration coverage for surfaces that remain useful but are not
first-release API commitments.

## Core Python API Suite

| Directory | Status | Primary contract |
| --- | --- | --- |
| `python/facade-tour/` scripts 01-05 | Core | Stable facade: open, create, project, navigation, compile snapshots, semantic refs, source save, and source edits. |
| `python/stdlib-authoring/` | Core | Typed `ModelBuilder` authoring, stdlib references, generated SysML, and descriptor-backed output. |
| `python/pilot-authoring/` | Core | Fluent typed authoring for metadata, nested parts, state definitions, transitions, generated SysML, and equivalence checks. |
| `python/semantic-construction-typed/` | Core | Typed authoring, compile snapshot, descriptor-backed open, and semantic legality helper. |

## Backburner Python Simulation Suite

| Directory | Status | Primary contract |
| --- | --- | --- |
| `python/simulation-state-machine/` | Backburner runnable | Descriptor-backed state-machine analysis case; Python asserts trace states. |
| `python/simulation-constraints-channels/` | Backburner runnable | State `do action` lowering, rate integration, and objective-derived trace channels. |
| `python/simulation-activity-readiness/` | Backburner runnable | Activity dynamic-behavior projection or precise readiness diagnostics. |
| `python/simulation-variant-trade-study/` | Backburner runnable | Temporary source variants, parameter edit, repeated simulation comparison. |
| `python/simulation-view-overlay/` | Backburner runnable | Trace-to-overlay JSON plus part-tree projection over the small thermal model. |

## Backburner Python Integration Suite

| Directory | Status | Primary contract |
| --- | --- | --- |
| `python/facade-tour/` scripts 06-08 | Backburner runnable | DSL query, analysis execution, and trade-study variants. |
| `python/model-graph-analysis/` | Backburner runnable | Sidecar launch/connect, graph extraction, topology analysis, and D3 report generation. |
| `python/edit-existing/` | Backburner runnable | Source-backed project open, semantic refs, transaction preview/apply, and optional writeback. |
| `python/capability-provider/` | Backburner runnable | Process-backed capability stdin/stdout ABI, findings, table artifacts, evidence graph, and deterministic response metadata. |
| `python/rest-api-tour/` | Backburner runnable | Plain-HTTP console API calls for health/version, workspace open, scoped editor/session endpoints, semantic legality, and cleanup. |
| `python/native-core/` | Backburner probe | PyO3 native workspace open when `mercurio._core` is installed; successful skip otherwise. |
| `python/lab-notebook/` | Backburner probe | Lab-kernel `LabModel` and parameter-sweep handles when `MERCURIO_LAB_KERNEL=1`; successful skip otherwise. |

## Core Python API Coverage Matrix

| Feature / risk area | Facade 01-05 | Stdlib authoring | Pilot authoring | Typed construction |
| --- | ---: | ---: | ---: | ---: |
| `mercurio.create` | x |  |  | x |
| `mercurio.project` / descriptor-backed source open | x |  |  |  |
| `mercurio.open` / descriptor-backed model open | x |  |  | x |
| Fluent typed declarations | x | x | x | x |
| Stdlib references |  | x |  | x |
| Generated SysML output | x | x | x | x |
| Compile snapshots | x | x | x | x |
| Semantic refs and navigation | x |  |  | x |
| Source-backed edits | x |  |  |  |
| Semantic legality helper |  |  |  | x |

## Backburner Python Integration Coverage Matrix

| Feature / risk area | Capability provider | REST tour | Native probe | Lab probe | Facade 06-08 | Edit existing |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Process capability request validation | x |  |  |  |  |  |
| Reasoning report serialization | x |  |  |  |  |  |
| Table artifact and finding output | x |  |  |  |  |  |
| Evidence graph output | x |  |  |  |  |  |
| Plain HTTP route coverage |  | x |  |  |  |  |
| Scoped session cell run |  | x |  |  | x |  |
| Scoped workspace cleanup |  | x |  |  |  |  |
| In-process native workspace path |  |  | x |  |  |  |
| Lab handle creation and parameter sweep |  |  |  | x |  |  |
| Analysis execution and variants |  |  |  |  | x |  |
| Transaction preview/apply |  |  |  |  |  | x |

## Python Simulation Coverage Matrix

| Feature / risk area | State machine | Constraints/channels | Activity readiness | Variant study | View overlay | Voron canonical |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Descriptor-backed project open | x | x | x | x |  | x |
| Analysis spec and readiness inspection | x | x | x | x | x | x |
| State-machine execution | x | x |  | x | x | x |
| Simulation trace status/duration | x | x |  | x | x | x |
| State timeline assertions | x |  |  |  | x | x |
| Objective-derived trace channels |  | x |  | x | x | x |
| Constraint/rate-derived channels |  | x |  | x | x | x |
| Activity execution/readiness diagnostics |  |  | x |  |  |  |
| Source-backed parameter edit |  |  |  | x |  |  |
| Repeated-run trade-study comparison |  |  |  | x |  |  |
| Trace-backed view/overlay shape |  |  |  |  | x | partial |
| Model/part projection path |  |  |  |  | x | partial |

## Maintenance Rules

- Prefer descriptor-backed fixtures when an example is intended for both Python
  and desktop inspection.
- Keep the core Python examples focused on opening, creating, navigation,
  typed/fluent authoring, compile snapshots, and source-backed edits.
- Put REST, Lab, capability-provider, DSL/session, analysis execution,
  simulation, view rendering, and native-core probes in backburner sections until
  they are promoted deliberately.
- Prefer small CI-stable fixtures for regression examples; keep rich product
  demonstrations such as Voron as canonical end-to-end evidence.
- If an example fails because the core behavior regressed, fix the core. If the
  public API intentionally changed, update the example and this descriptor in
  the same change.
