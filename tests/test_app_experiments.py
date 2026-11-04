"""AppTest: Hauptansicht, Experimente 1 bis 5, Spielwiese, Permalink und PDF (DEMO-PLAYBOOK §3, §5)."""

import os
from pathlib import Path

from streamlit.testing.v1 import AppTest

import mvw_constants as C
import mvw_evaluation as ev
from mvw_pdf_export import build_pdf

APP = str(Path(__file__).resolve().parent.parent / "app.py")
TIMEOUT = int(os.environ.get("APPTEST_TIMEOUT", "300"))


def _app(params=None) -> AppTest:
    at = AppTest.from_file(APP, default_timeout=TIMEOUT)
    for key, value in (params or {}).items():
        at.query_params[key] = value
    at.run()
    assert not at.exception, [str(e) for e in at.exception]
    return at


def _texts(at):
    return [m.value for m in list(at.success) + list(at.info) + list(at.warning) + list(at.error)]


def _click_preset(at, name):
    at.sidebar.button(key=f"preset_{name}").click().run()
    assert not at.exception, [str(e) for e in at.exception]


def test_default_shows_the_metrics_steps_and_the_verdict():
    at = _app()
    assert [(m.label, m.value) for m in at.metric] == [("Gezogener Test", "311"), ("Voller Test", "1 024"), ("Greedy-Wert", "108"), ("Optimum", "108")]
    assert any(t.startswith("Wald mit 10 Leitungen: Der gezogene Test fand in **311** Orakelaufrufen kein Gegenbeispiel") for t in _texts(at))
    assert any(t.startswith("Noch nichts gezogen.") for t in _texts(at))


def test_main_verdict_matches_each_preset():
    expected = {
        "Standardfall (Voreinstellung)": "Wald mit 10 Leitungen: Der gezogene Test fand in **311** Orakelaufrufen kein Gegenbeispiel",
        "Regenbogen-Wald": "Regenbogen-Wald mit 10 Leitungen: Der gezogene Test fand nach **23** Orakelaufrufen ein Gegenbeispiel",
        "Zuordnung": "Empfehlung: **Schnittverfahren (Stück 7 und 8)**",
        "Konflikte": "Empfehlung: **Näherung oder ganzzahliges Programm (Stück 2, 12)**",
        "Budget": "Greedy erreicht 51 von 92 (0,554 des Optimums)",
        "Stiller Fehler": "Das ist ein **stiller Fehler**",
    }
    at = _app()
    for name, needle in expected.items():
        _click_preset(at, name)
        assert any(needle in t for t in _texts(at)), name


def test_each_sidebar_widget_changes_the_view():
    at = _app()
    at.sidebar.selectbox(key="kind_select").set_value("knapsack").run()
    assert not at.exception and any(t.startswith("Budget mit 10 Leitungen:") for t in _texts(at))
    at.sidebar.slider(key="n_slider").set_value(8).run()
    assert not at.exception and any(t.startswith("Budget mit 8 Leitungen:") for t in _texts(at)) and [m.value for m in at.metric][1] == "256"
    at.sidebar.select_slider(key="budget_slider").set_value(30).run()
    assert not at.exception and int(at.sidebar.select_slider(key="budget_slider").value) == 30
    at.sidebar.selectbox(key="objective_select").set_value("paarbonus").run()
    assert not at.exception and any("Test auf Submodularität" in t for t in _texts(at))
    at.sidebar.selectbox(key="info_select").set_value("nacheinander").run()
    assert not at.exception and any("Informationslage (Angebote kommen nacheinander (online))" in t for t in _texts(at))
    at.sidebar.number_input(key="seed_input").set_value(11).run()
    assert not at.exception


def test_every_kind_runs():
    at = _app()
    for kind in C.KINDS:
        at.sidebar.selectbox(key="kind_select").set_value(kind).run()
        assert not at.exception, (kind, [str(e) for e in at.exception])
        assert any(f"{C.KIND_SHORT[kind]} mit 10 Leitungen:" in t for t in _texts(at)), kind


def test_on_demand_series_appear_and_stay():
    at = _app()
    assert not any(t.startswith("Ein Gegenbeispiel zum Matroid findet der Größentest") for t in _texts(at))
    at.button(key="ex1_run").click().run()
    assert not at.exception and any(t.startswith("Ein Gegenbeispiel zum Matroid findet der Größentest im Median") for t in _texts(at))
    at.button(key="ex2_run").click().run()
    assert not at.exception and any(t.startswith("Von 298 Nicht-Matroiden bestehen den gezogenen Test") for t in _texts(at))
    at.button(key="ex3_run").click().run()
    assert not at.exception and any(t.startswith("Über 600 Instanzen aus zehn Familien verliert") for t in _texts(at))
    at.button(key="ex4_run").click().run()
    assert not at.exception and any(t.startswith("Der Test auf Submodularität ist billiger als der auf das Matroid") for t in _texts(at))
    at.button(key="ex5_run").click().run()
    assert not at.exception and any(t.startswith("Bei allen fünf Matroid-Familien erreicht Greedy das Optimum") for t in _texts(at))
    _click_preset(at, "Budget")
    assert any(t.startswith("Von 298 Nicht-Matroiden") for t in _texts(at))                       # die Ergebnisse bleiben nach anderen Änderungen


def test_playground_draws_until_a_counterexample_appears():
    at = _app()
    first = next(d for d in range(1, 30) if ev.play_view(d)["found"])
    for _ in range(first):
        at.button(key="play_draw").click().run()
        assert not at.exception
    assert any(f"Nach **{first}** Ziehungen" in t and "kein Matroid" in t for t in _texts(at))
    at.button(key="play_reset").click().run()
    assert not at.exception and any(t.startswith("Noch nichts gezogen.") for t in _texts(at))


def test_permalink_loads_valid_values_and_ignores_invalid_choices():
    at = _app(dict(kind="stable", n="9", seed="5", info="verrauscht", objective="abdeckung", budget="1000"))
    sb = at.sidebar
    assert sb.selectbox(key="kind_select").value == "stable" and sb.slider(key="n_slider").value == 9 and sb.number_input(key="seed_input").value == 5
    assert sb.selectbox(key="info_select").value == "verrauscht" and sb.selectbox(key="objective_select").value == "abdeckung" and int(sb.select_slider(key="budget_slider").value) == 1000
    bad = _app(dict(kind="nichts", n="99", seed="-4", info="vielleicht", objective="x", budget="7"))
    b = bad.sidebar
    assert b.selectbox(key="kind_select").value == "graphic" and b.slider(key="n_slider").value == C.N_MAX and b.number_input(key="seed_input").value == 0
    assert b.selectbox(key="info_select").value == "bekannt" and b.selectbox(key="objective_select").value == "summe" and int(b.select_slider(key="budget_slider").value) == C.DEFAULT_BUDGET


def test_address_line_mirrors_the_settings():
    at = _app(dict(kind="bimatch"))
    assert str(at.query_params["kind"]) in ("bimatch", "['bimatch']")


def test_pdf_button_makes_a_download():
    at = _app()
    at.button(key="pdf_make").click().run()
    assert not at.exception and "pdf_made" in at.session_state and at.session_state["pdf_made"][1][:4] == b"%PDF"


def test_pdf_builds_for_every_kind_and_combination():
    for kind in C.KINDS:
        assert build_pdf(ev.Settings(kind=kind, n=8))[:4] == b"%PDF", kind
    assert build_pdf(ev.Settings(kind="stable", seed=11, info="verrauscht", objective="paarbonus"))[:4] == b"%PDF"
