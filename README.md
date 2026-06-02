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

Run all examples and tests with:

```powershell
cargo test
```
