from __future__ import annotations

import pygame
import pytest

from games_for_grandpa.core import Difficulty, Scene, SceneStack, Viewport


class StubScene(Scene):
    def handle_event(self, event: pygame.event.Event) -> None:
        del event

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        del surface


def test_scene_stack_uses_last_scene_as_active() -> None:
    first = StubScene()
    second = StubScene()
    stack = SceneStack()

    stack.push(first)
    stack.push(second)

    assert stack.active is second
    assert stack.pop() is second
    assert stack.active is first


def test_scene_stack_keeps_at_least_one_scene() -> None:
    stack = SceneStack()
    stack.push(StubScene())

    with pytest.raises(RuntimeError):
        stack.pop()


def test_difficulty_cycles() -> None:
    assert Difficulty.EASY.next() is Difficulty.NORMAL
    assert Difficulty.NORMAL.next() is Difficulty.CHALLENGE
    assert Difficulty.CHALLENGE.next() is Difficulty.EASY


def test_viewport_preserves_aspect_ratio_and_maps_mouse() -> None:
    viewport = Viewport.fit((1920, 1080))

    assert viewport.scale == 1.5
    assert viewport.to_logical((960, 540)) == (640, 360)


def test_viewport_letterboxes_wide_window() -> None:
    viewport = Viewport.fit((1600, 720))

    assert viewport.offset_x == 160
    assert viewport.offset_y == 0
    assert viewport.to_logical((160, 0)) == (0, 0)
