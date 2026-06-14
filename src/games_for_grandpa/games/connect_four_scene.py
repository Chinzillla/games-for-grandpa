from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.connect_four import (
    COLUMNS,
    ROWS,
    ConnectFourModel,
    ConnectState,
    Piece,
)
from games_for_grandpa.ui import GameHud, ResultActions

BOARD_RECT = pygame.Rect(290, 130, 700, 540)
CELL_SIZE = BOARD_RECT.width // COLUMNS


class ConnectFourScene(Scene):
    GAME_ID = "connect_four"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = ConnectFourModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)

    def _restart(self) -> None:
        self.model.reset()
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is not ConnectState.PLAYING:
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
        column = (event.pos[0] - BOARD_RECT.x) // CELL_SIZE
        if self.model.player_move(column):
            self.controller.play_sound("success")
            if self.model.state is not ConnectState.PLAYING:
                score = 1 if self.model.state is ConnectState.PLAYER_WON else 0
                self.controller.record_score(self.GAME_ID, score)
                self.controller.play_sound("complete")

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#2F80ED"), pygame.Color("#8CC7FF"))
        self._draw_title(surface)
        self._draw_board(surface)
        if self.model.state is not ConnectState.PLAYING:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_title(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(surface, "Drop a piece", 27, theme.INK, badge.center, bold=True)

    def _draw_board(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, pygame.Color("#1958B7"), BOARD_RECT, border_radius=26)
        for row in range(ROWS):
            for column in range(COLUMNS):
                center = (
                    BOARD_RECT.x + column * CELL_SIZE + CELL_SIZE // 2,
                    BOARD_RECT.y + row * 82 + 45,
                )
                piece = self.model.piece_at(row, column)
                color = theme.CREAM
                if piece is Piece.PLAYER:
                    color = theme.CORAL
                elif piece is Piece.COMPUTER:
                    color = theme.YELLOW
                pygame.draw.circle(surface, color, center, 34)
                pygame.draw.circle(surface, pygame.Color("#123C82"), center, 36, width=4)

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        message = {
            ConnectState.PLAYER_WON: "You won!",
            ConnectState.COMPUTER_WON: "Good game!",
            ConnectState.DRAW: "A draw!",
        }[self.model.state]
        theme.draw_text(surface, message, 52, theme.INK, (640, 310), bold=True)
