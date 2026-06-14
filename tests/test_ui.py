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

    assert list(registry) == [
        "target_tap",
        "three_in_row",
        "connect_four",
        "paddle_rally",
        "space_defense",
        "maze_chase",
        "whack_a_mole",
        "target_practice",
        "memory_cards",
        "jigsaw_puzzle",
        "fishing_game",
    ]
    assert [definition.title for definition in registry.values()] == [
        "Duck Hunt",
        "Tic Tac Toe",
        "Connect Four",
        "Pong",
        "Space Defense",
        "Maze Chase",
        "Whack-a-Mole",
        "Target Practice",
        "Memory Cards",
        "Jigsaw Puzzle",
        "Fishing",
    ]


def test_game_hud_only_shows_home_and_sound_during_play() -> None:
    controller = StubController()
    hud = GameHud(controller)

    assert hud.home_button.label == "Home"
    assert hud.sound_button.label == "Sound On"

    hud.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=hud.sound_button.rect.center)
    )
    assert not controller.settings.sound_enabled
