# Python Stdlib Authoring Example

Builds a satellite model (structure, power system, thermal control) using the
Python `ModelBuilder` API with attributes typed to ISQ quantity kinds and SI
units from the SysML standard library.

## What it shows

- `PartDefinition` / `PartUsage` for subsystem decomposition
- `AttributeUsage.typed(isq.*)` — ISQ quantity kinds (mass, power, length, duration…)
- `AttributeUsage.typed(scalar_values.*)` — scalar primitive types
- `builder.to_sysml()` to inspect the generated SysML source
- `builder.save()` to write `.sysml` files to disk

## Running

```
pip install mercurio          # or: pip install -e path/to/mercurio-host-adapters/python
python build_model.py
```

Generated SysML is printed to stdout and written to `./output/model.sysml`.
The adjacent `.project.json` points at that generated file so the example can
also be opened as a descriptor-backed Mercurio project.
