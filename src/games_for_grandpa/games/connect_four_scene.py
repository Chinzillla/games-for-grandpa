from __future__ import annotations

from dataclasses import dataclass

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.connect_four import (
    COLUMNS,
    ROWS,
    ConnectFourModel,
    ConnectState,
    DropResult,
    Piece,
)
from games_for_grandpa.ui import GameHud, ResultActions

BOARD_RECT = pygame.Rect(290, 130, 700, 540)
CELL_SIZE = BOARD_RECT.width // COLUMNS
ROW_STEP = 82


@dataclass(slots=True)
class FallingPiece:
    row: int
    column: int
    piece: Piece
    progress: float = 0.0


class ConnectFourScene(Scene):
    GAME_ID = "connect_four"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = ConnectFourModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.falling_pieces: list[FallingPiece] = []
        self.hover_column: int | None = None
        self.pending_computer_column: int | None = None
        self.finished_recorded = False

    def _restart(self) -> None:
        self.model.reset()
        self.falling_pieces.clear()
        self.hover_column = None
        self.pending_computer_column = None
        self.finished_recorded = False
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._showing_result():
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if hasattr(event, "pos"):
            self.hover_column = self._column_from_position(event.pos)
        if (
            self.model.state is not ConnectState.PLAYING
            or self.falling_pieces
            or self.pending_computer_column is not None
        ):
            return
        if (
            event.type != pygame.MOUSEBUTTONDOWN
            or event.button != 1
            or self.hover_column is None
        ):
            return
        drop = self.model.drop_player_piece(self.hover_column)
        if drop is not None:
            self._queue_drop_animation(drop)
            if self.model.state is ConnectState.PLAYING:
                self.pending_computer_column = self.model.choose_computer_column()
            self.controller.play_sound("success")

    def update(self, dt: float) -> None:
        for piece in self.falling_pieces:
            piece.progress = min(1.0, piece.progress + dt * 3.8)
        self.falling_pieces = [piece for piece in self.falling_pieces if piece.progress < 1.0]
        if not self.falling_pieces and self.pending_computer_column is not None:
            drop = self.model.drop_computer_piece(self.pending_computer_column)
            self.pending_computer_column = None
            if drop is not None:
                self._queue_drop_animation(drop)
                self.controller.play_sound("success")
        if not self.falling_pieces and self._showing_result() and not self.finished_recorded:
            self.finished_recorded = True
            score = 1 if self.model.state is ConnectState.PLAYER_WON else 0
            self.controller.record_score(self.GAME_ID, score)
            self.controller.play_sound("complete")

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#2F80ED"), pygame.Color("#8CC7FF"))
        self._draw_title(surface)
        self._draw_board(surface)
        if self._showing_result():
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_title(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        message = "Computer turn" if self.pending_computer_column is not None else "Drop a piece"
        theme.draw_text(surface, message, 27, theme.INK, badge.center, bold=True)

    def _draw_board(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, pygame.Color("#1958B7"), BOARD_RECT, border_radius=26)
        hidden = {(piece.row, piece.column) for piece in self.falling_pieces}
        self._draw_hover_coin(surface)
        for row in range(ROWS):
            for column in range(COLUMNS):
                center = (
                    BOARD_RECT.x + column * CELL_SIZE + CELL_SIZE // 2,
                    BOARD_RECT.y + row * ROW_STEP + 45,
                )
                piece = (
                    Piece.EMPTY
                    if (row, column) in hidden
                    else self.model.piece_at(row, column)
                )
                color = theme.CREAM
                if piece is Piece.PLAYER:
                    color = theme.CORAL
                elif piece is Piece.COMPUTER:
                    color = theme.YELLOW
                pygame.draw.circle(surface, color, center, 34)
                pygame.draw.circle(surface, pygame.Color("#123C82"), center, 36, width=4)
        for piece in self.falling_pieces:
            self._draw_falling_piece(surface, piece)

    def _draw_hover_coin(self, surface: pygame.Surface) -> None:
        column = self.pending_computer_column
        piece = Piece.COMPUTER
        if (
            column is None
            and self.hover_column is not None
            and self.model.state is ConnectState.PLAYING
        ):
            column = self.hover_column
            piece = Piece.PLAYER
        if column is None:
            return
        x = BOARD_RECT.x + column * CELL_SIZE + CELL_SIZE // 2
        color = theme.CORAL if piece is Piece.PLAYER else theme.YELLOW
        layer = pygame.Surface((82, 82), pygame.SRCALPHA)
        pygame.draw.circle(layer, pygame.Color(color.r, color.g, color.b, 145), (41, 41), 34)
        pygame.draw.circle(layer, pygame.Color(255, 255, 255, 180), (29, 29), 8)
        surface.blit(layer, layer.get_rect(center=(x, 102)))

    def _queue_drop_animation(self, drop: DropResult) -> None:
        self.falling_pieces = [FallingPiece(drop.row, drop.column, drop.piece)]

    @staticmethod
    def _column_from_position(position: tuple[int, int]) -> int | None:
        x, _ = position
        if not (BOARD_RECT.left <= x < BOARD_RECT.right):
            return None
        return (x - BOARD_RECT.x) // CELL_SIZE

    def _showing_result(self) -> bool:
        return self.model.state is not ConnectState.PLAYING and not self.falling_pieces

    @staticmethod
    def _draw_falling_piece(surface: pygame.Surface, piece: FallingPiece) -> None:
        target_x = BOARD_RECT.x + piece.column * CELL_SIZE + CELL_SIZE // 2
        target_y = BOARD_RECT.y + piece.row * ROW_STEP + 45
        eased = 1 - (1 - piece.progress) ** 3
        y = round(BOARD_RECT.y - 72 + (target_y - (BOARD_RECT.y - 72)) * eased)
        color = theme.CORAL if piece.piece is Piece.PLAYER else theme.YELLOW
        pygame.draw.circle(surface, theme.SHADOW, (target_x + 4, y + 7), 34)
        pygame.draw.circle(surface, color, (target_x, y), 34)
        pygame.draw.circle(surface, theme.WHITE, (target_x - 10, y - 10), 8)

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        message = {
            ConnectState.PLAYER_WON: "You won!",
            ConnectState.COMPUTER_WON: "Good game!",
            ConnectState.DRAW: "A draw!",
        }[self.model.state]
        theme.draw_text(surface, message, 52, theme.INK, (640, 310), bold=True)
