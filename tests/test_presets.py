"""Presets: Vollständigkeit, gültige Werte, Standard-Preset = Standardeinstellungen, und jedes Preset zeigt den Effekt, den sein Hilfetext verspricht."""

import mvw_constants as C
import mvw_evaluation as ev
import mvw_presets as P


def _view(name, **over):
    s = ev.Settings(**{**C.PRESETS[name], **over})
    return s, ev.run_view(s)


def test_every_preset_has_help_and_all_keys():
    assert set(C.PRESETS) == set(C.PRESET_HELP)
    for name, preset in C.PRESETS.items():
        assert set(preset) == set(P.PRESET_KEYS), name
        assert C.PRESET_HELP[name] and "TODO" not in C.PRESET_HELP[name] and "Gerüst" not in C.PRESET_HELP[name]


def test_preset_values_are_inside_the_bounds_and_choices():
    for p in C.PRESETS.values():
        assert p["kind"] in C.KINDS and C.N_MIN <= p["n"] <= C.N_MAX and 0 <= p["seed"] <= C.SEED_MAX and p["info"] in C.INFOS and p["objective"] in C.OBJECTIVES and p["budget"] in C.BUDGETS


def test_default_preset_equals_the_default_settings():
    assert ev.Settings(**C.PRESETS["Standardfall (Voreinstellung)"]) == ev.Settings()
    d = ev.Settings()
    keys = ("kind_select", "n_slider", "seed_input", "info_select", "objective_select", "budget_slider")
    assert [P.SETTING_SPECS[key].default for key in keys] == [d.kind, d.n, d.seed, d.info, d.objective, d.budget]


def test_setting_specs_cover_every_preset_key_and_have_valid_defaults():
    assert set(P.PRESET_KEYS.values()) == set(P.SETTING_SPECS)
    for spec in P.SETTING_SPECS.values():
        assert spec.choices is None or (spec.default in spec.choices and spec.lo in spec.choices and spec.hi in spec.choices)


def test_the_standard_preset_shows_a_passed_test_on_a_real_matroid():
    s, v = _view("Standardfall (Voreinstellung)")
    assert not v["found"] and v["truth"] and v["calls"] == 311 and v["g_val"] == v["o_val"] == 108
    assert "311 Orakelaufrufen" in C.PRESET_HELP["Standardfall (Voreinstellung)"] and "108" in C.PRESET_HELP["Standardfall (Voreinstellung)"]


def test_the_intersection_presets_find_a_counterexample_and_have_a_decomposition():
    for name, calls, g, o in (("Regenbogen-Wald", 23, 62, 66), ("Zuordnung", 153, 44, 51)):
        s, v = _view(name)
        assert v["found"] and v["cert_ok"] and v["fam"].parts is not None and v["path"] == "schnitt" and (v["calls"], v["g_val"], v["o_val"]) == (calls, g, o)
        assert f"{calls} Aufrufen" in C.PRESET_HELP[name] and f"{g} von {o}" in C.PRESET_HELP[name]


def test_the_other_presets_find_a_counterexample_without_a_decomposition():
    for name, calls, g, o in (("Konflikte", 252, 98, 133), ("Budget", 272, 51, 92)):
        s, v = _view(name)
        assert v["found"] and v["cert_ok"] and v["fam"].parts is None and v["path"] == "sonst" and (v["calls"], v["g_val"], v["o_val"]) == (calls, g, o)
        assert f"{calls} Aufrufen" in C.PRESET_HELP[name] and f"{g} von {o}" in C.PRESET_HELP[name]
    assert _view("Budget")[1]["g_val"] / _view("Budget")[1]["o_val"] < 0.56


def test_the_silent_error_preset_passes_the_test_but_is_no_matroid():
    s, v = _view("Stiller Fehler")
    assert not v["found"] and not v["truth"] and (v["calls"], v["g_val"], v["o_val"]) == (319, 81, 106)
    s2, v2 = _view("Stiller Fehler", budget=1000)
    assert v2["found"] and v2["calls"] == 652 and "652 Aufrufen" in C.PRESET_HELP["Stiller Fehler"] and "Budget 1 000" in C.PRESET_HELP["Stiller Fehler"]


def test_presets_differ_pairwise():
    assert len({tuple(sorted(p.items())) for p in C.PRESETS.values()}) == len(C.PRESETS)
