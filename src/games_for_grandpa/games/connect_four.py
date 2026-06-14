from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum

ROWS = 6
COLUMNS = 7
CONNECT_N = 4


class Piece(Enum):
    EMPTY = 0
    PLAYER = 1
    COMPUTER = 2


class ConnectState(Enum):
    PLAYING = "playing"
    PLAYER_WON = "player_won"
    COMPUTER_WON = "computer_won"
    DRAW = "draw"


@dataclass(frozen=True, slots=True)
class MoveScore:
    column: int
    score: int


@dataclass(frozen=True, slots=True)
class DropResult:
    row: int
    column: int
    piece: Piece


class ConnectFourModel:
    def __init__(self) -> None:
        self.cells = [Piece.EMPTY] * (ROWS * COLUMNS)
        self.legal_columns = set(range(COLUMNS))
        self.state = ConnectState.PLAYING

    def reset(self) -> None:
        self.cells = [Piece.EMPTY] * (ROWS * COLUMNS)
        self.legal_columns = set(range(COLUMNS))
        self.state = ConnectState.PLAYING

    def player_move(self, column: int) -> bool:
        if self.drop_player_piece(column) is None:
            return False
        if self.state is ConnectState.PLAYING:
            self.drop_computer_piece()
        return True

    def drop_player_piece(self, column: int) -> DropResult | None:
        if self.state is not ConnectState.PLAYING or column not in self.legal_columns:
            return None
        row = self._drop(column, Piece.PLAYER)
        self.state = self._state_after_move()
        return DropResult(row, column, Piece.PLAYER)

    def drop_computer_piece(self, column: int | None = None) -> DropResult | None:
        if self.state is not ConnectState.PLAYING:
            return None
        column = self.choose_computer_column() if column is None else column
        if column not in self.legal_columns:
            return None
        row = self._drop(column, Piece.COMPUTER)
        self.state = self._state_after_move()
        return DropResult(row, column, Piece.COMPUTER)

    def choose_computer_column(self) -> int:
        return self._choose_computer_column()

    def piece_at(self, row: int, column: int) -> Piece:
        return self.cells[row * COLUMNS + column]

    def _drop(self, column: int, piece: Piece) -> int:
        for row in range(ROWS - 1, -1, -1):
            if self.piece_at(row, column) is Piece.EMPTY:
                self.cells[row * COLUMNS + column] = piece
                if self.piece_at(0, column) is not Piece.EMPTY:
                    self.legal_columns.discard(column)
                return row
        raise ValueError("Column is full")

    def _undo(self, column: int) -> None:
        for row in range(ROWS):
            if self.piece_at(row, column) is not Piece.EMPTY:
                self.cells[row * COLUMNS + column] = Piece.EMPTY
                self.legal_columns.add(column)
                return
        raise ValueError("Column is empty")

    def _state_after_move(self) -> ConnectState:
        winner = self._winner()
        if winner is Piece.PLAYER:
            return ConnectState.PLAYER_WON
        if winner is Piece.COMPUTER:
            return ConnectState.COMPUTER_WON
        if not self.legal_columns:
            return ConnectState.DRAW
        return ConnectState.PLAYING

    def _winner(self) -> Piece | None:
        directions = ((0, 1), (1, 0), (1, 1), (1, -1))
        for row in range(ROWS):
            for column in range(COLUMNS):
                piece = self.piece_at(row, column)
                if piece is Piece.EMPTY:
                    continue
                for row_step, column_step in directions:
                    if self._has_line(row, column, row_step, column_step, piece):
                        return piece
        return None

    def _has_line(
        self,
        row: int,
        column: int,
        row_step: int,
        column_step: int,
        piece: Piece,
    ) -> bool:
        for offset in range(CONNECT_N):
            check_row = row + offset * row_step
            check_column = column + offset * column_step
            if not (0 <= check_row < ROWS and 0 <= check_column < COLUMNS):
                return False
            if self.piece_at(check_row, check_column) is not piece:
                return False
        return True

    def _choose_computer_column(self) -> int:
        # DSA: Depth-limited minimax with alpha-beta pruning searches likely replies first.
        ordered = sorted(self.legal_columns, key=lambda column: abs(column - COLUMNS // 2))
        best = MoveScore(ordered[0], -math.inf)
        for column in ordered:
            self._drop(column, Piece.COMPUTER)
            score = self._minimax(depth=3, maximizing=False, alpha=-math.inf, beta=math.inf)
            self._undo(column)
            if score > best.score:
                best = MoveScore(column, score)
        return best.column

    def _minimax(self, depth: int, *, maximizing: bool, alpha: float, beta: float) -> int:
        state = self._state_after_move()
        if state is ConnectState.COMPUTER_WON:
            return 10_000 + depth
        if state is ConnectState.PLAYER_WON:
            return -10_000 - depth
        if state is ConnectState.DRAW or depth == 0:
            return self._evaluate()

        ordered = sorted(self.legal_columns, key=lambda column: abs(column - COLUMNS // 2))
        if maximizing:
            value = -math.inf
            for column in ordered:
                self._drop(column, Piece.COMPUTER)
                value = max(
                    value,
                    self._minimax(depth - 1, maximizing=False, alpha=alpha, beta=beta),
                )
                self._undo(column)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return int(value)

        value = math.inf
        for column in ordered:
            self._drop(column, Piece.PLAYER)
            value = min(
                value,
                self._minimax(depth - 1, maximizing=True, alpha=alpha, beta=beta),
            )
            self._undo(column)
            beta = min(beta, value)
            if alpha >= beta:
                break
        return int(value)

    def _evaluate(self) -> int:
        score = 0
        directions = ((0, 1), (1, 0), (1, 1), (1, -1))
        for row in range(ROWS):
            for column in range(COLUMNS):
                for row_step, column_step in directions:
                    window = self._window(row, column, row_step, column_step)
                    if len(window) == CONNECT_N:
                        score += self._score_window(window)
        return score

    def _window(
        self,
        row: int,
        column: int,
        row_step: int,
        column_step: int,
    ) -> list[Piece]:
        result: list[Piece] = []
        for offset in range(CONNECT_N):
            check_row = row + offset * row_step
            check_column = column + offset * column_step
            if not (0 <= check_row < ROWS and 0 <= check_column < COLUMNS):
                return []
            result.append(self.piece_at(check_row, check_column))
        return result

    @staticmethod
    def _score_window(window: list[Piece]) -> int:
        computers = window.count(Piece.COMPUTER)
        players = window.count(Piece.PLAYER)
        if computers and players:
            return 0
        if computers:
            return 5**computers
        if players:
            return -(5**players)
        return 0
