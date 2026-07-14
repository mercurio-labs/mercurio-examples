use mercurio_language_contracts::LanguageRegistry;
use mercurio_simple_language::SimpleLanguageService;

fn main() {
    let mut registry = LanguageRegistry::new();
    registry.register(SimpleLanguageService);

    let source = "component Vehicle\ncomponent Engine\npart Vehicle.engine: Engine\nrequirement R1 \"Vehicle shall start\"\nsatisfy Vehicle -> R1\n";
    let library_context = mercurio_kir::KirDocument {
        metadata: Default::default(),
        elements: Vec::new(),
    };
    let report = registry.compile_path(
        std::path::Path::new("demo.simple"),
        source,
        &library_context,
    );

    println!("status: {:?}", report.status);
    println!("elements: {}", report.document.unwrap().elements.len());
}
