from __future__ import annotations

import math

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.memory_cards import (
    GRID_OPTIONS,
    MemoryCardsModel,
    MemoryState,
)
from games_for_grandpa.ui import Button, GameHud, ResultActions

BOARD_AREA = pygame.Rect(205, 115, 720, 540)
SIDE_PANEL = pygame.Rect(980, 120, 230, 470)
CARD_GAP = 18
PAIR_COLORS = (
    pygame.Color("#FF8A80"),
    pygame.Color("#80B9FF"),
    pygame.Color("#FFE082"),
    pygame.Color("#94E2A8"),
    pygame.Color("#C4B5FD"),
    pygame.Color("#FFCC80"),
    pygame.Color("#8FE3FF"),
    pygame.Color("#F9A8D4"),
)


class MemoryCardsScene(Scene):
    GAME_ID = "memory_cards"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = MemoryCardsModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.elapsed = 0.0
        self.card_pulses = [0.0] * self.model.card_count
        self.grid_buttons = [
            Button(
                pygame.Rect(SIDE_PANEL.x + 30, SIDE_PANEL.y + 116 + index * 78, 170, 58),
                f"{rows} x {columns}",
                lambda grid=(rows, columns): self._change_grid(grid),
                accent=theme.SKY,
            )
            for index, (rows, columns) in enumerate(GRID_OPTIONS)
        ]

    def _restart(self) -> None:
        self.model.reset()
        self.elapsed = 0.0
        self.card_pulses = [0.0] * self.model.card_count
        self.controller.play_sound("click")

    def _change_grid(self, grid_size: tuple[int, int]) -> None:
        self.model.reset(grid_size)
        self.card_pulses = [0.0] * self.model.card_count
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is MemoryState.COMPLETE:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event) or any(
            button.handle_event(event) for button in self.grid_buttons
        ):
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        for index, rect in enumerate(self._card_rects()):
            if rect.collidepoint(event.pos):
                if self.model.flip(index):
                    self.card_pulses[index] = 0.22
                    self.controller.play_sound("success")
                    if self.model.state is MemoryState.COMPLETE:
                        self.controller.record_score(self.GAME_ID, self.model.pair_count)
                        self.controller.play_sound("complete")
                return

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.card_pulses = [max(0.0, pulse - dt) for pulse in self.card_pulses]
        self.model.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#4C6FFF"), pygame.Color("#B8C6FF"))
        self._draw_score(surface)
        self._draw_side_panel(surface)
        for index, rect in enumerate(self._card_rects()):
            self._draw_card(surface, rect, index)
        if self.model.state is MemoryState.COMPLETE:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _card_rects(self) -> list[pygame.Rect]:
        rows, columns = self.model.rows, self.model.columns
        size = min(
            (BOARD_AREA.width - CARD_GAP * (columns - 1)) // columns,
            (BOARD_AREA.height - CARD_GAP * (rows - 1)) // rows,
        )
        total_width = columns * size + (columns - 1) * CARD_GAP
        total_height = rows * size + (rows - 1) * CARD_GAP
        start_x = BOARD_AREA.centerx - total_width // 2
        start_y = BOARD_AREA.centery - total_height // 2
        # DSA: The visible grid is derived by row/column arithmetic in O(n) for drawing.
        return [
            pygame.Rect(
                start_x + column * (size + CARD_GAP),
                start_y + row * (size + CARD_GAP),
                size,
                size,
            )
            for row in range(rows)
            for column in range(columns)
        ]

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Pairs  {self.model.matches} / {self.model.pair_count}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    def _draw_side_panel(self, surface: pygame.Surface) -> None:
        theme.draw_card(surface, SIDE_PANEL, color=theme.CREAM, shadow_offset=8, radius=26)
        theme.draw_text(
            surface, "Cards", 32, theme.INK, (SIDE_PANEL.centerx, SIDE_PANEL.y + 52), bold=True
        )
        theme.draw_text(
            surface,
            f"{self.model.card_count} total",
            25,
            theme.INK_SOFT,
            (SIDE_PANEL.centerx, SIDE_PANEL.y + 88),
        )
        selected = (self.model.rows, self.model.columns)
        for button, grid in zip(self.grid_buttons, GRID_OPTIONS, strict=True):
            button.primary = grid == selected
            button.draw(surface)

    def _draw_card(self, surface: pygame.Surface, rect: pygame.Rect, index: int) -> None:
        card = self.model.cards[index]
        face_up = card.face_up or card.matched
        pulse = self.card_pulses[index]
        draw_rect = rect.inflate(round(18 * pulse / 0.22), round(18 * pulse / 0.22))
        if self.model.state is MemoryState.SHOWING_MISMATCH and index in self.model.selected:
            draw_rect = draw_rect.move(round(math.sin(self.elapsed * 35.0) * 5), 0)
        color = PAIR_COLORS[card.pair_id % len(PAIR_COLORS)] if face_up else pygame.Color("#FFF8EA")
        theme.draw_card(surface, draw_rect, color=color, shadow_offset=6, radius=18)
        if face_up:
            pygame.draw.circle(surface, theme.WHITE, draw_rect.center, draw_rect.width // 3)
            self._draw_object(surface, draw_rect.center, card.pair_id, draw_rect.width)
        else:
            inset = max(26, draw_rect.width // 4)
            pygame.draw.rect(
                surface,
                pygame.Color("#6C7AA5"),
                draw_rect.inflate(-inset, -inset),
                border_radius=14,
            )
            pygame.draw.circle(
                surface, pygame.Color("#E8EEFF"), draw_rect.center, max(10, draw_rect.width // 11)
            )

    @staticmethod
    def _draw_object(
        surface: pygame.Surface, center: tuple[int, int], pair_id: int, size: int
    ) -> None:
        x, y = center
        scale = size / 130
        kind = pair_id % 8
        if kind == 0:
            for angle in range(0, 360, 60):
                px = x + round(math.cos(math.radians(angle)) * 19 * scale)
                py = y + round(math.sin(math.radians(angle)) * 19 * scale)
                pygame.draw.circle(surface, theme.PINK, (px, py), round(13 * scale))
            pygame.draw.circle(surface, theme.YELLOW, center, round(14 * scale))
        elif kind == 1:
            pygame.draw.circle(surface, pygame.Color("#F4A261"), center, round(26 * scale))
            pygame.draw.polygon(
                surface,
                pygame.Color("#F4A261"),
                [(x - 26, y - 16), (x - 12, y - 42), (x - 4, y - 12)],
            )
            pygame.draw.polygon(
                surface,
                pygame.Color("#F4A261"),
                [(x + 26, y - 16), (x + 12, y - 42), (x + 4, y - 12)],
            )
            pygame.draw.circle(
                surface, theme.BLACK, (x - round(9 * scale), y - round(4 * scale)), round(4 * scale)
            )
            pygame.draw.circle(
                surface, theme.BLACK, (x + round(9 * scale), y - round(4 * scale)), round(4 * scale)
            )
            pygame.draw.circle(surface, theme.CORAL, (x, y + round(8 * scale)), round(5 * scale))
        elif kind == 2:
            pygame.draw.rect(
                surface, theme.BLUE, pygame.Rect(x - 31, y - 12, 62, 25), border_radius=7
            )
            pygame.draw.polygon(
                surface,
                theme.SKY,
                [(x - 18, y - 13), (x - 5, y - 30), (x + 18, y - 30), (x + 31, y - 13)],
            )
            pygame.draw.circle(surface, theme.BLACK, (x - 20, y + 18), 8)
            pygame.draw.circle(surface, theme.BLACK, (x + 20, y + 18), 8)
        elif kind == 3:
            pygame.draw.rect(
                surface, theme.CREAM, pygame.Rect(x - 28, y - 5, 56, 40), border_radius=4
            )
            pygame.draw.polygon(
                surface, theme.CORAL, [(x - 34, y - 5), (x, y - 38), (x + 34, y - 5)]
            )
            pygame.draw.rect(
                surface, theme.BROWN, pygame.Rect(x - 8, y + 12, 16, 23), border_radius=3
            )
        elif kind == 4:
            pygame.draw.circle(surface, theme.YELLOW, center, round(28 * scale))
            for angle in range(0, 360, 45):
                start = (
                    x + round(math.cos(math.radians(angle)) * 36 * scale),
                    y + round(math.sin(math.radians(angle)) * 36 * scale),
                )
                end = (
                    x + round(math.cos(math.radians(angle)) * 48 * scale),
                    y + round(math.sin(math.radians(angle)) * 48 * scale),
                )
                pygame.draw.line(surface, theme.YELLOW_DARK, start, end, max(3, round(4 * scale)))
        elif kind == 5:
            pygame.draw.rect(
                surface, theme.BROWN, pygame.Rect(x - 8, y + 4, 16, 34), border_radius=5
            )
            pygame.draw.circle(surface, theme.GREEN, (x, y - 20), round(24 * scale))
            pygame.draw.circle(surface, theme.GREEN_DARK, (x - 18, y - 6), round(19 * scale))
            pygame.draw.circle(surface, theme.GREEN_DARK, (x + 18, y - 6), round(19 * scale))
        elif kind == 6:
            pygame.draw.ellipse(surface, theme.SKY, pygame.Rect(x - 34, y - 17, 58, 34))
            pygame.draw.polygon(
                surface, theme.BLUE, [(x + 18, y), (x + 42, y - 18), (x + 42, y + 18)]
            )
            pygame.draw.circle(surface, theme.BLACK, (x - 16, y - 3), 4)
        else:
            pygame.draw.circle(surface, theme.CORAL, (x, y + 5), round(25 * scale))
            pygame.draw.ellipse(surface, theme.GREEN, pygame.Rect(x + 1, y - 35, 25, 14))
            pygame.draw.line(surface, theme.BROWN, (x, y - 16), (x + 7, y - 32), 4)

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "All matched!", 52, theme.INK, (640, 300), bold=True)
        theme.draw_text(
            surface,
            f"{self.model.card_count} picture cards complete.",
            30,
            theme.INK_SOFT,
            (640, 355),
        )
