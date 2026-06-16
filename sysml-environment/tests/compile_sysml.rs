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
