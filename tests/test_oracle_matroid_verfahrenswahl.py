"""Orakel (ORACLE-PLAYBOOK §5): die Familien gegen eigene, unabhängige Definitionen der Zulässigkeit; Matroid-Eigenschaft erschöpfend; Optimum durch Aufzählung.

Die App prüft Wälder mit Union-Find, Zerlegungen durch Teilmengenaufzählung, Rang binär über eine Eliminationsbasis. Hier: Komponentenzählung mit Breitensuche, die Formel
|T| ≤ r₁(T) + r₂(T) für alle T ⊆ S (Matroidvereinigung), alle Teilmengensummen verschieden (lineare Unabhängigkeit über GF(2)), Endpunktpaare."""

import random
from collections import Counter
from itertools import combinations

import pytest

import mvw_algorithm as A
import mvw_constants as C
import mvw_scenario as S


def members(mask, n):
    return [i for i in range(n) if mask >> i & 1]


def forest_rank(edges, idx):
    """Rang der Zyklenmatroide der Kanten idx: Knoten minus Komponenten, per Breitensuche."""
    adj = {}
    for i in idx:
        u, v = edges[i]
        adj.setdefault(u, set()).add(v)
        adj.setdefault(v, set()).add(u)
    seen, comps = set(), 0
    for s in adj:
        if s in seen:
            continue
        comps += 1
        stack = [s]
        seen.add(s)
        while stack:
            x = stack.pop()
            for y in adj[x]:
                if y not in seen:
                    seen.add(y)
                    stack.append(y)
    return len(adj) - comps


def is_forest(edges, idx):
    return forest_rank(edges, idx) == len(idx)


def independent(fam, mask):
    n, d = fam.n, fam.data
    idx = members(mask, n)
    k = fam.kind
    if k == "uniform":
        return len(idx) <= d["k"]
    if k == "partition":
        cnt = Counter(d["col"][i] for i in idx)
        return all(cnt[c] <= d["cap"][c] for c in cnt)
    if k == "graphic":
        return is_forest(d["edges"], idx)
    if k == "binary":
        sums = set()
        for r in range(len(idx) + 1):
            for sub in combinations(idx, r):
                x = 0
                for i in sub:
                    x ^= d["vec"][i]
                sums.add(x)
        return len(sums) == 2 ** len(idx)                              # alle Teilmengensummen verschieden: linear unabhängig
    if k == "union2":
        return all(len(t) <= 2 * forest_rank(d["edges"], t) for r in range(len(idx) + 1) for t in combinations(idx, r))
    if k == "bimatch":
        return all(d["edges"][a][0] != d["edges"][b][0] and d["edges"][a][1] != d["edges"][b][1] for a, b in combinations(idx, 2))
    if k == "rainbow":
        return is_forest(d["edges"], idx) and len({d["col"][i] for i in idx}) == len(idx)
    if k == "stable":
        return not any(a in idx and b in idx for a, b in d["conf"])
    if k == "knapsack":
        return sum(d["size"][i] for i in idx) <= d["cap"]
    if k == "gmatch":
        return all(not set(d["edges"][a]) & set(d["edges"][b]) for a, b in combinations(idx, 2))
    raise AssertionError(k)


def exchange_axiom_everywhere(t, n):
    ind = [m for m in range(1 << n) if t[m]]
    return all(any(t[a | 1 << e] for e in members(b & ~a, n)) for a in ind for b in ind if A.pc(a) < A.pc(b))


@pytest.mark.parametrize("kind", C.KINDS)
def test_every_family_matches_its_independent_definition(kind):
    for seed in range(4):
        fam = S.make_family(kind, 8, seed)
        assert all(fam.ind[m] == independent(fam, m) for m in range(1 << 8)), (kind, seed)
        assert fam.ind[0] and A.is_hereditary(fam.ind, 8)


@pytest.mark.parametrize("kind", C.KINDS)
def test_the_exhaustive_check_equals_the_full_exchange_axiom(kind):
    for seed in range(4):
        fam = S.make_family(kind, 7, seed)
        assert A.is_matroid_full(fam.ind, 7) == exchange_axiom_everywhere(fam.ind, 7), (kind, seed)


@pytest.mark.parametrize("kind", C.MATROID_KINDS)
def test_the_five_matroid_families_are_matroids(kind):
    assert all(A.is_matroid_full(S.make_family(kind, 8, seed).ind, 8) for seed in range(6))


def test_the_intersection_parts_are_matroids_and_intersect_to_the_family():
    for kind in C.INTERSECTION_KINDS:
        for seed in range(4):
            fam = S.make_family(kind, 8, seed)
            ta, tb = fam.parts
            assert A.is_matroid_full(ta, 8) and A.is_matroid_full(tb, 8)
            assert all(fam.ind[m] == (ta[m] and tb[m]) for m in range(1 << 8))


def test_the_optimum_equals_a_second_enumeration_over_all_subsets():
    fam = S.make_family("knapsack", 9, 4)
    best = max(sum(fam.w[i] for i in members(m, 9)) for m in range(1 << 9) if independent(fam, m))
    assert A.opt(fam.ind, fam.w, 9)[0] == best


def test_greedy_value_is_a_feasible_value_not_above_the_optimum():
    for kind in C.KINDS:
        for seed in range(3):
            fam = S.make_family(kind, 8, seed)
            g, mask, picks = A.greedy(fam.ind, fam.w, 8)
            assert independent(fam, mask) and g == sum(fam.w[i] for i in picks) and g <= A.opt(fam.ind, fam.w, 8)[0]


def test_the_union_family_is_a_matroid_with_the_rank_formula():
    fam = S.make_family("union2", 7, 2)
    d = fam.data["edges"]
    for m in range(1 << 7):
        idx = members(m, 7)
        rank = max(len(s) for r in range(len(idx) + 1) for s in combinations(idx, r) if fam.ind[sum(1 << i for i in s)])
        assert rank == min(len(idx) - len(y) + 2 * forest_rank(d, y) for r in range(len(idx) + 1) for y in combinations(idx, r))
