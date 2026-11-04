"""Verfahrenswahl für Matroid-Probleme - interaktive Konzept-Demo
Sebastian Hanisch - Operations Research und Machine Learning

Stück 17 der Reihe „Matroide und Submodularität“ (Bereich Kombinatorik), der Abschluss. Aufbau und Regeln: DEMO-PLAYBOOK.md (§2).

Lauffähig mit: streamlit run app.py
"""

import streamlit as st

import mvw_constants as C
from mvw_evaluation import (
    Settings,
    element_rows,
    ex1_series,
    ex1_table,
    ex2_loss_table,
    ex2_series,
    ex2_table,
    ex3_series,
    ex3_table,
    ex4_series,
    ex4_table,
    ex5_series,
    ex5_table,
    play_view,
    quot,
    run_view,
    step_rows,
    verdict_ex1,
    verdict_ex2,
    verdict_ex3,
    verdict_ex4,
    verdict_ex5,
    verdict_play,
    verdict_run,
    zahl,
)
from mvw_layout import dunkles_design, kopf_css
from mvw_pdf_export import build_pdf
from mvw_presets import bounds, init_session_state_defaults, load_permalink_settings, randomize_seed, sidebar_presets, sync_query_params
from mvw_visualization import build_cost_bars, build_pass_bars, build_ratio_bars, build_rule_bars, build_selection, build_sub_lines

st.set_page_config(page_title="Verfahrenswahl für Matroid-Probleme – Sebastian Hanisch", layout="wide")


@st.cache_data(show_spinner="Experiment 1 rechnen (einige Sekunden) …")
def _ex1():
    return ex1_series()


@st.cache_data(show_spinner="Experiment 2 rechnen (einige Sekunden) …")
def _ex2():
    return ex2_series()


@st.cache_data(show_spinner="Experiment 3 rechnen (einige Sekunden) …")
def _ex3():
    return ex3_series()


@st.cache_data(show_spinner="Experiment 4 rechnen (einige Sekunden) …")
def _ex4():
    return ex4_series()


@st.cache_data(show_spinner="Experiment 5 rechnen (einige Sekunden) …")
def _ex5():
    return ex5_series()


def _draw():
    st.session_state["play_draws"] = st.session_state.get("play_draws", 0) + 1


def _reset_draws():
    st.session_state["play_draws"] = 0


# Fester Kopf: nur der Titel bleibt beim Scrollen oben (Stylesheet in mvw_layout.py).
st.html(kopf_css(dunkles_design()))
with st.container(key="kopf"):
    st.title("🧭 Verfahrenswahl für Matroid-Probleme – welches Verfahren wann")
st.markdown(
    """
Die Stücke davor haben ein Dutzend Verfahren gezeigt: **Greedy**, **Schnitt** und **Vereinigung** von Matroiden, **lokale Suche** und **Streaming**, **Sekretärregel** und **Bandit**, **Minimum-Norm-Punkt**. Hier die Frage, die man in der Praxis zuerst stellt: **Welches davon passt zu meinem Problem, und was kostet es, das herauszufinden?** Neu ist kein Rechenverfahren, gemessen wird die **Entscheidung** selbst. Zwei Fragen lassen sich am Orakel prüfen (**Ist die Familie ein Matroid? Ist die Zielfunktion submodular?**), drei nicht (**Schnitt, online, lernend**): Das sind Eigenschaften der Aufgabe. Gegenbeispiele findet ein Test billig, die **vollständige Prüfung** der Demo kostet alle 2^n Mengen, und was der Test durchlässt, kostet Greedy Wert.

Dies ist das **siebzehnte und letzte Stück** der Reihe „Matroide und Submodularität“. Weiter unten: fünf Experimente (🔬), eine **Spielwiese „Sie ziehen die Mengen“**, **🚧 Wo die Annahmen enden** und der Expander **📐 Mathematische Formulierung**.
"""
)

