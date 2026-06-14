from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.memory_cards import (
    CARD_COUNT,
    PAIR_COUNT,
    MemoryCardsModel,
    MemoryState,
)
from games_for_grandpa.ui import GameHud, ResultActions

CARD_RECTS = [
    pygame.Rect(300 + column * 175, 135 + row * 160, 130, 130)
    for row in range(3)
    for column in range(4)
]
PAIR_COLORS = (
    pygame.Color("#FF6B6B"),
    pygame.Color("#4D96FF"),
    pygame.Color("#FFD93D"),
    pygame.Color("#6BCB77"),
    pygame.Color("#BFA2DB"),
    pygame.Color("#FFB562"),
)


class MemoryCardsScene(Scene):
    GAME_ID = "memory_cards"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = MemoryCardsModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)

    def _restart(self) -> None:
        self.model.reset()
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is MemoryState.COMPLETE:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for index, rect in enumerate(CARD_RECTS):
            if rect.collidepoint(event.pos):
                if self.model.flip(index):
                    self.controller.play_sound("success")
                    if self.model.state is MemoryState.COMPLETE:
                        self.controller.record_score(self.GAME_ID, PAIR_COUNT)
                        self.controller.play_sound("complete")
                return

    def update(self, dt: float) -> None:
        self.model.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#4C6FFF"), pygame.Color("#B8C6FF"))
        self._draw_score(surface)
        for index, rect in enumerate(CARD_RECTS):
            self._draw_card(surface, rect, index)
        if self.model.state is MemoryState.COMPLETE:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Pairs  {self.model.matches} / {PAIR_COUNT}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    def _draw_card(self, surface: pygame.Surface, rect: pygame.Rect, index: int) -> None:
        card = self.model.cards[index]
        face_up = card.face_up or card.matched
        color = PAIR_COLORS[card.pair_id] if face_up else pygame.Color("#FFF8EA")
        theme.draw_card(surface, rect, color=color, shadow_offset=6, radius=18)
        if face_up:
            pygame.draw.circle(surface, theme.WHITE, rect.center, 35)
            theme.draw_text(surface, str(card.pair_id + 1), 36, theme.INK, rect.center, bold=True)
        else:
            pygame.draw.rect(
                surface,
                pygame.Color("#7D8DB5"),
                rect.inflate(-36, -36),
                border_radius=14,
            )

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "All matched!", 52, theme.INK, (640, 300), bold=True)
        theme.draw_text(surface, f"{CARD_COUNT} cards complete.", 30, theme.INK_SOFT, (640, 355))
