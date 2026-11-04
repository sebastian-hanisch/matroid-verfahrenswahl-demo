"""Kennzahlen, Entscheidungsbaum, Experimente und Verdikte. Alle sichtbaren Zahlen kommen aus diesen Funktionen."""

from __future__ import annotations

import random
import statistics
import zlib
from dataclasses import dataclass
from functools import lru_cache

import mvw_algorithm as A
import mvw_constants as C
import mvw_scenario as S


def num(x: float) -> str:
    """Ganze Zahl ohne, sonst mit bis zu drei Nachkommastellen (Dezimalkomma, typografisches Minus)."""
    if abs(x - round(x)) < 1e-9:
        return str(int(round(x))).replace("-", "−")
    return f"{x:.3f}".rstrip("0").rstrip(".").replace(".", ",").replace("-", "−")


def zahl(n: int) -> str:
    """Ganze Zahl mit Leerzeichen als Tausendertrenner."""
    return f"{n:,}".replace(",", " ").replace("-", "−")


def quot(x: float) -> str:
    """Quotient mit drei Nachkommastellen (Dezimalkomma)."""
    return f"{x:.3f}".replace(".", ",")


def prozent(x: float) -> str:
    """Anteil als Prozent mit einer Nachkommastelle (Dezimalkomma)."""
    return f"{100 * x:.1f}".replace(".", ",") + " %"


def prozent2(x: float) -> str:
    return f"{100 * x:.2f}".replace(".", ",") + " %"


def von(a: int, b: int) -> str:
    return f"{zahl(a)} von {zahl(b)}"


def seed_of(*parts) -> int:
    return zlib.crc32("".join(str(p) for p in parts).encode())


@dataclass(frozen=True)
class Settings:
    kind: str = "graphic"
    n: int = C.DEFAULT_N
    seed: int = C.DEFAULT_SEED
    info: str = "bekannt"
    objective: str = "summe"
    budget: int = C.DEFAULT_BUDGET


# --- Familie und Weg durch den Baum -----------------------------------------------------------------------------------------------------------


@lru_cache(maxsize=24)
def family(kind: str, n: int, seed: int) -> S.Family:
    return S.make_family(kind, n, seed)


@lru_cache(maxsize=24)
def truth_matroid(kind: str, n: int, seed: int) -> bool:
    fam = family(kind, n, seed)
    return A.is_matroid_full(fam.ind, fam.n)


def mask_text(mask: int, n: int) -> str:
    items = [str(i + 1) for i in A.elems(mask, n)]
    return "{" + ", ".join(items) + "}" if items else "∅"


