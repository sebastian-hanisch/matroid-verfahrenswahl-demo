"""Verdikte (reine Funktionen in mvw_evaluation.py) an festen Eingaben: jeder Zweig, jede Zahl im Text (DEMO-PLAYBOOK §4). Alles ist deterministisch (keine Löser)."""

import mvw_constants as C
import mvw_evaluation as ev


def S(name, **over):
    return ev.Settings(**{**C.PRESETS[name], **over})


def test_verdict_for_a_matroid_that_passes_the_test():
    s = S("Standardfall (Voreinstellung)")
    kind, text = ev.verdict_run(s, ev.run_view(s))
    assert kind == "info" and text == (
        "Wald mit 10 Leitungen: Der gezogene Test fand in **311** Orakelaufrufen kein Gegenbeispiel; die Familie wird als Matroid behandelt. Das stimmt: Die vollständige Prüfung (1 024 Aufrufe, statt 10 für Greedy selbst) bestätigt das Matroid. "
        "Greedy erreicht 108, das Optimum. Empfehlung: **Greedy (Stück 1 und 5)**.")


def test_verdict_for_a_counterexample_with_known_decomposition():
    s = S("Regenbogen-Wald")
    kind, text = ev.verdict_run(s, ev.run_view(s))
    assert kind == "info" and text == (
        "Regenbogen-Wald mit 10 Leitungen: Der gezogene Test fand nach **23** Orakelaufrufen ein Gegenbeispiel (A = {4, 5, 9}, B = {4, 6, 7, 10}: beide zulässig, |A| < |B|, aber keine Leitung aus B ∖ A passt zu A), also **kein Matroid**. "
        "Greedy erreicht 62 von 66 (0,939 des Optimums). Empfehlung: **Schnittverfahren (Stück 7 und 8)**. Der Wert des Schnittverfahrens ist hier das Optimum aus der Aufzählung (Platzhalter).")


def test_verdict_for_a_counterexample_without_decomposition():
    s = S("Konflikte")
    kind, text = ev.verdict_run(s, ev.run_view(s))
    assert kind == "info" and "nach **252** Orakelaufrufen ein Gegenbeispiel" in text and "Greedy erreicht 98 von 133 (0,737 des Optimums)" in text
    assert text.endswith("Empfehlung: **Näherung oder ganzzahliges Programm (Stück 2, 12)**.") and "Platzhalter" not in text


def test_verdict_for_a_silent_error_warns():
    s = S("Stiller Fehler")
    kind, text = ev.verdict_run(s, ev.run_view(s))
    assert kind == "warning" and "**stiller Fehler**" in text and "Greedy erreicht 81 von 106 (0,764 des Optimums)" in text and "in **319** Orakelaufrufen kein Gegenbeispiel" in text
    s2 = S("Stiller Fehler", budget=1000)                               # mit größerem Budget wird das Gegenbeispiel gefunden
    k2, t2 = ev.verdict_run(s2, ev.run_view(s2))
    assert k2 == "info" and "nach **652** Orakelaufrufen ein Gegenbeispiel" in t2


def test_objective_branches():
    s = S("Standardfall (Voreinstellung)", objective="abdeckung")
    kind, text = ev.verdict_run(s, ev.run_view(s))
    v = ev.run_view(s)
    assert kind == "info" and v["how"] == "Greedy auf den Zuwachs (Stück 11)" and "Die Zielfunktion bestand den Test auf Submodularität (300 Aufrufe)." in text and v["g_val"] <= v["o_val"]
    s = S("Standardfall (Voreinstellung)", objective="paarbonus")
    v = ev.run_view(s)
    kind, text = ev.verdict_run(s, v)
    assert v["sub_found"] and not v["sub_truth"] and kind == "warning" and "fiel im Test auf Submodularität nach" in text and "Die Garantie von Greedy gilt dafür nicht." in text
    s = S("Konflikte", objective="abdeckung")
    v = ev.run_view(s)
    assert v["found"] and v["how"] == "Greedy auf den Zuwachs als Start, danach lokale Suche (Stück 12)"


