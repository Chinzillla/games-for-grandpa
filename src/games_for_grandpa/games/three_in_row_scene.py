from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Difficulty, Scene
from games_for_grandpa.games.three_in_row import (
    Mark,
    ThreeInRowModel,
    ThreeInRowState,
)
from games_for_grandpa.ui import GameHud, ResultActions

BOARD_RECT = pygame.Rect(325, 125, 630, 570)
CELL_WIDTH = BOARD_RECT.width // 3
CELL_HEIGHT = BOARD_RECT.height // 3


class ThreeInRowScene(Scene):
    GAME_ID = "three_in_row"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = ThreeInRowModel(Difficulty.NORMAL)
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)

    def _restart(self) -> None:
        self.model.reset(Difficulty.NORMAL)
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is not ThreeInRowState.PLAYING:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if (
            event.type != pygame.MOUSEBUTTONDOWN
            or event.button != 1
            or not BOARD_RECT.collidepoint(event.pos)
        ):
            return

        column = (event.pos[0] - BOARD_RECT.x) // CELL_WIDTH
        row = (event.pos[1] - BOARD_RECT.y) // CELL_HEIGHT
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
        theme.vertical_gradient(surface, pygame.Color("#806CE8"), pygame.Color("#BFAFF8"))
        self._draw_title(surface)
        self._draw_board(surface)
        if self.model.state is not ThreeInRowState.PLAYING:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_title(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(505, 28, 270, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        message = {
            ThreeInRowState.PLAYING: "Your turn",
            ThreeInRowState.PLAYER_WON: "You won!",
            ThreeInRowState.COMPUTER_WON: "Good game!",
            ThreeInRowState.DRAW: "It's a draw!",
        }[self.model.state]
        theme.draw_text(surface, message, 28, theme.INK, badge.center, bold=True)

    def _draw_board(self, surface: pygame.Surface) -> None:
        theme.draw_card(surface, BOARD_RECT, color=theme.CREAM, shadow_offset=10, radius=34)
        for offset in (1, 2):
            x = BOARD_RECT.x + offset * CELL_WIDTH
            y = BOARD_RECT.y + offset * CELL_HEIGHT
            pygame.draw.line(
                surface,
                pygame.Color("#CFD8F0"),
                (x, BOARD_RECT.y + 20),
                (x, BOARD_RECT.bottom - 20),
                width=7,
            )
            pygame.draw.line(
                surface,
                pygame.Color("#CFD8F0"),
                (BOARD_RECT.x + 20, y),
                (BOARD_RECT.right - 20, y),
                width=7,
            )

        for index, mark in enumerate(self.model.board.cells):
            row, column = divmod(index, 3)
            cell = pygame.Rect(
                BOARD_RECT.x + column * CELL_WIDTH,
                BOARD_RECT.y + row * CELL_HEIGHT,
                CELL_WIDTH,
                CELL_HEIGHT,
            )
            if mark is Mark.PLAYER:
                self._draw_x(surface, cell)
            elif mark is Mark.COMPUTER:
                pygame.draw.circle(surface, theme.BLUE, cell.center, 62, width=17)

    @staticmethod
    def _draw_x(surface: pygame.Surface, cell: pygame.Rect) -> None:
        margin_x = 62
        margin_y = 52
        pygame.draw.line(
            surface,
            theme.CORAL,
            (cell.left + margin_x, cell.top + margin_y),
            (cell.right - margin_x, cell.bottom - margin_y),
            width=18,
        )
        pygame.draw.line(
            surface,
            theme.CORAL,
            (cell.right - margin_x, cell.top + margin_y),
            (cell.left + margin_x, cell.bottom - margin_y),
            width=18,
        )

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(370, 230, 540, 270)
        theme.draw_card(surface, panel, color=theme.WHITE, shadow_offset=8, radius=30)
        message = {
            ThreeInRowState.PLAYER_WON: "You won!",
            ThreeInRowState.COMPUTER_WON: "Nice try!",
            ThreeInRowState.DRAW: "A draw!",
        }[self.model.state]
        theme.draw_text(surface, message, 48, theme.INK, (640, 315), bold=True)