@lru_cache(maxsize=24)
def run_view(s: Settings) -> dict:
    fam = family(s.kind, s.n, s.seed)
    n, t = fam.n, fam.ind
    f = S.objective_table(s.objective, n, s.seed)
    rng = random.Random(seed_of(s.seed, s.kind, s.budget))
    found, calls, cert = A.sampled_test(t, rng, s.budget, n)
    truth = truth_matroid(s.kind, s.n, s.seed)
    if f is None:
        g_val, g_mask, g_picks = A.greedy(t, fam.w, n)
        o_val, o_mask = A.opt(t, fam.w, n)
    else:
        g_val, g_mask = A.greedy_f(t, f, n)
        o_val, o_mask = A.opt_f(t, f, n)
        g_picks = A.elems(g_mask, n)
    sub_found, sub_calls, sub_cert, sub_truth = None, 0, None, None
    if f is not None:
        sub_found, sub_calls, sub_cert = A.sub_sampled(f, random.Random(seed_of(s.seed, s.objective, s.budget)), s.budget, n)
        sub_truth = not A.sub_full(f, n)
    steps = []
    info_known = s.info == "bekannt"
    steps.append({"Frage": "Wie kommen die Angebote und die Nutzen?", "Art": "Wissen über die Aufgabe", "Antwort": C.INFO_NAMES[s.info], "Orakelaufrufe": 0,
                  "Folge": "weiter mit der Familie" if info_known else ("Stück 13 (Sekretär), falls die Familie ein Matroid ist" if s.info == "nacheinander" else "Stück 14 (Bandit), falls die Familie ein Matroid ist")})
    steps.append({"Frage": "Ist die Zielfunktion submodular?" if f is not None else "Ist die Zielfunktion eine Summe von Gewichten?", "Art": "Test (gezogen)" if f is not None else "Wissen über die Aufgabe",
                  "Antwort": ("Gegenbeispiel gefunden: nicht submodular" if sub_found else "kein Gegenbeispiel gefunden: als submodular behandelt") if f is not None else "ja: modular, Greedy-Gewichte gelten",
                  "Orakelaufrufe": sub_calls, "Folge": ("Garantie 1/2 (Matroid) oder 1 − 1/e entfällt (Stück 11)" if sub_found else "Stück 11: Garantie nachrechenbar") if f is not None else "Stück 1 und 5"})
    steps.append({"Frage": "Ist die Familie ein Matroid?", "Art": "Test (gezogen)", "Antwort": "Gegenbeispiel gefunden: kein Matroid" if found else "kein Gegenbeispiel gefunden: als Matroid behandelt",
                  "Orakelaufrufe": calls, "Folge": "weiter mit der Zerlegung" if found else "Greedy (Stück 1 und 5)"})
    if found:
        steps.append({"Frage": "Ist die Familie ein Schnitt zweier bekannter Matroide?", "Art": "Wissen über die Aufgabe", "Antwort": "ja, Zerlegung mitgeliefert" if fam.parts else "nein, keine Zerlegung bekannt",
                      "Orakelaufrufe": 0, "Folge": "Schnittverfahren (Stück 7 und 8)" if fam.parts else "Sonst: Näherung oder ganzzahliges Programm (Stück 2, 12)"})
    if found and fam.parts:
        path = "schnitt"
    elif found:
        path = "sonst"
    else:
        path = "greedy"
    if f is not None and found:
        value, how = g_val, "Greedy auf den Zuwachs als Start, danach lokale Suche (Stück 12)"
    elif path == "greedy":
        value, how = g_val, "Greedy (Stück 1 und 5)" if f is None else "Greedy auf den Zuwachs (Stück 11)"
    elif path == "schnitt":
        value, how = o_val, "Schnittverfahren (Stück 7 und 8)"
    else:
        value, how = o_val, "Näherung oder ganzzahliges Programm (Stück 2, 12)"
    if s.info == "nacheinander":
        how = "Stichprobenregel (Stück 13)" if not found else how + "; die Regeln aus Stück 13 sind nur für Matroide gemessen"
    elif s.info == "verrauscht":
        how = "Optimistisches Greedy (Stück 14)" if not found else how + "; die Regeln aus Stück 14 sind nur für Matroide gemessen"
    return {"fam": fam, "f": f, "found": found, "calls": calls, "cert": cert, "truth": truth, "path": path, "how": how, "value": value, "g_val": g_val, "g_mask": g_mask, "g_picks": g_picks,
            "o_val": o_val, "o_mask": o_mask, "sub_found": sub_found, "sub_calls": sub_calls, "sub_cert": sub_cert, "sub_truth": sub_truth, "steps": steps, "full_calls": 2 ** n,
            "cert_ok": bool(cert) and A.check_certificate(t, cert[0], cert[1], n)}


def step_rows(v: dict) -> list[dict]:
    return [{"Frage": r["Frage"], "Art": r["Art"], "Antwort": r["Antwort"], "Orakelaufrufe": zahl(r["Orakelaufrufe"]), "Folge": r["Folge"]} for r in v["steps"]]


def element_rows(v: dict) -> list[dict]:
    fam = v["fam"]
    rows = []
    for i in range(fam.n):
        row = {"Leitung": i + 1, "Beschreibung": fam.details[i]}
        if v["f"] is None:
            row["Gewicht"] = fam.w[i]
        row["Greedy"] = "ja" if v["g_mask"] >> i & 1 else ""
        row["Optimum"] = "ja" if v["o_mask"] >> i & 1 else ""
        rows.append(row)
    return rows


