from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Callable, Iterator
from dataclasses import dataclass, field
from enum import Enum
from typing import Protocol

import pygame

LOGICAL_WIDTH = 1280
LOGICAL_HEIGHT = 720
LOGICAL_SIZE = (LOGICAL_WIDTH, LOGICAL_HEIGHT)


class Difficulty(Enum):
    EASY = "Easy"
    NORMAL = "Normal"
    CHALLENGE = "Challenge"

    def next(self) -> Difficulty:
        members = list(type(self))
        return members[(members.index(self) + 1) % len(members)]


@dataclass(slots=True)
class Settings:
    sound_enabled: bool = True
    ui_scale: float = 1.0
    difficulties: dict[str, Difficulty] = field(default_factory=dict)

    def difficulty_for(self, game_id: str) -> Difficulty:
        return self.difficulties.get(game_id, Difficulty.EASY)


class Scene(ABC):
    """One screen in the application lifecycle."""

    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> None:
        """Handle one input or window event."""

    @abstractmethod
    def update(self, dt: float) -> None:
        """Advance state by dt seconds."""

    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """Render onto the logical canvas."""


class SceneStack:
    def __init__(self) -> None:
        # DSA: A list is used as a stack. Push/pop at the end are amortized O(1).
        self._scenes: list[Scene] = []

    @property
    def active(self) -> Scene:
        if not self._scenes:
            raise RuntimeError("Scene stack is empty")
        return self._scenes[-1]

    def push(self, scene: Scene) -> None:
        self._scenes.append(scene)

    def pop(self) -> Scene:
        if len(self._scenes) <= 1:
            raise RuntimeError("Cannot remove the final scene")
        return self._scenes.pop()

    def replace(self, scene: Scene) -> None:
        if self._scenes:
            self._scenes[-1] = scene
        else:
            self._scenes.append(scene)

    def reset(self, scene: Scene) -> None:
        self._scenes[:] = [scene]

    def __len__(self) -> int:
        return len(self._scenes)

    def __iter__(self) -> Iterator[Scene]:
        return iter(self._scenes)


class AppController(Protocol):
    settings: Settings

    def go_home(self) -> None: ...

    def request_exit(self) -> None: ...

    def start_game(self, game_id: str) -> None: ...

    def save_settings(self) -> None: ...

    def play_sound(self, sound_name: str) -> None: ...

    def record_score(self, game_id: str, score: int) -> None: ...

    def best_score(self, game_id: str) -> int: ...


SceneFactory = Callable[[AppController], Scene]


@dataclass(frozen=True, slots=True)
class GameDefinition:
    game_id: str
    title: str
    description: str
    scene_factory: SceneFactory
    difficulties: tuple[Difficulty, ...] = tuple(Difficulty)


@dataclass(frozen=True, slots=True)
class Viewport:
    scale: float
    offset_x: int
    offset_y: int
    width: int
    height: int

    @classmethod
    def fit(cls, window_size: tuple[int, int]) -> Viewport:
        window_width, window_height = window_size
        scale = min(window_width / LOGICAL_WIDTH, window_height / LOGICAL_HEIGHT)
        width = max(1, round(LOGICAL_WIDTH * scale))
        height = max(1, round(LOGICAL_HEIGHT * scale))
        return cls(
            scale=scale,
            offset_x=(window_width - width) // 2,
            offset_y=(window_height - height) // 2,
            width=width,
            height=height,
        )

    def to_logical(self, position: tuple[int, int]) -> tuple[int, int]:
        x, y = position
        if self.scale <= 0:
            return (-1, -1)
        return (
            round((x - self.offset_x) / self.scale),
            round((y - self.offset_y) / self.scale),
        )