with st.expander("So hängt es zusammen", expanded=True):
    st.markdown(
        """
1. **Wie kommen die Daten?** Alle Angebote vorher (offline), nacheinander (**online**, Stück 13) oder mit unbekanntem, verrauschtem Nutzen (**lernend**, Stück 14)? Das ist Wissen über die Aufgabe, kein Test.
2. **Zielfunktion:** Eine Summe von Gewichten, oder eine Abdeckung mit abnehmendem Zusatznutzen? Ob sie **submodular** ist, prüft ein gezogener Test (vier Aufrufe je Ziehung).
3. **Ist die Familie ein Matroid?** Ein gezogener Test sucht ein Gegenbeispiel zum Austauschaxiom: zwei zulässige Mengen A, B mit |A| < |B|, bei denen keine Leitung aus B ∖ A zu A passt. Findet er keins, wird die Familie als Matroid behandelt (bestätigt ist das nicht). Greedy ist dann optimal (Stück 1 und 5).
4. **Gegenbeispiel gefunden:** Ist die Familie ein **Schnitt zweier bekannter Matroide** (Zuordnung, Regenbogen-Wald), dann das Schnittverfahren (Stück 7 und 8); Greedy hat dort mindestens die Hälfte. Sonst Näherung oder ganzzahliges Programm (Stück 2, 12).
5. **Die Vereinigung zweier Matroide ist selbst ein Matroid** (Stück 9): Der Test sagt „ja“, ein eigener Ast ist sie nicht, nur das Orakel der Vereinigung kostet mehr Aufrufe.
        """
    )

st.caption("🔗 Die Adresszeile oben spiegelt Ihre aktuelle Konfiguration wider – einfach kopieren, um ein Szenario zu teilen.")

load_permalink_settings()
init_session_state_defaults()

with st.sidebar:
    sidebar_presets()  # Schnellstart oben, das aktive Preset ist hervorgehoben
    st.header("⚙️ Einstellungen")
    st.markdown("**Aufgabe**")
    kind = st.selectbox("Familie zulässiger Leitungsmengen", C.KINDS, key="kind_select", format_func=C.KIND_NAMES.get,
                        help="Fünf Matroide (Wald, Kardinalität, Farben, binär linear, zwei Wälder), zwei Schnitte zweier Matroide (Zuordnung, Regenbogen-Wald) und drei Familien ohne diese Struktur (Konflikte, Budget, Paarung).")
    n = st.slider("Leitungen n", *bounds("n_slider"), key="n_slider", help="Zahl der Leitungen (2^n Mengen). Die Messreihen verwenden feste Größen.")
    seed = st.number_input("Zufalls-Seed", *bounds("seed_input"), key="seed_input", step=1, help="Bestimmt Plan, Gewichte und Zufallsziehungen des Tests.")
    st.button("🎲 Neue Instanz generieren", width="stretch", on_click=randomize_seed)
    info = st.selectbox("Informationslage", C.INFOS, key="info_select", format_func=C.INFO_NAMES.get, help="Wissen über die Aufgabe, kein Test: Kommen die Angebote nacheinander (Stück 13) oder sind die Nutzen unbekannt (Stück 14)?")
    objective = st.selectbox("Zielfunktion", C.OBJECTIVES, key="objective_select", format_func=C.OBJECTIVE_NAMES.get,
                             help="Summe der Gewichte (modular) oder Abdeckung von 40 Haushalten; mit Paarbonus ist die Abdeckung nicht mehr submodular. Bei Abdeckungen läuft zusätzlich der Test auf Submodularität.")
    budget = st.select_slider("Prüfbudget (Orakelaufrufe)", C.BUDGETS, key="budget_slider", help="So viele Aufrufe des Unabhängigkeitsorakels darf der gezogene Test verbrauchen. Die vollständige Prüfung braucht 2^n.")

sync_query_params({"kind_select": kind, "n_slider": int(n), "seed_input": int(seed), "info_select": info, "objective_select": objective, "budget_slider": int(budget)})

settings = Settings(kind, int(n), int(seed), info, objective, int(budget))

# --- Der Weg durch den Baum -----------------------------------------------------------------------------------------------------------------