def verdict_run(s: Settings, v: dict) -> tuple[str, str]:
    fam = v["fam"]
    n = fam.n
    name = C.KIND_SHORT[s.kind]
    ratio = v["g_val"] / v["o_val"] if v["o_val"] else 1.0
    if v["truth"] and v["found"]:
        return "error", f"Widerspruch: Die Familie ist ein Matroid, der Test meldet ein Gegenbeispiel ({v['cert']})."
    if v["found"] and not v["cert_ok"]:
        return "error", "Widerspruch: Das gemeldete Gegenbeispiel besteht die Nachprüfung nicht."
    if v["g_val"] > v["o_val"] or v["value"] > v["o_val"]:
        return "error", "Widerspruch: Der Greedy-Wert liegt über dem Optimum."
    a, b = v["cert"] if v["cert"] else (0, 0)
    intro = f"{name} mit {n} Leitungen: "
    if v["found"]:
        text = (f"{intro}Der gezogene Test fand nach **{zahl(v['calls'])}** Orakelaufrufen ein Gegenbeispiel (A = {mask_text(a, n)}, B = {mask_text(b, n)}: beide zulässig, |A| < |B|, aber keine Leitung aus B ∖ A passt zu A), "
                f"also **kein Matroid**. ")
        if s.objective == "summe":
            text += f"Greedy erreicht {zahl(v['g_val'])} von {zahl(v['o_val'])} ({quot(ratio)} des Optimums). "
        else:
            text += f"Greedy auf den Zuwachs erreicht {zahl(v['g_val'])} von {zahl(v['o_val'])} Haushalten ({quot(ratio)}). "
        text += f"Empfehlung: **{v['how']}**."
        if v["path"] == "schnitt" and s.objective == "summe":
            text += " Der Wert des Schnittverfahrens ist hier das Optimum aus der Aufzählung (Platzhalter)."
        kind = "info"
    else:
        text = f"{intro}Der gezogene Test fand in **{zahl(v['calls'])}** Orakelaufrufen kein Gegenbeispiel; die Familie wird als Matroid behandelt. "
        if v["truth"]:
            text += f"Das stimmt: Die vollständige Prüfung ({zahl(v['full_calls'])} Aufrufe, statt {zahl(n)} für Greedy selbst) bestätigt das Matroid. Greedy erreicht {zahl(v['g_val'])}, das Optimum. "
            kind = "info"
        else:
            text += f"Das ist ein **stiller Fehler**: Die vollständige Prüfung zeigt, dass es kein Matroid ist. Greedy erreicht {zahl(v['g_val'])} von {zahl(v['o_val'])} ({quot(ratio)} des Optimums). "
            kind = "warning"
        text += f"Empfehlung: **{v['how']}**."
    if v["sub_found"] is not None:
        if v["sub_found"]:
            text += f" Die Zielfunktion fiel im Test auf Submodularität nach {zahl(v['sub_calls'])} Aufrufen durch: Die Garantie von Greedy gilt dafür nicht."
            if kind == "info":
                kind = "warning"
        else:
            text += f" Die Zielfunktion bestand den Test auf Submodularität ({zahl(v['sub_calls'])} Aufrufe)" + ("." if v["sub_truth"] else ", ist aber nicht submodular (stiller Fehler).")
            if not v["sub_truth"]:
                kind = "warning"
    if s.info != "bekannt":
        text += f" Die Informationslage ({C.INFO_NAMES[s.info]}) ist Wissen über die Aufgabe und steht vor der Familienfrage."
    return kind, text


# --- Messreihen -------------------------------------------------------------------------------------------------------------------------------


