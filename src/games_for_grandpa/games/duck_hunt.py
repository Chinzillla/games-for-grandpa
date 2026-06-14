from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from enum import Enum

from games_for_grandpa.core import Difficulty

DUCKS_TO_COMPLETE = 10
STARTING_LIVES = 10
FLIGHT_LEFT = 120.0
FLIGHT_RIGHT = 1160.0
FLIGHT_TOP = 125.0
FLIGHT_BOTTOM = 470.0
ESCAPE_MARGIN = 95.0
HIT_DISPLAY_SECONDS = 0.55


class DuckHuntState(Enum):
    PLAYING = "playing"
    HIT = "hit"
    COMPLETE = "complete"
    GAME_OVER = "game_over"


class DuckHuntEvent(Enum):
    ESCAPED = "escaped"
    COMPLETE = "complete"
    GAME_OVER = "game_over"


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
        Difficulty.EASY: 170.0,
        Difficulty.NORMAL: 220.0,
        Difficulty.CHALLENGE: 275.0,
    }
    HIT_RADIUS_BY_DIFFICULTY = {
        Difficulty.EASY: 88.0,
        Difficulty.NORMAL: 78.0,
        Difficulty.CHALLENGE: 70.0,
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
        self.lives = STARTING_LIVES
        self.hit_timer = 0.0
        self.state = DuckHuntState.PLAYING
        self.duck = Duck(0, 0, 0, 0)
        self._spawn_duck()

    @property
    def hit_radius(self) -> float:
        return self.HIT_RADIUS_BY_DIFFICULTY[self.difficulty]

    def update(self, dt: float) -> set[DuckHuntEvent]:
        events: set[DuckHuntEvent] = set()
        if self.state is DuckHuntState.HIT:
            self.hit_timer -= dt
            self.duck.y += 180.0 * dt
            if self.hit_timer <= 0:
                if self.score >= DUCKS_TO_COMPLETE:
                    self.state = DuckHuntState.COMPLETE
                    events.add(DuckHuntEvent.COMPLETE)
                else:
                    self._spawn_duck()
                    self.state = DuckHuntState.PLAYING
            return events
        if self.state is not DuckHuntState.PLAYING:
            return events
        self.duck.x += self.duck.vx * dt
        self.duck.y += self.duck.vy * dt

        # DSA: Constant-time bounds checks detect an escaped duck without scanning objects.
        if self._duck_escaped():
            events.update(self._lose_life())
        return events

    def shoot(self, position: tuple[int, int]) -> bool:
        if self.state is DuckHuntState.COMPLETE:
            return False
        x, y = position
        distance_squared = (x - self.duck.x) ** 2 + (y - self.duck.y) ** 2
        if distance_squared > self.hit_radius**2:
            return False

        self.score += 1
        self.hit_timer = HIT_DISPLAY_SECONDS
        self.state = DuckHuntState.HIT
        return True

    def reset(self, difficulty: Difficulty | None = None) -> None:
        if difficulty is not None:
            self.difficulty = difficulty
        self.scheduler.reset()
        self.score = 0
        self.lives = STARTING_LIVES
        self.hit_timer = 0.0
        self.state = DuckHuntState.PLAYING
        self._spawn_duck()

    def _duck_escaped(self) -> bool:
        return (
            self.duck.x < FLIGHT_LEFT - ESCAPE_MARGIN
            or self.duck.x > FLIGHT_RIGHT + ESCAPE_MARGIN
            or self.duck.y < FLIGHT_TOP - ESCAPE_MARGIN
            or self.duck.y > FLIGHT_BOTTOM + ESCAPE_MARGIN
        )

    def _lose_life(self) -> set[DuckHuntEvent]:
        self.lives = max(0, self.lives - 1)
        events = {DuckHuntEvent.ESCAPED}
        if self.lives == 0:
            self.state = DuckHuntState.GAME_OVER
            events.add(DuckHuntEvent.GAME_OVER)
        else:
            self._spawn_duck()
        return events

    def _spawn_duck(self) -> None:
        pattern = self.scheduler.next_pattern()
        speed = self.SPEED_BY_DIFFICULTY[self.difficulty]
        self.duck = Duck(
            pattern.start_x,
            pattern.start_y,
            pattern.direction_x * speed,
            pattern.direction_y * speed,
        )
