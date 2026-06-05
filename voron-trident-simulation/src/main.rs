//! Voron Trident 350 + Indx — concurrent multi-machine simulation example.
//!
//! Demonstrates Phase 4 of the Mercurio simulation stack:
//!
//! - **Three concurrent state machines** are authored in SysML and run on a shared time axis:
//!   `VoronLifecycle` (printer), `BedLifecycle` (heated bed), and
//!   `HotendLifecycle` (toolhead).
//! - **Rate effects** drive `bed.temperature` at 2.3 °C/s and
//!   `hotend.temperature` at 5.0 °C/s while their respective machines are
//!   in their `Heating` states.
//! - **Cross-machine coordination**: when the bed reaches 110 °C it writes
//!   `printer.bed_temperature = 110.0` via an Assign effect.  The printer
//!   machine's `Change` guard fires as soon as that value ≥ 105 °C,
//!   transitioning it from `Heating` → `Printing`.  This is the cross-part
//!   guard pattern: one machine's transition effect unblocks another
//!   machine's guard.
//!
//! Run with:
//!
//! ```
//! cargo run -p mercurio-voron-trident-simulation-example
//! ```

use std::collections::BTreeMap;

use mercurio_core::{KirElement, Runtime};
use mercurio_sysml::{
    ConcurrentSimulationScenario, ConcurrentSubjectScenario, KirDocument,
    StateMachineScenarioEvent, compile_sysml_text, load_sysml_baseline, run_concurrent_simulation,
    scenario_from_analysis_case,
};
use serde_json::{Value, json};

const VORON_MODEL: &str = include_str!("../model/voron-trident-350.sysml");

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let mut document = build_voron_document()?;
    append_print_sequence_analysis_case(&mut document)?;
    let runtime = Runtime::from_document(document)?;
    let scenario = scenario_from_analysis_case(&runtime, "analysis.PrintSequence")?;

    println!("Running Voron Trident 350 analysis case: PrintSequence");
    println!(
        "  subjects : {}",
        scenario
            .subjects
            .iter()
            .map(|s| s.subject_id.as_str())
            .collect::<Vec<_>>()
            .join(", ")
    );
    println!("  max_steps: {}", scenario.max_steps);
    println!();

    let trace = run_concurrent_simulation(&runtime, scenario)?;

    // ── Print the trace ──────────────────────────────────────────────────
    println!(
        "{:<6}  {:<18}  {:<18}  {:<18}  {:>8}  {:>10}",
        "t (s)", "Printer", "Bed", "Hotend", "Bed °C", "Hotend °C"
    );
    println!("{}", "─".repeat(90));

    for entry in &trace.timeline {
        let printer_state = entry
            .states
            .get("individual.printer")
            .and_then(|v| v.first())
            .map(|s| s.as_str())
            .unwrap_or("—");
        let bed_state = entry
            .states
            .get("individual.bed")
            .and_then(|v| v.first())
            .map(|s| s.as_str())
            .unwrap_or("—");
        let hotend_state = entry
            .states
            .get("individual.hotend")
            .and_then(|v| v.first())
            .map(|s| s.as_str())
            .unwrap_or("—");

        let bed_temp = entry
            .values
            .get(&("individual.bed".to_string(), "temperature".to_string()))
            .and_then(Value::as_f64)
            .unwrap_or(22.0);
        let hotend_temp = entry
            .values
            .get(&("individual.hotend".to_string(), "temperature".to_string()))
            .and_then(Value::as_f64)
            .unwrap_or(22.0);

        println!(
            "{:<6.1}  {:<18}  {:<18}  {:<18}  {:>7.1}°  {:>9.1}°",
            entry.t,
            shorten(printer_state),
            shorten(bed_state),
            shorten(hotend_state),
            bed_temp,
            hotend_temp,
        );
    }

    println!();
    println!(
        "Simulation complete — {} trace entries, status: {:?}",
        trace.timeline.len(),
        trace.status
    );

    // ── Show channels ────────────────────────────────────────────────────
    println!();
    println!("Channels recorded ({}):", trace.channels.len());
    for ch in &trace.channels {
        println!("  {:40}  {:?}", ch.id, ch.source);
    }

    Ok(())
}

// ── Scenario ─────────────────────────────────────────────────────────────────

