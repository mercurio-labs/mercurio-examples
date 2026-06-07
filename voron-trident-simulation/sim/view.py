"""
Voron Trident 350 — model structure + simulation viewer.

Demonstrates the mercurio Python API:
  - Load a compiled model from a KPAR or source directory
  - Walk the part tree and read model attributes
  - Run a named analysis case (PrintSequence)
  - Display structure + simulation data in an interactive Dash dashboard

Run:
    pip install mercurio dash plotly
    python view.py
    open http://localhost:8050
"""

import mercurio
import dash
from dash import dcc, html, Input, Output, ctx
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── 1. Load model ─────────────────────────────────────────────────────────────
#
# mercurio.open() accepts a .kpar archive, a workspace directory, or a
# single .sysml source file. Returns a ModelRuntime backed by compiled KIR.

model = mercurio.open(".")          # workspace root; compiles on first open

# ── 2. Walk the part tree ──────────────────────────────────────────────────────
#
# model.parts() returns a flat list of PartRef objects — every part usage in
# the model, depth-first. Each PartRef exposes:
#   .id          unique KIR element id
#   .name        usage name ("bed", "xCarriage", ...)
#   .kind        definition name ("HeatedBed", "XYCarriage", ...)
#   .parent      parent PartRef, or None for top-level
#   .depth       nesting depth (0 = top-level)
#   .attr(name, default)   read an attribute value from the compiled model

parts = model.parts()

# Build a parent→children map for the tree panel
from collections import defaultdict
children_of = defaultdict(list)
roots = []
for p in parts:
    if p.parent is None:
        roots.append(p)
    else:
        children_of[p.parent.id].append(p)

def tree_items(part, depth=0):
    indent = " " * (depth * 4)
    label  = f"{indent}{part.name} : {part.kind}"
    items  = [html.Li(label, id={"type": "part", "id": part.id},
                      style={"cursor": "pointer", "padding": "2px 4px",
                             "listStyle": "none", "fontFamily": "monospace",
                             "fontSize": "13px"})]
    for child in children_of[part.id]:
        items.extend(tree_items(child, depth + 1))
    return items

# ── 3. Build schematic 3D scene from model attributes ─────────────────────────
#
# The sim3d.json gives us rendering positions for some parts. For others we
# derive a hierarchical layout. Any script can do this differently — the model
# is the data source, the layout is the script's concern.

SCHEMATIC = {
    "bed":         {"pos": [0.0,  0.3,  0.0],  "size": 1.2, "color": "#ea580c"},
    "hotend":      {"pos": [0.0,  5.3, -3.5],  "size": 0.4, "color": "#06b6d4"},
    "motion":      {"pos": [0.0,  3.0,  0.0],  "size": 0.7, "color": "#6366f1"},
    "toolchanger": {"pos": [2.0,  5.0,  0.0],  "size": 0.6, "color": "#f59e0b"},
    "electronics": {"pos": [-3.0, 1.0,  0.0],  "size": 0.5, "color": "#10b981"},
}

def part_scatter(highlight_id=None):
    xs, ys, zs, labels, colors, sizes = [], [], [], [], [], []
    for p in parts:
        s = SCHEMATIC.get(p.name, {"pos": [0, 0, 0], "size": 0.3, "color": "#888"})
        xs.append(s["pos"][0])
        ys.append(s["pos"][1])
        zs.append(s["pos"][2])
        labels.append(f"<b>{p.name}</b><br>{p.kind}")
        sizes.append(s["size"] * 18)
        colors.append("#ffffff" if p.id == highlight_id else s["color"])

    trace = go.Scatter3d(
        x=xs, y=ys, z=zs,
        mode="markers+text",
        text=[p.name for p in parts],
        textposition="top center",
        hovertext=labels,
        hoverinfo="text",
        marker=dict(size=sizes, color=colors, opacity=0.85,
                    line=dict(color="#fff", width=1)),
        customdata=[p.id for p in parts],
    )

    # connections: show parent→child edges
    edge_x, edge_y, edge_z = [], [], []
    for p in parts:
        if p.parent and p.parent.name in SCHEMATIC and p.name in SCHEMATIC:
            ps = SCHEMATIC[p.parent.name]["pos"]
            cs = SCHEMATIC[p.name]["pos"]
            edge_x += [ps[0], cs[0], None]
            edge_y += [ps[1], cs[1], None]
            edge_z += [ps[2], cs[2], None]

    edges = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode="lines",
        line=dict(color="#444", width=2),
        hoverinfo="none",
        showlegend=False,
    )

    fig = go.Figure([edges, trace])
    fig.update_layout(
        paper_bgcolor="#0a0c15",
        scene=dict(
            bgcolor="#0a0c15",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False),
            zaxis=dict(visible=False),
            camera=dict(eye=dict(x=1.5, y=1.2, z=1.8)),
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        showlegend=False,
    )
    return fig

# ── 4. Run PrintSequence analysis ─────────────────────────────────────────────
#
# run_analysis() compiles the AnalysisCaseDefinition, extracts subjects and
# initial conditions, runs the concurrent simulation engine, and returns a
# SimulationTrace. All channels declared as objectives are guaranteed present.

trace = model.run_analysis("PrintSequence")

