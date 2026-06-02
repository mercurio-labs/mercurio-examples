use mercurio_language_contracts::{LanguageRegistry, SemanticCompileStatus};
use mercurio_simple_language::SimpleLanguageService;

#[test]
fn host_registers_simple_language() {
    let mut registry = LanguageRegistry::new();
    registry.register(SimpleLanguageService);
    let library_context = mercurio_kir::KirDocument {
        metadata: Default::default(),
        elements: Vec::new(),
    };

    let report = registry.compile_path(
        std::path::Path::new("vehicle.simple"),
        "component Vehicle\nrequirement R1 \"Vehicle shall start\"\nsatisfy Vehicle -> R1\n",
        &library_context,
    );

    assert_eq!(report.status, SemanticCompileStatus::Ok);
    assert!(report.document.unwrap().elements.iter().any(|element| element.id == "type.Vehicle"));
}