#[allow(dead_code)]
fn build_scenario() -> ConcurrentSimulationScenario {
    ConcurrentSimulationScenario {
        id: "voron.print_sequence".to_string(),
        subjects: vec![
            // ── Printer ────────────────────────────────────────────────
            ConcurrentSubjectScenario {
                subject_id: "individual.printer".to_string(),
                machine_id: "VoronLifecycle".to_string(),
                initial_state_id: None,
                // "start" fires the first After transition chain.
                events: vec![StateMachineScenarioEvent {
                    id: "event.printer.start".to_string(),
                    trigger: "start".to_string(),
                }],
            },
            // ── Heated bed ─────────────────────────────────────────────
            ConcurrentSubjectScenario {
                subject_id: "individual.bed".to_string(),
                machine_id: "BedLifecycle".to_string(),
                initial_state_id: None,
                events: vec![],
            },
            // ── Hotend ─────────────────────────────────────────────────
            ConcurrentSubjectScenario {
                subject_id: "individual.hotend".to_string(),
                machine_id: "HotendLifecycle".to_string(),
                initial_state_id: None,
                events: vec![],
            },
        ],
        max_steps: 200,
        step_duration_s: 1.0,
        initial_values: BTreeMap::from([
            (
                (
                    "individual.printer".to_string(),
                    "bed_temperature".to_string(),
                ),
                json!(22.0),
            ),
            (
                (
                    "individual.printer".to_string(),
                    "hotend_temperature".to_string(),
                ),
                json!(22.0),
            ),
            (
                ("individual.bed".to_string(), "temperature".to_string()),
                json!(22.0),
            ),
            (
                ("individual.hotend".to_string(), "temperature".to_string()),
                json!(22.0),
            ),
        ]),
    }
}

// ── KIR document ─────────────────────────────────────────────────────────────
//
// Compiles voron-trident-350.sysml, then appends the executable simulation
// metadata that is not yet lowerable from authored SysML.
//
// State machine topology
// ──────────────────────
//
//  VoronLifecycle (subject: individual.printer)
//    Idle ──[start event]──────────────────────> Homing
//    Homing ──[After 2.5s]─────────────────────> Heating
//    Heating ──[Change: printer.bed_temperature ≥ 105]──> Printing
//    Printing ──[After 5.0s]───────────────────> ToolChange
//    ToolChange ──[After 3.0s]─────────────────> Printing2
//
//  BedLifecycle (subject: individual.bed)
//    BedCold ──[After 0.5s]──────────────────── > BedHeating (nearly immediate)
//    BedHeating ──[After 37.8s, Rate(temp 2.3/s)]──> BedReady
//      entry into BedReady: Assign (printer.bed_temperature = 110)
//                           ← this triggers the printer's Change guard
//
//  HotendLifecycle (subject: individual.hotend)
//    HotendCold ──[After 0.5s]───────────────── > HotendHeating
//    HotendHeating ──[After 45.6s, Rate(temp 5.0/s)]──> HotendReady
//      entry into HotendReady: Assign (printer.hotend_temperature = 250)

fn build_voron_document() -> Result<KirDocument, Box<dyn std::error::Error>> {
    let stdlib = load_sysml_baseline()?;
    let mut document = compile_sysml_text(VORON_MODEL, "voron-trident-350.sysml", &stdlib)
        .map_err(|diagnostic| format!("failed to compile Voron SysML model: {diagnostic}"))?;
    append_runtime_subject_aliases(&mut document);
    append_simulation_semantic_overlay(&mut document)?;
    Ok(document)
}

