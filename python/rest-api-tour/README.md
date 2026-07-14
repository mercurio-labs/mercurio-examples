# REST API Tour

Directly drives `mercurio-console-api` with plain JSON requests. This example
uses the Python SDK only to launch and stop the local backend process; all API
calls are explicit HTTP calls through `urllib`.

Run from the repository root after building `mercurio-console-api`:

```powershell
python mercurio-examples/python/rest-api-tour/run_rest_api_tour.py
```

The tour covers health/version discovery, workspace open, scoped editor files,
session cell execution, semantic legality checks, and scoped cleanup.
