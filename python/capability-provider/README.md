# Standalone Capability Provider

Minimal process-backed capability provider using `mercurio_capability`.
It validates the stdin/stdout ABI without requiring a desktop project.

Run from the repository root:

```powershell
python mercurio-examples/python/capability-provider/test_provider.py
```

`provider.py` can also be launched directly by a Mercurio capability host. It
reads a `CapabilityRequest` JSON object from stdin and writes a
`ReasoningCapabilityRunResponse`-shaped JSON object to stdout.
