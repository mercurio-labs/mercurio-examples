# Model Graph Analysis With D3

This example is analysis-only. It compiles a SysML model, reads the Mercurio
semantic graph through the Python SDK, performs a small topology-based decision
analysis, and writes an interactive D3 HTML graph.

It does not call the simulation API and does not require a simulation binding.

## What It Shows

- `model/decision-review.sysml` defines a payload architecture review model.
- `analyze_model_d3.py` compiles the model and requests `workspace.graph(scope="l2")`.
- The Python script identifies decision candidates from element kind, name,
  properties, and graph degree.
- The generated HTML uses D3 force layout to visualize the model and highlights
  the decision candidates in the side panel.

## Running

Install the Python SDK in editable mode from the repository root if needed:

```powershell
python -m pip install -e mercurio-host-adapters/python
```

Then run:

```powershell
python mercurio-examples/python/model-graph-analysis/analyze_model_d3.py
```

If you already have a compatible Mercurio backend running, attach to it instead:

```powershell
python mercurio-examples/python/model-graph-analysis/analyze_model_d3.py --backend-url http://127.0.0.1:49152
```

The script prefers a repo-local `mercurio-console-api` binary when it exists.
If launch falls back to a command-based `mercurio.exe` on `PATH`, pass the
console API executable explicitly:

```powershell
python mercurio-examples/python/model-graph-analysis/analyze_model_d3.py --executable mercurio-product/target/debug/mercurio-console-api.exe
```

The script writes:

```text
mercurio-examples/python/model-graph-analysis/out/decision-review.html
```

Open that file in a browser. By default, the page imports D3 from jsDelivr.
For offline use, pass `--d3-url` with a local D3 ES module URL.

## Design Decisions

- The example lives outside `sim/` and avoids the simulation API so it is clearly
  an analysis example.
- Python owns the analysis decision logic; D3 owns only the visualization.
- The HTML embeds the analyzed graph data so the generated report is portable.
- D3 is loaded by URL rather than vendored into the repository.