#[allow(dead_code)]
fn build_legacy_voron_document() -> KirDocument {
    KirDocument {
        metadata: BTreeMap::new(),
        elements: vec![
            // ── Types ────────────────────────────────────────────────────
            el("type.Printer", "Model::Systems::PartDefinition", &[]),
            el("type.Bed", "Model::Systems::PartDefinition", &[]),
            el("type.Hotend", "Model::Systems::PartDefinition", &[]),
            // ── Individuals ──────────────────────────────────────────────
            el(
                "individual.printer",
                "Model::IndividualUsage",
                &[
                    ("declared_name", json!("printer")),
                    ("type", json!("type.Printer")),
                ],
            ),
            el(
                "individual.bed",
                "Model::IndividualUsage",
                &[("declared_name", json!("bed")), ("type", json!("type.Bed"))],
            ),
            el(
                "individual.hotend",
                "Model::IndividualUsage",
                &[
                    ("declared_name", json!("hotend")),
                    ("type", json!("type.Hotend")),
                ],
            ),
            // ── Guard calculations ───────────────────────────────────────
            // printer.bed_temperature >= 105
            el(
                "feature.Printer.bedReady",
                "Model::CalculationUsage",
                &[
                    ("declared_name", json!("bedReady")),
                    ("owner", json!("type.Printer")),
                    ("expression_ir", gte_path("bed_temperature", 105.0)),
                ],
            ),
            // ── VoronLifecycle ───────────────────────────────────────────
            state("state.printer.Idle", "VoronLifecycle", true, false),
            state("state.printer.Homing", "VoronLifecycle", false, false),
            state("state.printer.Heating", "VoronLifecycle", false, false),
            state("state.printer.Printing", "VoronLifecycle", false, false),
            state("state.printer.ToolChange", "VoronLifecycle", false, false),
            state("state.printer.Printing2", "VoronLifecycle", false, false),
            // Idle → Homing on "start" event
            transition(
                "tr.printer.idle_homing",
                "VoronLifecycle",
                "state.printer.Idle",
                "state.printer.Homing",
                "start",
                "event",
                &[],
            ),
            // Homing → Heating after 2.5s
            transition(
                "tr.printer.homing_heating",
                "VoronLifecycle",
                "state.printer.Homing",
                "state.printer.Heating",
                "2.5",
                "after",
                &[],
            ),
            // Heating → Printing when printer.bed_temperature >= 105
            transition(
                "tr.printer.heating_printing",
                "VoronLifecycle",
                "state.printer.Heating",
                "state.printer.Printing",
                "bed_temperature >= 105",
                "change",
                &[("guard_feature", json!("feature.Printer.bedReady"))],
            ),
            // Printing → ToolChange after 5s
            transition(
                "tr.printer.printing_toolchange",
                "VoronLifecycle",
                "state.printer.Printing",
                "state.printer.ToolChange",
                "5.0",
                "after",
                &[],
            ),
            // ToolChange → Printing2 after 3s; swap to T1
            transition(
                "tr.printer.toolchange_printing2",
                "VoronLifecycle",
                "state.printer.ToolChange",
                "state.printer.Printing2",
                "3.0",
                "after",
                &[(
                    "effects",
                    json!([
                        { "kind": "assign", "feature": "activeTool", "value": 1.0 }
                    ]),
                )],
            ),
            // ── BedLifecycle ─────────────────────────────────────────────
            state("state.bed.Cold", "BedLifecycle", true, false),
            state("state.bed.Heating", "BedLifecycle", false, false),
            state("state.bed.Ready", "BedLifecycle", false, false),
            // Cold → Heating immediately (0.5s warm-up)
            transition(
                "tr.bed.cold_heating",
                "BedLifecycle",
                "state.bed.Cold",
                "state.bed.Heating",
                "0.5",
                "after",
                &[],
            ),
            // Heating → Ready after 37.8s (22 + 2.3 * 37.8 ≈ 109 °C)
            // Rate effect drives bed.temperature upward.
            // Assign effect signals the printer: printer.bed_temperature = 110.
            transition(
                "tr.bed.heating_ready",
                "BedLifecycle",
                "state.bed.Heating",
                "state.bed.Ready",
                "37.8",
                "after",
                &[(
                    "effects",
                    json!([
                        {
                            "kind":            "rate",
                            "feature":         "temperature",
                            "rate_per_second": 2.3,
                            "unit":            "C"
                        },
                        // Write into the printer subject's namespace so the
                        // printer's Change guard can read it.
                        {
                            "kind":    "assign",
                            "feature": "bed_temperature",
                            "value":   110.0
                        }
                    ]),
                )],
            ),
            // ── HotendLifecycle ──────────────────────────────────────────
            state("state.hotend.Cold", "HotendLifecycle", true, false),
            state("state.hotend.Heating", "HotendLifecycle", false, false),
            state("state.hotend.Ready", "HotendLifecycle", false, false),
            // Cold → Heating immediately
            transition(
                "tr.hotend.cold_heating",
                "HotendLifecycle",
                "state.hotend.Cold",
                "state.hotend.Heating",
                "0.5",
                "after",
                &[],
            ),
            // Heating → Ready after 45.6s (22 + 5.0 * 45.6 = 250 °C)
            transition(
                "tr.hotend.heating_ready",
                "HotendLifecycle",
                "state.hotend.Heating",
                "state.hotend.Ready",
                "45.6",
                "after",
                &[(
                    "effects",
                    json!([
                        {
                            "kind":            "rate",
                            "feature":         "temperature",
                            "rate_per_second": 5.0,
                            "unit":            "C"
                        },
                        {
                            "kind":    "assign",
                            "feature": "hotend_temperature",
                            "value":   250.0
                        }
                    ]),
                )],
            ),
        ],
    }
}

