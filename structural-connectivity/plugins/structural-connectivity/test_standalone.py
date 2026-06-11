"""
Standalone test — runs the analysis without a Mercurio backend.

    python test_standalone.py

Feeds a synthetic graph that mirrors the satellite-system.sysml model,
including the intentionally orphaned DebugProbe cluster.
"""

from __future__ import annotations

import json
import sys
import io
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "..",
                                "mercurio-host-adapters", "python"))

from analyze_connectivity import analyze
from mercurio_capability import CapabilityRequest

SYNTHETIC_GRAPH = {
    "nodes": [
        # Root
        {"id": "Satellite",          "kind": "PartDefinition", "properties": {"declared_name": "Satellite"}},
        # Level 1
        {"id": "PayloadAssembly",    "kind": "PartDefinition", "properties": {"declared_name": "PayloadAssembly"}},
        {"id": "SpacecraftBus",      "kind": "PartDefinition", "properties": {"declared_name": "SpacecraftBus"}},
        {"id": "CommSubsystem",      "kind": "PartDefinition", "properties": {"declared_name": "CommunicationsSubsystem"}},
        # Level 2 — Payload
        {"id": "OpticalImager",      "kind": "PartDefinition", "properties": {"declared_name": "OpticalImager"}},
        {"id": "ImageProcessor",     "kind": "PartDefinition", "properties": {"declared_name": "ImageProcessor"}},
        # Level 2 — Bus
        {"id": "EPS",                "kind": "PartDefinition", "properties": {"declared_name": "ElectricalPowerSubsystem"}},
        {"id": "ADCS",               "kind": "PartDefinition", "properties": {"declared_name": "AttitudeControlSubsystem"}},
        {"id": "Thermal",            "kind": "PartDefinition", "properties": {"declared_name": "ThermalControlSubsystem"}},
        # Level 2 — Comms
        {"id": "RFTransceiver",      "kind": "PartDefinition", "properties": {"declared_name": "RFTransceiver"}},
        {"id": "DeployableAntenna",  "kind": "PartDefinition", "properties": {"declared_name": "DeployableAntenna"}},
        # Level 3 — EPS
        {"id": "SolarArray",         "kind": "PartDefinition", "properties": {"declared_name": "SolarArray"}},
        {"id": "Battery",            "kind": "PartDefinition", "properties": {"declared_name": "LithiumIonBattery"}},
        {"id": "PDU",                "kind": "PartDefinition", "properties": {"declared_name": "PowerDistributionUnit"}},
        # Level 3 — ADCS
        {"id": "RW1",                "kind": "PartDefinition", "properties": {"declared_name": "ReactionWheel"}},
        {"id": "RW2",                "kind": "PartDefinition", "properties": {"declared_name": "ReactionWheel"}},
        {"id": "RW3",                "kind": "PartDefinition", "properties": {"declared_name": "ReactionWheel"}},
        {"id": "StarTracker",        "kind": "PartDefinition", "properties": {"declared_name": "StarTracker"}},
        # Level 3 — Thermal
        {"id": "HeatPipe",           "kind": "PartDefinition", "properties": {"declared_name": "HeatPipe"}},
        {"id": "Radiator",           "kind": "PartDefinition", "properties": {"declared_name": "Radiator"}},
        # Orphaned cluster — not connected to Satellite
        {"id": "DebugProbe",         "kind": "PartDefinition", "properties": {"declared_name": "DebugProbe"}},
        {"id": "GSInterface",        "kind": "PartDefinition", "properties": {"declared_name": "GroundSupportInterface"}},
    ],
    "edges": [
        # Satellite → level 1
        {"source": "Satellite",       "target": "PayloadAssembly",   "relation": "owns"},
        {"source": "Satellite",       "target": "SpacecraftBus",     "relation": "owns"},
        {"source": "Satellite",       "target": "CommSubsystem",     "relation": "owns"},
        # Payload
        {"source": "PayloadAssembly", "target": "OpticalImager",     "relation": "owns"},
        {"source": "PayloadAssembly", "target": "ImageProcessor",    "relation": "owns"},
        # Bus
        {"source": "SpacecraftBus",   "target": "EPS",               "relation": "owns"},
        {"source": "SpacecraftBus",   "target": "ADCS",              "relation": "owns"},
        {"source": "SpacecraftBus",   "target": "Thermal",           "relation": "owns"},
        # Comms
        {"source": "CommSubsystem",   "target": "RFTransceiver",     "relation": "owns"},
        {"source": "CommSubsystem",   "target": "DeployableAntenna", "relation": "owns"},
        # EPS
        {"source": "EPS",             "target": "SolarArray",        "relation": "owns"},
        {"source": "EPS",             "target": "Battery",           "relation": "owns"},
        {"source": "EPS",             "target": "PDU",               "relation": "owns"},
        # ADCS
        {"source": "ADCS",            "target": "RW1",               "relation": "owns"},
        {"source": "ADCS",            "target": "RW2",               "relation": "owns"},
        {"source": "ADCS",            "target": "RW3",               "relation": "owns"},
        {"source": "ADCS",            "target": "StarTracker",       "relation": "owns"},
        # Thermal
        {"source": "Thermal",         "target": "HeatPipe",          "relation": "owns"},
        {"source": "Thermal",         "target": "Radiator",          "relation": "owns"},
        # Orphaned cluster — internal edge but disconnected from root
        {"source": "DebugProbe",      "target": "GSInterface",       "relation": "owns"},
    ],
}

REQUEST_JSON = {
    "request_id": "test-connectivity-001",
    "capability_id": "org.example.structural-connectivity",
    "context": {
        "context_id": "ctx.test",
        "kind": "accepted",
        "artifact": {"artifact_key": "test-kir", "kir_schema_version": "0.1"},
    },
    "parameters": {
        "graph": SYNTHETIC_GRAPH,
    },
}


def main() -> None:
    request = CapabilityRequest.from_json(REQUEST_JSON)
    request._descriptor = {
        "id": "org.example.structural-connectivity",
        "kind": "mercurio.capability.kind/static-analysis",
        "name": "Structural Connectivity Analysis",
        "version": "0.1.0",
        "api_version": "0.1",
        "deterministic": True,
        "input_artifact_kinds": ["kir", "graph"],
        "output_artifact_kinds": ["table", "reasoning_report"],
    }

    report = analyze(request)

    print(f"Status:   {report.status}")
    print(f"Findings: {len(report.findings)}")
    print()

    for f in report.findings:
        icon = {"info": "[i]", "warning": "[!]", "error": "[x]", "critical": "[!!]"}.get(f.severity, "[?]")
        print(f"  {icon} [{f.severity.upper()}] {f.title}")
        print(f"     {f.message}")
        print()

    print("Artifacts:")
    for a in report.artifacts:
        payload = a.payload
        columns = payload.get("columns", [])
        rows = payload.get("rows", [])
        print(f"  {a.id}  ({len(rows)} rows)")
        print(f"  {'  '.join(f'{c:<20}' for c in columns)}")
        print(f"  {'-' * (22 * len(columns))}")
        for row in rows:
            print(f"  {'  '.join(f'{str(v):<20}' for v in row)}")
        print()


if __name__ == "__main__":
    main()
