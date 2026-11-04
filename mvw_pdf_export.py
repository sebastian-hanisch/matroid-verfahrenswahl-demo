"""PDF-Export des aktuellen Beispiels (fpdf2). Kernschriften sind latin-1: Umlaute gehen, Sonderzeichen werden ersetzt."""

from __future__ import annotations

from fpdf import FPDF

import mvw_constants as C
from mvw_evaluation import Settings, run_view, step_rows, verdict_run

_REPLACE = {"→": "->", "–": "-", "—": "-", "−": "-", "≤": "<=", "≥": ">=", "·": "*", "€": "EUR", "„": '"', "“": '"', "×": "x", "≈": "~", "½": "1/2", "∅": "{}", "²": "^2", "∖": "\\", "…": "...", "⊆": "<=", "∈": "in"}


def _s(text) -> str:
    out = str(text).replace("**", "")
    for old, new in _REPLACE.items():
        out = out.replace(old, new)
    return out.encode("latin-1", "replace").decode("latin-1")


def build_pdf(s: Settings) -> bytes:
    v = run_view(s)
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=12)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 15)
    pdf.cell(0, 9, _s("Verfahrenswahl für Matroid-Probleme"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 5, _s(f"{C.KIND_NAMES[s.kind]}; {s.n} Leitungen, Seed {s.seed}; {C.INFO_NAMES[s.info]}; Zielfunktion: {C.OBJECTIVE_NAMES[s.objective]}; Prüfbudget {s.budget} Aufrufe."), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(0, 6, _s("Der Weg durch den Baum"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    for row in step_rows(v):
        pdf.multi_cell(0, 5, _s(f"{row['Frage']} [{row['Art']}] {row['Antwort']} ({row['Orakelaufrufe']} Aufrufe) -> {row['Folge']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.multi_cell(0, 5, _s(verdict_run(s, v)[1]), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _s("Quelle: matroid-verfahrenswahl-demo, Sebastian Hanisch."), new_x="LMARGIN", new_y="NEXT")
    return bytes(pdf.output())
