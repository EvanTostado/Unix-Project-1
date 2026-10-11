"""Prototype for the Linux Infrastructure Observability Dashboard.

All metric readings are SIMULATED. This app does not connect to GCP.
"""

from datetime import datetime
from random import randint, uniform

from dash import Dash, Input, Output, State, dcc, html
import plotly.graph_objects as go

SERVERS = ["vm-1", "vm-2", "vm-3", "vm-4"]

app = Dash(__name__)
app.title = "Linux Observability Dashboard"

app.layout = html.Div(
    [
        html.H1("Linux Infrastructure Observability"),
        html.P("Prototype — simulated metrics, not connected to GCP."),
        html.Label("Select server"),
        dcc.Dropdown(
            id="server-select",
            options=[{"label": name, "value": name} for name in SERVERS],
            value=SERVERS[0],
            clearable=False,
            style={"color": "#222"},
        ),
        dcc.Checklist(
            id="simulate-stress",
            options=[{"label": " Simulate high CPU on selected server", "value": "on"}],
            value=[],
            style={"marginTop": "14px"},
        ),
        html.Label("CPU warning threshold", style={"display": "block", "marginTop": "18px"}),
        dcc.Slider(40, 100, 10, value=80, marks={n: f"{n}%" for n in range(40, 101, 10)}, id="threshold"),
        html.Div(id="metric-cards", style={"display": "grid", "gridTemplateColumns": "repeat(auto-fit, minmax(150px, 1fr))", "gap": "12px", "marginTop": "22px"}),
        html.Div(id="alert", style={"fontWeight": "bold", "margin": "16px 0"}),
        dcc.Graph(id="cpu-chart"),
        dcc.Store(id="history", data={name: [] for name in SERVERS}),
        dcc.Interval(id="refresh", interval=2000, n_intervals=0),
    ],
    style={"maxWidth": "1050px", "margin": "30px auto", "padding": "20px", "backgroundColor": "#111827", "color": "#f9fafb", "fontFamily": "Arial, sans-serif", "borderRadius": "12px"},
)


@app.callback(
    Output("history", "data"),
    Input("refresh", "n_intervals"),
    State("history", "data"),
    State("server-select", "value"),
    State("simulate-stress", "value"),
)
def collect_mock_metrics(_tick, history, selected_server, simulation):
    """Generate mock readings for each VM; retain the last 120 samples."""
    history = history or {}
    for server in SERVERS:
        high_cpu = server == selected_server and "on" in simulation
        reading = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "cpu_percent": randint(88, 99) if high_cpu else randint(12, 54),
            "memory_percent": randint(25, 70),
            "disk_percent": randint(30, 75),
            "network_mbps": round(uniform(0.1, 20.0), 2),
            "process_count": randint(90, 220),
        }
        history[server] = (history.get(server, []) + [reading])[-120:]
    return history


@app.callback(
    Output("metric-cards", "children"),
    Output("alert", "children"),
    Output("cpu-chart", "figure"),
    Input("history", "data"),
    Input("server-select", "value"),
    Input("threshold", "value"),
)
def render_dashboard(history, selected_server, threshold):
    samples = (history or {}).get(selected_server, [])
    if not samples:
        return [], "Waiting for simulated samples...", go.Figure()

    latest = samples[-1]
    metrics = [
        ("CPU", f"{latest['cpu_percent']}%"),
        ("Memory", f"{latest['memory_percent']}%"),
        ("Disk", f"{latest['disk_percent']}%"),
        ("Network", f"{latest['network_mbps']:.2f} Mbps"),
        ("Processes", str(latest["process_count"])),
    ]
    cards = [
        html.Div(
            [html.Div(label, style={"fontSize": "14px"}), html.H2(value)],
            style={"background": "#1f2937", "padding": "12px", "borderRadius": "8px"},
        )
        for label, value in metrics
    ]
    alert = (
        f"WARNING: {selected_server} CPU exceeds {threshold}%"
        if latest["cpu_percent"] > threshold
        else f"OK: {selected_server} CPU is below the warning threshold"
    )
    chart = go.Figure(
        go.Scatter(
            x=[item["time"] for item in samples],
            y=[item["cpu_percent"] for item in samples],
            mode="lines+markers",
            name="CPU usage",
        )
    )
    chart.add_hline(y=threshold, line_dash="dash", annotation_text="Alert threshold")
    chart.update_layout(
        title=f"{selected_server} — CPU history (session only)",
        template="plotly_dark",
        paper_bgcolor="#111827",
        plot_bgcolor="#111827",
        xaxis_title="Time",
        yaxis_title="CPU (%)",
        yaxis_range=[0, 100],
    )
    return cards, alert, chart


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1")
