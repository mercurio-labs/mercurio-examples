"""
Structural Connectivity Analysis — Mercurio process-provider capability.

Demonstrates using the Python scientific ecosystem (NetworkX) for model analysis.
Receives a compiled model graph via stdin, builds a directed graph, and reports:

  - Orphaned parts: definitions/usages with no path from any root
  - Structural depth: how deep each part lives in the usage hierarchy
  - Centrality hotspots: PageRank-based identification of critical parts

Input:  mercurio.graph.v1  (nodes + edges from workspace.graph())
        Also accepts the graph embedded in request.parameters["graph"] for
        standalone testing without a running Mercurio backend.

Output: mercurio.table.v1  (per-part metrics table)
        findings for each orphaned part or definition

Requires: networkx
"""

from __future__ import annotations

import sys
import os

# Allow running from the repo root without installing the SDK.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",
                                "mercurio-host-adapters", "python"))

import networkx as nx

from mercurio_capability import (
    Artifact,
    CapabilityRequest,
    CapabilityRunner,
    ElementRef,
    EvidenceEdge,
    EvidenceGraph,
    EvidenceNode,
    Finding,
    ReasoningReport,
)

PART_KINDS = {"PartUsage", "PartDefinition", "IndividualUsage", "ItemDefinition", "ItemUsage"}

CAPABILITY_KIND = "mercurio.capability.kind/static-analysis"
CAPABILITY_ID = "org.example.structural-connectivity"


@CapabilityRunner.capability(
    id=CAPABILITY_ID,
    kind=CAPABILITY_KIND,
    name="Structural Connectivity Analysis",
    version="0.1.0",
    deterministic=True,
    input_artifact_kinds=["kir", "graph"],
    output_artifact_kinds=["table", "reasoning_report"],
)
def analyze(request: CapabilityRequest) -> ReasoningReport:
    graph_data = _resolve_graph(request)
    if graph_data is None:
        return request.report_inconclusive(
            findings=[
                Finding.warning(
                    id="connectivity.no-graph",
                    title="No graph data available",
                    message=(
                        "The request contained neither a 'kir' field nor a "
                        "'graph' parameter. Include the compiled workspace graph."
                    ),
                )
            ]
        )

    G, node_meta = _build_graph(graph_data)

    if G.number_of_nodes() == 0:
        return request.report_passed(
            findings=[
                Finding.info(
                    id="connectivity.empty",
                    title="No part nodes found",
                    message="The graph contained no PartUsage or PartDefinition nodes.",
                )
            ]
        )

    roots = [n for n in G.nodes if G.in_degree(n) == 0]

    # Components sorted largest-first; the primary system is the biggest.
    components = sorted(nx.weakly_connected_components(G), key=len, reverse=True)
    primary_component: set[str] = components[0] if components else set()
    stranded_components: list[set[str]] = components[1:]

    # Stranded: roots that live outside the primary (largest) component.
    stranded_roots = [r for r in roots if r not in primary_component]

    component_index: dict[str, int] = {}
    for idx, component in enumerate(components):
        for node in component:
            component_index[node] = idx

    depth = _compute_depths(G, [r for r in roots if r in primary_component] or roots)

    centrality = nx.pagerank(G, alpha=0.85) if G.number_of_edges() > 0 else {n: 0.0 for n in G.nodes}

    findings = _build_findings(stranded_roots, stranded_components, node_meta)
    artifacts = _build_artifacts(G, node_meta, depth, centrality, component_index, set(roots), primary_component)
    evidence = _build_evidence(stranded_roots, node_meta, G)

    status = "failed" if any(f.severity in ("error", "critical") for f in findings) else "passed"

    return ReasoningReport(
        request_id=request.request_id,
        capability_descriptor=request._descriptor,
        context=request.context,
        status=status,
        findings=findings,
        artifacts=artifacts,
        evidence=evidence,
    )


# ---------------------------------------------------------------------------
# Graph construction
# ---------------------------------------------------------------------------

def _resolve_graph(request: CapabilityRequest) -> dict | None:
    """Return graph dict from kir field, graph_facts, or parameters.graph."""
    # Prefer explicit parameter (e.g. standalone test invocation)
    if param_graph := request.param("graph"):
        return param_graph
    # kir may contain the compiled graph under "graph" or directly as nodes/edges
    kir = request.kir
    if kir:
        if "nodes" in kir and "edges" in kir:
            return kir
        if "graph" in kir:
            return kir["graph"]
    # graph_facts: list of {"predicate": "...", ...} — not a graph dict
    return None


def _build_graph(graph_data: dict) -> tuple[nx.DiGraph, dict[str, dict]]:
    """Build a NetworkX DiGraph from a mercurio.graph.v1 payload."""
    G = nx.DiGraph()
    node_meta: dict[str, dict] = {}

    for node in graph_data.get("nodes", []):
        node_id = str(node.get("id") or node.get("elementId") or "")
        if not node_id:
            continue
        kind = str(node.get("kind", ""))
        if not any(pk in kind for pk in PART_KINDS):
            continue
        props = node.get("properties", {})
        name = str(
            props.get("declared_name")
            or props.get("name")
            or node_id.rsplit(".", 1)[-1]
        )
        source_file = props.get("source_file") or props.get("sourceFile")
        node_meta[node_id] = {
            "name": name,
            "kind": kind,
            "qualified_name": props.get("qualified_name") or props.get("qualifiedName"),
            "source_file": source_file,
            "source_span": props.get("source_span") or props.get("sourceSpan"),
        }
        G.add_node(node_id, **node_meta[node_id])

    ownership_relations = {"owns", "contains", "usage_of", "specializes", "typing"}
    for edge in graph_data.get("edges", []):
        src = str(edge.get("source") or edge.get("sourceId") or "")
        tgt = str(edge.get("target") or edge.get("targetId") or "")
        relation = str(edge.get("relation") or edge.get("kind") or "")
        if src in G and tgt in G and relation in ownership_relations:
            G.add_edge(src, tgt, relation=relation)

    return G, node_meta


