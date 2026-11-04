"""Randfälle, an denen Kernroutinen erfahrungsgemäß brechen (DEMO-PLAYBOOK §12): kleinste Größen, Budgetgrenzen, leere Auswahl, Reglerecken, Spielwiese."""

import random

import mvw_algorithm as A
import mvw_constants as C
import mvw_evaluation as ev
import mvw_scenario as S


def test_empty_and_single_element_families():
    t = A.table_of(lambda m: A.pc(m) <= 1, 1)
    assert t == [True, True] and A.is_matroid_full(t, 1) and A.greedy(t, [5], 1) == (5, 1, [0]) and A.opt(t, [5], 1) == (5, 1)
    assert A.table_of(lambda m: m == 0, 3) == [True] + [False] * 7
    nothing = A.table_of(lambda m: m == 0, 3)                          # nur die leere Menge zulässig
    assert A.is_matroid_full(nothing, 3) and A.greedy(nothing, [1, 2, 3], 3) == (0, 0, []) and A.opt(nothing, [1, 2, 3], 3) == (0, 0)
    assert not A.sampled_test(nothing, random.Random(0), 100, 3)[0]


def test_the_smallest_budget_and_the_largest_size_work_for_every_kind():
    for kind in C.KINDS:
        for n, budget in ((C.N_MIN, C.BUDGETS[0]), (C.N_MAX, C.BUDGETS[-1])):
            s = ev.Settings(kind=kind, n=n, seed=0, budget=budget)
            v = ev.run_view(s)
            kind_v, text = ev.verdict_run(s, v)
            assert kind_v in ("info", "warning") and text and v["g_val"] <= v["o_val"] and v["calls"] <= budget + 3 * n
            assert (not v["found"]) or v["cert_ok"]
            if kind in C.MATROID_KINDS:
                assert not v["found"] and v["truth"] and v["g_val"] == v["o_val"]


def test_every_objective_and_information_combination_runs():
    for objective in C.OBJECTIVES:
        for info in C.INFOS:
            for kind in ("graphic", "bimatch", "stable"):
                s = ev.Settings(kind=kind, seed=2, info=info, objective=objective)
                v = ev.run_view(s)
                assert ev.verdict_run(s, v)[0] in ("info", "warning") and v["value"] <= v["o_val"]
                assert (v["sub_found"] is None) == (objective == "summe")
                assert len(ev.step_rows(v)) == (4 if v["found"] else 3)


def test_the_value_of_the_recommendation_follows_the_path():
    s = ev.Settings(kind="bimatch", seed=7)
    v = ev.run_view(s)
    assert v["path"] == "schnitt" and v["value"] == v["o_val"] and v["g_val"] < v["o_val"]
    s = ev.Settings(kind="graphic", seed=7)
    v = ev.run_view(s)
    assert v["path"] == "greedy" and v["value"] == v["g_val"] == v["o_val"]


def test_play_view_edges():
    pv = ev.play_view(0)
    assert pv["sets"] == [] and not pv["found"] and pv["calls"] == 0 and pv["w"] is None
    assert ev.play_view(1)["calls"] == 3 and ev.play_view(5)["calls"] == 15
    big = ev.play_view(40)
    assert big["found"] and big["small"] == 0b001 and big["large"] == 0b110 and (big["g"], big["b_val"]) == (3, 4)


def test_hand_family_matches_the_text():
    fam = S.hand_family()
    assert fam.n == 3 and fam.w == [1, 1, 1] and fam.details[0] == "oben 1 – unten 1" and fam.parts is not None


def test_series_data_is_shared_and_complete():
    sd = ev.series_data()
    assert set(sd["data"]) == set(C.SERIES_KINDS) and all(len(sd["data"][k]) == C.E_PER_KIND for k in C.SERIES_KINDS)
    assert sum(sum(sd["truth"][k]) for k in C.MATROID_KINDS) == 5 * C.E_PER_KIND


def test_the_series_orders_are_consistent():
    assert set(C.SERIES_KINDS) == set(C.KINDS) and C.KINDS[0] == "graphic" and C.KINDS[-1] not in {p["kind"] for p in C.PRESETS.values()}
    assert C.NON_MATROID_KINDS == C.INTERSECTION_KINDS + C.OTHER_KINDS
