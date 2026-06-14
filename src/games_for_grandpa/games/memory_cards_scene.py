from __future__ import annotations

import math

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
        self.elapsed = 0.0
        self.card_pulses = [0.0] * CARD_COUNT

    def _restart(self) -> None:
        self.model.reset()
        self.elapsed = 0.0
        self.card_pulses = [0.0] * CARD_COUNT
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
                    self.card_pulses[index] = 0.22
                    self.controller.play_sound("success")
                    if self.model.state is MemoryState.COMPLETE:
                        self.controller.record_score(self.GAME_ID, PAIR_COUNT)
                        self.controller.play_sound("complete")
                return

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.card_pulses = [max(0.0, pulse - dt) for pulse in self.card_pulses]
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
        pulse = self.card_pulses[index]
        draw_rect = rect.inflate(round(18 * pulse / 0.22), round(18 * pulse / 0.22))
        if self.model.state is MemoryState.SHOWING_MISMATCH and index in self.model.selected:
            draw_rect = draw_rect.move(round(math.sin(self.elapsed * 35.0) * 5), 0)
        color = PAIR_COLORS[card.pair_id] if face_up else pygame.Color("#FFF8EA")
        theme.draw_card(surface, draw_rect, color=color, shadow_offset=6, radius=18)
        if face_up:
            pygame.draw.circle(surface, theme.WHITE, draw_rect.center, 35)
            self._draw_symbol(surface, draw_rect.center, card.pair_id)
        else:
            pygame.draw.rect(
                surface,
                pygame.Color("#7D8DB5"),
                draw_rect.inflate(-36, -36),
                border_radius=14,
            )

    @staticmethod
    def _draw_symbol(surface: pygame.Surface, center: tuple[int, int], pair_id: int) -> None:
        x, y = center
        if pair_id == 0:
            pygame.draw.circle(surface, theme.CORAL, center, 20)
        elif pair_id == 1:
            pygame.draw.rect(
                surface,
                theme.BLUE,
                pygame.Rect(x - 22, y - 22, 44, 44),
                border_radius=8,
            )
        elif pair_id == 2:
            pygame.draw.polygon(
                surface,
                theme.YELLOW_DARK,
                [(x, y - 26), (x - 24, y + 18), (x + 24, y + 18)],
            )
        elif pair_id == 3:
            pygame.draw.polygon(
                surface,
                theme.GREEN_DARK,
                [(x, y - 27), (x + 27, y), (x, y + 27), (x - 27, y)],
            )
        elif pair_id == 4:
            pygame.draw.circle(surface, theme.PURPLE, center, 24, width=9)
        else:
            points = []
            for index in range(10):
                angle = -math.pi / 2 + index * math.pi / 5
                radius = 27 if index % 2 == 0 else 12
                points.append(
                    (
                        x + round(math.cos(angle) * radius),
                        y + round(math.sin(angle) * radius),
                    )
                )
            pygame.draw.polygon(surface, theme.PINK, points)

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "All matched!", 52, theme.INK, (640, 300), bold=True)
        theme.draw_text(surface, f"{CARD_COUNT} cards complete.", 30, theme.INK_SOFT, (640, 355))
