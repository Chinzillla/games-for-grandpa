from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

TARGETS_TO_WIN = 10


class TargetPracticeState(Enum):
    PLAYING = "playing"
    COMPLETE = "complete"


@dataclass(slots=True)
class MovingTarget:
    x: float
    y: float
    vx: float


class TargetPracticeModel:
    def __init__(self, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.target = MovingTarget(0, 0, 0)
        self.score = 0
        self.state = TargetPracticeState.PLAYING
        self.reset()

    def reset(self) -> None:
        self.score = 0
        self.state = TargetPracticeState.PLAYING
        self._spawn()

    def update(self, dt: float) -> None:
        if self.state is TargetPracticeState.COMPLETE:
            return
        # DSA: Constant-time vector movement and boundary reflection keep the target logic
        # predictable without storing a path history.
        self.target.x += self.target.vx * dt
        if self.target.x < 120:
            self.target.x = 120
            self.target.vx = abs(self.target.vx)
        elif self.target.x > 1160:
            self.target.x = 1160
            self.target.vx = -abs(self.target.vx)

    def shoot(self, position: tuple[int, int]) -> bool:
        if self.state is TargetPracticeState.COMPLETE:
            return False
        x, y = position
        # DSA: Squared-distance hit testing avoids sqrt and stays O(1) per click.
        if (x - self.target.x) ** 2 + (y - self.target.y) ** 2 > 85**2:
            return False
        self.score += 1
        if self.score >= TARGETS_TO_WIN:
            self.state = TargetPracticeState.COMPLETE
        else:
            self._spawn()
        return True

    def _spawn(self) -> None:
        self.target = MovingTarget(
            self.rng.choice((140.0, 1140.0)),
            self.rng.uniform(170.0, 450.0),
            self.rng.choice((-1.0, 1.0)) * 105.0,
        )
