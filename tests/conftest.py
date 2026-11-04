"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import mvw_scenario as S  # noqa: E402


@pytest.fixture
def hand():
    """Zuordnung mit drei Leitungen x = (oben 1, unten 1), y = (oben 1, unten 2), z = (oben 2, unten 1), Gewichte 1.
    Handrechnung: zulässig sind alle Mengen ohne doppelten Anschluss, also ∅, {x}, {y}, {z}, {y, z}; {x, y} und {x, z} nicht."""
    return S.hand_family()