def _compute_depths(G: nx.DiGraph, roots: list[str]) -> dict[str, int]:
    depths: dict[str, int] = {}
    for root in roots:
        for node, depth in nx.single_source_shortest_path_length(G, root).items():
            if node not in depths or depth < depths[node]:
                depths[node] = depth
    for node in G.nodes:
        if node not in depths:
            depths[node] = -1  # orphaned — no path from any root
    return depths


# ---------------------------------------------------------------------------
# Findings
# ---------------------------------------------------------------------------

def _build_findings(
    stranded_roots: list[str],
    stranded_components: list[set[str]],
    node_meta: dict[str, dict],
) -> list[Finding]:
    findings: list[Finding] = []

    for component in stranded_components:
        # Surface one finding per stranded component.
        roots_in_component = [n for n in stranded_roots if n in component]
        label_nodes = roots_in_component or sorted(component)[:3]
        names = [node_meta.get(n, {}).get("name") or n for n in label_nodes]
        summary = ", ".join(f"'{n}'" for n in names)
        if len(component) > len(label_nodes):
            summary += f" (+{len(component) - len(label_nodes)} more)"

        findings.append(
            Finding.warning(
                id=f"connectivity.stranded.{'_'.join(sorted(component)[:2])}",
                title=f"Stranded component: {summary}",
                message=(
                    f"{len(component)} part(s) form a separate subgraph not connected "
                    "to the primary system hierarchy. These definitions are never used "
                    "in the main ownership tree. Remove them or add usage relationships."
                ),
                elements=[
                    ElementRef(
                        element_id=n,
                        qualified_name=node_meta.get(n, {}).get("qualified_name"),
                        label=node_meta.get(n, {}).get("name") or n,
                    )
                    for n in sorted(component)
                ],
                evidence_ids=[f"fact.stranded.{n}" for n in sorted(component)],
                properties={"component_size": len(component)},
            )
        )

    return findings


# ---------------------------------------------------------------------------
# Artifacts
# ---------------------------------------------------------------------------

def _build_artifacts(
    G: nx.DiGraph,
    node_meta: dict[str, dict],
    depth: dict[str, int],
    centrality: dict[str, float],
    component_index: dict[str, int],
    roots: set[str],
    primary_component: set[str],
) -> list[Artifact]:
    rows = []
    for node_id in sorted(G.nodes, key=lambda n: (component_index.get(n, 999), depth.get(n, 999), n)):
        meta = node_meta.get(node_id, {})
        in_primary = node_id in primary_component
        is_root = node_id in roots
        if not in_primary:
            node_status = "stranded"
        elif is_root:
            node_status = "root"
        else:
            node_status = "connected"

        rows.append([
            meta.get("name") or node_id,
            meta.get("kind") or "",
            depth.get(node_id, -1),
            component_index.get(node_id, -1),
            round(centrality.get(node_id, 0.0), 4),
            node_status,
            G.in_degree(node_id),
            G.out_degree(node_id),
        ])

    return [
        Artifact.table(
            id="structural-connectivity-report",
            schema="mercurio.structural_connectivity.summary.v1",
            columns=["name", "kind", "depth", "component", "pagerank", "status", "in_degree", "out_degree"],
            rows=rows,
            digest=f"connectivity:{G.number_of_nodes()}:{G.number_of_edges()}",
        )
    ]


# ---------------------------------------------------------------------------
# Evidence graph
# ---------------------------------------------------------------------------

def _build_evidence(
    stranded_roots: list[str],
    node_meta: dict[str, dict],
    G: nx.DiGraph,
) -> EvidenceGraph:
    nodes: list[EvidenceNode] = []
    edges: list[EvidenceEdge] = []

    run_node_id = "analysis_run.structural-connectivity"
    nodes.append(EvidenceNode(
        id=run_node_id,
        kind="analysis_run",
        label="Structural Connectivity Analysis (NetworkX)",
    ))

    for node_id in stranded_roots:
        meta = node_meta.get(node_id, {})
        name = meta.get("name") or node_id

        element_node_id = f"element.{node_id}"
        fact_node_id = f"fact.stranded.{node_id}"

        nodes.append(EvidenceNode(
            id=element_node_id,
            kind="kir_element",
            label=name,
            element_refs=[ElementRef(element_id=node_id, label=name)],
        ))
        nodes.append(EvidenceNode(
            id=fact_node_id,
            kind="fact",
            label=f"not_in_primary_component({node_id})",
            properties={"in_degree": G.in_degree(node_id)},
        ))

        edges.append(EvidenceEdge(run_node_id, fact_node_id, "produced_by"))
        edges.append(EvidenceEdge(fact_node_id, element_node_id, "affects"))

    return EvidenceGraph(nodes=nodes, edges=edges)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    CapabilityRunner.run(analyze)