@lru_cache(maxsize=1)
def series_data() -> dict:
    """60 Instanzen je Familie (Seed 17, n = 10) mit Wahrheit, Greedy- und Optimum-Werten; die Grundlage der Experimente 2, 3 und 5."""
    rng = random.Random(C.E_SEED)
    data = {k: [S.gen(k, rng, C.E_N) for _ in range(C.E_PER_KIND)] for k in C.SERIES_KINDS}
    truth = {k: [A.is_matroid_full(f.ind, C.E_N) for f in data[k]] for k in C.SERIES_KINDS}
    vals = {k: [(A.greedy(f.ind, f.w, C.E_N)[0], A.opt(f.ind, f.w, C.E_N)[0]) for f in data[k]] for k in C.SERIES_KINDS}
    return {"data": data, "truth": truth, "vals": vals}


@lru_cache(maxsize=None)
def found_at(kind: str, i: int, budget: int) -> tuple[bool, int, tuple | None]:
    sd = series_data()
    f = sd["data"][kind][i]
    return A.sampled_test(f.ind, random.Random(seed_of(kind, budget)), budget, C.E_N)


def ex1_series() -> dict:
    """Prüfkosten gegen n: Größentest und Austauschtest, 30 Instanzen je Familie und n, Deckel 20 000 Aufrufe."""
    rows = []
    for n in C.E_SKALA_NS:
        rng = random.Random(C.E_SKALA_SEED + n)
        for k in C.NON_MATROID_KINDS:
            sz, ex, sc, ec, none = 0, 0, [], [], 0
            for i in range(C.E_SKALA_COUNT):
                fam = S.gen(k, rng, n)
                sd = seed_of(k, n, i)
                a, ca = A.size_test(fam.ind, random.Random(sd), C.E_SKALA_CAP, n)
                b, cb, _ = A.sampled_test(fam.ind, random.Random(sd), C.E_SKALA_CAP, n)
                sz += a
                ex += b
                if a:
                    sc.append(ca)
                if b:
                    ec.append(cb)
                none += (not a and not b)
            rows.append({"n": n, "kind": k, "size_found": sz, "size_median": statistics.median(sc) if sc else None, "ex_found": ex, "ex_median": statistics.median(ec) if ec else None, "none": none})
    return {"rows": rows, "count": C.E_SKALA_COUNT, "full": {n: 2 ** n for n in C.FULL_CHECK_NS}}


def ex1_table(res) -> list[dict]:
    out = []
    for r in res["rows"]:
        out.append({"n": r["n"], "Familie": C.KIND_SHORT[r["kind"]], "Größentest gefunden": f"{r['size_found']} von {res['count']}", "Median Aufrufe (Größe)": "–" if r["size_median"] is None else zahl(round(r["size_median"])),
                    "Austauschtest gefunden": f"{r['ex_found']} von {res['count']}", "Median Aufrufe (Austausch)": "–" if r["ex_median"] is None else zahl(round(r["ex_median"])), "von beiden nicht gefunden": r["none"]})
    return out


def _range_text(vals, fmt=lambda x: zahl(round(x))):
    return f"{fmt(min(vals))} bis {fmt(max(vals))}"


def verdict_ex1(res) -> tuple[str, str]:
    rows = res["rows"]
    count = res["count"]
    if any(r["size_found"] > count or r["ex_found"] > count for r in rows):
        return "error", "Widerspruch in der Messreihe."
    sm = [r["size_median"] for r in rows if r["size_median"] is not None]
    em = [r["ex_median"] for r in rows if r["ex_median"] is not None]
    both = sum(r["none"] for r in rows)
    full = res["full"]
    return "info", (f"Ein Gegenbeispiel zum Matroid findet der Größentest im Median nach **{_range_text(sm)}** Orakelaufrufen, der Austauschtest nach **{_range_text(em)}** (n = {rows[0]['n']} bis {rows[-1]['n']}, "
                    f"{count} Instanzen je Familie und n, Deckel {zahl(C.E_SKALA_CAP)} Aufrufe). Beide Tests zusammen ließen **{both}** von {zahl(len(rows) * count)} Instanzen unentdeckt (darunter können zufällige Matroide sein). "
                    f"Die Bestätigung gibt es nur vollständig: 2^n Aufrufe, das sind **{zahl(full[10])}** bei n = 10, **{zahl(full[20])}** bei n = 20 und **{zahl(full[30])}** bei n = 30; Greedy selbst braucht n.")


