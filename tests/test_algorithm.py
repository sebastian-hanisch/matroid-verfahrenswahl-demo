"""Kern an der Mini-Instanz von Hand (DEMO-PLAYBOOK §1b): Orakelzähler, Tests, Greedy, Optimum, Zertifikat, Submodularität, Formatierung."""

import random

import mvw_algorithm as A
import mvw_evaluation as ev

X, Y, Z = 0b001, 0b010, 0b100


def test_the_hand_family_has_the_five_admissible_sets(hand):
    assert [m for m in range(8) if hand.ind[m]] == [0, X, Y, Z, Y | Z]
    assert A.is_hereditary(hand.ind, 3) and not A.is_matroid_full(hand.ind, 3)


def test_oracle_counts_every_call(hand):
    orc = A.Oracle(hand.ind)
    assert orc(X) and not orc(X | Y) and orc.calls == 2
    orc(0)
    assert orc.calls == 3


def test_random_maximal_sets_are_x_or_yz_and_cost_n_calls(hand):
    sizes = set()
    for seed in range(30):
        orc = A.Oracle(hand.ind)
        mask, seq = A.random_maximal(orc, random.Random(seed), 3)
        assert orc.calls == 3 and mask in (X, Y | Z) and sum(1 << e for e in seq) == mask
        sizes.add(mask)
    assert sizes == {X, Y | Z}


def test_certificate_check_by_hand(hand):
    assert A.check_certificate(hand.ind, X, Y | Z, 3)                 # x + y und x + z sind gesperrt
    assert not A.check_certificate(hand.ind, Y, Y | Z, 3)             # y + z ist zulässig
    assert not A.check_certificate(hand.ind, Y | Z, X, 3)             # |A| < |B| verletzt
    assert not A.check_certificate(hand.ind, X, Y, 3)                 # gleich groß
    assert not A.check_certificate(hand.ind, X | Y, Z, 3)             # {x, y} ist selbst unzulässig


def test_sampled_and_size_test_find_the_counterexample_and_report_a_valid_certificate(hand):
    found, calls, cert = A.sampled_test(hand.ind, random.Random(1), 300, 3)
    assert found and cert is not None and A.check_certificate(hand.ind, *cert, 3) and calls < 300 + 12
    f2, c2 = A.size_test(hand.ind, random.Random(1), 60, 3)
    assert f2 and c2 % 3 == 0 and c2 >= 6                              # mindestens zwei maximale Mengen zu je 3 Aufrufen


def test_tests_never_flag_a_uniform_matroid():
    t = A.table_of(lambda m: A.pc(m) <= 2, 4)                          # U(2, 4)
    assert A.is_matroid_full(t, 4)
    for seed in range(20):
        assert not A.sampled_test(t, random.Random(seed), 200, 4)[0]
        assert not A.size_test(t, random.Random(seed), 200, 4)[0]


def test_budget_stops_the_test_without_a_finding(hand):
    found, calls, cert = A.sampled_test(hand.ind, random.Random(1), 0, 3)
    assert (found, calls, cert) == (False, 0, None)


def test_greedy_and_optimum_on_the_hand_family(hand):
    assert A.greedy(hand.ind, hand.w, 3) == (1, X, [0])               # Gleichstand: kleinster Index zuerst, danach sind y und z gesperrt
    assert A.opt(hand.ind, hand.w, 3) == (2, Y | Z)
    assert A.greedy(hand.ind, [1, 5, 4], 3)[0] == 9                    # y (5) und z (4)
    assert A.weight([3, 2, 2], Y | Z, 3) == 4


def test_certificate_weights_make_greedy_fail_by_hand(hand):
    w = A.certificate_weights(X, Y | Z, 3)
    assert w == [3, 2, 2] and A.greedy(hand.ind, w, 3)[0] == 3 and A.weight(w, Y | Z, 3) == 4
    assert A.certificate_weights(0b0011, 0b1110, 4) == [4, 4, 3, 3]    # p = 2: p + 2 auf A, p + 1 auf B ohne A (Element 0 liegt nur in A)


def test_greedy_on_a_matroid_equals_the_optimum():
    t = A.table_of(lambda m: A.pc(m) <= 2, 4)
    w = [5, 9, 1, 7]
    assert A.greedy(t, w, 4)[0] == A.opt(t, w, 4)[0] == 16


def test_full_check_detects_a_missing_exchange():
    t = A.table_of(lambda m: m not in (0b11,), 2)                      # {0, 1} gesperrt, Einzelne zulässig: U(1, 2), ein Matroid
    assert A.is_matroid_full(t, 2)
    t3 = A.table_of(lambda m: m in (0, 1, 2, 4, 6), 3)                 # die Hand-Familie
    assert not A.is_matroid_full(t3, 3)
    assert not A.is_hereditary(A.table_of(lambda m: m in (0, 3), 2), 2)


def test_submodularity_by_hand():
    cover = [{1, 2}, {2, 3}]
    f = [len(set().union(*[cover[i] for i in range(2) if m >> i & 1])) for m in range(4)]
    assert f == [0, 2, 2, 3]
    assert not A.sub_violated(f, 0, 0, 1) and not A.sub_full(f, 2)    # 2 + 2 >= 3 + 0
    sq = [A.pc(m) ** 2 for m in range(4)]
    assert A.sub_violated(sq, 0, 0, 1) and A.sub_full(sq, 2)           # 1 + 1 < 4 + 0
    found, calls, cert = A.sub_sampled(sq, random.Random(0), 40, 2)
    assert found and calls % 4 == 0 and A.sub_violated(sq, *cert)
    assert A.sub_sampled(f, random.Random(0), 3, 2) == (False, 0, None)  # weniger als eine Ziehung im Budget
    assert A.sub_sampled(f, random.Random(0), 40, 2) == (False, 40, None)


def test_greedy_and_optimum_for_a_coverage_function():
    cover = [{1, 2}, {2, 3}, {4}]
    f = [len(set().union(*[cover[i] for i in range(3) if m >> i & 1])) for m in range(8)]
    t = A.table_of(lambda m: A.pc(m) <= 2, 3)
    assert [f[m] for m in (0b011, 0b101, 0b110)] == [3, 3, 3]          # alle Paare decken drei Haushalte
    assert A.greedy_f(t, f, 3) == (3, 0b011)                           # Gleichstand der Zuwächse: kleinster Index zuerst
    assert A.opt_f(t, f, 3) == (3, 0b011)


def test_formatting_helpers():
    assert ev.num(3.0) == "3" and ev.num(0.5) == "0,5" and ev.num(-2.0) == "−2" and ev.num(12.84) == "12,84"
    assert ev.zahl(1048576) == "1 048 576" and ev.zahl(-5) == "−5"
    assert ev.quot(0.7333) == "0,733" and ev.prozent(0.0394) == "3,9 %" and ev.prozent2(0.0202) == "2,02 %" and ev.von(3, 10) == "3 von 10"
    assert ev.mask_text(0b101, 3) == "{1, 3}" and ev.mask_text(0, 3) == "∅"
