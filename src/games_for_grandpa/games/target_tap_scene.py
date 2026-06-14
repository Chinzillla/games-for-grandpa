from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.target_tap import (
    TARGETS_TO_COMPLETE,
    TargetTapModel,
    TargetTapState,
)
from games_for_grandpa.ui import GameToolbar


class TargetTapScene(Scene):
    GAME_ID = "target_tap"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.paused = False
        self.model = TargetTapModel(controller.settings.difficulty_for(self.GAME_ID))
        self.toolbar = GameToolbar(
            controller,
            self.GAME_ID,
            on_pause=self._toggle_pause,
            on_restart=self._restart,
            on_difficulty=self._restart,
            is_paused=lambda: self.paused,
        )

    def _toggle_pause(self) -> None:
        self.paused = not self.paused
        self.controller.play_sound("click")

    def _restart(self) -> None:
        self.paused = False
        self.model.reset(self.controller.settings.difficulty_for(self.GAME_ID))
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.toolbar.handle_event(event):
            return
        if self.paused or self.model.state is TargetTapState.COMPLETE:
            return
        if (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.model.click(event.pos)
        ):
            if self.model.state is TargetTapState.COMPLETE:
                self.controller.record_score(self.GAME_ID, self.model.score)
            sound = (
                "complete" if self.model.state is TargetTapState.COMPLETE else "success"
            )
            self.controller.play_sound(sound)

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.BACKGROUND)
        self.toolbar.draw(surface)
        theme.draw_left_text(
            surface,
            f"Targets: {self.model.score} / {TARGETS_TO_COMPLETE}",
            42,
            theme.TEXT,
            (42, 115),
            bold=True,
        )
        theme.draw_text(
            surface,
            "Click the large target. Missing does not cost a point.",
            34,
            theme.MUTED_TEXT,
            (750, 137),
        )

        if self.model.state is TargetTapState.PLAYING:
            self._draw_target(surface)
        else:
            self._draw_complete(surface)

        if self.paused:
            self._draw_paused(surface)

    def _draw_target(self, surface: pygame.Surface) -> None:
        center = (self.model.target.x, self.model.target.y)
        radius = self.model.radius
        pygame.draw.circle(surface, theme.PRIMARY, center, radius)
        pygame.draw.circle(surface, theme.BACKGROUND, center, round(radius * 0.65))
        pygame.draw.circle(surface, theme.ACCENT, center, round(radius * 0.36))
        pygame.draw.circle(surface, theme.TEXT, center, round(radius * 0.12))
        pygame.draw.circle(surface, theme.TEXT, center, radius, width=4)

    def _draw_complete(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(280, 205, 720, 370)
        pygame.draw.rect(surface, theme.PANEL, panel, border_radius=28)
        pygame.draw.rect(surface, theme.SUCCESS, panel, width=5, border_radius=28)
        theme.draw_text(surface, "You found all 10!", 64, theme.TEXT, (640, 325), bold=True)
        theme.draw_text(
            surface,
            "Choose Restart to play again.",
            38,
            theme.MUTED_TEXT,
            (640, 425),
        )

    def _draw_paused(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((1280, 622), pygame.SRCALPHA)
        overlay.fill((16, 42, 67, 225))
        surface.blit(overlay, (0, 98))
        theme.draw_text(surface, "Paused", 76, theme.TEXT, (640, 350), bold=True)
        theme.draw_text(
            surface,
            "Choose Continue when you are ready.",
            38,
            theme.MUTED_TEXT,
            (640, 435),
        )
