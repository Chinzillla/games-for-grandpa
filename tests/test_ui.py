from __future__ import annotations

import pygame

from games_for_grandpa.core import Settings
from games_for_grandpa.games import build_game_registry
from games_for_grandpa.ui import Button, GameHud


class StubController:
    def __init__(self) -> None:
        self.settings = Settings()
        self.home_calls = 0

    def go_home(self) -> None:
        self.home_calls += 1

    def save_settings(self) -> None:
        return

    def play_sound(self, sound_name: str) -> None:
        del sound_name


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
    assert [definition.title for definition in registry.values()] == [
        "Duck Hunt",
        "Tic Tac Toe",
        "Pong",
    ]


def test_game_hud_only_shows_home_and_menu_during_play() -> None:
    controller = StubController()
    restarts: list[str] = []
    hud = GameHud(
        controller,
        "target_tap",
        on_restart=lambda: restarts.append("restart"),
        on_difficulty=lambda: None,
    )

    assert not hud.paused
    assert hud.home_button.label == "Home"
    assert hud.menu_button.label == "Menu"

    hud.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=hud.menu_button.rect.center)
    )
    assert hud.paused

    hud.handle_event(
        pygame.event.Event(
            pygame.MOUSEBUTTONDOWN,
            button=1,
            pos=hud.menu_buttons[1].rect.center,
        )
    )
    assert not hud.paused
    assert restarts == ["restart"]
