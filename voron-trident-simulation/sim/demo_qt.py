"""
Voron Trident 350 — native Windows desktop app.

Real Windows window (PyQt6).  Two animated Plotly views inside QWebEngineView:
  • Animated state machine diagram  — states as nodes, transitions as arrows,
    play/pause + time slider animates through the simulation
  • Animated 3D schematic           — bed moves on Z, parts change colour
    as their state changes (Cold → Heating → Ready)

All native Qt widgets for the stat boxes, transition log, and parts table.
Click "↺ Restart" to re-run the simulation live (QThread, non-blocking).

Run:
    python demo_qt.py
"""

import os, sys, tempfile, traceback, logging
from pathlib import Path

# Log everything to a file next to this script so crashes are visible when
# the process is spawned detached (no console).
def _configure_logging() -> Path:
    candidates = [
        Path(__file__).resolve().parent / "demo_qt.log",
        Path(tempfile.gettempdir()) / "mercurio-demo_qt.log",
    ]
    for candidate in candidates:
        try:
            candidate.parent.mkdir(parents=True, exist_ok=True)
            with candidate.open("w", encoding="utf-8") as handle:
                handle.write("")
            logging.basicConfig(
                filename=str(candidate),
                filemode="w",
                level=logging.DEBUG,
                format="%(asctime)s  %(levelname)s  %(message)s",
            )
            return candidate
        except OSError:
            continue
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s  %(levelname)s  %(message)s",
    )
    return candidates[-1]

_log_path = _configure_logging()
def _log_unhandled_exception(exc_type, exc, tb):
    logging.error(
        "UNHANDLED EXCEPTION:\n%s",
        "".join(traceback.format_exception(exc_type, exc, tb)),
    )
    sys.__excepthook__(exc_type, exc, tb)

sys.excepthook = _log_unhandled_exception
logging.info("demo_qt.py starting")
logging.info("Python %s", sys.version)
logging.info("argv %s", sys.argv)

# Workspace root — honour the env var set by spawn_python_view; fall back to
# the parent of this file's sim/ folder so it also works when run manually.
WORKSPACE = os.environ.get(
    "MERCURIO_WORKSPACE",
    str(Path(__file__).resolve().parent.parent),
)
logging.info("WORKSPACE=%s", WORKSPACE)

# Prefer debug binary, then release binary, then whatever is on PATH.
_repo_root = Path(WORKSPACE).parent.parent
_python_support = _repo_root / "mercurio-host-adapters" / "python"
if _python_support.exists() and str(_python_support) not in sys.path:
    sys.path.insert(0, str(_python_support))
    logging.info("python support path=%s", _python_support)
for _candidate in [
    _repo_root / "mercurio-product/target/debug/mercurio-console-api.exe",
    _repo_root / "mercurio-product/target/release/mercurio-console-api.exe",
]:
    if _candidate.exists():
        os.environ.setdefault("MERCURIO_EXE", str(_candidate))
        logging.info("MERCURIO_EXE=%s", _candidate)
        break
else:
    logging.info("MERCURIO_EXE not found in repo tree; using PATH/env")

import mercurio
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView,
    QFrame, QSizePolicy,
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt6.QtGui  import QColor

# ── Palette ───────────────────────────────────────────────────────────────────
BG_DARK   = "#0b0d16"
BG_CARD   = "#0d0f1a"
BG_HEADER = "#11131f"
BORDER    = "#1c1f30"
TEXT_DIM  = "#475569"
TEXT_MID  = "#94a3b8"
TEXT_MAIN = "#cbd5e1"
ACCENT    = "#818cf8"
ORANGE    = "#ea580c"
CYAN      = "#06b6d4"

# State-machine fill colours (Plotly / hex)
STATE_FILL = {
    "Cold":       "#0f2540",
    "Heating":    "#7c2d12",
    "Ready":      "#14532d",
    "Parked":     "#1e293b",
    "Homing":     "#166534",
    "Rastering":  "#15803d",
    "Complete":   "#14532d",
    "Idle":       "#1e293b",
    "Priming":    "#92400e",
    "Extruding":  "#b45309",
    "Retracting": "#78350f",
    "T0Loaded":   "#3b0764",
    "Changing":   "#581c87",
    "T1Loaded":   "#4c1d95",
    "Printing":   "#312e81",
    "Printing2":  "#3730a3",
    "ToolChange": "#4c1d95",
}
# Bed Z range at each state (Voron Trident: bed moves down as it prints)
BED_Z = {
    "Cold":    (250, 268),
    "Heating": (185, 203),
    "Ready":   (105, 123),
}

SUBJECTS      = ["printer", "motion", "bed", "hotend", "extruder", "toolchanger"]
SUBJ_Y        = {subj: float(len(SUBJECTS) - 1 - i) for i, subj in enumerate(SUBJECTS)}
SUBJ_COLOR    = {
    "printer": "#6366f1",
    "motion": "#22c55e",
    "bed": ORANGE,
    "hotend": CYAN,
    "extruder": "#f59e0b",
    "toolchanger": "#a855f7",
}
PARAM_CHANNELS = [
    ("bed.temperature", "Bed temp", "C", 20.0, 115.0, ORANGE),
    ("hotend.temperature", "Hotend temp", "C", 20.0, 260.0, CYAN),
    ("motion.position_x", "Motion X", "mm", 0.0, 140.0, "#22c55e"),
    ("motion.position_y", "Motion Y", "mm", 0.0, 200.0, "#84cc16"),
    ("extruder.filamentUsed", "Filament", "mm^3", 0.0, 14.0, "#f59e0b"),
    ("toolchanger.changeProgress", "Tool change", "", 0.0, 1.0, "#a855f7"),
]

