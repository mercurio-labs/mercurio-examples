# Python Stdlib Authoring Example

Builds a simple electric drive system model using the Python `ModelBuilder` API
with attributes and ports typed to ISQ quantities and SI units from the SysML
standard library.

## What it shows

- `PartDefinition` / `PartUsage` for component decomposition
- `PortDefinition` / `PortUsage` with `direction` for interface typing
- `ConnectionUsage` linking component ports
- `AttributeUsage.typed(isq.*)` — ISQ quantity kinds (mass, power, frequency…)
- `AttributeUsage.typed(si.*)` — SI units (one, for dimensionless ratios)
- `builder.to_sysml()` to inspect the generated source
- `builder.save()` to write `.sysml` files to disk

## Running

```
pip install mercurio          # or: pip install -e path/to/mercurio-host-adapters/python
python build_model.py
```

Generated SysML is printed to stdout and written to `./output/model.sysml`.
