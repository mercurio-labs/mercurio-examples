# Mercurio Examples Descriptor

This descriptor is the human-readable contract for the examples tree. The
examples are runnable evidence for public integration surfaces, not just sample
code snippets. When a new surface ships, add it here and then add or update the
corresponding example folder.

## Python Simulation Suite

| Directory | Status | Primary contract |
| --- | --- | --- |
| `python/simulation-state-machine/` | Runnable | Descriptor-backed state-machine analysis case; Python asserts trace states. |
| `python/simulation-constraints-channels/` | Runnable | State `do action` lowering, rate integration, and objective-derived trace channels. |
| `python/simulation-activity-readiness/` | Runnable | Activity dynamic-behavior projection or precise readiness diagnostics. |
| `python/simulation-variant-trade-study/` | Runnable | Temporary source variants, parameter edit, repeated simulation comparison. |
| `python/simulation-view-overlay/` | Runnable | Trace-to-overlay JSON plus part-tree projection over the small thermal model. |

## Python Semantic/API Suite

| Directory | Status | Primary contract |
| --- | --- | --- |
| `python/semantic-construction-typed/` | Runnable | Typed authoring, compile snapshot, descriptor-backed open, and semantic legality helper. |
| `python/capability-provider/` | Runnable | Process-backed capability stdin/stdout ABI, findings, table artifacts, evidence graph, and deterministic response metadata. |
| `python/rest-api-tour/` | Runnable | Plain-HTTP console API calls for health/version, workspace open, scoped editor/session endpoints, semantic legality, and cleanup. |
| `python/native-core/` | Probe | PyO3 native workspace open when `mercurio._core` is installed; successful skip otherwise. |
| `python/lab-notebook/` | Probe | Lab-kernel `LabModel` and parameter-sweep handles when `MERCURIO_LAB_KERNEL=1`; successful skip otherwise. |

## Python Semantic/API Coverage Matrix

| Feature / risk area | Typed construction | Capability provider | REST tour | Native probe | Lab probe |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fluent typed declarations | x |  |  | x |  |
| Requirement factory declaration | x |  |  |  |  |
| Generated SysML compile snapshot | x |  |  | x |  |
| Descriptor-backed project open | x |  | x | x | via workspace |
| Semantic legality helper | x |  | x |  | x |
| Process capability request validation |  | x |  |  |  |
| Reasoning report serialization |  | x |  |  |  |
| Table artifact and finding output |  | x |  |  |  |
| Evidence graph output |  | x |  |  |  |
| Plain HTTP route coverage |  |  | x |  |  |
| Scoped session cell run |  |  | x |  |  |
| Scoped workspace cleanup |  |  | x |  |  |
| In-process native workspace path |  |  |  | x |  |
| Lab handle creation and parameter sweep |  |  |  |  | x |

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
- Prefer small CI-stable fixtures for regression examples; keep rich product
  demonstrations such as Voron as canonical end-to-end evidence.
- If an example fails because the core behavior regressed, fix the core. If the
  public API intentionally changed, update the example and this descriptor in
  the same change.