def ex2_series() -> dict:
    """Gezogener Austauschtest gegen Budget: gefundene Nicht-Matroide je Familie, stille Fehler und ihr Greedy-Verlust, Soundness bei den Matroiden."""
    sd = series_data()
    detect, nonm, avg = {}, {}, {}
    for k in C.NON_MATROID_KINDS:
        nonm[k] = sum(1 for m in sd["truth"][k] if not m)
        calls_found = []
        for b in C.E_BUDGETS:
            found = 0
            for i, m in enumerate(sd["truth"][k]):
                if m:
                    continue
                fd, calls, _ = found_at(k, i, b)
                found += fd
                if b == C.E_BUDGETS[-1] and fd:
                    calls_found.append(calls)
            detect[(k, b)] = found
        avg[k] = sum(calls_found) / len(calls_found) if calls_found else None
    false_alarm, n_matroids = 0, 0
    for k in C.MATROID_KINDS:
        for i, m in enumerate(sd["truth"][k]):
            if m:
                n_matroids += 1
                fd, _, _ = A.sampled_test(sd["data"][k][i].ind, random.Random(5), 1000, C.E_N)
                false_alarm += fd
    passed, worst, loss = {}, {}, {}
    total = sum(nonm.values())
    for b in C.E_BUDGETS:
        q = []
        for k in C.NON_MATROID_KINDS:
            for i, m in enumerate(sd["truth"][k]):
                if m:
                    continue
                fd, _, _ = found_at(k, i, b)
                if not fd:
                    g, o = sd["vals"][k][i]
                    q.append(g / o)
        passed[b] = len(q)
        worst[b] = min(q) if q else None
        loss[b] = (1 - sum(q) / len(q)) if q else 0.0
    return {"detect": detect, "nonm": nonm, "avg": avg, "false_alarm": false_alarm, "n_matroids": n_matroids, "passed": passed, "worst": worst, "loss": loss, "total": total}


def ex2_table(res) -> list[dict]:
    rows = []
    for k in C.NON_MATROID_KINDS:
        row = {"Familie": C.KIND_SHORT[k]}
        for b in C.E_BUDGETS:
            row[f"B = {zahl(b)}"] = f"{res['detect'][(k, b)]} von {res['nonm'][k]}"
        row["Aufrufe bis Fund (Mittel)"] = "–" if res["avg"][k] is None else num(round(res["avg"][k], 1))
        rows.append(row)
    return rows


def ex2_loss_table(res) -> list[dict]:
    return [{"Budget B": zahl(b), "bestehen den Test": f"{res['passed'][b]} von {res['total']}", "schlechtester Quotient": "–" if res["worst"][b] is None else quot(res["worst"][b]), "mittlerer Verlust": prozent(res["loss"][b])} for b in C.E_BUDGETS]


def verdict_ex2(res) -> tuple[str, str]:
    p, w, l = res["passed"], res["worst"], res["loss"]
    bs = C.E_BUDGETS
    if res["false_alarm"] or any(p[bs[i]] < p[bs[i + 1]] for i in range(len(bs) - 1)):
        return "error", "Widerspruch in der Messreihe: ein Matroid wurde als Nicht-Matroid gemeldet oder ein größeres Budget ließ mehr Nicht-Matroide durch."
    return "info", (f"Von {res['total']} Nicht-Matroiden bestehen den gezogenen Test bei Budget B = {' / '.join(zahl(b) for b in bs)}: **{' / '.join(str(p[b]) for b in bs)}**. "
                    f"Ihr mittlerer Greedy-Verlust ist **{' / '.join(prozent(l[b]) for b in bs)}**; der schlechteste Quotient bei B = {zahl(bs[0])} ist **{quot(w[bs[0]])}**. "
                    f"Gezogene Tests melden nie ein Matroid fälschlich als Nicht-Matroid (**{res['false_alarm']}** von {res['n_matroids']} bei B = 1 000), aber sie lassen Nicht-Matroide durch.")


