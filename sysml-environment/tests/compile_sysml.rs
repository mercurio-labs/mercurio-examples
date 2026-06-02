use mercurio_sysml::{SYSML_2_0_METAMODEL_057_ID, SysmlEnvironment, available_metamodels};

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

    assert!(metamodels
        .iter()
        .any(|metamodel| metamodel.id == SYSML_2_0_METAMODEL_057_ID));
}