# ── Animation timing ──────────────────────────────────────────────────────────
# One frame every FRAME_DT simulation-seconds; played at SPEEDUP × real speed.
# e.g. 92.4 s simulation at 10× → 92 frames × 100 ms = ~9 s wall-clock playback.
FRAME_DT = 1.0          # simulation seconds per frame
SPEEDUP  = 10           # how many sim-seconds equal one real second
FRAME_MS = int(FRAME_DT / SPEEDUP * 1000)   # ms per frame (= 100 ms)

QSS = f"""
* {{
    background-color: {BG_DARK};
    color: {TEXT_MAIN};
    font-family: "Segoe UI", system-ui, sans-serif;
    font-size: 13px;
}}
QLabel {{ background: transparent; }}
QFrame#card {{
    background-color: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
}}
QPushButton {{
    background-color: {BG_HEADER};
    color: {ACCENT};
    border: 1px solid {BORDER};
    border-radius: 6px;
    padding: 4px 18px;
    font-size: 12px;
}}
QPushButton:hover   {{ background-color: #1a1d2e; border-color: {ACCENT}; }}
QPushButton:pressed {{ background-color: {BG_DARK}; }}
QPushButton:disabled {{ color: #3d4468; border-color: {BORDER}; }}
QTableWidget {{
    background-color: {BG_CARD};
    border: none;
    gridline-color: {BORDER};
    font-size: 12px;
}}
QTableWidget::item {{ padding: 3px 8px; border: none; }}
QTableWidget::item:selected {{ background: #1c1f30; }}
QHeaderView::section {{
    background-color: {BG_HEADER};
    color: #3d4468;
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 4px 8px;
    font-size: 10px;
    letter-spacing: 0.08em;
}}
QScrollBar:vertical {{
    background: {BG_DARK}; width: 6px; border: none;
}}
QScrollBar::handle:vertical {{
    background: #252840; border-radius: 3px; min-height: 24px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
"""

# ── Data helpers ──────────────────────────────────────────────────────────────

def extract_subj_data(trace):
    """Per-subject: timeline of (time, state) and unique ordered states."""
    result = {}
    for subj in SUBJECTS:
        try:
            state_data = trace.states(subj)
            times = list(state_data.times)
            seq = [s[-1] if s else "?" for s in state_data.states]
        except Exception:
            logging.exception("failed to read state trace for %s", subj)
            times = []
            seq = []
        if not times or not seq:
            times = [0.0]
            seq = ["?"]
        uniq  = []
        for s in seq:
            if not uniq or uniq[-1] != s:
                uniq.append(s)
        result[subj] = {"times": times, "seq": seq, "uniq": uniq}
    return result

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

def state_at(subj_data, subj, t):
    d = subj_data[subj]
    cur = d["seq"][0] if d["seq"] else d["uniq"][0]
    for ti, s in zip(d["times"], d["seq"]):
        if ti <= t + 1e-6:
            cur = s
    return cur

def visited_at(subj_data, subj, t):
    d, seen = subj_data[subj], []
    for ti, s in zip(d["times"], d["seq"]):
        if ti <= t + 1e-6 and s not in seen:
            seen.append(s)
    return seen

def all_times(subj_data):
    return sorted({t for subj in SUBJECTS for t in subj_data[subj]["times"]})

def numeric_pairs(trace, channel_id: str) -> list[tuple[float, float]]:
    """Return numeric (time, value) samples for a channel, or [] if unavailable."""
    try:
        data = trace.channel(channel_id)
    except Exception:
        logging.exception("failed to read value channel %s", channel_id)
        return []
    pairs = []
    for t, value in zip(data.times, data.values):
        try:
            pairs.append((float(t), float(value)))
        except (TypeError, ValueError):
            continue
    return pairs

def value_at_pairs(pairs: list[tuple[float, float]], t: float) -> float | None:
    if not pairs:
        return None
    current = pairs[0][1]
    for sample_t, value in pairs:
        if sample_t <= t + 1e-6:
            current = value
        else:
            break
    return current

def normalize_value(value: float | None, vmin: float, vmax: float) -> float:
    if value is None or vmax <= vmin:
        return 0.0
    return max(0.0, min(1.0, (value - vmin) / (vmax - vmin)))

def frame_times(duration: float) -> list[float]:
    """Uniform time grid at FRAME_DT intervals covering the full simulation."""
    n = max(2, round(duration / FRAME_DT) + 1)
    return [round(i * FRAME_DT, 3) for i in range(n)]

def interp_bed_z(sd, t: float) -> tuple[float, float]:
    """
    Smoothly interpolate bed Z between BED_Z positions at state transitions.
    Uses smoothstep so the motion eases in/out.
    """
    times = sd["bed"]["times"]
    seq   = sd["bed"]["seq"]
    if not times or not seq:
        return BED_Z.get("Ready", (105, 123))

    # Find which transition bracket t falls in
    prev_i = 0
    for i, ti in enumerate(times):
        if ti <= t + 1e-6:
            prev_i = i

    prev_s = seq[prev_i]
    next_i = min(prev_i + 1, len(seq) - 1)
    next_s = seq[next_i]
    prev_t = times[prev_i]
    next_t = times[next_i]

    z0 = BED_Z.get(prev_s, (105, 123))
    z1 = BED_Z.get(next_s, (105, 123))

    if next_s == prev_s or next_t <= prev_t:
        return z0

    a = max(0.0, min(1.0, (t - prev_t) / (next_t - prev_t)))
    a = a * a * (3 - 2 * a)           # smoothstep easing
    return (z0[0] + a * (z1[0] - z0[0]),
            z0[1] + a * (z1[1] - z0[1]))


# ── Plotly HTML helpers ───────────────────────────────────────────────────────