def test_information_branches():
    s = S("Standardfall (Voreinstellung)", info="nacheinander")
    v = ev.run_view(s)
    assert v["how"] == "Stichprobenregel (Stück 13)" and "Informationslage (Angebote kommen nacheinander (online)) ist Wissen über die Aufgabe" in ev.verdict_run(s, v)[1]
    s = S("Standardfall (Voreinstellung)", info="verrauscht")
    assert ev.run_view(s)["how"] == "Optimistisches Greedy (Stück 14)"
    s = S("Konflikte", info="nacheinander")
    assert ev.run_view(s)["how"].endswith("die Regeln aus Stück 13 sind nur für Matroide gemessen")
    s = S("Konflikte", info="verrauscht")
    assert ev.run_view(s)["how"].endswith("die Regeln aus Stück 14 sind nur für Matroide gemessen")


def test_step_rows_and_element_rows():
    s = S("Zuordnung")
    v = ev.run_view(s)
    rows = ev.step_rows(v)
    assert [r["Frage"] for r in rows] == ["Wie kommen die Angebote und die Nutzen?", "Ist die Zielfunktion eine Summe von Gewichten?", "Ist die Familie ein Matroid?", "Ist die Familie ein Schnitt zweier bekannter Matroide?"]
    assert rows[2]["Orakelaufrufe"] == "153" and rows[2]["Antwort"] == "Gegenbeispiel gefunden: kein Matroid" and rows[3]["Folge"] == "Schnittverfahren (Stück 7 und 8)" and rows[0]["Orakelaufrufe"] == "0"
    el = ev.element_rows(v)
    assert len(el) == 10 and {"Leitung", "Beschreibung", "Gewicht", "Greedy", "Optimum"} == set(el[0]) and sum(1 for r in el if r["Greedy"]) == 3 and sum(1 for r in el if r["Optimum"]) == 3
    v2 = ev.run_view(S("Standardfall (Voreinstellung)", objective="abdeckung"))
    assert "Gewicht" not in ev.element_rows(v2)[0] and ev.step_rows(v2)[1]["Art"] == "Test (gezogen)"
    assert len(ev.step_rows(ev.run_view(S("Standardfall (Voreinstellung)")))) == 3


def test_run_verdict_errors_on_inconsistent_data():
    s = S("Regenbogen-Wald")
    v = ev.run_view(s)
    assert ev.verdict_run(s, {**v, "truth": True})[0] == "error"
    assert ev.verdict_run(s, {**v, "cert_ok": False})[0] == "error"
    assert ev.verdict_run(s, {**v, "g_val": v["o_val"] + 1})[0] == "error"


