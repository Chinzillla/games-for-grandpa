from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field
from enum import Enum

MOLES_TO_WIN = 20
HOLE_COUNT = 9
HIT_FEEDBACK_SECONDS = 0.35


class WhackState(Enum):
    PLAYING = "playing"
    COMPLETE = "complete"


@dataclass(slots=True)
class WhackAMoleModel:
    rng: random.Random
    score: int = 0
    active_hole: int = 0
    hit_hole: int | None = None
    hit_timer: float = 0.0
    timer: float = 0.0
    state: WhackState = WhackState.PLAYING
    recent_holes: deque[int] = field(default_factory=lambda: deque(maxlen=3))

    def __init__(self, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.score = 0
        self.active_hole = 0
        self.hit_hole = None
        self.hit_timer = 0.0
        self.timer = 0.0
        self.state = WhackState.PLAYING
        # DSA: A bounded deque keeps the last holes in O(1) append/pop time.
        self.recent_holes = deque(maxlen=3)
        self._move_mole()

    def update(self, dt: float) -> None:
        if self.hit_timer > 0:
            self.hit_timer = max(0.0, self.hit_timer - dt)
            if self.hit_timer == 0:
                self.hit_hole = None
        if self.state is WhackState.COMPLETE:
            return
        self.timer -= dt
        if self.timer <= 0:
            self._move_mole()

    def whack(self, hole: int) -> bool:
        if self.state is WhackState.COMPLETE or hole != self.active_hole:
            return False
        # DSA: Store the hit hole as a nullable index so drawing can read it in O(1).
        self.hit_hole = hole
        self.hit_timer = HIT_FEEDBACK_SECONDS
        self.score += 1
        if self.score >= MOLES_TO_WIN:
            self.state = WhackState.COMPLETE
        else:
            self._move_mole()
        return True

    def reset(self) -> None:
        self.score = 0
        self.state = WhackState.PLAYING
        self.hit_hole = None
        self.hit_timer = 0.0
        self.recent_holes.clear()
        self._move_mole()

    def _move_mole(self) -> None:
        choices = [hole for hole in range(HOLE_COUNT) if hole not in self.recent_holes]
        self.active_hole = self.rng.choice(choices)
        self.recent_holes.append(self.active_hole)
        self.timer = 1.25