def _load_html(view: QWebEngineView, html: str):
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False, encoding="utf-8")
    tmp.write(html)
    tmp.close()
    view.load(QUrl.fromLocalFile(tmp.name))


# ══════════════════════════════════════════════════════════════════════════════
#  ANIMATED STATE MACHINE DIAGRAM
# ══════════════════════════════════════════════════════════════════════════════

def make_state_machine_html(trace) -> str:
    """
    Plotly animated state machine built from the simulation trace.

    Layout: one row per subject (hotend / bed / printer).
    Each row shows states as rounded-square nodes connected by labelled arrows.
    The current active state is highlighted in the subject's accent colour.
    Play/pause + time slider drive the animation.
    """
    sd    = extract_subj_data(trace)
    times = frame_times(trace.duration)   # uniform 1-s grid over full simulation

    def sx(subj, state):
        """Normalised X position [0..1] for a state node."""
        uniq = sd[subj]["uniq"]
        n = len(uniq)
        if n <= 1:
            return 0.5
        idx = uniq.index(state) if state in uniq else 0
        return idx / (n - 1)

    def trigger_label(subj, from_s, to_s):
        d = sd[subj]
        for i in range(len(d["seq"]) - 1):
            if d["seq"][i] == from_s and d["seq"][i + 1] == to_s:
                t_change = d["times"][i + 1]
                for entry in trace._timeline:
                    if abs(entry.get("t", 0) - t_change) < 0.15:
                        for ev in entry.get("events", []):
                            return ev.get("trigger", "")
        return ""

    # ── Base figure ────────────────────────────────────────────────────────────
    fig = go.Figure()

    # Subject labels + static transition arrows
    for subj in SUBJECTS:
        y    = SUBJ_Y[subj]
        col  = SUBJ_COLOR[subj]
        uniq = sd[subj]["uniq"]

        fig.add_annotation(
            x=-0.06, y=y, text=f"<b>{subj}</b>",
            showarrow=False,
            font=dict(color=col, size=12, family="Segoe UI"),
            xanchor="right", xref="x", yref="y",
        )

        for i in range(len(uniq) - 1):
            x0  = sx(subj, uniq[i])
            x1  = sx(subj, uniq[i + 1])
            lbl = trigger_label(subj, uniq[i], uniq[i + 1])
            fig.add_annotation(
                x=x1 - 0.05, y=y,
                ax=x0 + 0.05, ay=y,
                xref="x", yref="y", axref="x", ayref="y",
                arrowhead=2, arrowsize=1.5, arrowwidth=2,
                arrowcolor="#252840",
                text=f'<span style="font-size:9px;color:#3d4468">{lbl}</span>',
                font=dict(size=9, color="#3d4468"),
                yshift=14, showarrow=True,
            )

    # One trace per subject: background nodes + active-state overlay
    trace_map = {}   # subj -> (bg_idx, active_idx)
    t_idx = 0

    for subj in SUBJECTS:
        y    = SUBJ_Y[subj]
        col  = SUBJ_COLOR[subj]
        uniq = sd[subj]["uniq"]
        n    = len(uniq)
        xs   = [sx(subj, s) for s in uniq]
        ys   = [y] * n

        # Background node trace (all states, dim)
        fig.add_trace(go.Scatter(
            x=xs, y=ys,
            mode="markers+text",
            marker=dict(symbol="square", size=58,
                        color="#0b0f1e",
                        line=dict(color="#1c2040", width=2)),
            text=uniq,
            textfont=dict(color="#475569", size=11, family="Segoe UI"),
            textposition="middle center",
            showlegend=False, hoverinfo="skip",
        ))
        bg_idx = t_idx; t_idx += 1

        # Active-state overlay (single point, starts at first state)
        init = sd[subj]["seq"][0] if sd[subj]["seq"] else uniq[0]
        fig.add_trace(go.Scatter(
            x=[sx(subj, init)], y=[y],
            mode="markers+text",
            marker=dict(symbol="square", size=60,
                        color=col,
                        line=dict(color="white", width=2.5)),
            text=[init],
            textfont=dict(color="white", size=11, family="Segoe UI"),
            textposition="middle center",
            showlegend=False, hoverinfo="skip",
        ))
        act_idx = t_idx; t_idx += 1

        trace_map[subj] = (bg_idx, act_idx)

    # ── Frames (one per simulation timestep) ───────────────────────────────────
    frames = []
    for t in times:
        fd, ft = [], []
        for subj in SUBJECTS:
            y    = SUBJ_Y[subj]
            col  = SUBJ_COLOR[subj]
            uniq = sd[subj]["uniq"]
            n    = len(uniq)
            xs   = [sx(subj, s) for s in uniq]
            ys   = [y] * n
            bg_idx, act_idx = trace_map[subj]

            active  = state_at(sd, subj, t)
            visited = visited_at(sd, subj, t)

            # Background: slightly highlight visited states
            bg_colors  = ["#141828" if s in visited and s != active else "#0b0f1e" for s in uniq]
            bg_borders = ["#25285e" if s in visited and s != active else "#1c2040" for s in uniq]

            fd.append(go.Scatter(
                x=xs, y=ys,
                mode="markers+text",
                marker=dict(symbol="square", size=58,
                            color=bg_colors,
                            line=dict(color=bg_borders, width=2)),
                text=uniq,
                textfont=dict(color="#475569", size=11, family="Segoe UI"),
                textposition="middle center",
            ))
            ft.append(bg_idx)

            fd.append(go.Scatter(
                x=[sx(subj, active)], y=[y],
                mode="markers+text",
                marker=dict(symbol="square", size=60,
                            color=col,
                            line=dict(color="white", width=2.5)),
                text=[active],
                textfont=dict(color="white", size=11, family="Segoe UI"),
                textposition="middle center",
            ))
            ft.append(act_idx)

        frames.append(go.Frame(data=fd, traces=ft, name=f"{t:.2f}"))

    fig.frames = frames

    # ── Slider + play / pause ──────────────────────────────────────────────────
    steps = [
        dict(
            args=[[f.name], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
            label=f"{float(f.name):.1f}s",
            method="animate",
        )
        for f in frames
    ]

    fig.update_layout(
        paper_bgcolor=BG_DARK, plot_bgcolor=BG_DARK,
        font=dict(color=TEXT_MAIN, family="Segoe UI"),
        xaxis=dict(visible=False, range=[-0.14, 1.1]),
        yaxis=dict(visible=False, range=[-0.65, 2.8]),
        margin=dict(l=110, r=20, t=72, b=80),
        height=400,
        updatemenus=[dict(
            type="buttons", showactive=False,
            x=0.0, y=1.2, xanchor="left",
            bgcolor=BG_HEADER, bordercolor=BORDER,
            pad={"r": 10, "t": 4, "b": 4},
            font=dict(color=ACCENT, size=12),
            buttons=[
                dict(
                    label="▶  Play",
                    method="animate",
                    args=[None, {
                        "frame": {"duration": FRAME_MS, "redraw": True},
                        "fromcurrent": True, "mode": "immediate",
                        "transition": {"duration": max(0, FRAME_MS - 20), "easing": "linear"},
                    }],
                ),
                dict(
                    label="⏸  Pause",
                    method="animate",
                    args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                ),
            ],
        )],
        sliders=[dict(
            active=0, steps=steps,
            currentvalue=dict(
                prefix="t = ", suffix=" s",
                font=dict(color=TEXT_MAIN, size=12),
                xanchor="left",
            ),
            pad=dict(t=14, b=10),
            bgcolor=BG_CARD, bordercolor=BORDER, tickcolor=BORDER,
            font=dict(color="#3d4468", size=10),
            len=1.0, x=0,
        )],
    )

    return fig.to_html(full_html=True, include_plotlyjs=True, config={"displayModeBar": False})


# ══════════════════════════════════════════════════════════════════════════════
#  ANIMATED 3D SCHEMATIC
# ══════════════════════════════════════════════════════════════════════════════

def make_replay_html(trace) -> str:
    """Animated state-machine and parametric replay driven by one time slider."""
    sd = extract_subj_data(trace)
    times = frame_times(trace.duration)
    value_series = {
        channel_id: numeric_pairs(trace, channel_id) or [(0.0, 0.0)]
        for channel_id, _label, _unit, _vmin, _vmax, _color in PARAM_CHANNELS
    }

    def sx(subj, state):
        uniq = sd[subj]["uniq"]
        if len(uniq) <= 1:
            return 0.5
        return uniq.index(state) / (len(uniq) - 1) if state in uniq else 0.0

    def trigger_label(subj, from_s, to_s):
        data = sd[subj]
        for i in range(len(data["seq"]) - 1):
            if data["seq"][i] == from_s and data["seq"][i + 1] == to_s:
                t_change = data["times"][i + 1]
                for entry in trace._timeline:
                    if abs(entry.get("t", 0.0) - t_change) < 0.15:
                        for ev in entry.get("events", []):
                            transition_id = ev.get("transition_id", "")
                            if subj in transition_id:
                                return ev.get("trigger", "")
                break
        return ""

    fig = make_subplots(
        rows=2,
        cols=1,
        row_heights=[0.68, 0.32],
        vertical_spacing=0.11,
    )

    for subj in SUBJECTS:
        y = SUBJ_Y[subj]
        col = SUBJ_COLOR[subj]
        uniq = sd[subj]["uniq"]
        fig.add_annotation(
            x=-0.06,
            y=y,
            text=f"<b>{subj}</b>",
            showarrow=False,
            font=dict(color=col, size=12, family="Segoe UI"),
            xanchor="right",
            xref="x",
            yref="y",
        )
        for i in range(len(uniq) - 1):
            x0 = sx(subj, uniq[i])
            x1 = sx(subj, uniq[i + 1])
            label = trigger_label(subj, uniq[i], uniq[i + 1])
            fig.add_annotation(
                x=x1 - 0.05,
                y=y,
                ax=x0 + 0.05,
                ay=y,
                xref="x",
                yref="y",
                axref="x",
                ayref="y",
                arrowhead=2,
                arrowsize=1.4,
                arrowwidth=2,
                arrowcolor="#252840",
                text=f'<span style="font-size:9px;color:#3d4468">{label}</span>',
                font=dict(size=9, color="#3d4468"),
                yshift=14,
                showarrow=True,
            )

    trace_map = {}
    trace_idx = 0
    for subj in SUBJECTS:
        y = SUBJ_Y[subj]
        col = SUBJ_COLOR[subj]
        uniq = sd[subj]["uniq"]
        xs = [sx(subj, state) for state in uniq]
        ys = [y] * len(uniq)

        fig.add_trace(go.Scatter(
            x=xs,
            y=ys,
            mode="markers+text",
            marker=dict(
                symbol="square",
                size=58,
                color="#0b0f1e",
                line=dict(color="#1c2040", width=2),
            ),
            text=uniq,
            textfont=dict(color="#475569", size=11, family="Segoe UI"),
            textposition="middle center",
            showlegend=False,
            hoverinfo="skip",
        ), row=1, col=1)
        bg_idx = trace_idx
        trace_idx += 1

        active = state_at(sd, subj, times[0])
        fig.add_trace(go.Scatter(
            x=[sx(subj, active)],
            y=[y],
            mode="markers+text",
            marker=dict(
                symbol="square",
                size=60,
                color=col,
                line=dict(color="white", width=2.5),
            ),
            text=[active],
            textfont=dict(color="white", size=11, family="Segoe UI"),
            textposition="middle center",
            showlegend=False,
            hoverinfo="skip",
        ), row=1, col=1)
        active_idx = trace_idx
        trace_idx += 1
        trace_map[subj] = (bg_idx, active_idx)

    marker_map = {}
    for channel_id, label, unit, vmin, vmax, col in PARAM_CHANNELS:
        pairs = value_series[channel_id]
        xs = [sample_t for sample_t, _value in pairs]
        ys = [normalize_value(value, vmin, vmax) for _sample_t, value in pairs]
        hovertext = [
            f"{label}: {value:.2f}{(' ' + unit) if unit else ''}<br>t={sample_t:.1f}s"
            for sample_t, value in pairs
        ]
        fig.add_trace(go.Scatter(
            x=xs,
            y=ys,
            mode="lines",
            name=label,
            line=dict(color=col, width=2),
            hovertext=hovertext,
            hoverinfo="text",
        ), row=2, col=1)
        trace_idx += 1

        value = value_at_pairs(pairs, times[0])
        fig.add_trace(go.Scatter(
            x=[times[0]],
            y=[normalize_value(value, vmin, vmax)],
            mode="markers",
            marker=dict(size=10, color=col, line=dict(color="white", width=1.5)),
            showlegend=False,
            hoverinfo="skip",
        ), row=2, col=1)
        marker_map[channel_id] = trace_idx
        trace_idx += 1

    fig.add_trace(go.Scatter(
        x=[times[0], times[0]],
        y=[0.0, 1.0],
        mode="lines",
        line=dict(color="#e2e8f0", width=1.5, dash="dot"),
        showlegend=False,
        hoverinfo="skip",
    ), row=2, col=1)
    cursor_idx = trace_idx

    frames = []
    for t in times:
        frame_data = []
        frame_traces = []
        for subj in SUBJECTS:
            y = SUBJ_Y[subj]
            col = SUBJ_COLOR[subj]
            uniq = sd[subj]["uniq"]
            xs = [sx(subj, state) for state in uniq]
            ys = [y] * len(uniq)
            bg_idx, active_idx = trace_map[subj]
            active = state_at(sd, subj, t)
            visited = visited_at(sd, subj, t)
            bg_colors = ["#141828" if state in visited and state != active else "#0b0f1e" for state in uniq]
            bg_borders = ["#25285e" if state in visited and state != active else "#1c2040" for state in uniq]

            frame_data.append(go.Scatter(
                x=xs,
                y=ys,
                mode="markers+text",
                marker=dict(
                    symbol="square",
                    size=58,
                    color=bg_colors,
                    line=dict(color=bg_borders, width=2),
                ),
                text=uniq,
                textfont=dict(color="#475569", size=11, family="Segoe UI"),
                textposition="middle center",
            ))
            frame_traces.append(bg_idx)

            frame_data.append(go.Scatter(
                x=[sx(subj, active)],
                y=[y],
                mode="markers+text",
                marker=dict(
                    symbol="square",
                    size=60,
                    color=col,
                    line=dict(color="white", width=2.5),
                ),
                text=[active],
                textfont=dict(color="white", size=11, family="Segoe UI"),
                textposition="middle center",
            ))
            frame_traces.append(active_idx)

        for channel_id, _label, _unit, vmin, vmax, col in PARAM_CHANNELS:
            pairs = value_series[channel_id]
            value = value_at_pairs(pairs, t)
            frame_data.append(go.Scatter(
                x=[t],
                y=[normalize_value(value, vmin, vmax)],
                mode="markers",
                marker=dict(size=10, color=col, line=dict(color="white", width=1.5)),
            ))
            frame_traces.append(marker_map[channel_id])

        frame_data.append(go.Scatter(
            x=[t, t],
            y=[0.0, 1.0],
            mode="lines",
            line=dict(color="#e2e8f0", width=1.5, dash="dot"),
        ))
        frame_traces.append(cursor_idx)
        frames.append(go.Frame(data=frame_data, traces=frame_traces, name=f"{t:.2f}"))

    fig.frames = frames
    steps = [
        dict(
            args=[[frame.name], {"frame": {"duration": 0, "redraw": True}, "mode": "immediate"}],
            label=f"{float(frame.name):.1f}s",
            method="animate",
        )
        for frame in frames
    ]

    fig.update_xaxes(visible=False, range=[-0.14, 1.1], row=1, col=1)
    fig.update_yaxes(
        visible=False,
        range=[-0.65, float(len(SUBJECTS)) - 0.2],
        row=1,
        col=1,
    )
    fig.update_xaxes(
        title_text="Simulation time (s)",
        range=[0.0, max(trace.duration, 1.0)],
        gridcolor=BORDER,
        zeroline=False,
        tickfont=dict(color="#64748b", size=10),
        title_font=dict(color="#64748b", size=11),
        row=2,
        col=1,
    )
    fig.update_yaxes(
        title_text="Normalized values",
        range=[-0.08, 1.08],
        tickvals=[0.0, 0.5, 1.0],
        ticktext=["min", "mid", "max"],
        gridcolor=BORDER,
        zeroline=False,
        tickfont=dict(color="#64748b", size=10),
        title_font=dict(color="#64748b", size=11),
        row=2,
        col=1,
    )
    fig.update_layout(
        paper_bgcolor=BG_DARK,
        plot_bgcolor=BG_DARK,
        font=dict(color=TEXT_MAIN, family="Segoe UI"),
        margin=dict(l=110, r=20, t=72, b=90),
        height=560,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=0.31,
            xanchor="left",
            x=0.0,
            bgcolor=BG_CARD,
            bordercolor=BORDER,
            font=dict(color=TEXT_MAIN, size=10),
        ),
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            x=0.0,
            y=1.2,
            xanchor="left",
            bgcolor=BG_HEADER,
            bordercolor=BORDER,
            pad={"r": 10, "t": 4, "b": 4},
            font=dict(color=ACCENT, size=12),
            buttons=[
                dict(
                    label="Play",
                    method="animate",
                    args=[None, {
                        "frame": {"duration": FRAME_MS, "redraw": True},
                        "fromcurrent": True,
                        "mode": "immediate",
                        "transition": {"duration": max(0, FRAME_MS - 20), "easing": "linear"},
                    }],
                ),
                dict(
                    label="Pause",
                    method="animate",
                    args=[[None], {"frame": {"duration": 0}, "mode": "immediate"}],
                ),
            ],
        )],
        sliders=[dict(
            active=0,
            steps=steps,
            currentvalue=dict(
                prefix="t = ",
                suffix=" s",
                font=dict(color=TEXT_MAIN, size=12),
                xanchor="left",
            ),
            pad=dict(t=14, b=10),
            bgcolor=BG_CARD,
            bordercolor=BORDER,
            tickcolor=BORDER,
            font=dict(color="#3d4468", size=10),
            len=1.0,
            x=0,
        )],
    )

    return fig.to_html(full_html=True, include_plotlyjs=True, config={"displayModeBar": False})


