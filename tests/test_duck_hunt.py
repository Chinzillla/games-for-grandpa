from __future__ import annotations

import random

from games_for_grandpa.core import Difficulty
from games_for_grandpa.games.duck_hunt import (
    DUCKS_TO_COMPLETE,
    ESCAPE_MARGIN,
    FLIGHT_RIGHT,
    HIT_DISPLAY_SECONDS,
    STARTING_LIVES,
    DuckHuntEvent,
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


def test_duck_escape_removes_one_life_and_respawns() -> None:
    model = DuckHuntModel()
    model.duck.x = FLIGHT_RIGHT + ESCAPE_MARGIN + 1

    events = model.update(0)

    assert DuckHuntEvent.ESCAPED in events
    assert model.lives == STARTING_LIVES - 1
    assert model.state is DuckHuntState.PLAYING


def test_zero_lives_ends_duck_hunt() -> None:
    model = DuckHuntModel()
    model.lives = 1
    model.duck.x = FLIGHT_RIGHT + ESCAPE_MARGIN + 1

    events = model.update(0)

    assert DuckHuntEvent.GAME_OVER in events
    assert model.lives == 0
    assert model.state is DuckHuntState.GAME_OVER


def test_missed_shot_does_not_remove_points() -> None:
    model = DuckHuntModel()

    assert not model.shoot((0, 0))
    assert model.score == 0


def test_shooting_duck_completes_after_ten_hits() -> None:
    model = DuckHuntModel()

    for _ in range(DUCKS_TO_COMPLETE):
        assert model.shoot((round(model.duck.x), round(model.duck.y)))
        assert model.state is DuckHuntState.HIT
        model.update(HIT_DISPLAY_SECONDS)

    assert model.score == DUCKS_TO_COMPLETE
    assert model.state is DuckHuntState.COMPLETE


def test_difficulty_increases_speed_and_reduces_hit_radius() -> None:
    easy = DuckHuntModel(Difficulty.EASY)
    challenge = DuckHuntModel(Difficulty.CHALLENGE)

    assert abs(challenge.duck.vx) > abs(easy.duck.vx)
    assert challenge.hit_radius < easy.hit_radius
