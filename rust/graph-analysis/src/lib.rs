//! Native mirror of `python/model-graph-analysis/analyze_model_d3.py`.
//!
//! The Python example asks a Mercurio backend for the compiled graph and
//! scores "decision candidates" over it. This crate runs the same analysis
//! in-process: compile with `SysmlEnvironment`, build `mercurio_core::Graph`,
//! and apply the same keyword-and-degree scoring. Instead of a D3 HTML page
//! it produces a machine-readable report.

use std::collections::{BTreeMap, BTreeSet};

use mercurio_core::{Element, Graph};
use serde::Serialize;
use serde_json::{Map, Value};

#[derive(Debug, Serialize)]
pub struct AnalysisView {
    pub title: String,
    pub nodes: Vec<NodeView>,
    pub links: Vec<LinkView>,
    pub decisions: Vec<NodeView>,
    pub summary: Summary,
}

#[derive(Debug, Clone, Serialize)]
pub struct NodeView {
    pub id: String,
    pub label: String,
    pub kind: String,
    pub score: i64,
    pub degree: usize,
    pub properties: Map<String, Value>,
}

#[derive(Debug, Serialize)]
pub struct LinkView {
    pub source: String,
    pub target: String,
    pub relation: String,
}

#[derive(Debug, Serialize)]
#[serde(rename_all = "camelCase")]
pub struct Summary {
    pub nodes: usize,
    pub links: usize,
    pub decision_candidates: usize,
}

/// Mirrors `build_analysis_view` in the Python example. The Python script
/// requests the backend graph at model scope, which is the layer-2 slice of
/// the compiled document, so the same filter is applied here.
pub fn build_analysis_view(graph: &Graph) -> AnalysisView {
    let model_elements: Vec<&Element> = graph
        .elements()
        .iter()
        .filter(|element| element.layer == 2)
        .collect();
    let model_ids: BTreeSet<u32> = model_elements.iter().map(|element| element.id).collect();

    let mut degree: BTreeMap<u32, usize> = BTreeMap::new();
    let mut links = Vec::new();
    for edge in graph.edges() {
        if !model_ids.contains(&edge.source) || !model_ids.contains(&edge.target) {
            continue;
        }
        let (Some(source), Some(target)) = (
            graph.element_id(edge.source),
            graph.element_id(edge.target),
        ) else {
            continue;
        };
        links.push(LinkView {
            source: source.to_string(),
            target: target.to_string(),
            relation: edge.relation.to_string(),
        });
        *degree.entry(edge.source).or_insert(0) += 1;
        *degree.entry(edge.target).or_insert(0) += 1;
    }

    let mut nodes = Vec::with_capacity(model_elements.len());
    for element in &model_elements {
        let properties = element.properties.to_btree_map();
        let label = node_label(element, &properties);
        let node_degree = degree.get(&element.id).copied().unwrap_or(0);
        let mut score = decision_score(&label, &element.kind, &properties);
        if node_degree >= 3 {
            score += 1;
        }
        nodes.push(NodeView {
            id: element.element_id.clone(),
            label,
            kind: element.kind.to_string(),
            score,
            degree: node_degree,
            properties: compact_properties(&properties),
        });
    }

    let mut decisions: Vec<NodeView> = nodes
        .iter()
        .filter(|node| node.score > 0)
        .cloned()
        .collect();
    decisions.sort_by(|left, right| {
        right
            .score
            .cmp(&left.score)
            .then(right.degree.cmp(&left.degree))
            .then(left.label.cmp(&right.label))
    });

    let summary = Summary {
        nodes: nodes.len(),
        links: links.len(),
        decision_candidates: decisions.len(),
    };
    AnalysisView {
        title: "Payload Architecture Decision Review".to_string(),
        nodes,
        links,
        decisions,
        summary,
    }
}

fn node_label(element: &Element, properties: &BTreeMap<String, Value>) -> String {
    for key in ["declared_name", "name"] {
        if let Some(value) = properties.get(key).and_then(Value::as_str)
            && !value.is_empty()
        {
            return value.to_string();
        }
    }
    element
        .element_id
        .rsplit('.')
        .next()
        .unwrap_or(&element.element_id)
        .to_string()
}

fn decision_score(label: &str, kind: &str, properties: &BTreeMap<String, Value>) -> i64 {
    let serialized = serde_json::to_string(properties).unwrap_or_default();
    let text = format!("{label} {kind} {serialized}").to_lowercase();
    let mut score = 0;
    for term in [
        "analysis",
        "objective",
        "requirement",
        "decision",
        "decide",
        "select",
    ] {
        if text.contains(term) {
            score += 2;
        }
    }
    for term in ["action", "criticality", "power", "mass", "latency"] {
        if text.contains(term) {
            score += 1;
        }
    }
    score
}

fn compact_properties(properties: &BTreeMap<String, Value>) -> Map<String, Value> {
    let mut keep = Map::new();
    for (key, value) in properties {
        let always_kept = matches!(
            key.as_str(),
            "declared_name" | "name" | "type" | "owner" | "definition" | "source_file"
        );
        if always_kept || matches!(value, Value::String(_) | Value::Number(_) | Value::Bool(_)) {
            keep.insert(key.clone(), value.clone());
        }
    }
    keep
}