// ── KIR element helpers ───────────────────────────────────────────────────────

fn el(id: &str, kind: &str, props: &[(&str, Value)]) -> KirElement {
    KirElement {
        id: id.to_string(),
        kind: kind.to_string(),
        layer: 0,
        properties: props
            .iter()
            .map(|(k, v)| (k.to_string(), v.clone()))
            .collect(),
    }
}

fn state(id: &str, owner: &str, initial: bool, is_final: bool) -> KirElement {
    el(
        id,
        "StateUsage",
        &[
            ("declared_name", json!(id)),
            ("owning_type", json!(owner)),
            ("is_initial", json!(initial)),
            ("is_final", json!(is_final)),
        ],
    )
}

fn transition(
    id: &str,
    owner: &str,
    source: &str,
    target: &str,
    trigger: &str,
    trigger_kind: &str,
    extra: &[(&str, Value)],
) -> KirElement {
    let mut props = vec![
        ("owning_type", json!(owner)),
        ("source", json!(source)),
        ("target", json!(target)),
        ("trigger", json!(trigger)),
        ("trigger_kind", json!(trigger_kind)),
    ];
    props.extend(extra.iter().map(|(k, v)| (*k, v.clone())));
    el(id, "TransitionUsage", &props)
}

fn initial_marker(id: &str, target: &str) -> KirElement {
    el(
        id,
        "SuccessionFlowUsage",
        &[
            ("target", json!(target)),
            ("trigger_kind", json!("completion")),
        ],
    )
}

/// Expression IR for `self.<feature> >= <threshold>`.
fn gte_path(feature: &str, threshold: f64) -> Value {
    json!({
        "kind": "binary",
        "op":   "greater_equal",
        "left": {
            "kind":     "path",
            "root":     "self",
            "segments": [feature]
        },
        "right": {
            "kind":  "literal",
            "value": threshold
        }
    })
}

fn append_runtime_subject_aliases(document: &mut KirDocument) {
    document.elements.extend([
        el(
            "individual.printer",
            "Model::IndividualUsage",
            &[
                ("declared_name", json!("printer")),
                ("type", json!("type.VoronTrident350.VoronPrinter")),
            ],
        ),
        el(
            "individual.bed",
            "Model::IndividualUsage",
            &[
                ("declared_name", json!("bed")),
                ("type", json!("type.VoronTrident350.HeatedBed")),
            ],
        ),
        el(
            "individual.hotend",
            "Model::IndividualUsage",
            &[
                ("declared_name", json!("hotend")),
                ("type", json!("type.VoronTrident350.Hotend")),
            ],
        ),
    ]);
}

