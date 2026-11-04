"""Szenario: die zehn Familien zulässiger Leitungsmengen und die Zielfunktionen (Abdeckung, Paarbonus, Vergleichsfamilien).

Jede Familie liegt als Tabelle der unabhängigen (zulässigen) Mengen über n Leitungen vor, dazu ganzzahlige Gewichte. Der Erzeuger zieht in fester Reihenfolge
aus einem `random.Random`, damit die Messreihen der App die Rechnung der Phase 0 sind."""

from __future__ import annotations

import random
from dataclasses import dataclass
from itertools import combinations

import mvw_algorithm as A
import mvw_constants as C


class UF:
    def __init__(self, n: int):
        self.p = list(range(n))

    def find(self, a: int) -> int:
        while self.p[a] != a:
            self.p[a] = self.p[self.p[a]]
            a = self.p[a]
        return a

    def union(self, a: int, b: int) -> bool:
        a, b = self.find(a), self.find(b)
        if a == b:
            return False
        self.p[a] = b
        return True


def forest(edges, mask: int, n: int) -> bool:
    uf = UF(8)
    for i in A.elems(mask, n):
        u, v = edges[i]
        if not uf.union(u, v):
            return False
    return True


@dataclass
class Family:
    kind: str
    n: int
    ind: list[bool]
    w: list[int]
    parts: tuple | None          # bei Schnitt-Familien die beiden Matroid-Tabellen (die Zerlegung wird mitgeliefert), sonst None
    details: list[str]           # eine Zeile je Leitung (Verbindung, Farbe, Größe …)
    data: dict                   # die Parameter der Instanz (Kanten, Farben, Konflikte …), für die unabhängigen Prüfungen in den Tests

    @property
    def is_matroid_truth(self) -> bool:
        return A.is_matroid_full(self.ind, self.n)


def node(i: int) -> str:
    return chr(65 + i)


def gen(kind: str, rng: random.Random, n: int) -> Family:
    """Eine Instanz der Familie `kind` mit n Leitungen. Reihenfolge der Ziehungen wie in der Phase 0 (Gewichte zuerst)."""
    w = [rng.randint(1, C.WEIGHT_MAX) for _ in range(n)]
    parts = None
    data: dict = {}
    if kind == "uniform":
        k = rng.randint(2, n - 3)
        data = {"k": k}
        t = A.table_of(lambda m: A.pc(m) <= k, n)
        details = [f"höchstens {k} Leitungen insgesamt" for _ in range(n)]
    elif kind == "partition":
        col = [rng.randrange(3) for _ in range(n)]
        cap = [rng.randint(1, 3) for _ in range(3)]
        data = {"col": col, "cap": cap}
        t = A.table_of(lambda m: all(sum(1 for i in A.elems(m, n) if col[i] == c) <= cap[c] for c in range(3)), n)
        details = [f"Farbe {col[i] + 1} (höchstens {cap[col[i]]})" for i in range(n)]
    elif kind == "graphic":
        edges = [tuple(rng.sample(range(6), 2)) for _ in range(n)]
        data = {"edges": edges}
        t = A.table_of(lambda m: forest(edges, m, n), n)
        details = [f"{node(u)}–{node(v)}" for u, v in edges]
    elif kind == "binary":
        vec = [rng.randint(0, 15) for _ in range(n)]
        data = {"vec": vec}

        def indep(m):
            basis = []
            for i in A.elems(m, n):
                x = vec[i]
                for b in basis:
                    x = min(x, x ^ b)
                if x == 0:
                    return False
                basis.append(x)
            return True
        t = A.table_of(indep, n)
        details = [f"Spalte {vec[i]:04b}" for i in range(n)]
    elif kind == "union2":
        edges = [tuple(rng.sample(range(5), 2)) for _ in range(n)]
        data = {"edges": edges}
        f = A.table_of(lambda m: forest(edges, m, n), n)
        t = [False] * (1 << n)
        for m in range(1 << n):
            sub = m
            while True:
                if f[sub] and f[m ^ sub]:
                    t[m] = True
                    break
                if sub == 0:
                    break
                sub = (sub - 1) & m
        details = [f"{node(u)}–{node(v)}" for u, v in edges]
    elif kind == "bimatch":
        edges = [(rng.randrange(5), rng.randrange(5)) for _ in range(n)]
        data = {"edges": edges}
        ta = A.table_of(lambda m: len({edges[i][0] for i in A.elems(m, n)}) == A.pc(m), n)
        tb = A.table_of(lambda m: len({edges[i][1] for i in A.elems(m, n)}) == A.pc(m), n)
        t = [a and b for a, b in zip(ta, tb)]
        parts = (ta, tb)
        details = [f"oben {u + 1} – unten {v + 1}" for u, v in edges]
    elif kind == "rainbow":
        edges = [tuple(rng.sample(range(6), 2)) for _ in range(n)]
        col = [rng.randrange(4) for _ in range(n)]
        data = {"edges": edges, "col": col}
        ta = A.table_of(lambda m: forest(edges, m, n), n)
        tb = A.table_of(lambda m: len({col[i] for i in A.elems(m, n)}) == A.pc(m), n)
        t = [a and b for a, b in zip(ta, tb)]
        parts = (ta, tb)
        details = [f"{node(u)}–{node(v)}, Farbe {col[i] + 1}" for i, (u, v) in enumerate(edges)]
    elif kind == "stable":
        conf = [(a, b) for a, b in combinations(range(n), 2) if rng.random() < 0.25]
        data = {"conf": conf}
        t = A.table_of(lambda m: not any(m >> a & 1 and m >> b & 1 for a, b in conf), n)
        details = [("Konflikt mit " + ", ".join(str(b + 1 if a == i else a + 1) for a, b in conf if i in (a, b))) if any(i in c for c in conf) else "kein Konflikt" for i in range(n)]
    elif kind == "knapsack":
        size = [rng.randint(1, 6) for _ in range(n)]
        cap = sum(size) // 3
        data = {"size": size, "cap": cap}
        t = A.table_of(lambda m: sum(size[i] for i in A.elems(m, n)) <= cap, n)
        details = [f"Größe {size[i]} (Summe höchstens {cap})" for i in range(n)]
    elif kind == "gmatch":
        edges = [tuple(rng.sample(range(6), 2)) for _ in range(n)]
        data = {"edges": edges}

        def indep_g(m):
            ends = [x for i in A.elems(m, n) for x in edges[i]]
            return len(ends) == len(set(ends))
        t = A.table_of(indep_g, n)
        details = [f"{node(u)}–{node(v)}" for u, v in edges]
    else:
        raise ValueError(kind)
    return Family(kind, n, t, w, parts, details, data)


