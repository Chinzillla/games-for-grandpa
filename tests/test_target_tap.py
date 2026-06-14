from __future__ import annotations

import random

from games_for_grandpa.core import Difficulty
from games_for_grandpa.games.target_tap import (
    TARGETS_TO_COMPLETE,
    TargetPosition,
    TargetScheduler,
    TargetTapModel,
    TargetTapState,
)


def test_scheduler_does_not_repeat_recent_positions() -> None:
    positions = [TargetPosition(index, 0) for index in range(6)]
    scheduler = TargetScheduler(positions, recent_count=3, rng=random.Random(7))

    generated = [scheduler.next_position() for _ in range(20)]

    for index, position in enumerate(generated):
        assert position not in generated[max(0, index - 3) : index]


def test_miss_does_not_remove_points_or_move_target() -> None:
    model = TargetTapModel()
    original_target = model.target

    hit = model.click((0, 0))

    assert not hit
    assert model.score == 0
    assert model.target == original_target


def test_clicking_target_scores_and_finishes_after_ten_hits() -> None:
    model = TargetTapModel()

    for _ in range(TARGETS_TO_COMPLETE):
        assert model.click((model.target.x, model.target.y))

    assert model.score == TARGETS_TO_COMPLETE
    assert model.state is TargetTapState.COMPLETE


def test_difficulty_changes_target_size() -> None:
    model = TargetTapModel(Difficulty.EASY)
    easy_radius = model.radius

    model.reset(Difficulty.CHALLENGE)

    assert model.radius < easy_radius
    assert model.score == 0
    assert model.state is TargetTapState.PLAYING

