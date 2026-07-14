"""
Voron Trident 350 — live simulation demo.

Shows a 3D printer schematic (parts colored by simulation state),
a Gantt-style state machine timeline, transition log, and analysis
summary.  Click Restart to re-run the simulation.

Run:
    python demo.py
    open http://localhost:8050
"""

import os
from pathlib import Path
WORKSPACE = str(Path(__file__).resolve().parent.parent)
_dev_exe = Path(WORKSPACE).parent.parent.parent / "mercurio-product/target/debug/mercurio-console-api.exe"
if _dev_exe.exists():
    os.environ.setdefault("MERCURIO_EXE", str(_dev_exe))

print("Loading model...")

import mercurio
import plotly.graph_objects as go
import dash
from dash import html, dcc, Input, Output

model     = mercurio.open(WORKSPACE)
parts     = model.parts()
cases     = model.analysis_cases()
print_seq = next(c for c in cases if c.label == "PrintSequence")

# ── Config ────────────────────────────────────────────────────────────────────

SUBJECTS = ["printer", "bed", "hotend"]
COLORS   = {"printer": "#6366f1", "bed": "#ea580c", "hotend": "#06b6d4"}

# Fill color per state (for 3D boxes)
STATE_FILL = {
    "Cold":       "#0f2540",
    "Heating":    "#9a3412",
    "Ready":      "#14532d",
    "Printing":   "#312e81",
    "Printing2":  "#3730a3",
    "ToolChange": "#4c1d95",
}
# Accent color per state (used for legend text / borders)
STATE_ACCENT = {
    "Cold":       "#60a5fa",
    "Heating":    "#fb923c",
    "Ready":      "#4ade80",
    "Printing":   "#818cf8",
    "Printing2":  "#a5b4fc",
    "ToolChange": "#c4b5fd",
}

DARK = {"backgroundColor": "#0b0d16", "color": "#cbd5e1"}
CARD = {**DARK, "padding": "16px 20px", "borderRadius": "8px",
        "border": "1px solid #1c1f30", "marginBottom": "12px"}
LABEL = {"fontSize": "10px", "fontWeight": "700", "letterSpacing": "0.1em",
         "textTransform": "uppercase", "color": "#3d4468", "marginBottom": "10px"}

# ── Data helpers ──────────────────────────────────────────────────────────────

def timeline_for(trace, subject):
    sd = trace.states(subject)
    rows = []
    for i, (t, states) in enumerate(zip(sd.times, sd.states)):
        label = states[-1] if states else "?"
        t_end = sd.times[i + 1] if i + 1 < len(sd.times) else trace.duration
        rows.append((t, t_end, label))
    return rows

def event_rows(trace):
    rows = []
    for entry in trace._timeline:
        t = entry.get("t", 0)
        for ev in entry.get("events", []):
            tid     = ev.get("transition_id", "")
            trigger = ev.get("trigger", "")
            label   = tid.rsplit(".", 1)[-1] if "." in tid else tid
            rows.append((t, label, trigger))
    return rows

def final_state(trace, subject):
    sd = trace.states(subject)
    return sd.states[-1][-1] if (sd.states and sd.states[-1]) else "?"

# ── 3D Schematic ──────────────────────────────────────────────────────────────

def _box(x0, y0, z0, x1, y1, z1, color, name, opacity=0.85, showlegend=True):
    """Solid Mesh3d box."""
    vx = [x0, x1, x1, x0, x0, x1, x1, x0]
    vy = [y0, y0, y1, y1, y0, y0, y1, y1]
    vz = [z0, z0, z0, z0, z1, z1, z1, z1]
    # 12 triangles → 6 faces
    i  = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
    j  = [1, 2, 5, 6, 1, 5, 3, 7, 3, 7, 2, 6]
    k  = [2, 3, 6, 7, 5, 4, 7, 6, 7, 4, 6, 5]
    return go.Mesh3d(
        x=vx, y=vy, z=vz, i=i, j=j, k=k,
        color=color, opacity=opacity, name=name,
        showlegend=showlegend,
        hovertemplate=f"<b>{name}</b><extra></extra>",
    )

