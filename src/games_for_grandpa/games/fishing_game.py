from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

FISH_TO_WIN = 3


class FishingState(Enum):
    PLAYING = "playing"
    HOOKED = "hooked"
    COMPLETE = "complete"


@dataclass(slots=True)
class Fish:
    x: float
    y: float
    vx: float
    size: float


class FishingModel:
    def __init__(self, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.rod_x = 640.0
        self.hook_depth = 90.0
        self.tension = 0.0
        self.score = 0
        self.lowering = False
        self.reeling = False
        self.state = FishingState.PLAYING
        self.fish = Fish(0, 0, 0, 1)
        self.reset()

    def reset(self) -> None:
        self.rod_x = 640.0
        self.hook_depth = 90.0
        self.tension = 0.0
        self.score = 0
        self.lowering = False
        self.reeling = False
        self.state = FishingState.PLAYING
        self._spawn_fish()

    def move_rod(self, x: float) -> None:
        # DSA: Clamping is constant-time bounds enforcement for mouse movement.
        self.rod_x = max(140.0, min(1140.0, x))

    def set_lowering(self, active: bool) -> None:
        self.lowering = active
        if active:
            self.reeling = False

    def set_reeling(self, active: bool) -> None:
        self.reeling = active
        if active:
            self.lowering = False

    def update(self, dt: float) -> None:
        if self.state is FishingState.COMPLETE:
            return
        # DSA: The fish and hook are small state machines updated with O(1) arithmetic.
        self.fish.x += self.fish.vx * dt
        if self.fish.x < 130 or self.fish.x > 1150:
            self.fish.vx *= -1

        if self.lowering:
            self.hook_depth = min(560.0, self.hook_depth + 240.0 * dt)
        elif self.reeling:
            self.hook_depth = max(90.0, self.hook_depth - 210.0 * dt)
            if self.state is FishingState.HOOKED:
                self.tension += (42.0 + self.fish.size * 24.0) * dt
        else:
            self.tension = max(0.0, self.tension - 48.0 * dt)

        if self.state is FishingState.PLAYING and self._hook_hits_fish():
            self.state = FishingState.HOOKED
            self.tension = 18.0

        if self.state is FishingState.HOOKED:
            if self.tension >= 100.0:
                self.state = FishingState.PLAYING
                self.hook_depth = 90.0
                self.tension = 0.0
                self._spawn_fish()
            elif self.hook_depth <= 92.0:
                self.score += 1
                if self.score >= FISH_TO_WIN:
                    self.state = FishingState.COMPLETE
                else:
                    self.state = FishingState.PLAYING
                    self.tension = 0.0
                    self._spawn_fish()

    def _hook_hits_fish(self) -> bool:
        # DSA: Axis-aligned distance checks give an O(1) forgiving hit box.
        return (
            abs(self.rod_x - self.fish.x) <= 42 * self.fish.size
            and abs(self.hook_depth - self.fish.y) <= 34
        )

    def _spawn_fish(self) -> None:
        size = self.rng.choice((0.8, 1.0, 1.25))
        self.fish = Fish(
            self.rng.uniform(180.0, 1100.0),
            self.rng.uniform(330.0, 535.0),
            self.rng.choice((-1.0, 1.0)) * self.rng.uniform(70.0, 125.0),
            size,
        )