def _box_data(x0, y0, z0, x1, y1, z1, color, name, opacity=0.85, showlegend=True):
    vx = [x0, x1, x1, x0, x0, x1, x1, x0]
    vy = [y0, y0, y1, y1, y0, y0, y1, y1]
    vz = [z0, z0, z0, z0, z1, z1, z1, z1]
    i  = [0, 0, 4, 4, 0, 0, 2, 2, 0, 0, 1, 1]
    j  = [1, 2, 5, 6, 1, 5, 3, 7, 3, 7, 2, 6]
    k  = [2, 3, 6, 7, 5, 4, 7, 6, 7, 4, 6, 5]
    return go.Mesh3d(
        x=vx, y=vy, z=vz, i=i, j=j, k=k,
        color=color, opacity=opacity, name=name,
        showlegend=showlegend,
        hovertemplate=f"<b>{name}</b><extra></extra>",
    )


def make_3d_html(trace) -> str:
    """
    Static 3D Voron Trident schematic showing final simulation state.

    Plotly's Mesh3d traces don't support frame-based animation (rejected promises).
    The schematic reflects the completed simulation — bed at print height, parts
    coloured by their final state.  It updates when the user clicks Restart.
    """
    sd = extract_subj_data(trace)
    S  = 350

    def final(subj):
        data = sd.get(subj, {"seq": [], "uniq": ["?"]})
        seq = data["seq"]
        return seq[-1] if seq else data["uniq"][0]

    def fill(s): return STATE_FILL.get(s, "#1e293b")

    bed_s    = final("bed")
    hotend_s = final("hotend")
    print_s  = final("printer")
    motion_s = final("motion")
    extruder_s = final("extruder")
    tool_s = final("toolchanger")
    bz0, bz1 = interp_bed_z(sd, trace.duration)   # bed at final position

    # Frame wireframe (all 12 edges as one Scatter3d)
    C = [(0,0,0),(S,0,0),(S,S,0),(0,S,0),(0,0,S),(S,0,S),(S,S,S),(0,S,S)]
    ex, ey, ez = [], [], []
    for a, b in [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),(0,4),(1,5),(2,6),(3,7)]:
        ax,ay,az = C[a]; bx,by,bz = C[b]
        ex += [ax, bx, None]; ey += [ay, by, None]; ez += [az, bz, None]

    fig = go.Figure()
    fig.add_trace(go.Scatter3d(
        x=ex, y=ey, z=ez,
        mode="lines", line=dict(color="#1c2040", width=3),
        showlegend=False, hoverinfo="skip",
    ))

    fig.add_trace(_box_data(0,   0,   0,   S,   38,  52,  "#0a0c18",      "Electronics",          0.75))
    fig.add_trace(_box_data(25,  25,  bz0, 325, 325, bz1, fill(bed_s),    f"Bed  [{bed_s}]",       0.90))
    fig.add_trace(_box_data(5,   5,   282, 28,  345, 296, fill(motion_s), f"Motion  [{motion_s}]", 0.72))
    fig.add_trace(_box_data(322, 5,   282, 345, 345, 296, fill(motion_s), "",                       0.72, showlegend=False))
    fig.add_trace(_box_data(28,  163, 280, 322, 182, 293, fill(print_s),  f"Printer  [{print_s}]", 0.60))
    fig.add_trace(_box_data(148, 156, 258, 202, 189, 302, fill(hotend_s), f"Hotend  [{hotend_s}]", 0.95))
    fig.add_trace(_box_data(165, 166, 250, 185, 179, 258, fill(extruder_s), f"Extruder  [{extruder_s}]", 0.95))
    fig.add_trace(_box_data(285, 42,  62,  338, 320, 92,  fill(tool_s),   f"Toolchanger  [{tool_s}]", 0.70))

    fig.update_layout(
        paper_bgcolor=BG_DARK,
        scene=dict(
            bgcolor=BG_CARD,
            xaxis=dict(visible=False, range=[0, S]),
            yaxis=dict(visible=False, range=[0, S]),
            zaxis=dict(visible=False, range=[0, S]),
            camera=dict(eye=dict(x=1.75, y=-1.5, z=1.15)),
            aspectmode="cube",
        ),
        margin=dict(l=0, r=0, t=10, b=10),
        height=320,
        legend=dict(bgcolor=BG_CARD, bordercolor=BORDER,
                    font=dict(color=TEXT_MAIN, size=11),
                    x=0.01, y=0.99, itemsizing="constant"),
        font=dict(color=TEXT_MAIN),
    )

    return fig.to_html(full_html=True, include_plotlyjs=True, config={"displayModeBar": False})