def _edge(ax, ay, az, bx, by, bz):
    return go.Scatter3d(
        x=[ax, bx, None], y=[ay, by, None], z=[az, bz, None],
        mode="lines", line=dict(color="#1c2040", width=3),
        showlegend=False, hoverinfo="skip",
    )

def make_3d(trace):
    """
    Voron Trident 350 schematic.

    Frame:  350 mm cube wireframe  (aluminum extrusions)
    Bed:    300×300 heated plate   — colored by bed state
    Gantry: twin Y rails + X bar  — colored by printer state
    Hotend: toolhead carriage      — colored by hotend state
    """
    bed_st    = final_state(trace, "bed")
    hotend_st = final_state(trace, "hotend")
    print_st  = final_state(trace, "printer")

    bc = STATE_FILL.get(bed_st,    "#1e293b")
    hc = STATE_FILL.get(hotend_st, "#1e293b")
    pc = STATE_FILL.get(print_st,  "#1e293b")

    S  = 350
    fig = go.Figure()

    # Frame wireframe — 12 edges of a 350mm cube
    C = [(0,0,0),(S,0,0),(S,S,0),(0,S,0),
         (0,0,S),(S,0,S),(S,S,S),(0,S,S)]
    for a, b in [(0,1),(1,2),(2,3),(3,0),
                 (4,5),(5,6),(6,7),(7,4),
                 (0,4),(1,5),(2,6),(3,7)]:
        fig.add_trace(_edge(*C[a], *C[b]))

    # Heated bed platform (moves on Z; shown at mid-travel)
    fig.add_trace(_box(25, 25, 105, 325, 325, 122,
                       bc, f"Bed  [{bed_st}]", 0.90))

    # Gantry: left Y rail
    fig.add_trace(_box(5,   5, 282,  28, 345, 296,
                       pc, f"Gantry  [{print_st}]", 0.72))
    # Gantry: right Y rail (same legend group, no duplicate entry)
    fig.add_trace(_box(322,  5, 282, 345, 345, 296,
                       pc, "", 0.72, showlegend=False))
    # Gantry: X cross-member (at current Y ≈ mid-travel)
    fig.add_trace(_box(28, 163, 280, 322, 182, 293,
                       "#11142a", "X rail", 0.65))

    # Hotend / toolhead carriage
    fig.add_trace(_box(148, 156, 258, 202, 189, 302,
                       hc, f"Hotend  [{hotend_st}]", 0.95))

    # Electronics bay (bottom of frame)
    fig.add_trace(_box(0, 0, 0, S, 38, 52,
                       "#0a0c18", "Electronics", 0.75))

    fig.update_layout(
        paper_bgcolor="#0b0d16",
        scene=dict(
            bgcolor="#0d0f1a",
            xaxis=dict(visible=False, range=[0, S]),
            yaxis=dict(visible=False, range=[0, S]),
            zaxis=dict(visible=False, range=[0, S]),
            camera=dict(
                eye=dict(x=1.75, y=-1.5, z=1.15),
                center=dict(x=0, y=0, z=-0.05),
            ),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=320,
        legend=dict(
            bgcolor="#0d0f1a", bordercolor="#1c1f30",
            font=dict(color="#cbd5e1", size=11),
            x=0.01, y=0.99, itemsizing="constant",
        ),
        font=dict(color="#cbd5e1"),
    )
    return fig

# ── Gantt chart ───────────────────────────────────────────────────────────────

def make_gantt(trace):
    fig = go.Figure()
    y_pos = {"printer": 0, "bed": 1, "hotend": 2}

    for subj in SUBJECTS:
        for t_start, t_end, label in timeline_for(trace, subj):
            dur = t_end - t_start
            fig.add_trace(go.Bar(
                x=[dur], y=[y_pos[subj]], base=[t_start],
                orientation="h",
                marker=dict(color=COLORS[subj], opacity=0.85,
                            line=dict(color="#0d0f1a", width=2)),
                text=label, textposition="inside", insidetextanchor="middle",
                showlegend=False, name=subj,
                hovertemplate=(
                    f"<b>{subj}</b><br>state: {label}<br>"
                    f"t={t_start:.1f}s → {t_end:.1f}s  ({dur:.1f}s)"
                    "<extra></extra>"
                ),
            ))

    # Legend swatches
    for subj in SUBJECTS:
        fig.add_trace(go.Bar(name=subj.capitalize(), x=[0], y=[-1],
                             marker=dict(color=COLORS[subj]), orientation="h"))

    fig.update_layout(
        barmode="stack",
        paper_bgcolor="#0b0d16", plot_bgcolor="#0d0f1a",
        font=dict(color="#cbd5e1", size=12),
        xaxis=dict(title="Simulation time (s)", gridcolor="#1c1f30",
                   zeroline=False, range=[-1, trace.duration + 2]),
        yaxis=dict(tickvals=[0,1,2], ticktext=["Printer","Bed","Hotend"],
                   gridcolor="#1c1f30"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02,
                    bgcolor="#11131f", bordercolor="#1c1f30"),
        margin=dict(l=70, r=20, t=40, b=50),
        height=250,
    )
    return fig

# ── Parts table (static — model structure doesn't change on restart) ──────────

def make_parts_table():
    usages = [p for p in parts if "Usage" in p.element_kind and "State" not in p.element_kind]
    defs   = [p for p in parts if "Definition" in p.element_kind]
    rows = []
    for p in usages:
        rows.append(html.Tr([
            html.Td(p.name,                   style={"color":"#818cf8","fontWeight":"600"}),
            html.Td(p.kind.split("::")[-1]),
            html.Td("usage",                  style={"color":"#3d4468","fontSize":"11px"}),
        ]))
    for p in defs:
        rows.append(html.Tr([
            html.Td(p.name,  style={"color":"#94a3b8"}),
            html.Td("—"),
            html.Td("definition", style={"color":"#3d4468","fontSize":"11px"}),
        ]))
    return html.Table([
        html.Thead(html.Tr([html.Th("Name"), html.Th("Type"), html.Th("Kind")])),
        html.Tbody(rows),
    ], style={"width":"100%","borderCollapse":"collapse","fontSize":"13px"})

# ── Stat box ──────────────────────────────────────────────────────────────────

def stat(label, value):
    return html.Div([
        html.Span(label, style={"fontSize":"10px","color":"#3d4468",
                                "textTransform":"uppercase","display":"block"}),
        html.Span(value, style={"fontSize":"18px","fontWeight":"600",
                                "color":"#e2e8f0","fontVariantNumeric":"tabular-nums"}),
    ], style={"backgroundColor":"#0d0f1a","padding":"8px 10px",
              "borderRadius":"6px","border":"1px solid #1c1f30"})

# ── App ───────────────────────────────────────────────────────────────────────

app = dash.Dash(__name__, title="Voron — Mercurio")

BTN = {
    "backgroundColor":"#11131f", "color":"#818cf8",
    "border":"1px solid #1c1f30", "borderRadius":"6px",
    "padding":"4px 16px", "cursor":"pointer",
    "fontSize":"11px", "fontFamily":"Segoe UI, system-ui, sans-serif",
    "marginLeft":"16px", "letterSpacing":"0.05em",
    "transition":"background 0.15s",
}

app.layout = html.Div([

    # ── Header ────────────────────────────────────────────────────────────────
    html.Div([
        html.Span("MERCURIO", style={"fontWeight":"700","letterSpacing":"0.2em",
                                      "fontSize":"11px","color":"#818cf8"}),
        html.Span(" · ", style={"color":"#252840","margin":"0 8px"}),
        html.Span("Voron Trident 350 + Indx  —  PrintSequence",
                  style={"fontSize":"12px","color":"#475569"}),
        html.Div(id="hdr-status",
                 style={"fontSize":"11px","color":"#6366f1","marginLeft":"auto",
                        "fontVariantNumeric":"tabular-nums"}),
        html.Button("↺  Restart", id="restart-btn", n_clicks=0, style=BTN),
    ], style={
        "display":"flex","alignItems":"center","padding":"10px 20px",
        "backgroundColor":"#11131f","borderBottom":"1px solid #1c1f30",
        "fontFamily":"Segoe UI, system-ui, sans-serif",
    }),

    # ── Body ─────────────────────────────────────────────────────────────────
    dcc.Loading(
        html.Div([

            # Left column: 3D + gantt + transitions
            html.Div([

                html.Div([
                    html.P("3D Schematic", style=LABEL),
                    dcc.Graph(id="fig-3d", config={"displayModeBar": False}),
                ], style=CARD),

                html.Div([
                    html.P("State Machine Timeline", style=LABEL),
                    dcc.Graph(id="fig-gantt", config={"displayModeBar": False}),
                ], style=CARD),

                html.Div([
                    html.P("Transition Log", style=LABEL),
                    html.Div(id="tbl-transitions"),
                ], style=CARD),

            ], style={"flex":"1","minWidth":"0"}),

            # Right column: summary + parts
            html.Div([

                html.Div([
                    html.P("Analysis Case", style=LABEL),
                    html.Span("PrintSequence",
                              style={"color":"#818cf8","fontWeight":"600",
                                     "fontSize":"15px","display":"block"}),
                    html.Span(print_seq.id,
                              style={"color":"#3d4468","fontSize":"11px","display":"block",
                                     "fontFamily":"Cascadia Code, Consolas, monospace",
                                     "marginBottom":"12px"}),
                    html.Div(id="stat-boxes",
                             style={"display":"grid","gridTemplateColumns":"1fr 1fr","gap":"8px"}),
                ], style=CARD),

                html.Div([
                    html.P(f"Model Parts ({len(parts)} total)", style=LABEL),
                    make_parts_table(),
                ], style={**CARD,"maxHeight":"420px","overflowY":"auto"}),

            ], style={"width":"340px","flexShrink":"0"}),

        ], style={"display":"flex","gap":"12px","padding":"12px 16px",
                  "fontFamily":"Segoe UI, system-ui, sans-serif","flex":"1"}),
        type="circle",
        color="#6366f1",
    ),

], style={**DARK,"minHeight":"100vh","display":"flex",
          "flexDirection":"column","fontFamily":"Segoe UI, system-ui, sans-serif"})

# ── Callback ──────────────────────────────────────────────────────────────────

@app.callback(
    Output("fig-3d",          "figure"),
    Output("fig-gantt",       "figure"),
    Output("tbl-transitions", "children"),
    Output("stat-boxes",      "children"),
    Output("hdr-status",      "children"),
    Input("restart-btn",      "n_clicks"),
)
def refresh(_n):
    trace = model.run_analysis("PrintSequence")
    ev    = event_rows(trace)

    transition_tbl = html.Table([
        html.Thead(html.Tr([
            html.Th("t (s)", style={"width":"60px"}),
            html.Th("Transition"),
            html.Th("Trigger"),
        ])),
        html.Tbody([
            html.Tr([
                html.Td(f"{t:.1f}", style={"color":"#6366f1",
                                           "fontVariantNumeric":"tabular-nums"}),
                html.Td(label, style={"fontFamily":"Cascadia Code, Consolas, monospace",
                                      "fontSize":"12px","color":"#94a3b8"}),
                html.Td(trigger, style={"color":"#3d4468","fontSize":"11px"}),
            ]) for t, label, trigger in ev
        ]),
    ], style={"width":"100%","borderCollapse":"collapse","fontSize":"12px",
              "fontFamily":"Segoe UI, system-ui, sans-serif"})

    boxes = [
        stat("Subjects",    str(print_seq.subject_count)),
        stat("Duration",    f"{trace.duration:.1f} s"),
        stat("Status",      trace.status),
        stat("Transitions", str(len(ev))),
    ]

    hdr = (f"{trace.status.upper()}  {trace.duration:.1f}s  "
           f"{print_seq.subject_count} subjects  {len(ev)} transitions")

    return make_3d(trace), make_gantt(trace), transition_tbl, boxes, hdr


if __name__ == "__main__":
    print("\nopen http://localhost:8050\n")
    app.run(debug=False, port=8050)
    model.close()
