from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from enum import Enum

from games_for_grandpa.core import Difficulty

DUCKS_TO_COMPLETE = 10
FLIGHT_LEFT = 120.0
FLIGHT_RIGHT = 1160.0
FLIGHT_TOP = 125.0
FLIGHT_BOTTOM = 525.0


class DuckHuntState(Enum):
    PLAYING = "playing"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class FlightPattern:
    start_x: float
    start_y: float
    direction_x: float
    direction_y: float


@dataclass(slots=True)
class Duck:
    x: float
    y: float
    vx: float
    vy: float


class FlightScheduler:
    def __init__(self, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.patterns = [
            FlightPattern(160, 210, 1.0, 0.30),
            FlightPattern(160, 390, 1.0, -0.35),
            FlightPattern(1120, 220, -1.0, 0.38),
            FlightPattern(1120, 410, -1.0, -0.28),
            FlightPattern(320, 500, 0.75, -0.65),
            FlightPattern(960, 500, -0.75, -0.65),
        ]
        # DSA: The bounded deque remembers recent pattern indices. Appending is O(1),
        # and old entries leave automatically, preventing repetitive flights.
        self.recent: deque[int] = deque(maxlen=3)

    def next_pattern(self) -> FlightPattern:
        choices = [index for index in range(len(self.patterns)) if index not in self.recent]
        index = self.rng.choice(choices)
        self.recent.append(index)
        return self.patterns[index]

    def reset(self) -> None:
        self.recent.clear()


class DuckHuntModel:
    SPEED_BY_DIFFICULTY = {
        Difficulty.EASY: 125.0,
        Difficulty.NORMAL: 175.0,
        Difficulty.CHALLENGE: 225.0,
    }
    HIT_RADIUS_BY_DIFFICULTY = {
        Difficulty.EASY: 82.0,
        Difficulty.NORMAL: 72.0,
        Difficulty.CHALLENGE: 62.0,
    }

    def __init__(
        self,
        difficulty: Difficulty = Difficulty.EASY,
        *,
        scheduler: FlightScheduler | None = None,
    ) -> None:
        self.difficulty = difficulty
        self.scheduler = scheduler or FlightScheduler()
        self.score = 0
        self.state = DuckHuntState.PLAYING
        self.duck = Duck(0, 0, 0, 0)
        self._spawn_duck()

    @property
    def hit_radius(self) -> float:
        return self.HIT_RADIUS_BY_DIFFICULTY[self.difficulty]

    def update(self, dt: float) -> None:
        if self.state is DuckHuntState.COMPLETE:
            return
        self.duck.x += self.duck.vx * dt
        self.duck.y += self.duck.vy * dt

        # DSA: Reflection checks each axis once, so movement remains O(1) per frame.
        if self.duck.x < FLIGHT_LEFT:
            self.duck.x = FLIGHT_LEFT
            self.duck.vx = abs(self.duck.vx)
        elif self.duck.x > FLIGHT_RIGHT:
            self.duck.x = FLIGHT_RIGHT
            self.duck.vx = -abs(self.duck.vx)

        if self.duck.y < FLIGHT_TOP:
            self.duck.y = FLIGHT_TOP
            self.duck.vy = abs(self.duck.vy)
        elif self.duck.y > FLIGHT_BOTTOM:
            self.duck.y = FLIGHT_BOTTOM
            self.duck.vy = -abs(self.duck.vy)

    def shoot(self, position: tuple[int, int]) -> bool:
        if self.state is DuckHuntState.COMPLETE:
            return False
        x, y = position
        distance_squared = (x - self.duck.x) ** 2 + (y - self.duck.y) ** 2
        if distance_squared > self.hit_radius**2:
            return False

        self.score += 1
        if self.score >= DUCKS_TO_COMPLETE:
            self.state = DuckHuntState.COMPLETE
        else:
            self._spawn_duck()
        return True

    def reset(self, difficulty: Difficulty | None = None) -> None:
        if difficulty is not None:
            self.difficulty = difficulty
        self.scheduler.reset()
        self.score = 0
        self.state = DuckHuntState.PLAYING
        self._spawn_duck()

    def _spawn_duck(self) -> None:
        pattern = self.scheduler.next_pattern()
        speed = self.SPEED_BY_DIFFICULTY[self.difficulty]
        self.duck = Duck(
            pattern.start_x,
            pattern.start_y,
            pattern.direction_x * speed,
            pattern.direction_y * speed,
        )
