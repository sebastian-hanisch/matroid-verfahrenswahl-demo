"""Kern: Orakel mit Zähler, Matroid-Tests (Größentest, Austauschtest, vollständig), Greedy, Optimum, Zertifikat und Test auf Submodularität.

Mengen sind Bitmasken über n Elementen; die Familie liegt als Tabelle `t[mask]` (unabhängig oder nicht) vor, die Zielfunktion als Tabelle `f[mask]`.
Alles ist reine Python-Arithmetik und deterministisch bei festem Seed."""

from __future__ import annotations

import random


def pc(x: int) -> int:
    return bin(x).count("1")


def elems(mask: int, n: int) -> list[int]:
    return [i for i in range(n) if mask >> i & 1]


def table_of(pred, n: int) -> list[bool]:
    return [bool(pred(m)) for m in range(1 << n)]


class Oracle:
    """Unabhängigkeitsorakel: jede Abfrage der Tabelle zählt einen Aufruf."""

    def __init__(self, t):
        self.t = t
        self.calls = 0

    def __call__(self, mask: int) -> bool:
        self.calls += 1
        return self.t[mask]


# --- Tests auf die Matroid-Eigenschaft ------------------------------------------------------------------------------------------------------------


def random_maximal(orc: Oracle, rng: random.Random, n: int) -> tuple[int, list[int]]:
    """Zufällige maximale unabhängige Menge: Elemente in Zufallsreihenfolge, jedes bleibt, wenn die Menge unabhängig bleibt (n Aufrufe)."""
    order = list(range(n))
    rng.shuffle(order)
    cur, seq = 0, []
    for i in order:
        if orc(cur | 1 << i):
            cur |= 1 << i
            seq.append(i)
    return cur, seq


def check_certificate(t, a: int, b: int, n: int) -> bool:
    """Gegenbeispiel zum Austauschaxiom: a und b unabhängig, |a| < |b|, und kein Element von b ∖ a passt zu a."""
    return t[a] and t[b] and pc(a) < pc(b) and not any(t[a | 1 << e] for e in elems(b & ~a, n))


def sampled_test(t, rng: random.Random, budget: int, n: int) -> tuple[bool, int, tuple[int, int] | None]:
    """Gezogener Austauschtest: zwei zufällige maximale Mengen X, Y; A ist ein zufälliger Anfang von X. Gefunden, wenn |A| < |Y| und kein Element von Y ∖ A zu A passt.
    Rückgabe: (Gegenbeispiel gefunden, Orakelaufrufe, Gegenbeispiel (A, B))."""
    orc = Oracle(t)
    while orc.calls < budget:
        _, xs = random_maximal(orc, rng, n)
        y, _ = random_maximal(orc, rng, n)
        a = 0
        for e in xs[: rng.randint(0, len(xs))]:
            a |= 1 << e
        if pc(a) < pc(y) and not any(orc(a | 1 << e) for e in elems(y & ~a, n)):
            return True, orc.calls, (a, y)
    return False, orc.calls, None


def size_test(t, rng: random.Random, budget: int, n: int) -> tuple[bool, int]:
    """Größentest: Zufällige maximale Mengen ziehen; verschieden große sind ein Gegenbeispiel (in einem Matroid sind alle gleich groß)."""
    orc = Oracle(t)
    first = None
    while orc.calls < budget:
        x, _ = random_maximal(orc, rng, n)
        if first is None:
            first = pc(x)
        elif pc(x) != first:
            return True, orc.calls
    return False, orc.calls


def is_matroid_full(t, n: int) -> bool:
    """Vollständige Prüfung: Austausch für alle Paare unabhängiger Mengen mit |B| = |A| + 1 (daraus folgt er für beliebige |A| < |B|, weil Teilmengen unabhängig bleiben)."""
    by_size: dict[int, list[int]] = {}
    for m in range(1 << n):
        if t[m]:
            by_size.setdefault(pc(m), []).append(m)
    for size, sets in by_size.items():
        for a in sets:
            for b in by_size.get(size + 1, ()):
                if not any(t[a | 1 << e] for e in elems(b & ~a, n)):
                    return False
    return True


