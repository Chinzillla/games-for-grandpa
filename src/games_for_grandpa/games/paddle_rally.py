from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from games_for_grandpa.core import Difficulty

PLAY_LEFT = 40.0
PLAY_RIGHT = 1240.0
PLAY_TOP = 140.0
PLAY_BOTTOM = 690.0
WINNING_SCORE = 5


def clamp(value: float, minimum: float, maximum: float) -> float:
    return max(minimum, min(value, maximum))


@dataclass(slots=True)
class Paddle:
    x: float
    y: float
    width: float = 28.0
    height: float = 150.0

    @property
    def left(self) -> float:
        return self.x - self.width / 2

    @property
    def right(self) -> float:
        return self.x + self.width / 2

    @property
    def top(self) -> float:
        return self.y - self.height / 2

    @property
    def bottom(self) -> float:
        return self.y + self.height / 2


@dataclass(slots=True)
class Ball:
    x: float
    y: float
    vx: float
    vy: float
    radius: float = 16.0


class RallyState(Enum):
    PLAYING = "playing"
    PLAYER_WON = "player_won"
    COMPUTER_WON = "computer_won"


class RallyEvent(Enum):
    PADDLE_HIT = "paddle_hit"
    WALL_HIT = "wall_hit"
    POINT = "point"
    COMPLETE = "complete"


class PaddleAI(Protocol):
    def move(
        self,
        ball: Ball,
        paddle: Paddle,
        dt: float,
    ) -> float: ...


def reflect_coordinate(value: float, minimum: float, maximum: float) -> float:
    """Reflect an unbounded coordinate between two walls in O(1)."""
    span = maximum - minimum
    if span <= 0:
        raise ValueError("Reflection bounds must have positive size")
    period = 2 * span
    normalized = (value - minimum) % period
    if normalized <= span:
        return minimum + normalized
    return maximum - (normalized - span)


def predict_intercept_y(ball: Ball, target_x: float) -> float:
    if ball.vx <= 0:
        return (PLAY_TOP + PLAY_BOTTOM) / 2
    travel_time = max(0.0, (target_x - ball.x) / ball.vx)
    projected = ball.y + ball.vy * travel_time
    # DSA: Mirroring a projected coordinate replaces step-by-step simulation with O(1) math.
    return reflect_coordinate(
        projected,
        PLAY_TOP + ball.radius,
        PLAY_BOTTOM - ball.radius,
    )


class TrackingAI:
    def __init__(
        self,
        *,
        reaction_interval: float,
        max_speed: float,
        predictive: bool,
    ) -> None:
        self.reaction_interval = reaction_interval
        self.max_speed = max_speed
        self.predictive = predictive
        self.time_until_reaction = 0.0
        self.target_y = (PLAY_TOP + PLAY_BOTTOM) / 2

    def move(self, ball: Ball, paddle: Paddle, dt: float) -> float:
        self.time_until_reaction -= dt
        if self.time_until_reaction <= 0:
            self.time_until_reaction = self.reaction_interval
            if ball.vx > 0:
                self.target_y = (
                    predict_intercept_y(ball, paddle.x) if self.predictive else ball.y
                )
            else:
                self.target_y = (PLAY_TOP + PLAY_BOTTOM) / 2

        difference = self.target_y - paddle.y
        step = clamp(difference, -self.max_speed * dt, self.max_speed * dt)
        minimum = PLAY_TOP + paddle.height / 2
        maximum = PLAY_BOTTOM - paddle.height / 2
        return clamp(paddle.y + step, minimum, maximum)


def ai_for(difficulty: Difficulty) -> PaddleAI:
    if difficulty is Difficulty.EASY:
        return TrackingAI(reaction_interval=0.45, max_speed=250.0, predictive=False)
    if difficulty is Difficulty.NORMAL:
        return TrackingAI(reaction_interval=0.20, max_speed=380.0, predictive=False)
    return TrackingAI(reaction_interval=0.08, max_speed=520.0, predictive=True)


