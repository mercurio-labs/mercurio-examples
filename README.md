# Mercurio Examples

Small, runnable examples for embedding Mercurio language services in an app.

## Examples

`simple-language/` defines and registers a minimal custom language service. It
parses a tiny line-oriented language and emits KIR elements.

Run it with:

```powershell
cargo run -p mercurio-simple-language --example compile
```

`sysml-environment/` uses the packaged SysML language and the latest available
SysML metamodel.

Run it with:

```powershell
cargo run -p mercurio-sysml-environment-example
```

`model-graph-analysis/` is a Python analysis example that compiles a SysML
model, extracts the Mercurio graph, scores decision candidates, and writes an
interactive D3 HTML visualization.

Run it with:

```powershell
python mercurio-examples/model-graph-analysis/analyze_model_d3.py
```

`python/` is the first-release pure Python example set. It demonstrates the
small public API for creating in-memory projects, saving projects, opening
descriptor-backed projects, querying snapshots, editing source, running DSL
queries, inspecting analysis cases, and creating variants.

Run one example with:

```powershell
python mercurio-examples/python/01_create_in_memory.py
```

`project-plugin-pacti-analysis/` is a project-local capability plugin example.
It declares a process-backed contract-analysis capability, a static web view,
and a Python wrapper that can be replaced with a stock Pacti adapter while
preserving Mercurio's neutral JSON DTO boundary.

`vehicle-mass-compliance/` is the canonical small analysis fixture. It models a
vehicle mass requirement and an analysis case that should evolve into the first
end-to-end query, calculation, constraint, verification, evidence, and view
workflow.

Run all examples and tests with:

```powershell
cargo test
```
