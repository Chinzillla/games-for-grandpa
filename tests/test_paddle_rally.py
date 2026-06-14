from __future__ import annotations

import pytest

from games_for_grandpa.core import Difficulty
from games_for_grandpa.games.paddle_rally import (
    PLAY_BOTTOM,
    PLAY_TOP,
    Ball,
    Paddle,
    PaddleRallyModel,
    RallyEvent,
    TrackingAI,
    predict_intercept_y,
    reflect_coordinate,
)


def test_reflect_coordinate_handles_multiple_wall_bounces() -> None:
    assert reflect_coordinate(13, 0, 10) == 7
    assert reflect_coordinate(27, 0, 10) == 7
    assert reflect_coordinate(-3, 0, 10) == 3


def test_prediction_reflects_ball_path_between_walls() -> None:
    ball = Ball(x=100, y=200, vx=100, vy=200, radius=10)

    predicted = predict_intercept_y(ball, target_x=500)

    assert PLAY_TOP + ball.radius <= predicted <= PLAY_BOTTOM - ball.radius
    assert predicted == pytest.approx(360)


def test_player_paddle_is_clamped_to_play_area() -> None:
    model = PaddleRallyModel()

    model.move_player(-100)
    assert model.player.top == PLAY_TOP

    model.move_player(1000)
    assert model.player.bottom == PLAY_BOTTOM


def test_ball_reflects_from_top_wall() -> None:
    model = PaddleRallyModel()
    model.ball.y = PLAY_TOP + model.ball.radius - 1
    model.ball.vy = -200

    events = model.update(0.01)

    assert model.ball.vy > 0
    assert RallyEvent.WALL_HIT in events


def test_ball_bounces_from_player_paddle() -> None:
    model = PaddleRallyModel()
    model.ball.x = model.player.right + model.ball.radius - 1
    model.ball.y = model.player.y
    model.ball.vx = -300
    model.ball.vy = 0

    events = model.update(0.001)

    assert model.ball.vx > 0
    assert RallyEvent.PADDLE_HIT in events


def test_ai_movement_is_capped_by_speed() -> None:
    ai = TrackingAI(reaction_interval=0, max_speed=100, predictive=False)
    paddle = Paddle(x=1000, y=300)
    ball = Ball(x=500, y=600, vx=100, vy=0)

    new_y = ai.move(ball, paddle, dt=0.25)

    assert new_y == pytest.approx(325)


def test_difficulty_increases_ai_speed() -> None:
    easy = PaddleRallyModel(Difficulty.EASY)
    challenge = PaddleRallyModel(Difficulty.CHALLENGE)

    assert isinstance(easy.ai, TrackingAI)
    assert isinstance(challenge.ai, TrackingAI)
    assert challenge.ai.max_speed > easy.ai.max_speed
    assert challenge.ai.predictive


def test_missing_ball_awards_point_and_resets_ball() -> None:
    model = PaddleRallyModel()
    model.ball.x = -100

    events = model.update(0)

    assert model.computer_score == 1
    assert model.ball.x == 640
    assert RallyEvent.POINT in events