def is_hereditary(t, n: int) -> bool:
    return t[0] and all(not t[m] or all(t[m & ~(1 << i)] for i in elems(m, n)) for m in range(1 << n))


# --- Greedy, Optimum, Zertifikat --------------------------------------------------------------------------------------------------------------


def weight(w, mask: int, n: int) -> int:
    return sum(w[i] for i in elems(mask, n))


def opt(t, w, n: int) -> tuple[int, int]:
    """Optimum durch Aufzählung aller Mengen (Platzhalter für das Schnittverfahren oder ein ganzzahliges Programm)."""
    best, best_m = -1, 0
    for m in range(1 << n):
        if t[m]:
            v = weight(w, m, n)
            if v > best:
                best, best_m = v, m
    return best, best_m


def greedy(t, w, n: int) -> tuple[int, int, list[int]]:
    """Greedy nach absteigendem Gewicht (Gleichstand: kleinerer Index). Rückgabe: (Wert, Menge, gewählte Elemente in Reihenfolge)."""
    cur, picks = 0, []
    for i in sorted(range(n), key=lambda i: (-w[i], i)):
        if t[cur | 1 << i]:
            cur |= 1 << i
            picks.append(i)
    return weight(w, cur, n), cur, picks


def certificate_weights(a: int, b: int, n: int) -> list[int]:
    """Gewichte zum Gegenbeispiel (a, b) mit p = |a|: p + 2 auf a, p + 1 auf b ∖ a, sonst 0. Greedy erreicht p · (p + 2), b mindestens (p + 1)²."""
    p = pc(a)
    return [p + 2 if a >> i & 1 else p + 1 if b >> i & 1 else 0 for i in range(n)]


def opt_f(t, f, n: int) -> tuple[int, int]:
    best, best_m = -1, 0
    for m in range(1 << n):
        if t[m] and f[m] > best:
            best, best_m = f[m], m
    return best, best_m


def greedy_f(t, f, n: int) -> tuple[int, int]:
    """Greedy nach größtem Zuwachs der Zielfunktion f unter der Familie t, solange der Zuwachs positiv ist."""
    cur = 0
    while True:
        best, best_e = 0, -1
        for e in range(n):
            if not cur >> e & 1 and t[cur | 1 << e]:
                gain = f[cur | 1 << e] - f[cur]
                if gain > best:
                    best, best_e = gain, e
        if best_e < 0:
            return f[cur], cur
        cur |= 1 << best_e


# --- Test auf Submodularität ------------------------------------------------------------------------------------------------------------------


def sub_violated(f, a: int, e: int, g: int) -> bool:
    return f[a | 1 << e] + f[a | 1 << g] < f[a | 1 << e | 1 << g] + f[a]


def sub_sampled(f, rng: random.Random, budget: int, n: int) -> tuple[bool, int, tuple[int, int, int] | None]:
    """Gezogener Test: Menge A, zwei Elemente e, g außerhalb; verletzt, wenn f(A+e) + f(A+g) < f(A+e+g) + f(A). Vier Aufrufe je Ziehung."""
    calls = 0
    while calls + 4 <= budget:
        a = rng.getrandbits(n)
        out = [i for i in range(n) if not a >> i & 1]
        if len(out) < 2:
            continue
        e, g = rng.sample(out, 2)
        calls += 4
        if sub_violated(f, a, e, g):
            return True, calls, (a, e, g)
    return False, calls, None


def sub_full(f, n: int) -> bool:
    """Wahr, wenn irgendwo verletzt (vollständige Prüfung über alle A, e, g)."""
    for a in range(1 << n):
        out = [i for i in range(n) if not a >> i & 1]
        for x in range(len(out)):
            for y in range(x + 1, len(out)):
                if sub_violated(f, a, out[x], out[y]):
                    return True
    return False
