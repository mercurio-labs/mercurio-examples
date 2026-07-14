from __future__ import annotations

import argparse
import json
import os
from html import escape
from pathlib import Path
from typing import Any

from mercurio.backend import Mercurio
from mercurio.errors import MercurioLaunchError


DEFAULT_D3_URL = "https://cdn.jsdelivr.net/npm/d3@7/+esm"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile a Mercurio model graph and render an analysis view with D3."
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Workspace containing the SysML model.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).resolve().parent / "out" / "decision-review.html",
        help="HTML file to write.",
    )
    parser.add_argument(
        "--d3-url",
        default=DEFAULT_D3_URL,
        help="D3 ES module URL. Use a local file URL for offline viewing.",
    )
    parser.add_argument(
        "--backend-url",
        help="Attach to an existing Mercurio backend instead of launching one.",
    )
    parser.add_argument(
        "--executable",
        help=(
            "Mercurio console API executable to launch. Defaults to a repo-local "
            "mercurio-console-api binary when one is available."
        ),
    )
    args = parser.parse_args()

    if args.backend_url:
        backend = Mercurio.connect(args.backend_url)
        workspace = backend.open_workspace(str(args.workspace), mode="compiled")
        result = workspace.compile_project()
        if not result.ok:
            raise SystemExit(f"compile failed: {result.data}")
        graph = workspace.graph(scope="l2")
        workspace.close()
    else:
        executable = args.executable or default_console_api_executable()
        try:
            with Mercurio.launch(executable=executable) as backend:
                workspace = backend.open_workspace(str(args.workspace), mode="compiled")
                result = workspace.compile_project()
                if not result.ok:
                    raise SystemExit(f"compile failed: {result.data}")
                graph = workspace.graph(scope="l2")
        except MercurioLaunchError as error:
            raise SystemExit(launch_help(error, executable)) from error

    view = build_analysis_view(graph)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(render_html(view, args.d3_url), encoding="utf-8")
    print(f"wrote {args.output}")
    print(
        f"analyzed {len(view['nodes'])} nodes, {len(view['links'])} links, "
        f"{len(view['decisions'])} decision candidates"
    )


def default_console_api_executable() -> str | None:
    repo_root = Path(__file__).resolve().parents[2]
    suffix = ".exe" if os.name == "nt" else ""
    candidate = (
        repo_root
        / "mercurio-product"
        / "target"
        / "debug"
        / f"mercurio-console-api{suffix}"
    )
    if candidate.exists():
        return str(candidate)
    return None


def launch_help(error: MercurioLaunchError, executable: str | None) -> str:
    lines = [
        f"failed to launch Mercurio console API: {error}",
        "",
        "This example needs the HTTP console API executable, not the command-based "
        "`mercurio` CLI.",
    ]
    if executable:
        lines.append(f"Tried executable: {executable}")
    else:
        lines.extend(
            [
                "No repo-local console API binary was found, so the Python SDK fell "
                "back to executable discovery.",
                "Build it with:",
                "  cargo build -p mercurio-console-api",
                "Then run this script again, or pass:",
                "  --executable C:\\path\\to\\mercurio-console-api.exe",
            ]
        )
    lines.extend(
        [
            "",
            "If a backend is already running, use:",
            "  --backend-url http://127.0.0.1:<port>",
        ]
    )
    return "\n".join(lines)


