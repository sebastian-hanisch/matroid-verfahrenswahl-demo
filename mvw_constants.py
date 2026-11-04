"""Konstanten: Regler-Grenzen, Familien, Messreihen und Presets."""

MATROID_KINDS = ("graphic", "uniform", "partition", "binary", "union2")
INTERSECTION_KINDS = ("bimatch", "rainbow")
OTHER_KINDS = ("stable", "knapsack", "gmatch")
KINDS = MATROID_KINDS + INTERSECTION_KINDS + OTHER_KINDS
NON_MATROID_KINDS = INTERSECTION_KINDS + OTHER_KINDS
SERIES_KINDS = ("uniform", "partition", "graphic", "binary", "union2") + NON_MATROID_KINDS      # Reihenfolge der Ziehungen in den Messreihen (wie in Phase 0)
KIND_NAMES = {
    "graphic": "Wald: keine Schleife im Plan (Matroid)",
    "uniform": "Kardinalität: höchstens k Leitungen (Matroid)",
    "partition": "Farben: höchstens eine bis drei je Kabelfarbe (Matroid)",
    "binary": "Binär linear: Spalten über GF(2) (Matroid)",
    "union2": "Zwei Netze: in zwei Wälder zerlegbar (Matroid)",
    "bimatch": "Zuordnung: jeder Anschluss höchstens einmal (Schnitt zweier Matroide)",
    "rainbow": "Regenbogen-Wald: Wald und lauter verschiedene Farben (Schnitt zweier Matroide)",
    "stable": "Konflikte: Leitungspaare, die nicht zusammen gehen",
    "knapsack": "Budget: Gesamtgröße höchstens ein Drittel",
    "gmatch": "Paarung im allgemeinen Graphen: jeder Standort höchstens einmal",
}
KIND_SHORT = {"graphic": "Wald", "uniform": "Kardinalität", "partition": "Farben", "binary": "Binär linear", "union2": "Zwei Wälder", "bimatch": "Zuordnung", "rainbow": "Regenbogen-Wald", "stable": "Konflikte",
              "knapsack": "Budget", "gmatch": "Paarung"}

N_MIN, N_MAX, DEFAULT_N = 8, 12, 10
SEED_MAX, DEFAULT_SEED = 999999, 3
BUDGETS = (30, 100, 300, 1000, 3000)
DEFAULT_BUDGET = 300
INFOS = ("bekannt", "nacheinander", "verrauscht")
INFO_NAMES = {"bekannt": "alle Angebote vorher bekannt", "nacheinander": "Angebote kommen nacheinander (online)", "verrauscht": "Nutzen unbekannt und verrauscht (lernend)"}
OBJECTIVES = ("summe", "abdeckung", "paarbonus")
OBJECTIVE_NAMES = {"summe": "Summe der Gewichte", "abdeckung": "Abdeckung von 40 Haushalten", "paarbonus": "Abdeckung mit Paarbonus (Synergie)"}
HOUSEHOLDS = 40
WEIGHT_MAX = 30

# Messreihen (alle deterministisch über feste Seeds; Phase 0 ist dieselbe Rechnung)
E_N = 10                                                    # Elemente der Messreihen 2 bis 5
E_PER_KIND = 60
E_SEED = 17
E_BUDGETS = (30, 100, 300, 1000, 3000)
E_RULE_BUDGETS = (100, 300, 1000)
E_SKALA_SEED, E_SKALA_NS, E_SKALA_COUNT, E_SKALA_CAP = 117, (8, 10, 12, 14), 30, 20000
E_SUB_SEED, E_SUB_COUNT, E_SUB_BUDGETS = 217, 60, (20, 40, 100, 400, 1000, 4000)
E_SUB_KINDS = ("abdeckung", "budget", "paarbonus", "einpaar", "quadrat", "zufall")
E_SUB_KIND_NAMES = {"abdeckung": "Abdeckung", "budget": "Budget-Abdeckung", "paarbonus": "Abdeckung + Paarbonus", "einpaar": "Abdeckung + ein Paar (Bonus 1)", "quadrat": "Quadrat der Größe", "zufall": "Zufallstabelle"}
E_SUB_TRUTH = {"abdeckung": "submodular", "budget": "submodular", "paarbonus": "nicht submodular", "einpaar": "meist nicht submodular", "quadrat": "supermodular", "zufall": "meist nicht submodular"}
CERT_BUDGET = 1000
FULL_CHECK_NS = (10, 20, 30)

