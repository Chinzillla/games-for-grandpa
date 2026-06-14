from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame  # noqa: E402

from games_for_grandpa.app import App  # noqa: E402
from games_for_grandpa.scenes import HomeScene  # noqa: E402


def main() -> int:
    output = Path("docs/images")
    output.mkdir(parents=True, exist_ok=True)
    app = App(smoke_test=True)
    try:
        names = {
            "target_tap": "duck-hunt",
            "three_in_row": "tic-tac-toe",
            "paddle_rally": "pong",
        }
        scenes = [("game-room", HomeScene(app, app.registry))]
        scenes.extend(
            (names[definition.game_id], definition.scene_factory(app))
            for definition in app.registry.values()
        )
        for name, scene in scenes:
            scene.draw(app.canvas)
            pygame.image.save(app.canvas, output / f"{name}.png")
        menu_scene = app.registry["target_tap"].scene_factory(app)
        menu_scene.hud.menu_open = True
        menu_scene.draw(app.canvas)
        pygame.image.save(app.canvas, output / "game-menu.png")
    finally:
        app.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
