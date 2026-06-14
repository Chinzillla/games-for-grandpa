from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass
from enum import Enum

from games_for_grandpa.core import Difficulty

TARGETS_TO_COMPLETE = 10


class TargetTapState(Enum):
    PLAYING = "playing"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class TargetPosition:
    x: int
    y: int


class TargetScheduler:
    def __init__(
        self,
        positions: list[TargetPosition],
        *,
        recent_count: int = 4,
        rng: random.Random | None = None,
    ) -> None:
        if len(positions) <= recent_count:
            raise ValueError("Position pool must be larger than the recent-position history")
        self.positions = positions
        # DSA: A bounded deque keeps only recent positions. Append is O(1), and the
        # oldest item is discarded automatically when the deque reaches maxlen.
        self.recent: deque[TargetPosition] = deque(maxlen=recent_count)
        self.rng = rng or random.Random()

    def next_position(self) -> TargetPosition:
        # DSA: Filtering the small position list is O(n) and prevents repetitive spawns.
        available = [position for position in self.positions if position not in self.recent]
        chosen = self.rng.choice(available)
        self.recent.append(chosen)
        return chosen

    def reset(self) -> None:
        self.recent.clear()


class TargetTapModel:
    RADIUS_BY_DIFFICULTY = {
        Difficulty.EASY: 72,
        Difficulty.NORMAL: 60,
        Difficulty.CHALLENGE: 50,
    }

    def __init__(
        self,
        difficulty: Difficulty = Difficulty.EASY,
        *,
        scheduler: TargetScheduler | None = None,
    ) -> None:
        positions = [
            TargetPosition(x, y)
            for y in (220, 400, 580)
            for x in (170, 405, 640, 875, 1110)
        ]
        self.scheduler = scheduler or TargetScheduler(positions)
        self.difficulty = difficulty
        self.score = 0
        self.state = TargetTapState.PLAYING
        self.target = self.scheduler.next_position()

    @property
    def radius(self) -> int:
        return self.RADIUS_BY_DIFFICULTY[self.difficulty]

    def click(self, position: tuple[int, int]) -> bool:
        if self.state is TargetTapState.COMPLETE:
            return False
        x, y = position
        distance_squared = (x - self.target.x) ** 2 + (y - self.target.y) ** 2
        if distance_squared > self.radius**2:
            return False

        self.score += 1
        if self.score >= TARGETS_TO_COMPLETE:
            self.state = TargetTapState.COMPLETE
        else:
            self.target = self.scheduler.next_position()
        return True

    def reset(self, difficulty: Difficulty | None = None) -> None:
        if difficulty is not None:
            self.difficulty = difficulty
        self.scheduler.reset()
        self.score = 0
        self.state = TargetTapState.PLAYING
        self.target = self.scheduler.next_position()

