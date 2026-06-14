from __future__ import annotations

import pygame

from games_for_grandpa.games import build_game_registry
from games_for_grandpa.ui import Button


def test_button_only_responds_to_left_click_inside() -> None:
    clicks: list[str] = []
    button = Button(pygame.Rect(10, 10, 100, 60), "Play", lambda: clicks.append("clicked"))

    outside = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(0, 0))
    right_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=3, pos=(20, 20))
    left_click = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(20, 20))

    assert not button.handle_event(outside)
    assert not button.handle_event(right_click)
    assert button.handle_event(left_click)
    assert clicks == ["clicked"]


def test_registry_has_stable_ids() -> None:
    registry = build_game_registry()

    assert list(registry) == ["target_tap", "three_in_row", "paddle_rally"]