st.markdown("## 🎯 Der Weg durch den Baum")
v = run_view(settings)
fam = v["fam"]
st.caption(f"{C.KIND_NAMES[kind]}: {fam.n} Leitungen, {zahl(2 ** fam.n)} Teilmengen. Zielfunktion: {C.OBJECTIVE_NAMES[objective]}.")
mc = st.columns(4)
mc[0].metric("Gezogener Test", zahl(v["calls"]), delta="Gegenbeispiel" if v["found"] else "nichts gefunden", delta_color="off", help="Orakelaufrufe des gezogenen Matroid-Tests (Austausch, Zufallsziehungen) bis zum Gegenbeispiel oder bis das Budget aufgebraucht ist.")
mc[1].metric("Voller Test", zahl(v["full_calls"]), help="Orakelaufrufe der vollständigen Prüfung (alle 2^n Mengen); Greedy selbst braucht n.")
mc[2].metric("Greedy-Wert", zahl(v["g_val"]))
mc[3].metric("Optimum", zahl(v["o_val"]), delta=f"Quotient {quot(v['g_val'] / v['o_val'])}" if v["o_val"] else None, delta_color="off", help="Aus der Aufzählung aller Mengen.")
st.markdown("**Die Fragen nacheinander**")
st.dataframe(step_rows(v), hide_index=True, width="stretch")
if v["f"] is None:
    values, ylabel = fam.w, "Gewicht"
else:
    values, ylabel = [v["f"][1 << i] for i in range(fam.n)], "Haushalte allein"
st.markdown("**Was Greedy und das Optimum wählen**")
st.plotly_chart(build_selection(values, v["g_mask"], v["o_mask"], ylabel), width="stretch", key="sel_chart")
with st.expander("Die Leitungen im Einzelnen"):
    st.dataframe(element_rows(v), hide_index=True, width="stretch")

if st.button("📄 PDF des aktuellen Beispiels erstellen", key="pdf_make"):
    st.session_state["pdf_made"] = (settings, build_pdf(settings))
made = st.session_state.get("pdf_made")
if made and made[0] == settings:
    st.download_button("⬇️ PDF herunterladen", data=made[1], file_name="verfahrenswahl-matroid.pdf", mime="application/pdf", key="pdf_download")

# --- Kernfrage -----------------------------------------------------------------------------------------------------------------------------------

st.markdown("## ❓ Kernfrage: Welches Verfahren passt, und was kostet das Fragen?")
kind_v, text_v = verdict_run(settings, v)
getattr(st, kind_v)(text_v)

with st.expander("Online und lernend: die Zahlen aus Stück 13 und 14 (Literatur dieser Reihe, nicht hier gemessen)"):
    for title, text in C.TAFEL:
        st.markdown(f"**{title}:** {text}")

st.markdown("---")

# --- Experimente ---------------------------------------------------------------------------------------------------------------------------------

st.subheader("🔬 Experiment 1: Was das Prüfen kostet")
st.caption(f"Nicht-Matroide mit n = {', '.join(str(x) for x in C.E_SKALA_NS)} Leitungen, {C.E_SKALA_COUNT} Instanzen je Familie und n: Wie viele Orakelaufrufe braucht der Größentest (zwei zufällige maximale Mengen verschieden groß), wie viele der Austauschtest, und wie viele die vollständige Prüfung?")
if st.button("📊 Prüfkosten messen", key="ex1_run"):
    st.session_state["ex1_done"] = True
if st.session_state.get("ex1_done"):
    r1 = _ex1()
    st.plotly_chart(build_cost_bars([r for r in r1["rows"]], C.E_SKALA_NS), width="stretch", key="ex1_chart")
    st.dataframe(ex1_table(r1), hide_index=True, width="stretch", height=300)
    kind_v, text_v = verdict_ex1(r1)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 2: Stille Fehler")
st.caption(f"{C.E_PER_KIND} Instanzen je Familie mit n = {C.E_N} (Seed {C.E_SEED}): Wie viele Nicht-Matroide findet der gezogene Test bei Budget B, wie viele lässt er durch, und was kostet Greedy auf den Durchgelassenen?")
if st.button("📊 Stille Fehler messen", key="ex2_run"):
    st.session_state["ex2_done"] = True
