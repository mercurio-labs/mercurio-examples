use mercurio_sysml::SysmlEnvironment;

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let env = SysmlEnvironment::latest_metamodel()?;
    let source = r#"
package Demo {
    part def Vehicle;
    part vehicle : Vehicle;
}
"#;

    let document = env.compile_text(source, "demo.sysml")?;

    println!("metamodel: {}", env.metamodel().id);
    println!("elements: {}", document.elements.len());

    Ok(())
}