def ex3_series() -> dict:
    """Die Regel als Ganzes: Test mit Budget B, dann Greedy (nicht gefunden) oder exakt (gefunden), gegen immer Greedy."""
    sd = series_data()
    rows = []
    total = sum(len(sd["data"][k]) for k in C.SERIES_KINDS)
    loss_greedy = sum(1 - g / o for k in C.SERIES_KINDS for g, o in sd["vals"][k]) / total
    for b in C.E_RULE_BUDGETS:
        loss_rule, wrong = 0.0, 0
        for k in C.SERIES_KINDS:
            for i, (g, o) in enumerate(sd["vals"][k]):
                fd, _, _ = found_at(k, i, b)
                val = o if fd else g
                wrong += (not fd) and (not sd["truth"][k][i])
                loss_rule += 1 - val / o
        rows.append({"budget": b, "rule": loss_rule / total, "wrong": wrong})
    return {"rows": rows, "greedy": loss_greedy, "total": total}


def ex3_table(res) -> list[dict]:
    out = [{"Verfahren": "immer Greedy", "mittlerer Verlust": prozent2(res["greedy"]), "falsch durchgelassen": "–"}]
    for r in res["rows"]:
        out.append({"Verfahren": f"erst testen (B = {zahl(r['budget'])}), dann wählen", "mittlerer Verlust": prozent2(r["rule"]), "falsch durchgelassen": von(r["wrong"], res["total"])})
    return out


def verdict_ex3(res) -> tuple[str, str]:
    rows = res["rows"]
    if any(r["rule"] > res["greedy"] + 1e-12 for r in rows):
        return "error", "Widerspruch: Die Regel ist schlechter als immer Greedy."
    return "info", (f"Über {res['total']} Instanzen aus zehn Familien verliert „immer Greedy“ im Mittel **{prozent2(res['greedy'])}** des Optimums; die Regel „erst testen, dann wählen“ verliert bei Budget "
                    f"{' / '.join(zahl(r['budget']) for r in rows)} nur **{' / '.join(prozent2(r['rule']) for r in rows)}** (falsch durchgelassen: {' / '.join(str(r['wrong']) for r in rows)}). "
                    "Erkannte Nicht-Matroide gelten dabei als exakt gelöst: Das Optimum aus der Aufzählung steht für das Schnittverfahren oder ein ganzzahliges Programm.")


def ex4_series() -> dict:
    """Gezogener Test auf Submodularität gegen Budget, sechs Familien von Zielfunktionen (n = 10, 60 je Familie)."""
    rng = random.Random(C.E_SUB_SEED)
    rows = []
    for k in C.E_SUB_KINDS:
        tabs = [S.sub_table(k, rng, C.E_N) for _ in range(C.E_SUB_COUNT)]
        bad = [A.sub_full(t, C.E_N) for t in tabs]
        cells, calls_found, false_alarm = {}, [], 0
        for b in C.E_SUB_BUDGETS:
            found = 0
            for i, (t, vio) in enumerate(zip(tabs, bad)):
                fd, c, _ = A.sub_sampled(t, random.Random(seed_of(k, i, b)), b, C.E_N)
                found += fd
                if fd and not vio:
                    false_alarm += 1
                if fd and b == C.E_SUB_BUDGETS[-1]:
                    calls_found.append(c)
            cells[b] = found
        rows.append({"kind": k, "violated": sum(bad), "cells": cells, "avg": sum(calls_found) / len(calls_found) if calls_found else None, "false_alarm": false_alarm})
    return {"rows": rows, "count": C.E_SUB_COUNT}


