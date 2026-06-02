use std::collections::BTreeMap;

use mercurio_kir::{KirDocument, KirElement};
use mercurio_language_contracts::{
    CompileContext, Diagnostic, LanguageService, SemanticCompileReport, SemanticCompileStatus,
};
use serde_json::json;

#[derive(Debug, Default)]
pub struct SimpleLanguageService;

impl LanguageService for SimpleLanguageService {
    fn language_id(&self) -> &str {
        "simple"
    }

    fn extensions(&self) -> &[&str] {
        &["simple"]
    }

    fn compile(
        &self,
        source: &str,
        context: CompileContext<'_>,
    ) -> SemanticCompileReport<KirDocument> {
        match compile_simple(source, context.source_name) {
            Ok(document) => SemanticCompileReport {
                status: SemanticCompileStatus::Ok,
                diagnostics: Vec::new(),
                document: Some(document),
            },
            Err(diagnostic) => SemanticCompileReport {
                status: SemanticCompileStatus::Failed,
                diagnostics: vec![diagnostic],
                document: None,
            },
        }
    }
}

pub fn compile_simple(source: &str, source_name: &str) -> Result<KirDocument, Diagnostic> {
    let mut elements = Vec::new();

    for (line_index, raw_line) in source.lines().enumerate() {
        let line = raw_line.trim();
        if line.is_empty() || line.starts_with('#') {
            continue;
        }

        if let Some(name) = line.strip_prefix("component ") {
            let name = required_name(name, line_index)?;
            elements.push(element(
                format!("type.{name}"),
                "Simple::Component",
                name,
                source_name,
                line_index,
                BTreeMap::new(),
            ));
            continue;
        }

        if let Some(rest) = line.strip_prefix("part ") {
            let (owner_and_name, ty) = rest.split_once(':').ok_or_else(|| {
                diagnostic("part statement must be `part Owner.name: Type`", line_index)
            })?;
            let (owner, name) = owner_and_name.trim().split_once('.').ok_or_else(|| {
                diagnostic("part statement must include `Owner.name`", line_index)
            })?;
            let owner = required_name(owner, line_index)?;
            let name = required_name(name, line_index)?;
            let ty = required_name(ty, line_index)?;
            elements.push(element(
                format!("feature.{owner}.{name}"),
                "Simple::Part",
                name,
                source_name,
                line_index,
                BTreeMap::from([
                    ("owner".to_string(), json!(format!("type.{owner}"))),
                    ("type".to_string(), json!(format!("type.{ty}"))),
                ]),
            ));
            continue;
        }

        if let Some(rest) = line.strip_prefix("requirement ") {
            let (id, body) = rest.split_once(' ').ok_or_else(|| {
                diagnostic("requirement statement must be `requirement Id \"text\"`", line_index)
            })?;
            let id = required_name(id, line_index)?;
            let body = body.trim().trim_matches('"');
            elements.push(element(
                format!("requirement.{id}"),
                "Simple::Requirement",
                id,
                source_name,
                line_index,
                BTreeMap::from([("body".to_string(), json!(body))]),
            ));
            continue;
        }

        if let Some(rest) = line.strip_prefix("satisfy ") {
            let (source, target) = rest
                .split_once("->")
                .ok_or_else(|| diagnostic("satisfy statement must be `satisfy Source -> Requirement`", line_index))?;
            let source = required_name(source, line_index)?;
            let target = required_name(target, line_index)?;
            let relationship_name = format!("{source}_satisfies_{target}");
            elements.push(element(
                format!("relationship.{relationship_name}"),
                "Simple::Satisfy",
                &relationship_name,
                source_name,
                line_index,
                BTreeMap::from([
                    ("source".to_string(), json!(format!("type.{source}"))),
                    ("target".to_string(), json!(format!("requirement.{target}"))),
                ]),
            ));
            continue;
        }

        return Err(diagnostic("unknown simple-language statement", line_index));
    }

    Ok(KirDocument { metadata: BTreeMap::new(), elements }.normalized_for_persistence())
}

fn element(
    id: String,
    kind: &str,
    declared_name: &str,
    source_name: &str,
    line_index: usize,
    mut properties: BTreeMap<String, serde_json::Value>,
) -> KirElement {
    properties.insert("declared_name".to_string(), json!(declared_name));
    properties.insert("source_file".to_string(), json!(source_name));
    properties.insert(
        "source_span".to_string(),
        json!({ "start_line": line_index + 1, "end_line": line_index + 1 }),
    );
    KirElement { id, kind: kind.to_string(), layer: 2, properties }
}

fn required_name(value: &str, line_index: usize) -> Result<&str, Diagnostic> {
    let value = value.trim();
    if value.is_empty() {
        return Err(diagnostic("expected a name", line_index));
    }
    Ok(value)
}

fn diagnostic(message: impl Into<String>, line_index: usize) -> Diagnostic {
    Diagnostic::new(format!("{} at line {}", message.into(), line_index + 1), None)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn compiles_components_and_requirement() {
        let document = compile_simple(
            "component Vehicle\ncomponent Engine\npart Vehicle.engine: Engine\nrequirement R1 \"Vehicle shall start\"\nsatisfy Vehicle -> R1\n",
            "demo.simple",
        )
        .unwrap();

        assert!(document.elements.iter().any(|element| element.id == "type.Vehicle"));
        assert!(document.elements.iter().any(|element| element.id == "feature.Vehicle.engine"));
        assert!(document.elements.iter().any(|element| element.id == "requirement.R1"));
    }
}
