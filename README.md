# Verfahrenswahl für Matroid-Probleme – welches Verfahren wann – Streamlit-Demo

<!-- TODO nach dem Deploy: direkt hierher den Live-Link setzen (Leerzeile davor und danach):
**[→ Demo live ausprobieren](https://sebastianhanisch-matroid-verfahrenswahl-demo.streamlit.app/)** -->

Siebzehntes und letztes Stück der Reihe **Matroide und Submodularität** (Bereich Kombinatorik) in der „Konzepte“-Reihe für die Website „Sebastian Hanisch – Operations Research und Machine Learning“. Die Stücke davor haben ein Dutzend Verfahren gezeigt: **Greedy**, **Schnitt** und **Vereinigung** von Matroiden, **lokale Suche** und **Streaming**, **Sekretärregel** und **Bandit**, **Minimum-Norm-Punkt**. Hier die Frage, die man in der Praxis zuerst stellt: **Welches davon passt zu meinem Problem, und was kostet es, das herauszufinden?** Neu ist kein Rechenverfahren; gemessen wird die **Entscheidung** selbst. Zwei Fragen lassen sich am Orakel prüfen (**Ist die Familie ein Matroid? Ist die Zielfunktion submodular?**), drei nicht (**Schnitt, online, lernend**).

**Einordnung in die Reihe:** Nachfolger von [tutte-matroid-demo](../tutte-matroid-demo) (Stück 16) und [submodulare-minimierung-demo](../submodulare-minimierung-demo) (Stück 15); verweist auf Stück 1 und 5 (Greedy), 2 (Unabhängigkeitssysteme), 7 und 8 (Schnitt), 9 (Vereinigung), 11 und 12 (Submodularität), 13 (Sekretär) und 14 (Bandit). **Abgrenzung:** `kegel-verfahrenswahl-demo` (Konvexe-Optimierung-Linie) hat dasselbe Muster („keiner gewinnt überall“), misst aber Löser gegeneinander; hier wird die Entscheidung gemessen.

## Warum dieses Problem

Wer eine Auswahlaufgabe mit Nebenbedingungen löst, wählt ein Verfahren nach der Struktur der Aufgabe. Ob die Struktur ein Matroid ist, sieht man ihr nicht an: Man kann nur das Unabhängigkeitsorakel befragen. Offen ist, was das kostet und was passiert, wenn der Test sich täuscht.

## Befunde und Korrekturen gegenüber dem Plan

- **Die Vereinigung ist kein eigener Ast.** Sie ist selbst ein Matroid (Stück 9): Wald ∨ Wald hat bei **60 von 60** Instanzen Greedy = Optimum; der Matroid-Test antwortet „ja“, nur das Orakel der Vereinigung kostet mehr Aufrufe.
- **Der Matroid-Test erkennt den Schnitt nicht.** Er sagt nur „kein Matroid“; die Zerlegung in zwei Matroide wird mitgeliefert, ob sie sich aus dem Orakel finden lässt, ist nicht untersucht. Auch die Einordnung „kein Schnitt“ (Konflikte, Budget, Paarung) beruht auf der Erzeugung, nicht auf einer Prüfung.
- **Online und lernend sind Eigenschaften der Informationslage,** nicht der Familie: Sie stehen vor der Familienfrage. Die Zahlen aus Stück 13 und 14 sind dort gemessen und hier nur zitiert.
- **Das Prüfen ist unsymmetrisch teuer:** Gegenbeispiele sind bei den gemessenen Familien billig, die vollständige Prüfung der Demo kostet alle 2^n Aufrufe; ob es mit weniger geht, ist nicht untersucht.
- **„Sonst?“ ist nicht leer:** Bei Konflikten, Budget und Paarung erreicht Greedy in diesen Messreihen im Mittel 0,929 bis 0,961 des Optimums; einzelne Instanzen liegen deutlich darunter (kleinster beobachteter Quotient der 60er-Reihen 0,612, in anderen Ziehungen bis etwa 0,48).
- **Zahlen wie in Phase 0** (gleiche Seeds und Erzeuger). Das Optimum der Schnitt-Familien kommt aus der Aufzählung (Platzhalter für das Schnittverfahren aus Stück 7 und 8).
- **Port 9357;** Repo `matroid-verfahrenswahl-demo`, Präfix `mvw_`; nur Streamlit, Plotly und fpdf2 zur Laufzeit (reine Python-Arithmetik, kein numpy).

## Modell

**Familien als Tabellen** der zulässigen Mengen über n Leitungen (n ≤ 14), Gewichte ganzzahlig von 1 bis 30. **Fünf Matroide:** Wald (Zyklenmatroide eines Plans), Kardinalität, Farben (drei Farben, Kapazität 1 bis 3), binär linear (Spalten über GF(2)), zwei Wälder (Vereinigung). **Zwei Schnitte zweier Matroide:** Zuordnung (jeder obere und untere Anschluss höchstens einmal) und Regenbogen-Wald (Wald und lauter verschiedene Farben). **Drei weitere:** Konflikte (Leitungspaare, die nicht zusammen gehen), Budget (Gesamtgröße höchstens ein Drittel) und Paarung im allgemeinen Graphen. **Zielfunktionen:** Summe der Gewichte, Abdeckung von 40 Haushalten (je Leitung 15 %), Abdeckung mit Paarbonus; in den Messreihen außerdem Budget-Abdeckung, ein einzelnes Paar mit Bonus 1, Quadrat der Größe und Zufallstabelle.

## Methodik

- **Orakel mit Zähler:** `Oracle` zählt jeden Zugriff auf die Tabelle der zulässigen Mengen.
- **Größentest:** zufällige maximale Mengen ziehen (je n Aufrufe); verschieden große sind ein Gegenbeispiel.
- **Gezogener Austauschtest:** zwei zufällige maximale Mengen X, Y, ein zufälliger Anfang A von X; Gegenbeispiel, wenn |A| < |Y| und keine Leitung aus Y ∖ A zu A passt. Er meldet nie ein Matroid fälschlich.
- **Vollständige Prüfung:** Austausch für alle Paare zulässiger Mengen mit |B| = |A| + 1 (2^n Aufrufe).
- **Zertifikat (Stück 5):** Aus einem Gegenbeispiel (A, B) mit p = |A| entstehen Gewichte p + 2 auf A, p + 1 auf B ∖ A, sonst 0; Greedy erreicht p(p + 2), B mindestens (p + 1)².
- **Test auf Submodularität:** vier Aufrufe je Ziehung (A, e, g); verletzt, wenn f(A+e) + f(A+g) < f(A+e+g) + f(A).
- **Messreihen:** feste Seeds, kein Löser, plattformunabhängig; Zeiten werden nicht gemessen.

## Befunde (gemessen, keine Behauptungen)

Alle Zahlen stehen in `tests/test_claims.py` und werden dort mit den Funktionen der App nachgerechnet.

| Voreinstellung | Familie | Aufrufe des Tests (Budget 300) | Gegenbeispiel | Greedy | Optimum |
|---|---|---|---|---|---|
| Standardfall (Wald, Seed 3) | Matroid | 311 | nein | 108 | 108 |
| Regenbogen-Wald (Seed 10) | Schnitt | 23 | ja | 62 | 66 |
| Zuordnung (Seed 7) | Schnitt | 153 | ja | 44 | 51 |
| Konflikte (Seed 11) | kein Schnitt | 252 | ja | 98 | 133 |
| Budget (Seed 3) | kein Schnitt | 272 | ja | 51 | 92 |
| Stiller Fehler (Zuordnung, Seed 5) | Schnitt | 319 | nein | 81 | 106 |

Das Budget wird erst nach einer vollständigen Ziehung (rund 2n Aufrufe) geprüft, daher Werte über 300.

| Frage | Befund |
|---|---|
| **Experiment 1: Prüfkosten** (n = 8, 10, 12, 14; 30 Instanzen je Familie und n; Deckel 20 000 Aufrufe) | Größentest findet Gegenbeispiele im Median nach **16 bis 182** Orakelaufrufen, der Austauschtest nach **74 bis 355** (Median je Zelle; mit anderen Seeds etwa 16 bis 63 und 102 bis 367); beide Tests zusammen ließen **6** von 600 Instanzen unentdeckt. Alle 6 sind (Aufzählung aller Paare unabhängiger Mengen) zufällig doch Matroide, es blieb kein Nicht-Matroid unentdeckt. Vollständige Prüfung: **1 024** Aufrufe bei n = 10, **1 048 576** bei n = 20, **1 073 741 824** bei n = 30. |
| **Experiment 2: Stille Fehler** (60 Instanzen je Familie, n = 10, Seed 17) | Von 298 Nicht-Matroiden bestehen den gezogenen Test bei Budget B = 30 / 100 / 300 / 1 000 / 3 000: **275 / 210 / 86 / 9 / 1**; mittlerer Greedy-Verlust der Durchgelassenen **4,1 % / 3,9 % / 3,7 % / 1,5 % / 0,0 %**; schlechtester Quotient bei B = 30 **0,612** (Minimum aus den durchgelassenen Instanzen). Mit anderen Seeds schwanken die Anzahlen um etwa ±10; der Verlust 0,0 % bei B = 3 000 beruht auf einer einzigen Instanz. Falsch gemeldete Matroide: **0 von 300** bei B = 1 000. |
| **Experiment 3: Die Regel** (600 Instanzen) | Immer Greedy verliert im Mittel **2,02 %** des Optimums (gemittelt über fünf Matroid- und fünf Nicht-Matroid-Familien; bei den Nicht-Matroiden allein etwa 4 %); die Regel „erst testen, dann wählen“ bei Budget 100 / 300 / 1 000 **1,35 % / 0,53 % / 0,02 %** (falsch durchgelassen **210 / 86 / 9**), gezählt ist nur der Wert, ohne Rechenkosten für das exakte Lösen erkannter Nicht-Matroide und für den Test; mit anderen Seeds schwanken die Werte (Regel etwa 1,3 / 0,5 / 0,05 %). |
| **Experiment 4: Submodularität** (n = 10, 60 je Art) | Abdeckung und Budget-Abdeckung: **0 von 60** verletzt, **0** Fehlalarme. Abdeckung mit Paarbonus fällt im Mittel nach **12,8** Aufrufen auf, Quadrat der Größe nach **4**, Zufallstabelle nach **8,7**. Ein einziges Paar mit Bonus 1: **49 von 60** überhaupt verletzt; gefunden **41 von 49** bei 400, **49 von 49** bei 1 000 Aufrufen (Mittel **237,1**); in drei untersuchten Seeds waren bei 1 000 Aufrufen alle gefunden. Bei diesem einen schwachen Paar ist der Test mit rund 240 Aufrufen nicht billiger als der Austauschtest. |
| **Experiment 5: Greedy und Zertifikat** | Bei allen fünf Matroid-Familien Greedy = Optimum **60 von 60**. Kleinste beobachtete Quotienten (Stichprobenminima aus je 60 Instanzen): Zuordnung **0,796**, Regenbogen-Wald **0,733**, Konflikte **0,714**, Budget **0,612**, Paarung **0,667**; Schnitt zweier Matroide in diesen 60 Instanzen je Familie nicht unter **0,733** (bewiesene Schranke ½; in größeren Stichproben bis etwa 0,6). Aus jedem der **289** gefundenen Gegenbeispiele (B = 1 000) entstehen Gewichte, bei denen Greedy scheitert: **289 von 289**. |
| **Spielwiese** (Zuordnung mit drei Leitungen) | Greedy nimmt Leitung 1 und erreicht **1**, das Optimum {2, 3} hat **2** (Quotient 0,5, scharf). Gegenbeispiel A = {1}, B = {2, 3}; Gewichte 3 / 2 / 2: Greedy **3**, B **4**. |

## Ehrliche Grenzen

- **Kleine Familien als Tabelle** (n ≤ 14); große Instanzen mit echtem Orakel und echter Rechenzeit sind nicht gemessen.
- **Das Optimum steht für das Schnittverfahren.** Der Aufzählungswert ersetzt den Wert des Verfahrens aus Stück 7 und 8; dort gemessen, hier nicht gegengeprüft.
- **Die Zerlegung in zwei Matroide wird mitgeliefert;** ob sie sich aus dem Orakel finden lässt, ist nicht untersucht.
- **Online und lernend sind Wissen,** nicht geprüft; die Zahlen aus Stück 13 und 14 sind zitiert, nicht neu gemessen.
- **Gezogene Tests beweisen nichts;** die vollständige Prüfung der Demo kostet 2^n Aufrufe, ob es mit weniger geht, ist nicht untersucht.
- **Submodularität an wenigen Arten gemessen;** schwache Verletzungen brauchen viele Aufrufe.
- **Härte (NP-Schwere) nicht gemessen** und nicht nachgeschlagen.
- **Beispiele zufällig und klein,** mit festen Seeds.
- **Quellen nur als Lehrbuchwissen und Erinnerung** (Rado, Edmonds); nicht gegen Primärtexte geprüft. Gemessen, nicht zitiert, sind die Prüfkosten, die stillen Fehler und die Verluste der Regel.

## Verifikation

- **Kern:** Orakelzähler, Größen-, Austausch- und vollständiger Test, Greedy, Optimum, Zertifikat, Test auf Submodularität und Formatierung gegen Handrechnung (`tests/conftest.py`, `tests/test_algorithm.py`); Randfälle: Reglerecken, leere Mengen, Spielwiese ohne Ziehung (`tests/test_edge_cases.py`).
- **Orakel** (`tests/test_oracle_matroid_verfahrenswahl.py`): die Familien gegen eigene, unabhängige Definitionen der Zulässigkeit (Komponentenzählung statt Union-Find, Endpunktmengen, Konfliktpaare, Gewichtssumme); Matroid-Eigenschaft durch erschöpfende Prüfung aller Paare, nicht durch den gezogenen Test; Optimum durch Aufzählung.
- **Eigenschaften** (`tests/test_properties.py`): kein Matroid wird je als Nicht-Matroid gemeldet; jedes gemeldete Gegenbeispiel besteht die Nachprüfung; Greedy ist bei Matroiden optimal; Schnitt zweier Matroide bleibt über der Hälfte; Zertifikat-Gewichte lassen Greedy scheitern; submodulare Funktionen werden nie als verletzt gemeldet.
- **Verdikte und Presets:** jeder Zweig und jede Zahl der Verdikte; jedes Preset zeigt den versprochenen Effekt; kein einzelner Reglerwechsel trifft ein anderes Preset.
- **Zahlen aus dieser README:** `tests/test_claims.py`.
- **Oberfläche:** AppTest-Rauchtest (jeder Button, jeder Regler an den Grenzen), Hauptansicht, fünf Experimente, Spielwiese, Permalink, PDF; Layout (Kopf, Schnellstart, Hervorhebung) und Footer.
- **Umfang:** siehe `pytest --collect-only -q tests`.

## Dateistruktur

| Datei | Inhalt |
|---|---|
| `app.py` | Streamlit-Oberfläche: der Weg durch den Baum, Kernfrage, fünf Experimente, Spielwiese, Grenzen, Formeln |
| `mvw_constants.py` | Familien, Reglergrenzen, Messgrößen, Farben, Presets |
| `mvw_scenario.py` | die zehn Familien, die Zielfunktionen und das Handbeispiel |
| `mvw_algorithm.py` | Orakel mit Zähler, Tests auf Matroid und Submodularität, Greedy, Optimum, Zertifikat |
| `mvw_evaluation.py` | Weg durch den Baum, Messreihen der Experimente, Spielwiese, Verdikte |
| `mvw_visualization.py` | Auswahl, Kostenbalken, Verlustbalken, Linien |
| `mvw_presets.py` | Permalink, Presets, Zufalls-Seed |
| `mvw_layout.py` | fester Kopf |
| `mvw_pdf_export.py` | PDF des aktuellen Beispiels |
| `tests/` | Kern, Orakel, Eigenschaften, Verdikte, Presets, Claims, Randfälle, Oberfläche, Layout, Footer, Importe |

## Bewusst nicht umgesetzt

- Neue Rechenverfahren; das Schnittverfahren selbst (Stück 7 und 8); Beweise; Härtebeweise; große Instanzen; Komplexitätsklassen („Greedy-Härte“).
- Online- und Lernzweig als eigene Messung (zitiert aus Stück 13 und 14).
- Erklärseite „verständlich erklärt“ und Website-Einbindung (erst mit der vollständigen Linie).

## Lokal ausführen

```bash
pip install -r requirements.txt
streamlit run app.py
```

Tests: `pip install -r requirements-dev.txt`, dann `python -m pytest tests -q`. Die CI läuft mit Python 3.12 (`.github/workflows/tests.yml`); die in Streamlit Cloud eingestellte Python-Version ist beim Deploy zu nennen.

Gebaut mit Streamlit, Plotly und fpdf2.

---

Diese Demo ist Teil des Portfolios von [Sebastian Hanisch](https://sebastianhanisch.net) – Operations Research und Machine Learning ([Über mich](https://sebastianhanisch.net/ueber-mich.html)). Mehr zur Reihe: [Matroide: vom Spannbaum zur Verfahrenswahl](https://sebastianhanisch.net/konzepte-matroide.html).