def build_analysis_view(graph: dict[str, Any]) -> dict[str, Any]:
    nodes_by_id: dict[str, dict[str, Any]] = {}
    degree: dict[str, int] = {}

    for raw_node in graph.get("nodes", []):
        node_id = str(raw_node.get("id", ""))
        if not node_id:
            continue
        properties = raw_node.get("properties", {})
        label = str(
            raw_node.get("label")
            or properties.get("declared_name")
            or properties.get("name")
            or node_id.rsplit(".", 1)[-1]
        )
        kind = str(raw_node.get("kind", "Element"))
        score = decision_score(label, kind, properties)
        nodes_by_id[node_id] = {
            "id": node_id,
            "label": label,
            "kind": kind,
            "score": score,
            "properties": compact_properties(properties),
        }
        degree[node_id] = 0

    links: list[dict[str, Any]] = []
    for raw_edge in graph.get("edges", []):
        source = str(raw_edge.get("source", ""))
        target = str(raw_edge.get("target", ""))
        if source not in nodes_by_id or target not in nodes_by_id:
            continue
        relation = str(raw_edge.get("relation", raw_edge.get("kind", "relates")))
        links.append({"source": source, "target": target, "relation": relation})
        degree[source] += 1
        degree[target] += 1

    for node_id, node in nodes_by_id.items():
        node["degree"] = degree[node_id]
        if degree[node_id] >= 3:
            node["score"] += 1

    nodes = list(nodes_by_id.values())
    decisions = sorted(
        [node for node in nodes if node["score"] > 0],
        key=lambda node: (-node["score"], -node["degree"], node["label"]),
    )

    return {
        "title": "Payload Architecture Decision Review",
        "nodes": nodes,
        "links": links,
        "decisions": decisions,
        "summary": {
            "nodes": len(nodes),
            "links": len(links),
            "decisionCandidates": len(decisions),
        },
    }


def decision_score(label: str, kind: str, properties: dict[str, Any]) -> int:
    text = " ".join([label, kind, json.dumps(properties, sort_keys=True)]).lower()
    score = 0
    for term in ("analysis", "objective", "requirement", "decision", "decide", "select"):
        if term in text:
            score += 2
    for term in ("action", "criticality", "power", "mass", "latency"):
        if term in text:
            score += 1
    return score


def compact_properties(properties: dict[str, Any]) -> dict[str, Any]:
    keep = {}
    for key, value in properties.items():
        if key in {"declared_name", "name", "type", "owner", "definition", "source_file"}:
            keep[key] = value
        elif isinstance(value, (str, int, float, bool)):
            keep[key] = value
    return keep


def render_html(view: dict[str, Any], d3_url: str) -> str:
    payload = json.dumps(view, ensure_ascii=True, indent=2)
    title = escape(str(view["title"]))
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      font-family: Arial, Helvetica, sans-serif;
      color: #17202a;
      background: #f7f8fa;
    }}
    header {{
      padding: 18px 24px 12px;
      border-bottom: 1px solid #d8dee8;
      background: #ffffff;
    }}
    h1 {{
      margin: 0;
      font-size: 20px;
      font-weight: 700;
    }}
    .summary {{
      display: flex;
      gap: 18px;
      margin-top: 8px;
      color: #52616f;
      font-size: 13px;
    }}
    main {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 340px;
      height: calc(100vh - 75px);
    }}
    svg {{
      width: 100%;
      height: 100%;
      background: #ffffff;
    }}
    aside {{
      overflow: auto;
      border-left: 1px solid #d8dee8;
      background: #fbfcfd;
      padding: 16px;
    }}
    h2 {{
      margin: 0 0 12px;
      font-size: 15px;
    }}
    .candidate {{
      border: 1px solid #d8dee8;
      border-radius: 8px;
      background: #ffffff;
      padding: 10px;
      margin-bottom: 10px;
    }}
    .candidate strong {{
      display: block;
      font-size: 13px;
      margin-bottom: 4px;
    }}
    .candidate span {{
      display: block;
      color: #52616f;
      font-size: 12px;
      overflow-wrap: anywhere;
    }}
    .link {{
      stroke: #aeb8c6;
      stroke-opacity: 0.7;
    }}
    .node circle {{
      stroke: #ffffff;
      stroke-width: 1.5px;
    }}
    .node text {{
      font-size: 11px;
      paint-order: stroke;
      stroke: #ffffff;
      stroke-width: 3px;
      stroke-linejoin: round;
    }}
    .decision circle {{
      stroke: #24292f;
      stroke-width: 2.5px;
    }}
  </style>
