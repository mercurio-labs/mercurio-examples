# Python Pilot Authoring Example

Recreates small SysML v2 Pilot samples with the Python authoring API:

- `training/39. Metadata/Metadata Example-1.sysml`
- `training/23. State Definitions/State Definition Example-1.sysml`

## What It Shows

- Clean package creation with `stdlib_imports=False`
- `MetadataDefinition.annotates(...)` for normalized annotated elements
- `MetadataUsage.about([...])` for multi-target metadata applications
- Nested `PartUsage` trees and multiplicities
- `StateDefinition`, `StateUsage`, and `TransitionUsage` shorthand
- `builder.to_sysml()` and `builder.save()`

## Running

```powershell
pip install -e ..\..\mercurio-host-adapters\python
python build_metadata_example.py
python build_state_definition_example.py
python verify_equivalence.py
```

Generated SysML is printed to stdout and written under `output/`.
The adjacent `.project.json` opens the generated output as a descriptor-backed
Mercurio project.

`verify_equivalence.py` compiles each original Pilot source and the generated
Python-authored source, then compares their normalized semantic snapshots.
