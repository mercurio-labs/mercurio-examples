# Vehicle Mass Compliance

This example is the canonical small analysis fixture for Mercurio's common noun
architecture.

It is intentionally simple:

```text
Model -> Element -> Query -> Result -> View
Model -> Analysis Case -> Calculation / Constraint -> Verification -> Evidence
```

The model describes a vehicle with chassis, battery, and motor components. The
analysis question is whether the configured vehicle mass stays below the
required maximum mass.

## Expected Analysis

```text
chassis.mass_kg = 400
battery.mass_kg = 550
motor.mass_kg   = 120

total_mass_kg = 1070
max_mass_kg   = 1500
margin_kg     = 430
verdict       = pass
```

## Current DSL Queries

Run these from the Analysis dock query editor.

```rhai
model.parts().select(["declared_name", "element_id", "kind"])
```

```rhai
model.parts()
  .where(|p| p.kind == "SysML::Systems::PartDefinition")
  .select(["declared_name", "element_id"])
```

```rhai
count_by_kind(model.elements())
```

The DSL stdlib supports `sum(...)` over numeric arrays. Numeric owned features
with literal `expression_ir` values can be read through `property(...)`, so the
mass calculation query is:

```rhai
sum(model.parts().map(|p| p.property("mass_kg")))
```

The first executable analysis result can be expressed as a single row:

```rhai
let vehicle = model.parts()
  .where(|p| p.property("declared_name") == "Vehicle")
  .first();
let total = sum(model.parts().map(|p| p.property("mass_kg")));
let max = vehicle.property("max_mass_kg");
#{
  total_mass_kg: total,
  max_mass_kg: max,
  margin_kg: max - total,
  verdict: if total <= max { "pass" } else { "fail" }
}
```

## Target Workflow

This fixture should evolve into the first end-to-end analysis workflow:

1. `Query` selects the vehicle subject and component attributes.
2. `Calculation` computes `total_mass_kg`.
3. `Constraint` evaluates `total_mass_kg <= max_mass_kg`.
4. `Requirement` records the mass limit.
5. `Verification Case` records pass/fail and margin evidence.
6. `View` presents the result as a table and graph.

The current model keeps the SysML source lightweight while preserving names that
future parsing, analysis, and verification features can bind to directly.
