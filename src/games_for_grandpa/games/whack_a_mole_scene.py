from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.whack_a_mole import (
    HOLE_COUNT,
    MOLES_TO_WIN,
    WhackAMoleModel,
    WhackState,
)
from games_for_grandpa.ui import GameHud, ResultActions

HOLE_RECTS = [
    pygame.Rect(350 + column * 200, 180 + row * 145, 130, 90)
    for row in range(3)
    for column in range(3)
]


class WhackAMoleScene(Scene):
    GAME_ID = "whack_a_mole"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = WhackAMoleModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)

    def _restart(self) -> None:
        self.model.reset()
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is WhackState.COMPLETE:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for index, rect in enumerate(HOLE_RECTS):
            if rect.collidepoint(event.pos):
                if self.model.whack(index):
                    self.controller.play_sound("success")
                    if self.model.state is WhackState.COMPLETE:
                        self.controller.record_score(self.GAME_ID, self.model.score)
                        self.controller.play_sound("complete")
                return

    def update(self, dt: float) -> None:
        self.model.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#7ED957"), pygame.Color("#C6F6A8"))
        self._draw_score(surface)
        for index, rect in enumerate(HOLE_RECTS):
            self._draw_hole(surface, rect, index == self.model.active_hole)
        if self.model.state is WhackState.COMPLETE:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Moles  {self.model.score} / {MOLES_TO_WIN}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    @staticmethod
    def _draw_hole(surface: pygame.Surface, rect: pygame.Rect, active: bool) -> None:
        pygame.draw.ellipse(surface, pygame.Color("#5A3B1B"), rect)
        pygame.draw.ellipse(surface, pygame.Color("#2F2218"), rect.inflate(-18, -18))
        if active:
            mole = pygame.Rect(rect.centerx - 42, rect.centery - 70, 84, 98)
            pygame.draw.ellipse(surface, pygame.Color("#8B5E34"), mole)
            pygame.draw.circle(
                surface,
                pygame.Color("#F5D0A9"),
                (mole.centerx - 20, mole.y + 38),
                14,
            )
            pygame.draw.circle(
                surface,
                pygame.Color("#F5D0A9"),
                (mole.centerx + 20, mole.y + 38),
                14,
            )
            pygame.draw.circle(surface, theme.BLACK, (mole.centerx - 16, mole.y + 34), 5)
            pygame.draw.circle(surface, theme.BLACK, (mole.centerx + 16, mole.y + 34), 5)

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "Great job!", 52, theme.INK, (640, 290), bold=True)
        theme.draw_text(
            surface,
            f"{HOLE_COUNT} holes, {MOLES_TO_WIN} moles.",
            30,
            theme.INK_SOFT,
            (640, 350),
        )
