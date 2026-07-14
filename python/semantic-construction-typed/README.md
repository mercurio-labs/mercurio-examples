# Typed Semantic Construction

Builds a small SysML model through the Python authoring API using typed
elements instead of raw text assembly. The script exercises the fluent
declaration helpers across part, port, attribute, requirement, and usage
elements.

Run from the repository root:

```powershell
python mercurio-examples/python/semantic-construction-typed/build_typed_model.py
```

The script compiles the generated model in memory, saves a temporary
descriptor-backed project, opens it through Mercurio, and checks semantic
legality helpers over typed usage/definition pairs.