bed_temp    = trace.channel("bed.temperature")       # .times, .values, .unit
hotend_temp = trace.channel("hotend.temperature")
bed_states  = trace.states("bed")                    # .times, .states (strings)
hotend_states = trace.states("hotend")
printer_states = trace.states("printer")

def make_trace_fig():
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=("Temperature", "Active State"),
        vertical_spacing=0.14,
    )
    fig.add_trace(go.Scatter(
        x=bed_temp.times, y=bed_temp.values,
        name="Bed (°C)", line=dict(color="#ea580c", width=2),
    ), row=1, col=1)
    fig.add_trace(go.Scatter(
        x=hotend_temp.times, y=hotend_temp.values,
        name="Hotend (°C)", line=dict(color="#06b6d4", width=2),
    ), row=1, col=1)

    # state timelines as step plots
    for subj, s, color in [
        ("printer", printer_states, "#6366f1"),
        ("bed",     bed_states,     "#ea580c"),
        ("hotend",  hotend_states,  "#06b6d4"),
    ]:
        fig.add_trace(go.Scatter(
            x=s.times, y=[f"{subj}.{v}" for v in s.states],
            name=subj, mode="lines+markers",
            line=dict(shape="hv", color=color, width=1.5),
            marker=dict(size=5),
        ), row=2, col=1)

    fig.update_layout(
        paper_bgcolor="#0a0c15",
        plot_bgcolor="#111827",
        font=dict(color="#e5e7eb"),
        legend=dict(bgcolor="#1f2937", bordercolor="#374151"),
        margin=dict(l=50, r=20, t=30, b=40),
        height=420,
    )
    fig.update_xaxes(gridcolor="#1f2937", zerolinecolor="#374151")
    fig.update_yaxes(gridcolor="#1f2937", zerolinecolor="#374151")
    return fig

# ── 5. Dash layout ─────────────────────────────────────────────────────────────

DARK = {"backgroundColor": "#111827", "color": "#e5e7eb"}
PANEL = {**DARK, "padding": "12px", "borderRadius": "6px",
         "border": "1px solid #1f2937"}

app = dash.Dash(__name__)
app.layout = html.Div([
    html.H2("Voron Trident 350 — Mercurio Model View",
            style={"color": "#e5e7eb", "margin": "0 0 16px 0",
                   "fontFamily": "sans-serif", "fontWeight": 500}),

    html.Div([
        # Left: part tree
        html.Div([
            html.H4("Parts", style={"color": "#9ca3af", "margin": "0 0 8px 0",
                                    "fontSize": "12px", "textTransform": "uppercase",
                                    "letterSpacing": "0.05em"}),
            html.Ul(
                [item for root in roots for item in tree_items(root)],
                id="part-tree",
                style={"padding": 0, "margin": 0},
            ),
        ], style={**PANEL, "width": "18%", "overflowY": "auto", "maxHeight": "600px"}),

        # Centre: 3D schematic
        html.Div([
            dcc.Graph(id="scene-3d", figure=part_scatter(),
                      style={"height": "580px"},
                      config={"displayModeBar": False}),
        ], style={"width": "42%", "padding": "0 12px"}),

        # Right: simulation traces
        html.Div([
            html.H4("PrintSequence", style={"color": "#9ca3af", "margin": "0 0 8px 0",
                                            "fontSize": "12px", "textTransform": "uppercase",
                                            "letterSpacing": "0.05em"}),
            dcc.Graph(figure=make_trace_fig(),
                      config={"displayModeBar": False}),
        ], style={**PANEL, "width": "40%"}),

    ], style={"display": "flex", "gap": "0", "alignItems": "flex-start"}),

    # Selected part attributes
    html.Div(id="attr-panel",
             style={**PANEL, "marginTop": "12px", "fontFamily": "monospace",
                    "fontSize": "13px", "minHeight": "60px"}),

], style={**DARK, "padding": "24px", "minHeight": "100vh", "fontFamily": "sans-serif"})


@app.callback(
    Output("scene-3d", "figure"),
    Output("attr-panel", "children"),
    Input("scene-3d", "clickData"),
    Input({"type": "part", "id": dash.ALL}, "n_clicks"),
)
def on_select(click_data, _tree_clicks):
    triggered = ctx.triggered_id

    # resolve which part was selected
    part_id = None
    if isinstance(triggered, dict) and triggered.get("type") == "part":
        part_id = triggered["id"]
    elif click_data:
        part_id = click_data["points"][0].get("customdata")

    if part_id is None:
        return part_scatter(), html.Span("Click a part to inspect its attributes.",
                                         style={"color": "#6b7280"})

    part = next((p for p in parts if p.id == part_id), None)
    if part is None:
        return part_scatter(), ""

    # read all attributes from the compiled model
    attrs = part.attrs()   # dict[str, Any]
    rows = [
        html.Span(f"{part.name} : {part.kind}",
                  style={"color": "#e5e7eb", "fontWeight": "bold",
                         "display": "block", "marginBottom": "6px"}),
    ] + [
        html.Span(f"  {k} = {v}",
                  style={"color": "#9ca3af", "display": "block"})
        for k, v in attrs.items()
    ]

    return part_scatter(highlight_id=part_id), rows


if __name__ == "__main__":
    app.run(debug=True)
