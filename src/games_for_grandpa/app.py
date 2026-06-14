from __future__ import annotations

import argparse
import os
import tempfile
from collections.abc import Sequence
from pathlib import Path

import pygame

from games_for_grandpa import theme
from games_for_grandpa.audio import SoundBank
from games_for_grandpa.core import (
    LOGICAL_SIZE,
    GameDefinition,
    SceneStack,
    Viewport,
)
from games_for_grandpa.games import build_game_registry
from games_for_grandpa.persistence import JsonDataStore
from games_for_grandpa.scenes import HomeScene


class App:
    def __init__(self, *, smoke_test: bool = False) -> None:
        self.smoke_test = smoke_test
        self.running = True
        if smoke_test:
            data_path = Path(tempfile.gettempdir()) / "games-for-grandpa-smoke.json"
            self.data_store = JsonDataStore(data_path)
        else:
            self.data_store = JsonDataStore()
        saved = self.data_store.load()
        self.settings = saved.settings
        self.scores = saved.scores
        self.registry: dict[str, GameDefinition] = build_game_registry()

        pygame.mixer.pre_init(44_100, -16, 1, 512)
        pygame.init()
        pygame.display.set_caption("Games for Grandpa")
        if smoke_test:
            window_size = LOGICAL_SIZE
        else:
            display = pygame.display.Info()
            window_size = (display.current_w, display.current_h)
        self.window = pygame.display.set_mode(window_size, pygame.RESIZABLE)
        self.canvas = pygame.Surface(LOGICAL_SIZE)
        self.clock = pygame.time.Clock()
        self.sound_bank = SoundBank()
        self.scenes = SceneStack()
        self.scenes.push(HomeScene(self, self.registry))

    def go_home(self) -> None:
        self.scenes.reset(HomeScene(self, self.registry))

    def request_exit(self) -> None:
        self.running = False

    def start_game(self, game_id: str) -> None:
        definition = self.registry[game_id]
        self.scenes.push(definition.scene_factory(self))

    def save_settings(self) -> None:
        self.data_store.save(self.settings, self.scores)

    def play_sound(self, sound_name: str) -> None:
        if self.settings.sound_enabled:
            self.sound_bank.play(sound_name)

    def record_score(self, game_id: str, score: int) -> None:
        self.scores[game_id] = max(score, self.scores.get(game_id, 0))
        self.save_settings()

    def best_score(self, game_id: str) -> int:
        return self.scores.get(game_id, 0)

    def smoke_test_scenes(self) -> None:
        for definition in self.registry.values():
            scene = definition.scene_factory(self)
            scene.update(1 / 60)
            scene.draw(self.canvas)

    @staticmethod
    def shutdown() -> None:
        theme.font.cache_clear()
        pygame.quit()

    def _logical_event(
        self, event: pygame.event.Event, viewport: Viewport
    ) -> pygame.event.Event:
        if not hasattr(event, "pos"):
            return event
        attributes = dict(event.dict)
        attributes["pos"] = viewport.to_logical(event.pos)
        return pygame.event.Event(event.type, attributes)

    def _draw_window(self) -> None:
        viewport = Viewport.fit(self.window.get_size())
        scaled = pygame.transform.smoothscale(self.canvas, (viewport.width, viewport.height))
        self.window.fill("black")
        self.window.blit(scaled, (viewport.offset_x, viewport.offset_y))
        pygame.display.flip()

    def run(self, *, frame_limit: int | None = None) -> int:
        frames = 0
        while self.running:
            dt = min(self.clock.tick(60) / 1000.0, 0.05)
            viewport = Viewport.fit(self.window.get_size())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                self.scenes.active.handle_event(self._logical_event(event, viewport))

            self.scenes.active.update(dt)
            self.scenes.active.draw(self.canvas)
            self._draw_window()

            frames += 1
            if frame_limit is not None and frames >= frame_limit:
                self.running = False

        self.shutdown()
        return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Accessible mouse-only games")
    parser.add_argument(
        "--smoke-test",
        action="store_true",
        help=argparse.SUPPRESS,
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.smoke_test:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
        os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    app = App(smoke_test=args.smoke_test)
    if args.smoke_test:
        app.smoke_test_scenes()
    return app.run(frame_limit=3 if args.smoke_test else None)
