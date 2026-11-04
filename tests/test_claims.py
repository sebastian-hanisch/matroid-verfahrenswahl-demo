"""Jede Zahl der README („Befunde“) wird hier mit den Funktionen der App nachgerechnet (DEMO-PLAYBOOK §4)."""

from pathlib import Path

import mvw_algorithm as A
import mvw_constants as C
import mvw_evaluation as ev

README = (Path(__file__).resolve().parent.parent / "README.md").read_text(encoding="utf-8")


def test_the_preset_table():
    rows = {"Standardfall (Wald, Seed 3)": ("Standardfall (Voreinstellung)", "Matroid"), "Regenbogen-Wald (Seed 10)": ("Regenbogen-Wald", "Schnitt"), "Zuordnung (Seed 7)": ("Zuordnung", "Schnitt"),
            "Konflikte (Seed 11)": ("Konflikte", "kein Schnitt"), "Budget (Seed 3)": ("Budget", "kein Schnitt"), "Stiller Fehler (Zuordnung, Seed 5)": ("Stiller Fehler", "Schnitt")}
    for label, (preset, typ) in rows.items():
        s = ev.Settings(**C.PRESETS[preset])
        v = ev.run_view(s)
        assert s.budget == 300
        assert (v["fam"].parts is not None) == (typ == "Schnitt") and (v["truth"] == (typ == "Matroid"))
        row = f"| {label} | {typ} | {v['calls']} | {'ja' if v['found'] else 'nein'} | {v['g_val']} | {v['o_val']} |"
        assert row in README, row


def test_experiment_1():
    res = ev.ex1_series()
    rows = res["rows"]
    sm = [r["size_median"] for r in rows if r["size_median"] is not None]
    em = [r["ex_median"] for r in rows if r["ex_median"] is not None]
    assert (round(min(sm)), round(max(sm)), round(min(em)), round(max(em)), sum(r["none"] for r in rows), len(rows) * res["count"]) == (16, 182, 74, 355, 6, 600)
    assert res["full"] == {10: 1024, 20: 1048576, 30: 1073741824} and [2 ** n for n in (10, 20, 30)] == [1024, 1048576, 1073741824]
    for text in ("Größentest findet Gegenbeispiele im Median nach **16 bis 182** Orakelaufrufen, der Austauschtest nach **74 bis 355**; beide Tests zusammen ließen **6** von 600 Instanzen unentdeckt.",
                 "Vollständige Prüfung: **1 024** Aufrufe bei n = 10, **1 048 576** bei n = 20, **1 073 741 824** bei n = 30."):
        assert text in README, text


def test_experiment_2():
    res = ev.ex2_series()
    b = C.E_BUDGETS
    assert (res["total"], res["false_alarm"], res["n_matroids"]) == (298, 0, 300)
    assert [res["passed"][x] for x in b] == [275, 210, 86, 9, 1]
    assert [ev.prozent(res["loss"][x]) for x in b] == ["4,1 %", "3,9 %", "3,7 %", "1,5 %", "0,0 %"] and ev.quot(res["worst"][b[0]]) == "0,612"
    text = ("Von 298 Nicht-Matroiden bestehen den gezogenen Test bei Budget B = 30 / 100 / 300 / 1 000 / 3 000: **275 / 210 / 86 / 9 / 1**; mittlerer Greedy-Verlust der Durchgelassenen **4,1 % / 3,9 % / 3,7 % / 1,5 % / 0,0 %**; "
            "schlechtester Quotient bei B = 30 **0,612**. Falsch gemeldete Matroide: **0 von 300** bei B = 1 000.")
    assert text in README


def test_experiment_3():
    res = ev.ex3_series()
    assert ev.prozent2(res["greedy"]) == "2,02 %" and [ev.prozent2(r["rule"]) for r in res["rows"]] == ["1,35 %", "0,53 %", "0,02 %"] and [r["wrong"] for r in res["rows"]] == [210, 86, 9] and res["total"] == 600
    text = "Immer Greedy verliert im Mittel **2,02 %** des Optimums; die Regel „erst testen, dann wählen“ bei Budget 100 / 300 / 1 000 **1,35 % / 0,53 % / 0,02 %** (falsch durchgelassen **210 / 86 / 9**)."
    assert text in README


