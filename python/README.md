# Mercurio Pure Python Examples

This folder is the first-release Python example set. The examples use the small
public facade only:

```python
import mercurio
from mercurio import model
```

They do not define plugins, extension modules, or custom native bindings. Some
examples require the Mercurio native wheel or an installed sidecar because
opening, compiling, querying, and analysis execution need the runtime.

## Setup

From `mercurio-host-adapters/python`:

```powershell
pip install -e ".[test]"
```

Run examples from the repository root:

```powershell
python mercurio-examples/python/01_create_in_memory.py
```

## Examples

| Script | Demonstrates |
| --- | --- |
| `01_create_in_memory.py` | Create a model fully in memory and inspect generated SysML. |
| `02_create_and_save.py` | Create a file-backed project and save it to disk. |
| `03_open_existing_project.py` | Open a descriptor-backed project and compile it. |
| `04_query_snapshot.py` | Query an immutable compiled snapshot. |
| `05_edit_existing_project.py` | Copy an existing project, edit it, and save the result. |
| `06_dsl_query.py` | Run the Mercurio DSL query facade. |
| `07_analysis_case.py` | Inspect and run an analysis case from a project. |
| `08_trade_study_variants.py` | Create low-cost source variants for a trade study. |

The `fixtures/` directory contains small SysML projects used by the examples.
