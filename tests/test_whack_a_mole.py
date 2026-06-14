from __future__ import annotations

import random

from games_for_grandpa.games.whack_a_mole import MOLES_TO_WIN, WhackAMoleModel, WhackState


def test_mole_moves_when_timer_runs_out() -> None:
    model = WhackAMoleModel(rng=random.Random(1))
    first = model.active_hole

    model.update(2.0)

    assert model.active_hole != first


def test_whacking_active_mole_scores_and_completes() -> None:
    model = WhackAMoleModel(rng=random.Random(2))

    for _ in range(MOLES_TO_WIN):
        assert model.whack(model.active_hole)

    assert model.score == MOLES_TO_WIN
    assert model.state is WhackState.COMPLETE


def test_wrong_hole_does_not_score() -> None:
    model = WhackAMoleModel(rng=random.Random(3))
    wrong_hole = (model.active_hole + 1) % 9

    assert not model.whack(wrong_hole)
    assert model.score == 0