def test_experiment_4():
    res = ev.ex4_series()
    by = {r["kind"]: r for r in res["rows"]}
    b = C.E_SUB_BUDGETS
    assert (by["abdeckung"]["violated"], by["budget"]["violated"], sum(r["false_alarm"] for r in res["rows"])) == (0, 0, 0)
    assert [ev.num(round(by[k]["avg"], 1)) for k in ("paarbonus", "quadrat", "zufall", "einpaar")] == ["12,8", "4", "8,7", "237,1"]
    assert (by["einpaar"]["violated"], by["einpaar"]["cells"][b[3]], by["einpaar"]["cells"][b[4]]) == (49, 41, 49)
    text = ("Abdeckung und Budget-Abdeckung: **0 von 60** verletzt, **0** Fehlalarme. Abdeckung mit Paarbonus fällt im Mittel nach **12,8** Aufrufen auf, Quadrat der Größe nach **4**, Zufallstabelle nach **8,7**. "
            "Ein einziges Paar mit Bonus 1: **49 von 60** überhaupt verletzt; gefunden **41 von 49** bei 400, **49 von 49** bei 1 000 Aufrufen (Mittel **237,1**).")
    assert text in README and b[3] == 400 and b[4] == 1000


def test_experiment_5():
    res = ev.ex5_series()
    mins = {r["kind"]: ev.quot(r["min"]) for r in res["rows"]}
    assert mins == {"uniform": "1,000", "partition": "1,000", "graphic": "1,000", "binary": "1,000", "union2": "1,000", "bimatch": "0,796", "rainbow": "0,733", "stable": "0,714", "knapsack": "0,612", "gmatch": "0,667"}
    assert all(r["equal"] == 60 for r in res["rows"] if r["kind"] in C.MATROID_KINDS) and ev.quot(res["inter_min"]) == "0,733" and (res["cert_total"], res["cert_ok"], res["cert_valid"]) == (289, 289, 289)
    text = ("Bei allen fünf Matroid-Familien Greedy = Optimum **60 von 60**. Kleinste Quotienten: Zuordnung **0,796**, Regenbogen-Wald **0,733**, Konflikte **0,714**, Budget **0,612**, Paarung **0,667**; "
            "Schnitt zweier Matroide nie unter **0,733** (Schranke ½). Aus jedem der **289** gefundenen Gegenbeispiele (B = 1 000) entstehen Gewichte, bei denen Greedy scheitert: **289 von 289**.")
    assert text in README
    means = [r["mean"] for r in res["rows"] if r["kind"] in C.NON_MATROID_KINDS]
    assert (ev.quot(min(means)), ev.quot(max(means))) == ("0,929", "0,981")
    assert "Greedy erreicht dort im Mittel 0,929 bis 0,981 des Optimums, im schlechtesten Fall 0,612." in README


def test_the_union_family_claim_and_the_play_example():
    sd = ev.series_data()
    assert sum(1 for i, f in enumerate(sd["data"]["union2"]) if sd["truth"]["union2"][i] and sd["vals"]["union2"][i][0] == sd["vals"]["union2"][i][1]) == 60
    assert "Wald ∨ Wald hat bei **60 von 60** Instanzen Greedy = Optimum" in README
    pv = ev.play_view(40)
    assert A.greedy(pv["fam"].ind, pv["fam"].w, 3)[0] == 1 and A.opt(pv["fam"].ind, pv["fam"].w, 3)[0] == 2 and (pv["g"], pv["b_val"]) == (3, 4) and pv["w"] == [3, 2, 2]
    assert "Greedy nimmt Leitung 1 und erreicht **1**, das Optimum {2, 3} hat **2** (Quotient 0,5, scharf). Gegenbeispiel A = {1}, B = {2, 3}; Gewichte 3 / 2 / 2: Greedy **3**, B **4**." in README


def test_constants_named_in_the_readme():
    assert (C.E_N, C.E_PER_KIND, C.E_SEED, C.E_SKALA_NS, C.E_SKALA_COUNT, C.E_SKALA_CAP, C.E_SUB_COUNT, C.HOUSEHOLDS, C.WEIGHT_MAX) == (10, 60, 17, (8, 10, 12, 14), 30, 20000, 60, 40, 30)
    for text in ("Port 9357", "Präfix `mvw_`", "n = 8, 10, 12, 14; 30 Instanzen je Familie und n; Deckel 20 000 Aufrufe", "60 Instanzen je Familie, n = 10, Seed 17", "Abdeckung von 40 Haushalten (je Leitung 15 %)", "Gewichte ganzzahlig von 1 bis 30"):
        assert text in README, text