</head>
<body>
  <header>
    <h1>{title}</h1>
    <div class="summary">
      <span id="node-count"></span>
      <span id="link-count"></span>
      <span id="decision-count"></span>
    </div>
  </header>
  <main>
    <svg role="img" aria-label="Model graph decision analysis"></svg>
    <aside>
      <h2>Decision Candidates</h2>
      <div id="decisions"></div>
    </aside>
  </main>
  <script type="module">
    import * as d3 from "{escape(d3_url)}";

    const data = {payload};
    document.querySelector("#node-count").textContent = `${{data.summary.nodes}} nodes`;
    document.querySelector("#link-count").textContent = `${{data.summary.links}} links`;
    document.querySelector("#decision-count").textContent =
      `${{data.summary.decisionCandidates}} decision candidates`;

    const decisions = d3.select("#decisions");
    decisions.selectAll(".candidate")
      .data(data.decisions)
      .join("div")
      .attr("class", "candidate")
      .html(d => `<strong>${{escapeHtml(d.label)}}</strong><span>${{escapeHtml(d.kind)}} | score ${{d.score}} | degree ${{d.degree}}</span>`);

    const svg = d3.select("svg");
    const width = svg.node().clientWidth;
    const height = svg.node().clientHeight;
    const color = d3.scaleOrdinal()
      .domain(["Analysis", "Requirement", "Action", "Part", "Attribute", "Element"])
      .range(["#7c3aed", "#0f766e", "#dc6b19", "#2563eb", "#64748b", "#475569"]);

    const simulation = d3.forceSimulation(data.nodes)
      .force("link", d3.forceLink(data.links).id(d => d.id).distance(95).strength(0.45))
      .force("charge", d3.forceManyBody().strength(-320))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("collision", d3.forceCollide().radius(d => 18 + d.score * 2));

    const link = svg.append("g")
      .selectAll("line")
      .data(data.links)
      .join("line")
      .attr("class", "link")
      .attr("stroke-width", 1.5);

    const node = svg.append("g")
      .selectAll("g")
      .data(data.nodes)
      .join("g")
      .attr("class", d => d.score > 0 ? "node decision" : "node")
      .call(drag(simulation));

    node.append("circle")
      .attr("r", d => 7 + Math.min(8, d.score * 1.5))
      .attr("fill", d => color(groupFor(d.kind)));

    node.append("title")
      .text(d => `${{d.label}}\\n${{d.kind}}\\nscore ${{d.score}}, degree ${{d.degree}}`);

    node.append("text")
      .attr("x", 12)
      .attr("y", 4)
      .text(d => d.label);

    simulation.on("tick", () => {{
      link
        .attr("x1", d => d.source.x)
        .attr("y1", d => d.source.y)
        .attr("x2", d => d.target.x)
        .attr("y2", d => d.target.y);

      node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
    }});

    function groupFor(kind) {{
      if (kind.includes("Analysis")) return "Analysis";
      if (kind.includes("Requirement")) return "Requirement";
      if (kind.includes("Action") || kind.includes("Decision")) return "Action";
      if (kind.includes("Part")) return "Part";
      if (kind.includes("Attribute")) return "Attribute";
      return "Element";
    }}

    function drag(simulation) {{
      function dragstarted(event) {{
        if (!event.active) simulation.alphaTarget(0.3).restart();
        event.subject.fx = event.subject.x;
        event.subject.fy = event.subject.y;
      }}
      function dragged(event) {{
        event.subject.fx = event.x;
        event.subject.fy = event.y;
      }}
      function dragended(event) {{
        if (!event.active) simulation.alphaTarget(0);
        event.subject.fx = null;
        event.subject.fy = null;
      }}
      return d3.drag().on("start", dragstarted).on("drag", dragged).on("end", dragended);
    }}

    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, character => ({{
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#039;"
      }}[character]));
    }}
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    main()