def ex4_table(res) -> list[dict]:
    out = []
    for r in res["rows"]:
        row = {"Zielfunktion": C.E_SUB_KIND_NAMES[r["kind"]], "nicht submodular": f"{r['violated']} von {res['count']}"}
        for b in C.E_SUB_BUDGETS:
            row[f"B = {zahl(b)}"] = f"{r['cells'][b]} von {r['violated']}" if r["violated"] else "–"
        row["Aufrufe bis Fund (Mittel)"] = "–" if r["avg"] is None else num(round(r["avg"], 1))
        out.append(row)
    return out


def verdict_ex4(res) -> tuple[str, str]:
    by = {r["kind"]: r for r in res["rows"]}
    if any(r["false_alarm"] for r in res["rows"]) or by["abdeckung"]["violated"] or by["budget"]["violated"]:
        return "error", "Widerspruch in der Messreihe: eine submodulare Zielfunktion wurde als verletzt gemeldet."
    ep, pb, qd, zf = by["einpaar"], by["paarbonus"], by["quadrat"], by["zufall"]
    b = C.E_SUB_BUDGETS
    return "info", (f"Der Test auf Submodularität ist billiger als der auf das Matroid: Eine Abdeckung mit Paarbonus fällt im Mittel nach **{num(round(pb['avg'], 1))}** Aufrufen auf, das Quadrat der Größe nach **{num(round(qd['avg'], 1))}**, "
                    f"eine Zufallstabelle nach **{num(round(zf['avg'], 1))}**. Ein einziges Paar mit Bonus 1 braucht **{ep['cells'][b[3]]} von {ep['violated']}** bei {zahl(b[3])} und **{ep['cells'][b[4]]} von {ep['violated']}** "
                    f"bei {zahl(b[4])} Aufrufen (Mittel {num(round(ep['avg'], 1))}). Falsch gemeldete submodulare Zielfunktionen: **0**.")


def ex5_series() -> dict:
    """Greedy gegen Optimum je Familie und das Zertifikat: aus jedem gefundenen Gegenbeispiel Gewichte bauen, bei denen Greedy scheitert."""
    sd = series_data()
    rows, cert_total, cert_ok, cert_valid = [], 0, 0, 0
    for k in C.SERIES_KINDS:
        vals = sd["vals"][k]
        rs = [g / o for g, o in vals]
        rows.append({"kind": k, "matroids": sum(sd["truth"][k]), "equal": sum(1 for r in rs if abs(r - 1) < 1e-12), "mean": sum(rs) / len(rs), "min": min(rs)})
    for k in C.NON_MATROID_KINDS:
        for i, f in enumerate(sd["data"][k]):
            fd, _, cert = found_at(k, i, C.CERT_BUDGET)
            if not fd:
                continue
            a, b = cert
            cert_total += 1
            cert_valid += A.check_certificate(f.ind, a, b, C.E_N)
            w = A.certificate_weights(a, b, C.E_N)
            g = A.greedy(f.ind, w, C.E_N)[0]
            cert_ok += g < A.weight(w, b, C.E_N)
    inter_min = min(r["min"] for r in rows if r["kind"] in C.INTERSECTION_KINDS)
    return {"rows": rows, "cert_total": cert_total, "cert_ok": cert_ok, "cert_valid": cert_valid, "inter_min": inter_min, "count": C.E_PER_KIND}


def ex5_table(res) -> list[dict]:
    return [{"Familie": C.KIND_SHORT[r["kind"]], "Matroide": f"{r['matroids']} von {res['count']}", "Greedy = Optimum": f"{r['equal']} von {res['count']}", "mittlerer Quotient": quot(r["mean"]), "kleinster Quotient": quot(r["min"])} for r in res["rows"]]


