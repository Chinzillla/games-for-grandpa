from __future__ import annotations

import math
import random
from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from games_for_grandpa.core import Difficulty

WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)
MOVE_ORDER = (4, 0, 2, 6, 8, 1, 3, 5, 7)


class Mark(Enum):
    EMPTY = ""
    PLAYER = "X"
    COMPUTER = "O"


class ThreeInRowState(Enum):
    PLAYING = "playing"
    PLAYER_WON = "player_won"
    COMPUTER_WON = "computer_won"
    DRAW = "draw"


class Board:
    def __init__(self, cells: list[Mark] | None = None) -> None:
        self.cells = list(cells) if cells is not None else [Mark.EMPTY] * 9
        if len(self.cells) != 9:
            raise ValueError("A Three in a Row board must have nine cells")
        # DSA: A set gives average O(1) membership and removal for legal moves.
        self.legal_moves: set[int] = {
            index for index, mark in enumerate(self.cells) if mark is Mark.EMPTY
        }

    def place(self, index: int, mark: Mark) -> None:
        if mark is Mark.EMPTY:
            raise ValueError("Cannot place an empty mark")
        if index not in self.legal_moves:
            raise ValueError(f"Cell {index} is not available")
        self.cells[index] = mark
        self.legal_moves.remove(index)

    def undo(self, index: int) -> None:
        if self.cells[index] is Mark.EMPTY:
            raise ValueError(f"Cell {index} is already empty")
        self.cells[index] = Mark.EMPTY
        self.legal_moves.add(index)

    def winner(self) -> Mark:
        for first, second, third in WINNING_LINES:
            mark = self.cells[first]
            if (
                mark is not Mark.EMPTY
                and mark is self.cells[second]
                and mark is self.cells[third]
            ):
                return mark
        return Mark.EMPTY

    def state(self) -> ThreeInRowState:
        winner = self.winner()
        if winner is Mark.PLAYER:
            return ThreeInRowState.PLAYER_WON
        if winner is Mark.COMPUTER:
            return ThreeInRowState.COMPUTER_WON
        if not self.legal_moves:
            return ThreeInRowState.DRAW
        return ThreeInRowState.PLAYING

    def ordered_moves(self) -> list[int]:
        return [move for move in MOVE_ORDER if move in self.legal_moves]

    def key(self) -> tuple[Mark, ...]:
        return tuple(self.cells)


class MoveStrategy(Protocol):
    def choose_move(self, board: Board) -> int: ...


@dataclass(slots=True)
class RandomStrategy:
    rng: random.Random

    def choose_move(self, board: Board) -> int:
        if not board.legal_moves:
            raise ValueError("No legal moves remain")
        return self.rng.choice(sorted(board.legal_moves))


class MinimaxStrategy:
    def __init__(
        self,
        *,
        max_depth: int | None,
        randomize_equal: bool,
        rng: random.Random | None = None,
    ) -> None:
        self.max_depth = max_depth
        self.randomize_equal = randomize_equal
        self.rng = rng or random.Random()
        # DSA: This dictionary memoizes repeated search states for average O(1) lookup.
        self.memo: dict[tuple[object, ...], int] = {}

    def choose_move(self, board: Board) -> int:
        if not board.legal_moves:
            raise ValueError("No legal moves remain")
        best_score = -math.inf
        best_moves: list[int] = []
        depth_left = self.max_depth

        for move in board.ordered_moves():
            board.place(move, Mark.COMPUTER)
            score = self._score(board, Mark.PLAYER, depth_left, -math.inf, math.inf)
            board.undo(move)
            if score > best_score:
                best_score = score
                best_moves = [move]
            elif score == best_score:
                best_moves.append(move)

        if self.randomize_equal:
            return self.rng.choice(best_moves)
        return best_moves[0]

    def _score(
        self,
        board: Board,
        turn: Mark,
        depth_left: int | None,
        alpha: float,
        beta: float,
    ) -> int:
        state = board.state()
        if state is not ThreeInRowState.PLAYING:
            return self._terminal_score(board, state)
        if depth_left is not None and depth_left <= 0:
            return self._heuristic(board)

        # Including the search window makes cached alpha-beta results safe to reuse.
        key = (board.key(), turn, depth_left, alpha, beta)
        if key in self.memo:
            return self.memo[key]

        next_depth = None if depth_left is None else depth_left - 1
        if turn is Mark.COMPUTER:
            value = -math.inf
            for move in board.ordered_moves():
                board.place(move, Mark.COMPUTER)
                value = max(
                    value,
                    self._score(board, Mark.PLAYER, next_depth, alpha, beta),
                )
                board.undo(move)
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
        else:
            value = math.inf
            for move in board.ordered_moves():
                board.place(move, Mark.PLAYER)
                value = min(
                    value,
                    self._score(board, Mark.COMPUTER, next_depth, alpha, beta),
                )
                board.undo(move)
                beta = min(beta, value)
                if alpha >= beta:
                    break

        result = int(value)
        self.memo[key] = result
        return result

    @staticmethod
    def _terminal_score(board: Board, state: ThreeInRowState) -> int:
        remaining = len(board.legal_moves)
        if state is ThreeInRowState.COMPUTER_WON:
            return 100 + remaining
        if state is ThreeInRowState.PLAYER_WON:
            return -100 - remaining
        return 0

    @staticmethod
    def _heuristic(board: Board) -> int:
        score = 0
        for line in WINNING_LINES:
            marks = [board.cells[index] for index in line]
            computers = marks.count(Mark.COMPUTER)
            players = marks.count(Mark.PLAYER)
            if computers and not players:
                score += 3**computers
            elif players and not computers:
                score -= 3**players
        if board.cells[4] is Mark.COMPUTER:
            score += 2
        elif board.cells[4] is Mark.PLAYER:
            score -= 2
        return score


def strategy_for(
    difficulty: Difficulty,
    *,
    rng: random.Random | None = None,
) -> MoveStrategy:
    random_source = rng or random.Random()
    if difficulty is Difficulty.EASY:
        return RandomStrategy(random_source)
    if difficulty is Difficulty.NORMAL:
        return MinimaxStrategy(max_depth=3, randomize_equal=True, rng=random_source)
    return MinimaxStrategy(max_depth=None, randomize_equal=False, rng=random_source)


class ThreeInRowModel:
    def __init__(
        self,
        difficulty: Difficulty = Difficulty.EASY,
        *,
        strategy: MoveStrategy | None = None,
    ) -> None:
        self.difficulty = difficulty
        self.board = Board()
        self.strategy = strategy or strategy_for(difficulty)

    @property
    def state(self) -> ThreeInRowState:
        return self.board.state()

    def player_move(self, index: int) -> bool:
        if self.state is not ThreeInRowState.PLAYING or index not in self.board.legal_moves:
            return False
        self.board.place(index, Mark.PLAYER)
        if self.state is ThreeInRowState.PLAYING:
            computer_move = self.strategy.choose_move(self.board)
            self.board.place(computer_move, Mark.COMPUTER)
        return True

    def reset(self, difficulty: Difficulty | None = None) -> None:
        if difficulty is not None:
            self.difficulty = difficulty
        self.board = Board()
        self.strategy = strategy_for(self.difficulty)

