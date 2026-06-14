from __future__ import annotations

import random

from games_for_grandpa.core import Difficulty
from games_for_grandpa.games.duck_hunt import (
    DUCKS_TO_COMPLETE,
    FLIGHT_LEFT,
    DuckHuntModel,
    DuckHuntState,
    FlightScheduler,
)


def test_scheduler_avoids_three_recent_flight_patterns() -> None:
    scheduler = FlightScheduler(rng=random.Random(9))
    generated = [scheduler.next_pattern() for _ in range(30)]

    for index, pattern in enumerate(generated):
        assert pattern not in generated[max(0, index - 3) : index]


def test_duck_moves_with_elapsed_time() -> None:
    model = DuckHuntModel()
    start = (model.duck.x, model.duck.y)

    model.update(0.5)

    assert (model.duck.x, model.duck.y) != start


def test_duck_reflects_at_flight_boundary() -> None:
    model = DuckHuntModel()
    model.duck.x = FLIGHT_LEFT - 1
    model.duck.vx = -100

    model.update(0)

    assert model.duck.x == FLIGHT_LEFT
    assert model.duck.vx > 0


def test_missed_shot_does_not_remove_points() -> None:
    model = DuckHuntModel()

    assert not model.shoot((0, 0))
    assert model.score == 0


def test_shooting_duck_completes_after_ten_hits() -> None:
    model = DuckHuntModel()

    for _ in range(DUCKS_TO_COMPLETE):
        assert model.shoot((round(model.duck.x), round(model.duck.y)))

    assert model.score == DUCKS_TO_COMPLETE
    assert model.state is DuckHuntState.COMPLETE


def test_difficulty_increases_speed_and_reduces_hit_radius() -> None:
    easy = DuckHuntModel(Difficulty.EASY)
    challenge = DuckHuntModel(Difficulty.CHALLENGE)

    assert abs(challenge.duck.vx) > abs(easy.duck.vx)
    assert challenge.hit_radius < easy.hit_radius