def make_family(kind: str, n: int, seed: int) -> Family:
    return gen(kind, random.Random(seed), n)


# --- Zielfunktionen ---------------------------------------------------------------------------------------------------------------------------


def sub_table(kind: str, rng: random.Random, n: int) -> list[int]:
    """Tabelle f[mask] einer Zielfunktion über n Elemente. abdeckung/paarbonus/einpaar: Abdeckung von 40 Haushalten (je Leitung 15 %); budget: min(Summe, Deckel);
    quadrat: |S|²; zufall: Zufallswerte."""
    if kind in ("abdeckung", "paarbonus", "einpaar"):
        cover = [sum(1 << h for h in range(C.HOUSEHOLDS) if rng.random() < 0.15) for _ in range(n)]
        bonus = {}
        if kind == "paarbonus":
            for a, b in combinations(range(n), 2):
                if rng.random() < 0.3:
                    bonus[(a, b)] = rng.randint(2, 6)
        if kind == "einpaar":
            bonus[tuple(sorted(rng.sample(range(n), 2)))] = 1

        def f(m):
            c = 0
            for i in range(n):
                if m >> i & 1:
                    c |= cover[i]
            v = A.pc(c)
            for (a, b), z in bonus.items():
                if m >> a & 1 and m >> b & 1:
                    v += z
            return v
    elif kind == "budget":
        w = [rng.randint(1, 9) for _ in range(n)]
        cap = sum(w) // 2

        def f(m):
            return min(cap, sum(w[i] for i in range(n) if m >> i & 1))
    elif kind == "quadrat":
        def f(m):
            return A.pc(m) ** 2
    else:
        tab = [rng.randint(0, 30) for _ in range(1 << n)]

        def f(m):
            return tab[m]
    return [f(m) for m in range(1 << n)]


def objective_table(objective: str, n: int, seed: int) -> list[int] | None:
    """Zielfunktion der Hauptansicht; `summe` ist modular (None: die Gewichte der Familie gelten)."""
    if objective == "summe":
        return None
    return sub_table("abdeckung" if objective == "abdeckung" else "paarbonus", random.Random(f"{seed}-{objective}"), n)


# --- Handbeispiel: Zuordnung mit drei Leitungen -----------------------------------------------------------------------------------------------


def hand_family() -> Family:
    """x = (oben 1, unten 1), y = (oben 1, unten 2), z = (oben 2, unten 1); Gewichte 1. Greedy (Reihenfolge x, y, z) nimmt x und sperrt y und z."""
    edges = [(0, 0), (0, 1), (1, 0)]
    n = 3
    ta = A.table_of(lambda m: len({edges[i][0] for i in A.elems(m, n)}) == A.pc(m), n)
    tb = A.table_of(lambda m: len({edges[i][1] for i in A.elems(m, n)}) == A.pc(m), n)
    return Family("bimatch", n, [a and b for a, b in zip(ta, tb)], [1, 1, 1], (ta, tb), ["oben 1 – unten 1", "oben 1 – unten 2", "oben 2 – unten 1"], {"edges": edges})
