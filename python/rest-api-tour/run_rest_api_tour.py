from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from mercurio_ex_support import configure_imports

configure_imports()

from mercurio.backend import Mercurio  # noqa: E402


def request_json(base_url: str, method: str, path: str, payload: dict | None = None, query: dict | None = None):
    url = base_url.rstrip("/") + path
    if query:
        url = f"{url}?{urlencode(query)}"
    body = None
    headers = {"accept": "application/json"}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["content-type"] = "application/json"
    request = Request(url, data=body, headers=headers, method=method)
    with urlopen(request, timeout=30) as response:
        raw = response.read()
        if not raw:
            return None
        return json.loads(raw.decode("utf-8"))


def main() -> None:
    fixture = Path(__file__).resolve().parents[1] / "simulation-state-machine"
    backend = Mercurio.launch(timeout=45)
    base_url = backend.client.base_url
    workspace_id = None
    try:
        health = request_json(base_url, "GET", "/api/health")
        version = request_json(base_url, "GET", "/api/version")
        releases = request_json(base_url, "GET", "/api/releases/sysml")
        assert health
        assert version["apiVersion"] == 1
        assert releases["releases"]

        opened = request_json(
            base_url,
            "POST",
            "/api/workspaces",
            {"path": str(fixture), "mode": "compiled"},
        )
        workspace_id = opened["workspaceId"]

        files = request_json(base_url, "GET", f"/api/workspaces/{workspace_id}/editor/files")
        assert any(item["path"].endswith(".sysml") for item in files["files"])

        cell = request_json(
            base_url,
            "POST",
            f"/api/workspaces/{workspace_id}/session/cells/run",
            {
                "cellId": "rest-tour.count-elements",
                "kind": "query",
                "language": "mercurio_dsl",
                "source": "model.parts().count()",
                "parameters": {},
            },
        )
        assert cell["status"] == "passed"

        legality = request_json(
            base_url,
            "POST",
            f"/api/workspaces/{workspace_id}/semantic/legality/check",
            {
                "operation": {
                    "kind": "usageTyping",
                    "usageKind": "PartUsage",
                    "definitionKind": "PartDefinition",
                },
                "facts": [],
            },
        )
        status = str(legality.get("status") or "").lower()
        assert legality.get("allowed") is True or status.startswith("allowed")

        print(f"REST tour opened workspace {workspace_id}")
        print(f"version={version['version']} releases={len(releases['releases'])}")
        print("rest api tour example passed")
    finally:
        if workspace_id is not None:
            request_json(base_url, "DELETE", f"/api/workspaces/{workspace_id}")
        backend.close()


if __name__ == "__main__":
    main()
