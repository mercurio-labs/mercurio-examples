# Project Plugin Pacti Analysis

This example shows a project-local Mercurio capability plugin. The Mercurio UI
does not need to know about Python or Pacti: it discovers a neutral capability,
plans it, asks for workspace trust, and then invokes the declared process
provider with JSON over stdin/stdout.

The plugin lives in `plugins/pacti-contract-analysis` and declares:

- a `process` provider: `python plugins/pacti-contract-analysis/analyze_pacti.py`
- a static view asset: `views/contract-summary/index.html`
- permissions: workspace read, no network, no source mutation

The core `.project.json` describes the SysML model and stdlib dependency;
`mercurio.extensions.json` registers the project-local plugin.

The Python wrapper currently emits a deterministic example report. A real Pacti
wrapper can replace the body of `analyze_pacti.py` while preserving the same
Mercurio DTO boundary.