# ── Simulation worker thread ───────────────────────────────────────────────────

class SimThread(QThread):
    done = pyqtSignal(object)

    def __init__(self, model):
        super().__init__()
        self._model = model

    def run(self):
        self.done.emit(self._model.run_analysis("PrintSequence"))


# ── Qt widget helpers ─────────────────────────────────────────────────────────

def section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet(
        "font-size: 10px; font-weight: 700; letter-spacing: 0.1em; "
        "color: #3d4468; margin-bottom: 4px;"
    )
    return lbl


def labeled_card(title: str, inner: QWidget) -> QFrame:
    frame = QFrame()
    frame.setObjectName("card")
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(16, 12, 16, 12)
    lay.setSpacing(6)
    lay.addWidget(section_label(title))
    lay.addWidget(inner)
    return frame


class StatBox(QWidget):
    def __init__(self, label: str, value: str = "—"):
        super().__init__()
        self.setStyleSheet(
            f"background: {BG_DARK}; border: 1px solid {BORDER}; border-radius: 6px;"
        )
        lay = QVBoxLayout(self)
        lay.setContentsMargins(10, 8, 10, 8)
        lay.setSpacing(2)
        self._lbl = QLabel(label.upper())
        self._lbl.setStyleSheet("font-size: 10px; color: #3d4468; letter-spacing: 0.08em; border: none;")
        self._val = QLabel(value)
        self._val.setStyleSheet("font-size: 18px; font-weight: 600; color: #e2e8f0; border: none;")
        lay.addWidget(self._lbl)
        lay.addWidget(self._val)

    def set_value(self, v: str):
        self._val.setText(v)


