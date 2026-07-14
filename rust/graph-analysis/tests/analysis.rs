use mercurio_core::Graph;
use mercurio_graph_analysis_example::build_analysis_view;
use mercurio_sysml::SysmlEnvironment;

#[test]
fn decision_review_model_yields_scored_candidates() {
    let environment = SysmlEnvironment::latest_metamodel().unwrap();
    let source =
        include_str!("../../../python/model-graph-analysis/model/decision-review.sysml");
    let document = environment
        .compile_text(source, "decision-review.sysml")
        .unwrap();
    let graph = Graph::from_document(document).unwrap();

    let view = build_analysis_view(&graph);

    assert!(view.summary.nodes > 0);
    assert!(view.summary.links > 0);
    assert!(view.summary.decision_candidates > 0);
    assert!(
        view.decisions
            .iter()
            .any(|node| node.label == "PayloadArchitectureReview"),
        "expected the analysis definition to be a decision candidate"
    );
    // Candidates are sorted best-first and only include scored nodes.
    assert!(
        view.decisions
            .windows(2)
            .all(|pair| pair[0].score >= pair[1].score)
    );
    assert!(view.decisions.iter().all(|node| node.score > 0));
}