class PaddleRallyModel:
    def __init__(
        self,
        difficulty: Difficulty = Difficulty.EASY,
        *,
        ai: PaddleAI | None = None,
        rng: random.Random | None = None,
    ) -> None:
        self.difficulty = difficulty
        self.rng = rng or random.Random()
        center_y = (PLAY_TOP + PLAY_BOTTOM) / 2
        self.player = Paddle(90.0, center_y)
        self.computer = Paddle(1190.0, center_y)
        self.ai = ai or ai_for(difficulty)
        self.player_score = 0
        self.computer_score = 0
        self.state = RallyState.PLAYING
        self.ball = Ball(640.0, center_y, -430.0, 180.0)

    def move_player(self, mouse_y: float) -> None:
        self.player.y = clamp(
            mouse_y,
            PLAY_TOP + self.player.height / 2,
            PLAY_BOTTOM - self.player.height / 2,
        )

    def update(self, dt: float) -> set[RallyEvent]:
        if self.state is not RallyState.PLAYING:
            return set()

        events: set[RallyEvent] = set()
        self.computer.y = self.ai.move(self.ball, self.computer, dt)
        self.ball.x += self.ball.vx * dt
        self.ball.y += self.ball.vy * dt

        if self.ball.y - self.ball.radius <= PLAY_TOP:
            self.ball.y = PLAY_TOP + self.ball.radius
            self.ball.vy = abs(self.ball.vy)
            events.add(RallyEvent.WALL_HIT)
        elif self.ball.y + self.ball.radius >= PLAY_BOTTOM:
            self.ball.y = PLAY_BOTTOM - self.ball.radius
            self.ball.vy = -abs(self.ball.vy)
            events.add(RallyEvent.WALL_HIT)

        if self._hits_paddle(self.player) and self.ball.vx < 0:
            self.ball.x = self.player.right + self.ball.radius
            self._bounce_from(self.player, direction=1)
            events.add(RallyEvent.PADDLE_HIT)
        elif self._hits_paddle(self.computer) and self.ball.vx > 0:
            self.ball.x = self.computer.left - self.ball.radius
            self._bounce_from(self.computer, direction=-1)
            events.add(RallyEvent.PADDLE_HIT)

        if self.ball.x + self.ball.radius < PLAY_LEFT:
            self.computer_score += 1
            events |= self._after_point(direction=-1)
        elif self.ball.x - self.ball.radius > PLAY_RIGHT:
            self.player_score += 1
            events |= self._after_point(direction=1)
        return events

    def _hits_paddle(self, paddle: Paddle) -> bool:
        # DSA: Axis-aligned overlap checks collision in constant O(1) time.
        return (
            self.ball.x + self.ball.radius >= paddle.left
            and self.ball.x - self.ball.radius <= paddle.right
            and self.ball.y + self.ball.radius >= paddle.top
            and self.ball.y - self.ball.radius <= paddle.bottom
        )

    def _bounce_from(self, paddle: Paddle, *, direction: int) -> None:
        speed = min(abs(self.ball.vx) * 1.035, 700.0)
        self.ball.vx = speed * direction
        relative_hit = clamp((self.ball.y - paddle.y) / (paddle.height / 2), -1.0, 1.0)
        self.ball.vy = relative_hit * 360.0
        if abs(self.ball.vy) < 90.0:
            self.ball.vy = 90.0 if self.ball.vy >= 0 else -90.0

    def _after_point(self, *, direction: int) -> set[RallyEvent]:
        events = {RallyEvent.POINT}
        if self.player_score >= WINNING_SCORE:
            self.state = RallyState.PLAYER_WON
            events.add(RallyEvent.COMPLETE)
        elif self.computer_score >= WINNING_SCORE:
            self.state = RallyState.COMPUTER_WON
            events.add(RallyEvent.COMPLETE)
        else:
            self._reset_ball(direction)
        return events

    def _reset_ball(self, direction: int) -> None:
        self.ball.x = 640.0
        self.ball.y = (PLAY_TOP + PLAY_BOTTOM) / 2
        self.ball.vx = 430.0 * direction
        self.ball.vy = self.rng.choice((-220.0, -160.0, 160.0, 220.0))

    def reset(self, difficulty: Difficulty | None = None) -> None:
        if difficulty is not None:
            self.difficulty = difficulty
        center_y = (PLAY_TOP + PLAY_BOTTOM) / 2
        self.player.y = center_y
        self.computer.y = center_y
        self.player_score = 0
        self.computer_score = 0
        self.state = RallyState.PLAYING
        self.ai = ai_for(self.difficulty)
        self._reset_ball(direction=-1)

