from __future__ import annotations

from games_for_grandpa.games.target_practice import (
    TARGETS_TO_WIN,
    TargetPracticeModel,
    TargetPracticeState,
)


def test_target_moves_and_bounces() -> None:
    model = TargetPracticeModel()
    model.target.x = 1190
    model.target.vx = 100

    model.update(0.1)

    assert model.target.x == 1160
    assert model.target.vx < 0


def test_hit_scores_and_completes() -> None:
    model = TargetPracticeModel()
    for _ in range(TARGETS_TO_WIN):
        assert model.shoot((round(model.target.x), round(model.target.y)))

    assert model.state is TargetPracticeState.COMPLETE
    assert model.score == TARGETS_TO_WIN