fn append_simulation_semantic_overlay(
    document: &mut KirDocument,
) -> Result<(), Box<dyn std::error::Error>> {
    document.elements.push(el(
        "feature.Printer.bedReady",
        "Model::CalculationUsage",
        &[
            ("declared_name", json!("bedReady")),
            ("owner", json!("type.VoronTrident350.VoronPrinter")),
            ("expression_ir", gte_path("bed_temperature", 105.0)),
        ],
    ));

    let printer_initial = state_by_name_mut(document, "Idle", "VoronPrinter")?
        .id
        .clone();
    let bed_initial = state_by_name_mut(document, "Cold", "HeatedBed")?.id.clone();
    let hotend_initial = state_by_name_mut(document, "Cold", "Hotend")?.id.clone();

    state_by_name_mut(document, "Idle", "VoronPrinter")?
        .properties
        .insert("is_initial".to_string(), json!(true));
    state_by_name_mut(document, "Cold", "HeatedBed")?
        .properties
        .insert("is_initial".to_string(), json!(true));
    state_by_name_mut(document, "Cold", "Hotend")?
        .properties
        .insert("is_initial".to_string(), json!(true));
    document.elements.extend([
        initial_marker("initial.printer.lifecycle", &printer_initial),
        initial_marker("initial.bed.lifecycle", &bed_initial),
        initial_marker("initial.hotend.lifecycle", &hotend_initial),
    ]);

    transition_by_name_mut(document, "heating_printing", "VoronPrinter")?
        .properties
        .insert(
            "guard_feature".to_string(),
            json!("feature.Printer.bedReady"),
        );
    transition_by_name_mut(document, "toolchange_printing2", "VoronPrinter")?
        .properties
        .insert(
            "effects".to_string(),
            json!([{ "kind": "assign", "feature": "activeTool", "value": 1.0 }]),
        );
    transition_by_name_mut(document, "heating_ready", "HeatedBed")?
        .properties
        .insert(
            "effects".to_string(),
            json!([
                {
                    "kind":            "rate",
                    "feature":         "temperature",
                    "rate_per_second": 2.3,
                    "unit":            "C"
                },
                {
                    "kind":    "assign",
                    "feature": "bed_temperature",
                    "value":   110.0
                }
            ]),
        );
    transition_by_name_mut(document, "heating_ready", "Hotend")?
        .properties
        .insert(
            "effects".to_string(),
            json!([
                {
                    "kind":            "rate",
                    "feature":         "temperature",
                    "rate_per_second": 5.0,
                    "unit":            "C"
                },
                {
                    "kind":    "assign",
                    "feature": "hotend_temperature",
                    "value":   250.0
                }
            ]),
        );

    Ok(())
}

fn transition_by_name_mut<'a>(
    document: &'a mut KirDocument,
    name: &str,
    owner_hint: &str,
) -> Result<&'a mut KirElement, Box<dyn std::error::Error>> {
    if let Some(index) = document.elements.iter().position(|element| {
        (element.kind.contains("Transition") || element.id.starts_with("transition."))
            && element
                .properties
                .get("declared_name")
                .and_then(Value::as_str)
                .is_some_and(|declared| declared == name)
            && (element
                .properties
                .get("owning_type")
                .or_else(|| element.properties.get("owner"))
                .and_then(Value::as_str)
                .is_some_and(|owner| owner.contains(owner_hint))
                || element.id.contains(owner_hint))
    }) {
        return Ok(&mut document.elements[index]);
    }

    let candidates = document
        .elements
        .iter()
        .filter(|element| element.id.contains(name) || element.kind.contains("Transition"))
        .map(|element| {
            format!(
                "{} kind={} owner={:?} name={:?}",
                element.id,
                element.kind,
                element
                    .properties
                    .get("owning_type")
                    .or_else(|| element.properties.get("owner")),
                element.properties.get("declared_name")
            )
        })
        .collect::<Vec<_>>()
        .join("; ");
    Err(format!(
        "compiled model is missing transition `{name}` for `{owner_hint}`; candidates: {candidates}"
    )
    .into())
}

fn state_by_name_mut<'a>(
    document: &'a mut KirDocument,
    name: &str,
    owner_hint: &str,
) -> Result<&'a mut KirElement, Box<dyn std::error::Error>> {
    if let Some(index) = document.elements.iter().position(|element| {
        (element.kind.contains("StateUsage") || element.id.starts_with("state."))
            && element
                .properties
                .get("declared_name")
                .and_then(Value::as_str)
                .is_some_and(|declared| declared == name)
            && (element
                .properties
                .get("owning_type")
                .and_then(Value::as_str)
                .is_some_and(|owner| owner.contains(owner_hint))
                || element.id.contains(owner_hint))
    }) {
        return Ok(&mut document.elements[index]);
    }

    Err(format!("compiled model is missing state `{name}` for `{owner_hint}`").into())
}