if st.session_state.get("ex2_done"):
    r2 = _ex2()
    st.plotly_chart(build_pass_bars(r2), width="stretch", key="ex2_chart")
    st.dataframe(ex2_table(r2), hide_index=True, width="stretch")
    st.dataframe(ex2_loss_table(r2), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex2(r2)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 3: Die Regel gegen „immer Greedy“")
st.caption("Dieselben 600 Instanzen aus zehn Familien: Wer erst testet und bei einem Gegenbeispiel genauer rechnet, verliert weniger als wer immer Greedy nimmt. Erkannte Nicht-Matroide gelten als exakt gelöst (Optimum aus der Aufzählung).")
if st.button("📊 Regel vergleichen", key="ex3_run"):
    st.session_state["ex3_done"] = True
if st.session_state.get("ex3_done"):
    r3 = _ex3()
    st.plotly_chart(build_rule_bars(r3), width="stretch", key="ex3_chart")
    st.dataframe(ex3_table(r3), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex3(r3)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 4: Ist die Zielfunktion submodular?")
st.caption(f"Sechs Arten von Zielfunktionen (n = {C.E_N}, {C.E_SUB_COUNT} je Art): Wie schnell findet der gezogene Test (vier Aufrufe je Ziehung) eine Verletzung des abnehmenden Zusatznutzens, auch wenn sie nur ein einziges Paar betrifft?")
if st.button("📊 Test auf Submodularität messen", key="ex4_run"):
    st.session_state["ex4_done"] = True
if st.session_state.get("ex4_done"):
    r4 = _ex4()
    st.plotly_chart(build_sub_lines(r4), width="stretch", key="ex4_chart")
    st.dataframe(ex4_table(r4), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex4(r4)
    getattr(st, kind_v)(text_v)

st.subheader("🔬 Experiment 5: Greedy gegen Optimum und das Zertifikat")
st.caption("Je Familie: Wie oft trifft Greedy das Optimum, und wie schlecht ist der schlechteste Fall? Dazu das Zertifikat aus Stück 5: Aus jedem gefundenen Gegenbeispiel (A, B) entstehen Gewichte, bei denen Greedy scheitert.")
if st.button("📊 Greedy und Zertifikat prüfen", key="ex5_run"):
    st.session_state["ex5_done"] = True
if st.session_state.get("ex5_done"):
    r5 = _ex5()
    st.plotly_chart(build_ratio_bars(r5), width="stretch", key="ex5_chart")
    st.dataframe(ex5_table(r5), hide_index=True, width="stretch")
    kind_v, text_v = verdict_ex5(r5)
    getattr(st, kind_v)(text_v)

st.markdown("---")

# --- Spielwiese ----------------------------------------------------------------------------------------------------------------------------------

st.subheader("🛠️ Spielwiese: Sie ziehen die Mengen")
st.caption("Die Zuordnung mit drei Leitungen: 1 = (oben 1, unten 1), 2 = (oben 1, unten 2), 3 = (oben 2, unten 1), alle mit Gewicht 1. Jede Ziehung wählt die Leitungen in Zufallsreihenfolge und behält jede, die zulässig bleibt. Sobald zwei verschieden große maximale Mengen vorliegen, ist die Familie als Nicht-Matroid entlarvt.")
st.session_state.setdefault("play_draws", 0)
pc1, pc2 = st.columns(2)
pc1.button("🎲 Nächste Ziehung", key="play_draw", on_click=_draw, width="stretch")
pc2.button("↺ Von vorn", key="play_reset", on_click=_reset_draws, width="stretch")
pv = play_view(int(st.session_state["play_draws"]))
kind_v, text_v = verdict_play(pv)
getattr(st, kind_v)(text_v)
if pv["rows"]:
    st.dataframe(pv["rows"], hide_index=True, width="stretch")

st.markdown("---")

# --- Grenzen -------------------------------------------------------------------------------------------------------------------------------------

st.subheader("🚧 Wo die Annahmen enden")
st.markdown(
    """
| Annahme | Was passiert, wenn sie verletzt ist (wer setzt an) |
|---|---|
| **Kleine Familien als Tabelle** | Alle Familien liegen als Tabelle aller 2^n Mengen vor (n ≤ 14); das Optimum kommt aus der Aufzählung. Große Instanzen mit echtem Orakel und echter Rechenzeit sind nicht gemessen. **(nicht in dieser Reihe)** |
| **Das Optimum steht für das Schnittverfahren** | Bei erkannten Nicht-Matroiden mit Zerlegung gilt hier der Aufzählungswert als „Wert des Schnittverfahrens“; dass das Verfahren aus Stück 7 und 8 ihn polynomiell erreicht, ist dort gemessen, hier nicht gegengeprüft. **(Stück 7 und 8)** |
| **Die Zerlegung wird mitgeliefert** | Der Test sagt nur „kein Matroid“. Ob sich eine Zerlegung in zwei Matroide aus dem Orakel finden lässt, ist nicht untersucht. **(nicht gemessen)** |
| **Online und lernend sind Wissen** | Die Informationslage wird angegeben, nicht geprüft; die Zahlen aus Stück 13 und 14 sind dort gemessen und hier nur zitiert. **(Stück 13 und 14)** |
| **Gezogene Tests beweisen nichts** | Kein Gegenbeispiel in B Aufrufen heißt nicht „Matroid“: Experiment 2 zeigt durchgelassene Nicht-Matroide. Die vollständige Prüfung der Demo kostet 2^n Aufrufe; ob es mit weniger geht, ist nicht untersucht. **(Experiment 2)** |
| **Submodularität nur an einer Abdeckung gemessen** | Der Test auf abnehmenden Zusatznutzen läuft auf Abdeckungen, Budgetdeckeln, Quadraten und Zufallstabellen; schwache Verletzungen brauchen viele Aufrufe. **(Experiment 4)** |
| **Härte nicht gemessen** | Dass viele dieser Probleme NP-schwer sind, steht in der Literatur und ist hier **nicht** nachgeschlagen und nicht gemessen. **(Literatur, nicht geprüft)** |
| **Beispiele zufällig und klein** | Alle Aussagen gelten für die gezogenen Instanzen mit festen Seeds. **(nicht allgemein)** |
"""
)

st.markdown("---")

with st.expander("📐 Mathematische Formulierung"):
    st.markdown(
        r"""
**Gegeben** eine Familie $\mathcal{I} \subseteq 2^E$ zulässiger Mengen ($\lvert E \rvert = n$, erblich: Teilmengen zulässiger Mengen sind zulässig), die nur über ein **Unabhängigkeitsorakel** $S \mapsto [S \in \mathcal{I}]$ zugänglich ist, und Gewichte $w : E \to \mathbb{N}$.

**Matroid** heißt $\mathcal{I}$, wenn für alle $A, B \in \mathcal{I}$ mit $\lvert A \rvert < \lvert B \rvert$ ein $e \in B \setminus A$ mit $A \cup \{e\} \in \mathcal{I}$ existiert (Austauschaxiom). Ein **Gegenbeispiel** ist ein Paar $(A, B)$ ohne ein solches $e$. In einem Matroid sind alle maximalen zulässigen Mengen gleich groß; verschieden große maximale Mengen sind also ein Gegenbeispiel (Größentest). Der **gezogene Test** zieht zwei zufällige maximale Mengen $X, Y$ (je $n$ Aufrufe) und einen zufälligen Anfang $A$ von $X$ und prüft den Austausch für $(A, Y)$; er meldet nie ein Matroid fälschlich. Die **vollständige Prüfung** braucht alle $2^n$ Mengen.

**Zertifikat (Stück 5).** Ist $(A, B)$ ein Gegenbeispiel, $p = \lvert A \rvert$, so gilt für $w_e = p + 2$ ($e \in A$), $w_e = p + 1$ ($e \in B \setminus A$), sonst $0$: Greedy erreicht $p(p+2) = (p+1)^2 - 1$, die Menge $B$ mindestens $(p+1)^2$.

**Submodularität.** $f$ ist submodular genau dann, wenn $f(A + e) + f(A + g) \ge f(A + e + g) + f(A)$ für alle $A$ und $e, g \notin A$. Der gezogene Test prüft vier Aufrufe je Ziehung $(A, e, g)$.

**Garantien aus der Reihe** (dort gemessen, hier zitiert): Greedy ist bei einem Matroid für jede Gewichtung optimal (Stück 5); beim Schnitt zweier Matroide erreicht Greedy nach Gewicht mindestens die Hälfte des Optimums (jede maximale gemeinsame Menge hat mindestens die halbe Mächtigkeit des Maximums; Stück 7); bei monotoner submodularer Zielfunktion erreicht Greedy $1 - 1/e$ unter einer Kardinalitätsschranke und $1/2$ unter einer Matroidschranke (Stück 11).

**Literatur.** Matroid-Axiome, Greedy-Charakterisierung (Rado, Edmonds), Schnitt und Vereinigung (Edmonds) sind Lehrbuchwissen. Aussagen zur Härte sind nicht nachgeschlagen. Gemessen, nicht zitiert, sind hier die Prüfkosten, die stillen Fehler und die Verluste der Regel.
        """
    )

st.markdown("---")
st.caption(
    "Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – "
    "Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). "
    "Mehr zur Reihe: [Matroide: vom Spannbaum zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-matroide.html)."
)
