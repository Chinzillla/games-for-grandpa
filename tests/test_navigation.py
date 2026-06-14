from __future__ import annotations

import pygame

from games_for_grandpa.app import App
from games_for_grandpa.core import Viewport
from games_for_grandpa.games.target_tap_scene import TargetTapScene
from games_for_grandpa.scenes import HomeScene


def test_player_can_open_game_and_return_home_using_mouse_only() -> None:
    app = App(smoke_test=True)
    try:
        assert isinstance(app.scenes.active, HomeScene)

        app.scenes.active.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(260, 548))
        )
        assert isinstance(app.scenes.active, TargetTapScene)

        app.scenes.active.handle_event(
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(80, 50))
        )
        assert isinstance(app.scenes.active, HomeScene)
    finally:
        app.shutdown()


def test_every_scene_renders_at_720p_and_1080p() -> None:
    app = App(smoke_test=True)
    try:
        scenes = [HomeScene(app, app.registry)]
        scenes.extend(definition.scene_factory(app) for definition in app.registry.values())

        for scene in scenes:
            scene.draw(app.canvas)
            for window_size in ((1280, 720), (1920, 1080)):
                viewport = Viewport.fit(window_size)
                scaled = pygame.transform.smoothscale(
                    app.canvas,
                    (viewport.width, viewport.height),
                )
                assert scaled.get_size() == window_size
    finally:
        app.shutdown()

