from __future__ import annotations

from mercurio_ex_support import configure_imports

configure_imports()

from mercurio_capability import (  # noqa: E402
    Artifact,
    CapabilityRequest,
    CapabilityRunner,
    EvidenceGraph,
    EvidenceNode,
    Finding,
)


@CapabilityRunner.capability(
    id="org.mercurio.examples.kind-inventory",
    kind="mercurio.capability.kind/model-inspection",
    name="Kind Inventory",
    version="0.1.0",
    input_artifact_kinds=["kir"],
    output_artifact_kinds=["table", "reasoning_report"],
    applicability_types=["Package", "PartDefinition", "PartUsage"],
    also_workspace=True,
)
def analyze(request: CapabilityRequest):
    elements = request.kir.get("elements", [])
    if not isinstance(elements, list):
        elements = []

    counts: dict[str, int] = {}
    for element in elements:
        if not isinstance(element, dict):
            continue
        kind = str(element.get("kind") or element.get("metatype") or "unknown")
        counts[kind] = counts.get(kind, 0) + 1

    rows = [[kind, count] for kind, count in sorted(counts.items())]
    artifact = Artifact.table(
        "kind-counts",
        "org.mercurio.examples.kind_counts.v1",
        ["kind", "count"],
        rows,
    )
    evidence = EvidenceGraph(
        nodes=[
            EvidenceNode(
                id="input-kir",
                kind="artifact",
                label="Input KIR",
                properties={
                    "artifact_key": request.context["artifact"]["artifact_key"],
                    "kir_content_hash": request.kir_content_hash,
                },
            )
        ]
    )
    finding = Finding.info(
        "kind-inventory.completed",
        "Kind inventory completed",
        f"Counted {sum(counts.values())} KIR elements across {len(counts)} kinds.",
        evidence_ids=["input-kir"],
    )
    return request.report_passed(
        findings=[finding],
        artifacts=[artifact],
        evidence=evidence,
    )


if __name__ == "__main__":
    CapabilityRunner.run(analyze)
