# Structural Connectivity Example

This is a Mercurio desktop/workbench project that registers a project-local
Python capability for static structural analysis.

The model is `model/satellite-system.sysml`. It intentionally includes a
`DebugProbe` part-definition cluster that is not connected to the primary
`Satellite` hierarchy. The capability should report that disconnected component
as a warning.

## What It Shows

- `.project.json` descriptor-backed SysML project loading.
- `mercurio.extensions.json` project-local plugin registration.
- A process-backed Python capability provider.
- NetworkX analysis over a compiled Mercurio graph.
- Table artifacts, findings, and evidence graph output through the
  `mercurio_capability` SDK.
- A static plugin view declared by `views/connectivity-report/index.html`.

## Desktop Workflow

Open this folder in the Mercurio workbench:

```text
mercurio-examples/desktop/structural-connectivity
```

Then run the `Structural Connectivity Analysis` capability. The capability
provider is:

```text
plugins/structural-connectivity/analyze_connectivity.py
```

The provider receives a compiled graph payload, computes component connectivity
and PageRank-style centrality, and returns a table artifact plus warnings for
stranded structural components.

## Standalone Python Check

The provider also includes a synthetic-graph check that does not require a
running Mercurio backend:

```powershell
cd mercurio-examples/desktop/structural-connectivity/plugins/structural-connectivity
python -m pip install networkx
python test_standalone.py
```

The standalone script feeds a small graph that mirrors the satellite model and
prints the resulting findings and table artifact.
