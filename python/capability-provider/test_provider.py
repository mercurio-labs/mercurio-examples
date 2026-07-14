from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def capability_request() -> dict:
    return {
        "requestId": "example-request-001",
        "capabilityId": "org.mercurio.examples.kind-inventory",
        "context": {
            "context_id": "example-context",
            "kind": "workspace",
            "artifact": {
                "artifact_key": "example.kir",
                "kir_schema_version": "mercurio.kir.v1",
                "kir_content_hash": "sha256:example",
            },
        },
        "focus": [],
        "parameters": {},
        "kir": {
            "elements": [
                {"id": "pkg", "kind": "Package"},
                {"id": "sensorDef", "kind": "PartDefinition"},
                {"id": "sensorUse", "kind": "PartUsage"},
                {"id": "controllerUse", "kind": "PartUsage"},
            ]
        },
        "graph_facts": [],
    }


def main() -> None:
    provider = Path(__file__).with_name("provider.py")
    result = subprocess.run(
        [sys.executable, str(provider)],
        input=json.dumps(capability_request()),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr or result.stdout)

    payload = json.loads(result.stdout)
    report = payload["report"]
    assert report["status"] == "passed"
    assert payload["metadata"]["runner"] == "mercurio_capability/0.1"
    table = report["artifacts"][0]["payload"]
    assert ["PartUsage", 2] in table["rows"]
    assert report["evidence"]["nodes"][0]["kind"] == "artifact"

    print("capability provider example passed")


if __name__ == "__main__":
    main()
