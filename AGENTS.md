# mercurio-examples — Agent Orientation

Worked examples and integration test projects. Each subdirectory is self-contained and demonstrates a specific Mercurio capability. Examples are consumers of the Mercurio APIs — they must not introduce workarounds that paper over core bugs.

---

## Examples

| Directory | Language | What it demonstrates |
|-----------|----------|----------------------|
| `simple-language/` | Rust | Minimal custom language service: parses a line-oriented language into KIR |
| `sysml-environment/` | Rust | Using the packaged SysML environment with the latest metamodel |
| `model-graph-analysis/` | Python | Compile SysML, extract the semantic graph, score candidates, D3 visualization |
| `project-plugin-pacti-analysis/` | Python + Rust | Project-local capability plugin: process-backed, static web view, Python wrapper |
| `structural-connectivity/` | Mixed | Structural connectivity analysis |
| `voron-trident-simulation/` | SysML + Python | 3D printer simulation — primary integration test for the simulation engine |

---

## The Voron Example

`voron-trident-simulation/` is the canonical integration target for the simulation pipeline. It is the verification script at the end of `../docs/codex-python-simulation-api.md`.

After implementing simulation API changes, verify with:

```python
import mercurio

with mercurio.open("mercurio-examples/voron-trident-simulation") as model:
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
python mercurio-examples/model-graph-analysis/analyze_model_d3.py
```

---

## Key Constraint

If an example breaks after a core change, fix the core or update the example to match the new API — do not add core workarounds to preserve old example behaviour.
