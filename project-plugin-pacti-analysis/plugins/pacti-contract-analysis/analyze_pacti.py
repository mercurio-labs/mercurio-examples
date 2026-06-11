import json
import sys


def main() -> None:
    request = json.load(sys.stdin)
    request_id = request.get("request_id") or request.get("requestId") or "pacti-contract-analysis"
    capability_id = request.get("capability_id") or request.get("capabilityId") or "org.example.pacti.contracts"
    context = request.get("context") or {
        "context_id": "project-plugin-pacti-example",
        "kind": "accepted",
        "artifact": {
            "artifact_key": "example",
            "kir_schema_version": "0.1"
        }
    }

    # Stock Pacti integration belongs behind this boundary. This example keeps
    # the plugin protocol stable even when pacti is not installed.
    rows = [
        {
            "id": "check.power-budget",
            "status": "passed",
            "subject": "controller",
            "detail": "Assumption/guarantee check completed by project plugin wrapper."
        }
    ]
    report = {
        "request_id": request_id,
        "capability": {
            "id": capability_id,
            "kind": "contract_analysis",
            "name": "Pacti Contract Analysis",
            "version": "0.1.0",
            "api_version": "0.1",
            "deterministic": True,
            "input_artifact_kinds": ["kir"],
            "output_artifact_kinds": ["table", "reasoning_report"]
        },
        "context": context,
        "status": "passed",
        "findings": [],
        "artifacts": [
            {
                "id": "pacti-contract-summary",
                "kind": "table",
                "schema": "mercurio.contract_analysis.summary.v1",
                "digest": "example:pacti-contract-summary",
                "element_refs": [],
                "payload": {
                    "columns": ["id", "status", "subject", "detail"],
                    "rows": rows
                }
            }
        ],
        "evidence": {
            "nodes": [],
            "edges": []
        }
    }
    json.dump({"report": report, "metadata": {"adapter": "example-pacti-wrapper"}}, sys.stdout)


if __name__ == "__main__":
    main()
