use std::error::Error;
use std::path::PathBuf;

use mercurio_core::Graph;
use mercurio_graph_analysis_example::build_analysis_view;
use mercurio_sysml::SysmlEnvironment;

/// The same model the Python mirror analyzes, so outputs are comparable.
const DEFAULT_MODEL_SOURCE: &str =
    include_str!("../../../python/model-graph-analysis/model/decision-review.sysml");

fn main() -> Result<(), Box<dyn Error>> {
    let (source, source_name) = match std::env::args().nth(1) {
        Some(path) => (std::fs::read_to_string(&path)?, path),
        None => (
            DEFAULT_MODEL_SOURCE.to_string(),
            "decision-review.sysml".to_string(),
        ),
    };

    let environment = SysmlEnvironment::latest_metamodel()?;
    let document = environment.compile_text(&source, &source_name)?;
    let graph = Graph::from_document(document)?;
    let view = build_analysis_view(&graph);

    let output_path = PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("out/decision-review.json");
    if let Some(parent) = output_path.parent() {
        std::fs::create_dir_all(parent)?;
    }
    std::fs::write(&output_path, serde_json::to_string_pretty(&view)?)?;

    println!("wrote {}", output_path.display());
    println!(
        "analyzed {} nodes, {} links, {} decision candidates",
        view.summary.nodes, view.summary.links, view.summary.decision_candidates
    );
    println!("top decision candidates:");
    for node in view.decisions.iter().take(5) {
        println!(
            "  score {:>2}  degree {:>2}  {} ({})",
            node.score, node.degree, node.label, node.kind
        );
    }

    Ok(())
}