# ── Main window ───────────────────────────────────────────────────────────────

class VoronWindow(QMainWindow):

    def __init__(self, model, parts, cases):
        super().__init__()
        self._model  = model
        self._parts  = parts
        self._cases  = cases
        self._thread: SimThread | None = None
        self._ps     = next(c for c in cases if c.label == "PrintSequence")

        self.setWindowTitle("Mercurio — Voron Trident 350")
        self.resize(1500, 960)
        self.setStyleSheet(QSS)

        root = QWidget()
        self.setCentralWidget(root)
        vbox = QVBoxLayout(root)
        vbox.setContentsMargins(0, 0, 0, 0)
        vbox.setSpacing(0)
        vbox.addWidget(self._make_header())
        vbox.addWidget(self._make_body(), 1)

    # ── Header ────────────────────────────────────────────────────────────────

    def _make_header(self) -> QWidget:
        hdr = QWidget()
        hdr.setStyleSheet(f"background: {BG_HEADER}; border-bottom: 1px solid {BORDER};")
        hdr.setFixedHeight(44)
        lay = QHBoxLayout(hdr)
        lay.setContentsMargins(20, 0, 20, 0)

        logo  = QLabel("MERCURIO")
        logo.setStyleSheet(f"font-weight: 700; letter-spacing: 0.2em; font-size: 11px; color: {ACCENT};")
        sep   = QLabel(" · ")
        sep.setStyleSheet("color: #252840; margin: 0 8px;")
        title = QLabel("Voron Trident 350 + Indx  —  PrintSequence")
        title.setStyleSheet(f"font-size: 12px; color: {TEXT_DIM};")

        self._status_lbl = QLabel("")
        self._status_lbl.setStyleSheet(f"font-size: 11px; color: {ACCENT};")

        self._restart_btn = QPushButton("↺  Restart")
        self._restart_btn.setFixedHeight(28)
        self._restart_btn.clicked.connect(self._on_restart)

        lay.addWidget(logo)
        lay.addWidget(sep)
        lay.addWidget(title)
        lay.addStretch()
        lay.addWidget(self._status_lbl)
        lay.addWidget(self._restart_btn)
        return hdr

    # ── Body ─────────────────────────────────────────────────────────────────

    def _make_body(self) -> QWidget:
        body = QWidget()
        lay  = QHBoxLayout(body)
        lay.setContentsMargins(12, 12, 12, 12)
        lay.setSpacing(12)
        lay.addWidget(self._make_left(), 1)
        lay.addWidget(self._make_right())
        return body

    # ── Left column: state machine + transitions ──────────────────────────────

    def _make_left(self) -> QWidget:
        w   = QWidget()
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # State machine (main animated view)
        self._view_sm = QWebEngineView()
        self._view_sm.setMinimumHeight(560)
        lay.addWidget(labeled_card("State Machines + Parametric Replay", self._view_sm))

        # Transition log table
        self._tbl_ev = self._make_event_table()
        lay.addWidget(labeled_card("Transition Log", self._tbl_ev))

        return w

    def _make_event_table(self) -> QTableWidget:
        tbl = QTableWidget(0, 3)
        tbl.setHorizontalHeaderLabels(["t (s)", "Transition", "Trigger"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setMaximumHeight(180)
        return tbl

    # ── Right column: 3D + stats + parts ─────────────────────────────────────

    def _make_right(self) -> QWidget:
        w = QWidget()
        w.setFixedWidth(400)
        lay = QVBoxLayout(w)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(10)

        # 3D animated schematic
        self._view_3d = QWebEngineView()
        self._view_3d.setMinimumHeight(320)
        lay.addWidget(labeled_card("3D Schematic  — final state", self._view_3d))

        # Stats
        case_w = QWidget()
        case_l = QVBoxLayout(case_w)
        case_l.setContentsMargins(0, 0, 0, 0)
        case_l.setSpacing(4)
        name_lbl = QLabel("PrintSequence")
        name_lbl.setStyleSheet(f"font-weight:600;font-size:15px;color:{ACCENT};")
        case_l.addWidget(name_lbl)
        id_lbl = QLabel(self._ps.id)
        id_lbl.setStyleSheet("font-size:10px;color:#3d4468;font-family:'Cascadia Code',Consolas,monospace;")
        case_l.addWidget(id_lbl)
        grid = QGridLayout()
        grid.setSpacing(8); grid.setContentsMargins(0, 8, 0, 0)
        self._stat_subjects    = StatBox("Subjects",    str(self._ps.subject_count))
        self._stat_duration    = StatBox("Duration",    "—")
        self._stat_status      = StatBox("Status",      "—")
        self._stat_transitions = StatBox("Transitions", "—")
        grid.addWidget(self._stat_subjects,    0, 0)
        grid.addWidget(self._stat_duration,    0, 1)
        grid.addWidget(self._stat_status,      1, 0)
        grid.addWidget(self._stat_transitions, 1, 1)
        case_l.addLayout(grid)
        lay.addWidget(labeled_card("Analysis Case", case_w))

        # Parts table
        lay.addWidget(labeled_card(
            f"Model Parts ({len(self._parts)} total)",
            self._make_parts_table(),
        ), 1)

        return w

    def _make_parts_table(self) -> QTableWidget:
        usages = [p for p in self._parts if "Usage" in p.element_kind and "State" not in p.element_kind]
        defs   = [p for p in self._parts if "Definition" in p.element_kind]
        rows   = usages + defs
        tbl = QTableWidget(len(rows), 3)
        tbl.setHorizontalHeaderLabels(["Name", "Type", "Kind"])
        tbl.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        tbl.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        tbl.verticalHeader().setVisible(False)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        for r, p in enumerate(usages):
            n = QTableWidgetItem(p.name); n.setForeground(QColor(ACCENT))
            tbl.setItem(r, 0, n)
            tbl.setItem(r, 1, QTableWidgetItem(p.kind.split("::")[-1]))
            u = QTableWidgetItem("usage"); u.setForeground(QColor("#3d4468"))
            tbl.setItem(r, 2, u)
        for i, p in enumerate(defs):
            r = len(usages) + i
            n = QTableWidgetItem(p.name); n.setForeground(QColor(TEXT_MID))
            tbl.setItem(r, 0, n)
            tbl.setItem(r, 1, QTableWidgetItem("—"))
            d = QTableWidgetItem("definition"); d.setForeground(QColor("#3d4468"))
            tbl.setItem(r, 2, d)
        return tbl

    # ── Update all UI from a trace ────────────────────────────────────────────

    def update_from_trace(self, trace):
        # Animated Plotly charts
        _load_html(self._view_sm, make_replay_html(trace))
        _load_html(self._view_3d, make_3d_html(trace))

        # Transition log
        ev = event_rows(trace)
        self._tbl_ev.setRowCount(len(ev))
        for row, (t, label, trigger) in enumerate(ev):
            ti = QTableWidgetItem(f"{t:.1f}"); ti.setForeground(QColor(ACCENT))
            li = QTableWidgetItem(label);      li.setForeground(QColor(TEXT_MID))
            ri = QTableWidgetItem(trigger);    ri.setForeground(QColor("#3d4468"))
            self._tbl_ev.setItem(row, 0, ti)
            self._tbl_ev.setItem(row, 1, li)
            self._tbl_ev.setItem(row, 2, ri)

        # Stat boxes
        self._stat_duration.set_value(f"{trace.duration:.1f} s")
        self._stat_status.set_value(trace.status)
        self._stat_transitions.set_value(str(len(ev)))

        # Header
        self._status_lbl.setText(
            f"{trace.status.upper()}  {trace.duration:.1f}s  "
            f"{self._ps.subject_count} subjects  {len(ev)} transitions"
        )
        self._restart_btn.setEnabled(True)
        self._restart_btn.setText("↺  Restart")

    # ── Restart ───────────────────────────────────────────────────────────────

    def _on_restart(self):
        self._restart_btn.setEnabled(False)
        self._restart_btn.setText("Running…")
        self._thread = SimThread(self._model)
        self._thread.done.connect(self.update_from_trace)
        self._thread.start()

    def closeEvent(self, event):
        self._model.close()
        super().closeEvent(event)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    logging.info("main() entered")
    try:
        logging.info("mercurio.open(%s)", WORKSPACE)
        model = mercurio.open(WORKSPACE)
        logging.info("model opened OK")

        parts = model.parts()
        logging.info("parts: %d", len(parts))

        cases = model.analysis_cases()
        logging.info("cases: %s", [c.label for c in cases])

        logging.info("run_analysis PrintSequence")
        trace = model.run_analysis("PrintSequence")
        logging.info("trace: status=%s duration=%.1f", trace.status, trace.duration)

        app = QApplication(sys.argv)
        app.setStyle("Fusion")

        win = VoronWindow(model, parts, cases)
        win.show()
        win.update_from_trace(trace)

        logging.info("entering Qt event loop")
        sys.exit(app.exec())

    except Exception:
        tb = traceback.format_exc()
        logging.error("CRASH:\n%s", tb)

        # Show a visible error dialog so the window doesn't just flash closed.
        try:
            from PyQt6.QtWidgets import QMessageBox
            _app = QApplication.instance() or QApplication(sys.argv)
            msg = QMessageBox()
            msg.setWindowTitle("Mercurio — Simulation Error")
            msg.setIcon(QMessageBox.Icon.Critical)
            msg.setText("The simulation failed to start.")
            msg.setDetailedText(tb)
            msg.setInformativeText(f"Log: {_log_path}")
            msg.exec()
        except Exception:
            pass
        sys.exit(1)


if __name__ == "__main__":
    main()
