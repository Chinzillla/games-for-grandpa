from __future__ import annotations

import argparse
import os
from collections.abc import Sequence

import pygame

from games_for_grandpa.core import (
    LOGICAL_SIZE,
    Scene,
    SceneStack,
    Settings,
    Viewport,
)

BACKGROUND = pygame.Color("#102A43")
FOREGROUND = pygame.Color("#F7FAFC")


class WelcomeScene(Scene):
    def handle_event(self, event: pygame.event.Event) -> None:
        del event

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(BACKGROUND)
        title_font = pygame.font.Font(None, 76)
        body_font = pygame.font.Font(None, 38)
        title = title_font.render("Games for Grandpa", True, FOREGROUND)
        body = body_font.render("The game room is getting ready.", True, FOREGROUND)
        surface.blit(title, title.get_rect(center=(640, 280)))
        surface.blit(body, body.get_rect(center=(640, 370)))


class App:
    def __init__(self, *, smoke_test: bool = False) -> None:
        self.smoke_test = smoke_test
        self.running = True
        self.settings = Settings()
        self.registry: dict[str, object] = {}

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
        self.scenes = SceneStack()
        self.scenes.push(WelcomeScene())

    def go_home(self) -> None:
        self.scenes.reset(WelcomeScene())

    def start_game(self, game_id: str) -> None:
        raise KeyError(f"Game is not registered yet: {game_id}")

    def save_settings(self) -> None:
        return

    def play_sound(self, sound_name: str) -> None:
        del sound_name

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

        pygame.quit()
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
    return app.run(frame_limit=3 if args.smoke_test else None)

