use std::sync::Arc;

use mercurio_core::{Graph, RhaiEngine};
use mercurio_sysml::{SYSML_2_0_METAMODEL_057_ID, SysmlEnvironment, available_metamodels};
use serde_json::Value;

const SYSML_2_0_PILOT_2026_04_ID: &str = "sysml-2.0-pilot-2026-04";

#[test]
fn compiles_sysml_with_latest_metamodel() {
    let env = SysmlEnvironment::latest_metamodel().unwrap();
    let document = env
        .compile_text("package Demo { part def Vehicle; }", "demo.sysml")
        .unwrap();

    assert_eq!(env.metamodel().id, SYSML_2_0_METAMODEL_057_ID);
    assert!(!document.elements.is_empty());
}

#[test]
fn lists_available_metamodels() {
    let metamodels = available_metamodels().unwrap();

    assert!(
        metamodels
            .iter()
            .any(|metamodel| metamodel.id == SYSML_2_0_METAMODEL_057_ID)
    );
    assert!(
        metamodels
            .iter()
            .any(|metamodel| metamodel.id == SYSML_2_0_PILOT_2026_04_ID)
    );
}

#[test]
fn compiles_sysml_with_2026_04_release_selector() {
    let env = SysmlEnvironment::for_metamodel("2026-04").unwrap();
    let document = env
        .compile_text("package Demo { part def Vehicle; }", "demo.sysml")
        .unwrap();

    assert_eq!(env.metamodel().id, SYSML_2_0_PILOT_2026_04_ID);
    assert!(!document.elements.is_empty());
}

#[test]
fn compiles_vehicle_mass_compliance_fixture() {
    let env = SysmlEnvironment::latest_metamodel().unwrap();
    let source = include_str!("../../vehicle-mass-compliance/model/vehicle-mass-compliance.sysml");
    let document = env
        .compile_text(source, "vehicle-mass-compliance.sysml")
        .unwrap();

    assert!(document.elements.iter().any(|element| {
        element
            .properties
            .get("declared_name")
            .and_then(|name| name.as_str())
            == Some("Vehicle")
    }));
    assert!(document.elements.iter().any(|element| {
        element
            .properties
            .get("declared_name")
            .and_then(|name| name.as_str())
            == Some("VehicleMassComplianceAnalysis")
    }));
}

#[test]
fn vehicle_mass_compliance_fixture_evaluates_mass_query() {
    let graph = vehicle_mass_compliance_graph();

    let result = RhaiEngine::new()
        .eval_query(
            graph,
            r#"sum(model.parts().map(|p| p.property("mass_kg")))"#,
        )
        .unwrap();

    assert_eq!(result.columns, vec!["value"]);
    assert_eq!(result.rows[0][0].as_f64(), Some(1070.0));
}

#[test]
fn vehicle_mass_compliance_fixture_evaluates_analysis_result() {
    let graph = vehicle_mass_compliance_graph();

    let result = RhaiEngine::new()
        .eval_query(
            graph,
            r#"
                let vehicle = model.parts()
                    .where(|p| p.property("declared_name") == "Vehicle")
                    .first();
                let total = sum(model.parts().map(|p| p.property("mass_kg")));
                let max = vehicle.property("max_mass_kg");
                #{
                    total_mass_kg: total,
                    max_mass_kg: max,
                    margin_kg: max - total,
                    verdict: if total <= max { "pass" } else { "fail" }
                }
            "#,
        )
        .unwrap();

    assert_eq!(
        cell(&result, "total_mass_kg").and_then(Value::as_f64),
        Some(1070.0)
    );
    assert_eq!(
        cell(&result, "max_mass_kg").and_then(Value::as_f64),
        Some(1500.0)
    );
    assert_eq!(
        cell(&result, "margin_kg").and_then(Value::as_f64),
        Some(430.0)
    );
    assert_eq!(
        cell(&result, "verdict").and_then(Value::as_str),
        Some("pass")
    );
}

fn vehicle_mass_compliance_graph() -> Arc<Graph> {
    let env = SysmlEnvironment::latest_metamodel().unwrap();
    let source = include_str!("../../vehicle-mass-compliance/model/vehicle-mass-compliance.sysml");
    let document = env
        .compile_text(source, "vehicle-mass-compliance.sysml")
        .unwrap();
    Arc::new(Graph::from_document(document).unwrap())
}

fn cell<'a>(result: &'a mercurio_core::DslQueryResult, column: &str) -> Option<&'a Value> {
    let column_index = result
        .columns
        .iter()
        .position(|candidate| candidate == column)?;
    result.rows.first()?.get(column_index)
}
