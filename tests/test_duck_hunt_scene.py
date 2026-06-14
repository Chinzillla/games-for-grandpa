from __future__ import annotations

import pygame

from games_for_grandpa.app import App
from games_for_grandpa.games.duck_hunt_scene import DuckHuntScene


def test_duck_hunt_missed_shot_only_plays_gunshot() -> None:
    app = App(smoke_test=True)
    sounds: list[str] = []
    app.play_sound = sounds.append  # type: ignore[method-assign]
    try:
        scene = DuckHuntScene(app)

        scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=(0, 0), button=1))

        assert sounds == ["gunshot"]
    finally:
        app.shutdown()


def test_duck_hunt_hit_plays_gunshot_then_quack() -> None:
    app = App(smoke_test=True)
    sounds: list[str] = []
    app.play_sound = sounds.append  # type: ignore[method-assign]
    try:
        scene = DuckHuntScene(app)
        target = (round(scene.model.duck.x), round(scene.model.duck.y))

        scene.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, pos=target, button=1))

        assert sounds == ["gunshot", "quack"]
    finally:
        app.shutdown()