def test_experiment_verdicts_on_handmade_data():
    rows = [{"n": n, "kind": "bimatch", "size_found": 28, "size_median": 20.0, "ex_found": 30, "ex_median": 100.0, "none": 0} for n in (8, 10, 12, 14)]
    res1 = {"rows": rows, "count": 30, "full": {10: 1024, 20: 1048576, 30: 1073741824}}
    kind, text = ev.verdict_ex1(res1)
    assert kind == "info" and "im Median nach **20 bis 20** Orakelaufrufen, der Austauschtest nach **100 bis 100**" in text and "**0** von 120 Instanzen unentdeckt" in text and "**1 073 741 824** bei n = 30" in text
    assert ev.verdict_ex1({**res1, "rows": [{**rows[0], "ex_found": 31}]})[0] == "error"
    assert ev.ex1_table(res1)[0] == {"n": 8, "Familie": "Zuordnung", "Größentest gefunden": "28 von 30", "Median Aufrufe (Größe)": "20", "Austauschtest gefunden": "30 von 30", "Median Aufrufe (Austausch)": "100", "von beiden nicht gefunden": 0}

    b = C.E_BUDGETS
    res2 = {"detect": {(k, x): 1 for k in C.NON_MATROID_KINDS for x in b}, "nonm": {k: 2 for k in C.NON_MATROID_KINDS}, "avg": {k: 12.34 for k in C.NON_MATROID_KINDS}, "false_alarm": 0, "n_matroids": 300,
            "passed": dict(zip(b, (50, 40, 30, 20, 10))), "worst": dict(zip(b, (0.6, 0.65, 0.7, 0.8, None))), "loss": dict(zip(b, (0.04, 0.03, 0.02, 0.01, 0.0))), "total": 298}
    kind, text = ev.verdict_ex2(res2)
    assert kind == "info" and "**50 / 40 / 30 / 20 / 10**" in text and "**4,0 % / 3,0 % / 2,0 % / 1,0 % / 0,0 %**" in text and "**0,6**" not in text and "**0,600**" in text and "**0** von 300" in text
    assert ev.verdict_ex2({**res2, "false_alarm": 1})[0] == "error" and ev.verdict_ex2({**res2, "passed": dict(zip(b, (1, 2, 3, 4, 5)))})[0] == "error"
    assert ev.ex2_table(res2)[0]["Aufrufe bis Fund (Mittel)"] == "12,3" and ev.ex2_loss_table(res2)[4]["schlechtester Quotient"] == "–" and ev.ex2_loss_table(res2)[0]["bestehen den Test"] == "50 von 298"

    res3 = {"rows": [{"budget": 100, "rule": 0.0135, "wrong": 210}, {"budget": 300, "rule": 0.0053, "wrong": 86}], "greedy": 0.0202, "total": 600}
    kind, text = ev.verdict_ex3(res3)
    assert kind == "info" and "„immer Greedy“ im Mittel **2,02 %**" in text and "**1,35 % / 0,53 %**" in text and "(falsch durchgelassen: 210 / 86)" in text
    assert ev.verdict_ex3({**res3, "greedy": 0.001})[0] == "error" and ev.ex3_table(res3)[1] == {"Verfahren": "erst testen (B = 100), dann wählen", "mittlerer Verlust": "1,35 %", "falsch durchgelassen": "210 von 600"}

    sb = C.E_SUB_BUDGETS
    cells = lambda x: {b: x for b in sb}
    rows4 = [{"kind": k, "violated": v, "cells": cells(v), "avg": 5.0 if v else None, "false_alarm": 0} for k, v in (("abdeckung", 0), ("budget", 0), ("paarbonus", 60), ("einpaar", 49), ("quadrat", 60), ("zufall", 60))]
    res4 = {"rows": rows4, "count": 60}
    kind, text = ev.verdict_ex4(res4)
    assert kind == "info" and "nach **5** Aufrufen auf" in text and "**49 von 49** bei 400" in text
    assert ev.verdict_ex4({"rows": [{**rows4[0], "violated": 1}] + rows4[1:], "count": 60})[0] == "error" and ev.ex4_table(res4)[0]["B = 20"] == "–"

    rows5 = [{"kind": k, "matroids": 60 if k in C.MATROID_KINDS else 0, "equal": 60 if k in C.MATROID_KINDS else 40, "mean": 1.0 if k in C.MATROID_KINDS else 0.95, "min": 1.0 if k in C.MATROID_KINDS else 0.7} for k in C.SERIES_KINDS]
    res5 = {"rows": rows5, "cert_total": 289, "cert_ok": 289, "cert_valid": 289, "inter_min": 0.733, "count": 60}
    kind, text = ev.verdict_ex5(res5)
    assert kind == "info" and "(**60 von 60** je Familie)" in text and "nie unter **0,733**" in text and "**289 von 289**" in text
    assert ev.verdict_ex5({**res5, "cert_ok": 288})[0] == "error" and ev.verdict_ex5({**res5, "inter_min": 0.4})[0] == "error"


def test_play_verdict_branches():
    pv0 = ev.play_view(0)
    assert ev.verdict_play(pv0)[1].startswith("Noch nichts gezogen.") and pv0["rows"] == []
    seen = {}
    for d in range(1, 12):
        pv = ev.play_view(d)
        seen[d] = pv["found"]
    first = min(d for d, f in seen.items() if f)
    pv = ev.play_view(first)
    kind, text = ev.verdict_play(pv)
    assert kind == "info" and pv["cert_ok"] and "zwei maximale Mengen verschiedener Größe: A = {1} (Größe 1) und B = {2, 3} (Größe 2)" in text and "Greedy erreicht **3**, die Menge B hat **4**" in text
    if first > 1:
        assert "sind alle maximalen Mengen gleich groß" in ev.verdict_play(ev.play_view(first - 1))[1]
    assert ev.verdict_play({**pv, "cert_ok": False})[0] == "error"
