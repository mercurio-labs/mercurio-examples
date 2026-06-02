# Mercurio Simple Language

A tiny non-SysML language used to prove the Mercurio host model.

The language supports four statements:

```text
component Vehicle
component Engine
part Vehicle.engine: Engine
requirement R1 "Vehicle shall start"
satisfy Vehicle -> R1
```

It implements `LanguageService` and emits KIR directly. This is intentionally small: the point is to show that a host can register a completely different language without changing Mercurio core.

Run:

```powershell
cargo test
cargo run --example compile
```
