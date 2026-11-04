"""Plotly-Abbildungen. Alle Achsen sind gesperrt (fixedrange), damit Touch-Geräte beim Scrollen nicht am Diagramm hängen bleiben."""

import plotly.graph_objects as go

import mvw_constants as C


def lock_axes(fig):
    fig.update_xaxes(fixedrange=True)
    fig.update_yaxes(fixedrange=True)
    return fig


def _base(fig, height=340):
    fig.update_layout(height=height, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", y=-0.25), plot_bgcolor="rgba(0,0,0,0)")
    return lock_axes(fig)


def build_selection(values, g_mask, o_mask, ylabel, height=320):
    """Wert je Leitung (Gewicht oder Einzelwert), gefärbt nach Auswahl: beide, nur Greedy, nur Optimum, keine."""
    n = len(values)
    groups = [("von beiden gewählt", C.COLOR_BAR, lambda i: g_mask >> i & 1 and o_mask >> i & 1), ("nur Greedy", C.COLOR_BAR2, lambda i: g_mask >> i & 1 and not o_mask >> i & 1),
              ("nur Optimum", C.COLOR_NODE, lambda i: o_mask >> i & 1 and not g_mask >> i & 1), ("nicht gewählt", C.COLOR_OTHER, lambda i: not (g_mask >> i & 1 or o_mask >> i & 1))]
    fig = go.Figure()
    for name, color, pred in groups:
        idx = [i for i in range(n) if pred(i)]
        fig.add_trace(go.Bar(name=name, x=[str(i + 1) for i in idx], y=[values[i] for i in idx], marker_color=color, hovertemplate="Leitung %{x}: %{y}<extra></extra>"))
    fig.update_layout(barmode="stack")
    fig.update_xaxes(type="category", title_text="Leitung", categoryorder="array", categoryarray=[str(i + 1) for i in range(n)])
    fig.update_yaxes(title_text=ylabel)
    return _base(fig, height)


def build_cost_bars(rows, ns, height=340):
    """Median der Orakelaufrufe bis zum Fund (Austauschtest) je Familie und n, dazu 2^n als Linie (logarithmisch)."""
    fig = go.Figure()
    palette = [C.COLOR_BAR, C.COLOR_BAR2, C.COLOR_NODE, "#7570b3", "#66a61e"]
    kinds = []
    for r in rows:
        if r["kind"] not in kinds:
            kinds.append(r["kind"])
    for color, k in zip(palette, kinds):
        sel = [r for r in rows if r["kind"] == k]
        fig.add_trace(go.Bar(name=C.KIND_SHORT[k], x=[f"n = {r['n']}" for r in sel], y=[r["ex_median"] for r in sel], marker_color=color, hovertemplate="%{x}: %{y} Aufrufe<extra></extra>"))
    fig.add_trace(go.Scatter(name="vollständige Prüfung 2^n", x=[f"n = {n}" for n in ns], y=[2 ** n for n in ns], mode="lines+markers", line=dict(color="black", dash="dot"), hovertemplate="%{x}: %{y} Aufrufe<extra></extra>"))
    fig.update_layout(barmode="group")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="Aufrufe (logarithmisch)", type="log")
    return _base(fig, height)


def build_pass_bars(res, height=300):
    """Nicht-Matroide, die den gezogenen Test bestehen (stille Fehler), je Budget."""
    xs = [f"B = {b}" for b in C.E_BUDGETS]
    fig = go.Figure([go.Bar(name="bestehen den Test", x=xs, y=[res["passed"][b] for b in C.E_BUDGETS], marker_color=C.COLOR_BAR2, text=[str(res["passed"][b]) for b in C.E_BUDGETS], textposition="outside",
                            hovertemplate="%{x}: %{y} Nicht-Matroide<extra></extra>")])
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text=f"von {res['total']} Nicht-Matroiden", range=[0, res["total"] * 1.12])
    return _base(fig, height)


def build_rule_bars(res, height=300):
    """Mittlerer Verlust gegen das Optimum: immer Greedy gegen die Regel bei drei Budgets."""
    names = ["immer Greedy"] + [f"Regel, B = {r['budget']}" for r in res["rows"]]
    vals = [100 * res["greedy"]] + [100 * r["rule"] for r in res["rows"]]
    fig = go.Figure([go.Bar(x=names, y=vals, marker_color=[C.COLOR_OTHER] + [C.COLOR_BAR] * len(res["rows"]), text=[f"{v:.2f}".replace(".", ",") + " %" for v in vals], textposition="outside", hovertemplate="%{x}: %{y:.2f} %<extra></extra>")])
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="mittlerer Verlust in %", range=[0, max(vals) * 1.2])
    return _base(fig, height)


def build_sub_lines(res, height=320):
    """Anteil gefundener Verletzungen der Submodularität je Budget (logarithmische Achse der Aufrufe)."""
    fig = go.Figure()
    for r in res["rows"]:
        if not r["violated"]:
            continue
        fig.add_trace(go.Scatter(name=C.E_SUB_KIND_NAMES[r["kind"]], x=list(C.E_SUB_BUDGETS), y=[r["cells"][b] / r["violated"] for b in C.E_SUB_BUDGETS], mode="lines+markers", hovertemplate="B = %{x}: %{y:.0%}<extra></extra>"))
    fig.update_xaxes(type="log", title_text="Budget B (Orakelaufrufe)")
    fig.update_yaxes(title_text="Anteil gefunden", tickformat=".0%", range=[0, 1.05])
    return _base(fig, height)


def build_ratio_bars(res, height=320):
    """Kleinster Greedy-Quotient je Familie; die Linie bei 0,5 ist die Schranke für den Schnitt zweier Matroide."""
    names = [C.KIND_SHORT[r["kind"]] for r in res["rows"]]
    mins = [r["min"] for r in res["rows"]]
    colors = [C.COLOR_BAR if r["kind"] in C.MATROID_KINDS else C.COLOR_BAR2 for r in res["rows"]]
    fig = go.Figure([go.Bar(x=names, y=mins, marker_color=colors, hovertemplate="%{x}: %{y:.3f}<extra></extra>")])
    fig.add_hline(y=0.5, line_dash="dot", line_color="black", annotation_text="Schranke ½", annotation_position="right")
    fig.update_xaxes(type="category")
    fig.update_yaxes(title_text="kleinster Quotient Greedy / Optimum", range=[0, 1.05])
    _base(fig, height)
    fig.update_layout(margin=dict(l=10, r=80, t=10, b=10))
    return fig