# Literatur dieser Reihe (nicht neu gemessen; Quelle: Stück 13 und 14)
TAFEL = (
    ("Stück 13 (Sekretär)", "Die wachsende Stichprobe behält im Wald bei Rang 4 / 7 / 11 / 15 mit verdoppelnden Nutzen 0,544 / 0,500 / 0,527 / 0,554 des Optimums (gleichverteilt 0,704 bis 0,780); erst kommt, erst bekommt fällt bei aufsteigender Reihenfolge auf 0,063 (Kardinalität) und 0,119 (Wald)."),
    ("Stück 14 (Bandit)", "Optimistisches Greedy: das Bedauern wächst erst bei großen T logarithmisch; mit Konstante 0,25 statt 1,5 sinkt es bei Lücke 0,2 und T = 2 000 von 223,4 auf 49,8 (Standardfall), von 217,1 auf 71,1 (Experiment 1) und von 212,4 auf 77,9 (Experiment 5)."),
)

COLOR_BAR = "#2F6B65"
COLOR_BAR2 = "#d95f02"
COLOR_NODE = "#4c78a8"
COLOR_OTHER = "rgba(150,150,150,0.55)"

PRESETS = {
    "Standardfall (Voreinstellung)": {"kind": "graphic", "n": 10, "seed": 3, "info": "bekannt", "objective": "summe", "budget": 300},
    "Regenbogen-Wald": {"kind": "rainbow", "n": 10, "seed": 10, "info": "bekannt", "objective": "summe", "budget": 300},
    "Zuordnung": {"kind": "bimatch", "n": 10, "seed": 7, "info": "bekannt", "objective": "summe", "budget": 300},
    "Konflikte": {"kind": "stable", "n": 10, "seed": 11, "info": "bekannt", "objective": "summe", "budget": 300},
    "Budget": {"kind": "knapsack", "n": 10, "seed": 3, "info": "bekannt", "objective": "summe", "budget": 300},
    "Stiller Fehler": {"kind": "bimatch", "n": 10, "seed": 5, "info": "bekannt", "objective": "summe", "budget": 300},
}
PRESET_HELP = {
    "Standardfall (Voreinstellung)": "Wald mit 10 Leitungen (Seed 3): Der gezogene Test findet in 311 Orakelaufrufen kein Gegenbeispiel, die vollständige Prüfung (1 024 Aufrufe) bestätigt das Matroid. Greedy erreicht 108, das Optimum.",
    "Regenbogen-Wald": "Wald und lauter verschiedene Kabelfarben (Seed 10): Gegenbeispiel nach 23 Aufrufen, kein Matroid. Greedy erreicht 62 von 66 (0,939). Die Zerlegung in zwei Matroide ist bekannt: Schnittverfahren (Stück 7 und 8).",
    "Zuordnung": "Jeder obere und jeder untere Anschluss höchstens einmal (Seed 7): Gegenbeispiel nach 153 Aufrufen, kein Matroid. Greedy erreicht 44 von 51 (0,863). Zwei Partitionsmatroide: Schnittverfahren.",
    "Konflikte": "Leitungspaare, die nicht zusammen gehen (Seed 11): Gegenbeispiel nach 252 Aufrufen. Greedy erreicht 98 von 133 (0,737). Keine bekannte Zerlegung in zwei Matroide (Konfliktgraph, nicht geprüft): Näherung oder ganzzahliges Programm.",
    "Budget": "Gesamtgröße höchstens ein Drittel (Seed 3): Gegenbeispiel nach 272 Aufrufen. Greedy erreicht nur 51 von 92 (0,554), ein schlechter Fall dieser Familie (in der Messreihe liegt der kleinste Quotient bei 0,612, in anderen Ziehungen darunter).",
    "Stiller Fehler": "Dieselbe Zuordnung wie oben, aber Seed 5: Der Test findet bei Budget 300 in 319 Aufrufen nichts und lässt die Familie als Matroid durch. Sie ist keins; Greedy erreicht 81 von 106 (0,764). Mit Budget 1 000 findet er das Gegenbeispiel nach 652 Aufrufen.",
}
