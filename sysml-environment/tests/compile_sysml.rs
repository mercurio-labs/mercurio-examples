use std::sync::Arc;

use mercurio_core::{Graph, RhaiEngine};
use mercurio_sysml::{SYSML_2_0_METAMODEL_057_ID, SysmlEnvironment, available_metamodels};

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
        element.properties.get("declared_name").and_then(|name| name.as_str())
            == Some("Vehicle")
    }));
    assert!(document.elements.iter().any(|element| {
        element.properties.get("declared_name").and_then(|name| name.as_str())
            == Some("VehicleMassComplianceAnalysis")
    }));
}

#[test]
fn vehicle_mass_compliance_fixture_evaluates_mass_query() {
    let env = SysmlEnvironment::latest_metamodel().unwrap();
    let source = include_str!("../../vehicle-mass-compliance/model/vehicle-mass-compliance.sysml");
    let document = env
        .compile_text(source, "vehicle-mass-compliance.sysml")
        .unwrap();
    let graph = Arc::new(Graph::from_document(document).unwrap());

    let result = RhaiEngine::new()
        .eval_query(
            graph,
            r#"sum(model.parts().map(|p| p.property("mass_kg")))"#,
        )
        .unwrap();

    assert_eq!(result.columns, vec!["value"]);
    assert_eq!(result.rows[0][0].as_f64(), Some(1070.0));
}