fn machine_id_for_state(
    document: &KirDocument,
    state_name: &str,
    owner_hint: &str,
) -> Result<String, Box<dyn std::error::Error>> {
    document
        .elements
        .iter()
        .find(|element| {
            (element.kind.contains("StateUsage") || element.id.starts_with("state."))
                && element
                    .properties
                    .get("declared_name")
                    .and_then(Value::as_str)
                    .is_some_and(|declared| declared == state_name)
                && (element
                    .properties
                    .get("owning_type")
                    .and_then(Value::as_str)
                    .is_some_and(|owner| owner.contains(owner_hint))
                    || element.id.contains(owner_hint))
        })
        .and_then(|element| {
            element
                .properties
                .get("owning_type")
                .and_then(Value::as_str)
                .map(ToOwned::to_owned)
        })
        .ok_or_else(|| {
            let candidates = document
                .elements
                .iter()
                .filter(|element| element.id.contains(state_name))
                .map(|element| {
                    format!(
                        "{} kind={} owner={:?} name={:?}",
                        element.id,
                        element.kind,
                        element.properties.get("owning_type"),
                        element.properties.get("declared_name")
                    )
                })
                .collect::<Vec<_>>()
                .join("; ");
            format!(
                "compiled model is missing state `{state_name}` for `{owner_hint}`; candidates: {candidates}"
            )
            .into()
        })
}

fn state_id_for_state(
    document: &KirDocument,
    state_name: &str,
    owner_hint: &str,
) -> Result<String, Box<dyn std::error::Error>> {
    document
        .elements
        .iter()
        .find(|element| {
            (element.kind.contains("StateUsage") || element.id.starts_with("state."))
                && element
                    .properties
                    .get("declared_name")
                    .and_then(Value::as_str)
                    .is_some_and(|declared| declared == state_name)
                && (element
                    .properties
                    .get("owning_type")
                    .and_then(Value::as_str)
                    .is_some_and(|owner| owner.contains(owner_hint))
                    || element.id.contains(owner_hint))
        })
        .map(|element| element.id.clone())
        .ok_or_else(|| {
            format!("compiled model is missing state `{state_name}` for `{owner_hint}`").into()
        })
}

fn shorten(s: &str) -> &str {
    // Strip the common state id prefixes for display
    s.rsplit('.').next().unwrap_or(s)
}

fn append_print_sequence_analysis_case(
    document: &mut KirDocument,
) -> Result<(), Box<dyn std::error::Error>> {
    let printer_machine = machine_id_for_state(document, "Idle", "VoronPrinter")?;
    let bed_machine = machine_id_for_state(document, "Cold", "HeatedBed")?;
    let hotend_machine = machine_id_for_state(document, "Cold", "Hotend")?;
    let printer_initial = state_id_for_state(document, "Idle", "VoronPrinter")?;
    let bed_initial = state_id_for_state(document, "Cold", "HeatedBed")?;
    let hotend_initial = state_id_for_state(document, "Cold", "Hotend")?;

    document.elements.push(el(
        "analysis.PrintSequence",
        "SysML::Systems::AnalysisCaseDefinition",
        &[
            ("declared_name", json!("PrintSequence")),
            ("simulation_kind", json!("concurrent_state_machine")),
            ("max_steps", json!(200)),
            ("step_duration_s", json!(1.0)),
            (
                "subjects",
                json!([
                    {
                        "subject": "individual.printer",
                        "machine": printer_machine,
                        "initial_state": printer_initial,
                        "events": [
                            { "id": "event.printer.start", "trigger": "start" }
                        ]
                    },
                    {
                        "subject": "individual.bed",
                        "machine": bed_machine,
                        "initial_state": bed_initial,
                        "events": []
                    },
                    {
                        "subject": "individual.hotend",
                        "machine": hotend_machine,
                        "initial_state": hotend_initial,
                        "events": []
                    }
                ]),
            ),
            (
                "initial_values",
                json!({
                    "individual.printer|bed_temperature": 22.0,
                    "individual.printer|hotend_temperature": 22.0,
                    "individual.bed|temperature": 22.0,
                    "individual.hotend|temperature": 22.0
                }),
            ),
            (
                "objectives",
                json!([
                    "individual.bed|temperature",
                    "individual.hotend|temperature",
                    "individual.printer|bed_temperature",
                    "individual.printer|hotend_temperature"
                ]),
            ),
        ],
    ));
    Ok(())
}
