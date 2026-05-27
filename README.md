# Mercurio Examples

Public model corpus, scenario files, tutorials, and expected outputs for
Mercurio.

This repository is a peer of `mercurio-core`. Core keeps only small fixtures
needed for local tests and smoke checks; larger examples and demo corpora should
move here over time.

Recommended layout:

```text
sysml/
  training/
  validation/
  domain/
kerml/
  examples/
kir/
  snapshots/
scenarios/
  state_machine/
expected/
  projections/
docs/
```

Tooling can locate this repo with:

```powershell
$env:MERCURIO_EXAMPLES_ROOT = "C:\dev\git\mercurio\mercurio-examples"
```
