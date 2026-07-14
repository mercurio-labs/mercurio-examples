# Native Core Probe

Checks whether the in-process PyO3 native core (`mercurio._core`) is available
and, when it is, opens a temporary descriptor-backed project without launching
the HTTP sidecar.

Run from the repository root:

```powershell
python mercurio-examples/python/native-core/probe_native_core.py
```

If the native extension is not installed in the current Python environment, the
script exits successfully with a clear skip message. That keeps the example
usable in source-only checkouts while still documenting the native path.
