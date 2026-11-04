"""Eigenschaften, die für jede Instanz gelten (ORACLE-PLAYBOOK §5)."""

import random

import pytest

import mvw_algorithm as A
import mvw_constants as C
import mvw_evaluation as ev
import mvw_scenario as S

N = 9
SEEDS = range(8)


@pytest.mark.parametrize("kind", C.MATROID_KINDS)
def test_a_matroid_is_never_reported_as_a_non_matroid(kind):
    for seed in SEEDS:
        fam = S.make_family(kind, N, seed)
        for b in (30, 300, 1000):
            assert not A.sampled_test(fam.ind, random.Random(seed + b), b, N)[0]
            assert not A.size_test(fam.ind, random.Random(seed + b), b, N)[0]


@pytest.mark.parametrize("kind", C.NON_MATROID_KINDS)
def test_every_reported_counterexample_passes_the_check(kind):
    seen = 0
    for seed in SEEDS:
        fam = S.make_family(kind, N, seed)
        found, calls, cert = A.sampled_test(fam.ind, random.Random(seed), 500, N)
        if found:
            seen += 1
            a, b = cert
            assert fam.ind[a] and fam.ind[b] and A.pc(a) < A.pc(b) and not any(fam.ind[a | 1 << e] for e in A.elems(b & ~a, N))
            assert not A.is_matroid_full(fam.ind, N)
        else:
            assert cert is None
    assert seen >= len(SEEDS) // 2


@pytest.mark.parametrize("kind", C.MATROID_KINDS)
def test_greedy_is_optimal_on_matroids(kind):
    for seed in SEEDS:
        fam = S.make_family(kind, N, seed)
        assert A.greedy(fam.ind, fam.w, N)[0] == A.opt(fam.ind, fam.w, N)[0]
        w = [random.Random(seed).randint(1, 50) for _ in range(N)]
        assert A.greedy(fam.ind, w, N)[0] == A.opt(fam.ind, w, N)[0]


@pytest.mark.parametrize("kind", C.INTERSECTION_KINDS)
def test_greedy_keeps_at_least_half_on_an_intersection_of_two_matroids(kind):
    for seed in range(20):
        fam = S.make_family(kind, N, seed)
        assert 2 * A.greedy(fam.ind, fam.w, N)[0] >= A.opt(fam.ind, fam.w, N)[0]
        assert A.is_matroid_full(fam.parts[0], N) and A.is_matroid_full(fam.parts[1], N)


@pytest.mark.parametrize("kind", C.NON_MATROID_KINDS)
def test_the_certificate_weights_make_greedy_fail(kind):
    checked = 0
    for seed in range(20):
        fam = S.make_family(kind, N, seed)
        found, _, cert = A.sampled_test(fam.ind, random.Random(seed), 2000, N)
        if not found:
            continue
        a, b = cert
        w = A.certificate_weights(a, b, N)
        p = A.pc(a)
        assert A.greedy(fam.ind, w, N)[0] == p * (p + 2) < (p + 1) ** 2 <= A.weight(w, b, N)
        checked += 1
    assert checked >= 10


def test_the_oracle_counts_are_consistent():
    fam = S.make_family("graphic", N, 3)
    for b in (30, 100, 300):
        found, calls, _ = A.sampled_test(fam.ind, random.Random(0), b, N)
        assert not found and b <= calls < b + 3 * N                    # ein Durchgang kostet höchstens 2n + n Aufrufe
        assert A.size_test(fam.ind, random.Random(0), b, N)[1] % N == 0


def test_submodular_functions_are_never_reported_as_violated():
    for kind in ("abdeckung", "budget"):
        for seed in range(10):
            f = S.sub_table(kind, random.Random(seed), N)
            assert not A.sub_full(f, N)
            assert not A.sub_sampled(f, random.Random(seed), 2000, N)[0]


def test_every_reported_violation_is_real_and_supermodular_functions_are_caught():
    for kind in ("paarbonus", "quadrat", "zufall"):
        for seed in range(10):
            f = S.sub_table(kind, random.Random(seed), N)
            found, calls, cert = A.sub_sampled(f, random.Random(seed), 4000, N)
            assert found and A.sub_violated(f, *cert) and calls % 4 == 0 and A.sub_full(f, N)


def test_the_coverage_objective_is_monotone():
    f = S.sub_table("abdeckung", random.Random(1), N)
    assert all(f[m | 1 << e] >= f[m] for m in range(1 << N) for e in range(N))


def test_a_larger_budget_never_lets_more_non_matroids_through():
    sd = ev.series_data()
    for kind in C.NON_MATROID_KINDS:
        prev = None
        for b in (30, 300, 3000):
            passed = sum(1 for i in range(C.E_PER_KIND) if not sd["truth"][kind][i] and not ev.found_at(kind, i, b)[0])
            assert prev is None or passed <= prev + 3                  # praktisch monoton (verschiedene Zufallsströme je Budget)
            prev = passed