def verdict_ex5(res) -> tuple[str, str]:
    mat = [r for r in res["rows"] if r["kind"] in C.MATROID_KINDS]
    if any(r["equal"] != res["count"] for r in mat) or res["cert_ok"] != res["cert_total"] or res["cert_valid"] != res["cert_total"] or res["inter_min"] < 0.5:
        return "error", "Widerspruch in der Messreihe."
    others = [r for r in res["rows"] if r["kind"] in C.NON_MATROID_KINDS]
    return "info", (f"Bei allen fünf Matroid-Familien erreicht Greedy das Optimum (**{res['count']} von {res['count']}** je Familie). Bei den fünf anderen liegt der kleinste Quotient zwischen **{quot(min(r['min'] for r in others))}** und "
                    f"**{quot(max(r['min'] for r in others))}**; bei den beiden Schnitten zweier Matroide nie unter **{quot(res['inter_min'])}**, also über der Schranke ½ aus Stück 7. Aus jedem der **{res['cert_total']}** gefundenen "
                    f"Gegenbeispiele (B = {zahl(C.CERT_BUDGET)}) entstehen Gewichte, bei denen Greedy scheitert: **{res['cert_ok']} von {res['cert_total']}**.")


# --- Spielwiese: Zuordnung mit drei Leitungen, von Hand gezogen ---------------------------------------------------------------------------------


def play_view(draws: int) -> dict:
    """`draws` zufällige maximale Mengen (je 3 Aufrufe) der Zuordnung mit drei Leitungen; Gegenbeispiel, sobald zwei verschieden große dabei sind."""
    fam = S.hand_family()
    orc = A.Oracle(fam.ind)
    sets = []
    for i in range(draws):
        mask, seq = A.random_maximal(orc, random.Random(1000 + i), fam.n)
        sets.append((mask, seq))
    small = min(sets, key=lambda x: A.pc(x[0]))[0] if sets else None
    large = max(sets, key=lambda x: A.pc(x[0]))[0] if sets else None
    found = bool(sets) and A.pc(small) != A.pc(large)
    cert_ok = found and A.check_certificate(fam.ind, small, large, fam.n)
    w = A.certificate_weights(small, large, fam.n) if found else None
    g = A.greedy(fam.ind, w, fam.n)[0] if found else None
    rows = [{"Ziehung": i + 1, "maximale Menge": mask_text(m, fam.n), "Größe": A.pc(m), "Reihenfolge der Annahme": " → ".join(str(e + 1) for e in seq)} for i, (m, seq) in enumerate(sets)]
    return {"fam": fam, "sets": sets, "calls": orc.calls, "found": found, "cert_ok": cert_ok, "small": small, "large": large, "w": w, "g": g, "b_val": A.weight(w, large, fam.n) if found else None, "rows": rows}


def verdict_play(pv: dict) -> tuple[str, str]:
    n = pv["fam"].n
    if not pv["sets"]:
        return "info", "Noch nichts gezogen. Jede Ziehung wählt Leitungen in Zufallsreihenfolge und behält jede, die zulässig bleibt (3 Orakelaufrufe)."
    if not pv["found"]:
        return "info", (f"Nach **{len(pv['sets'])}** Ziehungen (**{pv['calls']}** Orakelaufrufe) sind alle maximalen Mengen gleich groß. Das beweist nichts: In einem Matroid wäre es immer so, aber auch ein Nicht-Matroid "
                        "kann bei wenigen Ziehungen so aussehen. Weiter ziehen.")
    if not pv["cert_ok"]:
        return "error", "Widerspruch: Das Gegenbeispiel besteht die Nachprüfung nicht."
    return "info", (f"Nach **{len(pv['sets'])}** Ziehungen (**{pv['calls']}** Orakelaufrufe) gibt es zwei maximale Mengen verschiedener Größe: A = {mask_text(pv['small'], n)} (Größe {A.pc(pv['small'])}) und B = {mask_text(pv['large'], n)} "
                    f"(Größe {A.pc(pv['large'])}). Keine Leitung aus B ∖ A passt zu A: **kein Matroid**. Gewichte aus dem Gegenbeispiel ({' / '.join(str(x) for x in pv['w'])}): Greedy erreicht **{pv['g']}**, die Menge B hat **{pv['b_val']}**.")
