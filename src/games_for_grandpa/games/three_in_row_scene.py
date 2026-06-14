from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.three_in_row import (
    Mark,
    ThreeInRowModel,
    ThreeInRowState,
)
from games_for_grandpa.ui import GameToolbar

BOARD_RECT = pygame.Rect(120, 170, 510, 510)
CELL_SIZE = BOARD_RECT.width // 3


class ThreeInRowScene(Scene):
    GAME_ID = "three_in_row"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.paused = False
        self.model = ThreeInRowModel(controller.settings.difficulty_for(self.GAME_ID))
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
        if (
            self.paused
            or self.model.state is not ThreeInRowState.PLAYING
            or event.type != pygame.MOUSEBUTTONDOWN
            or event.button != 1
            or not BOARD_RECT.collidepoint(event.pos)
        ):
            return

        column = (event.pos[0] - BOARD_RECT.x) // CELL_SIZE
        row = (event.pos[1] - BOARD_RECT.y) // CELL_SIZE
        index = row * 3 + column
        if self.model.player_move(index):
            if self.model.state is not ThreeInRowState.PLAYING:
                score = 1 if self.model.state is ThreeInRowState.PLAYER_WON else 0
                self.controller.record_score(self.GAME_ID, score)
            sound = "complete" if self.model.state is not ThreeInRowState.PLAYING else "success"
            self.controller.play_sound(sound)

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.BACKGROUND)
        self.toolbar.draw(surface)
        self._draw_board(surface)
        self._draw_instructions(surface)
        if self.paused:
            self._draw_paused(surface)

    def _draw_board(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, theme.PANEL, BOARD_RECT, border_radius=18)
        for offset in (1, 2):
            x = BOARD_RECT.x + offset * CELL_SIZE
            y = BOARD_RECT.y + offset * CELL_SIZE
            pygame.draw.line(
                surface,
                theme.MUTED_TEXT,
                (x, BOARD_RECT.y),
                (x, BOARD_RECT.bottom),
                width=6,
            )
            pygame.draw.line(
                surface,
                theme.MUTED_TEXT,
                (BOARD_RECT.x, y),
                (BOARD_RECT.right, y),
                width=6,
            )

        for index, mark in enumerate(self.model.board.cells):
            row, column = divmod(index, 3)
            cell = pygame.Rect(
                BOARD_RECT.x + column * CELL_SIZE,
                BOARD_RECT.y + row * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )
            if mark is Mark.PLAYER:
                margin = 42
                pygame.draw.line(
                    surface,
                    theme.PRIMARY,
                    (cell.left + margin, cell.top + margin),
                    (cell.right - margin, cell.bottom - margin),
                    width=14,
                )
                pygame.draw.line(
                    surface,
                    theme.PRIMARY,
                    (cell.right - margin, cell.top + margin),
                    (cell.left + margin, cell.bottom - margin),
                    width=14,
                )
            elif mark is Mark.COMPUTER:
                pygame.draw.circle(
                    surface,
                    theme.ACCENT,
                    cell.center,
                    56,
                    width=14,
                )

    def _draw_instructions(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(700, 170, 500, 510)
        pygame.draw.rect(surface, theme.PANEL, panel, border_radius=22)
        pygame.draw.rect(surface, theme.ACCENT, panel, width=4, border_radius=22)
        theme.draw_text(
            surface,
            "Three in a Row",
            52,
            theme.TEXT,
            (panel.centerx, 235),
            bold=True,
        )
        theme.draw_text(
            surface,
            "Click an empty square.",
            34,
            theme.MUTED_TEXT,
            (panel.centerx, 315),
        )
        theme.draw_text(
            surface,
            "You are the gold X.",
            34,
            theme.PRIMARY,
            (panel.centerx, 365),
        )
        theme.draw_text(
            surface,
            "Computer is the blue O.",
            34,
            theme.ACCENT,
            (panel.centerx, 415),
        )

        messages = {
            ThreeInRowState.PLAYING: "Your turn",
            ThreeInRowState.PLAYER_WON: "You made three!",
            ThreeInRowState.COMPUTER_WON: "The computer made three.",
            ThreeInRowState.DRAW: "A friendly draw!",
        }
        color = (
            theme.SUCCESS
            if self.model.state in {ThreeInRowState.PLAYER_WON, ThreeInRowState.DRAW}
            else theme.TEXT
        )
        theme.draw_text(
            surface,
            messages[self.model.state],
            44,
            color,
            (panel.centerx, 525),
            bold=True,
        )
        if self.model.state is not ThreeInRowState.PLAYING:
            theme.draw_text(
                surface,
                "Choose Restart to play again.",
                30,
                theme.MUTED_TEXT,
                (panel.centerx, 600),
            )

    def _draw_paused(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((1280, 622), pygame.SRCALPHA)
        overlay.fill((16, 42, 67, 235))
        surface.blit(overlay, (0, 98))
        theme.draw_text(surface, "Paused", 76, theme.TEXT, (640, 350), bold=True)
        theme.draw_text(
            surface,
            "Choose Continue when you are ready.",
            38,
            theme.MUTED_TEXT,
            (640, 435),
        )
