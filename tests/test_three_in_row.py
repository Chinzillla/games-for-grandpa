from __future__ import annotations

import random

import pytest

from games_for_grandpa.core import Difficulty
from games_for_grandpa.games.three_in_row import (
    Board,
    Mark,
    MinimaxStrategy,
    RandomStrategy,
    ThreeInRowState,
    strategy_for,
)


@pytest.mark.parametrize(
    "line",
    [
        (0, 1, 2),
        (3, 4, 5),
        (6, 7, 8),
        (0, 3, 6),
        (1, 4, 7),
        (2, 5, 8),
        (0, 4, 8),
        (2, 4, 6),
    ],
)
def test_board_detects_every_winning_line(line: tuple[int, int, int]) -> None:
    board = Board()
    for index in line:
        board.place(index, Mark.PLAYER)

    assert board.winner() is Mark.PLAYER
    assert board.state() is ThreeInRowState.PLAYER_WON


def test_board_rejects_occupied_cell() -> None:
    board = Board()
    board.place(4, Mark.PLAYER)

    with pytest.raises(ValueError):
        board.place(4, Mark.COMPUTER)


def test_random_strategy_returns_legal_move() -> None:
    board = Board()
    board.place(4, Mark.PLAYER)
    strategy = RandomStrategy(random.Random(2))

    assert strategy.choose_move(board) in board.legal_moves


def test_challenge_ai_takes_immediate_win() -> None:
    board = Board(
        [
            Mark.COMPUTER,
            Mark.COMPUTER,
            Mark.EMPTY,
            Mark.PLAYER,
            Mark.PLAYER,
            Mark.EMPTY,
            Mark.EMPTY,
            Mark.EMPTY,
            Mark.EMPTY,
        ]
    )
    strategy = MinimaxStrategy(max_depth=None, randomize_equal=False)

    assert strategy.choose_move(board) == 2


def test_challenge_ai_blocks_immediate_loss() -> None:
    board = Board(
        [
            Mark.PLAYER,
            Mark.PLAYER,
            Mark.EMPTY,
            Mark.EMPTY,
            Mark.COMPUTER,
            Mark.EMPTY,
            Mark.EMPTY,
            Mark.EMPTY,
            Mark.EMPTY,
        ]
    )
    strategy = MinimaxStrategy(max_depth=None, randomize_equal=False)

    assert strategy.choose_move(board) == 2


def test_challenge_ai_cannot_lose_from_any_player_path() -> None:
    strategy = strategy_for(Difficulty.CHALLENGE)
    visited: set[tuple[Mark, ...]] = set()

    def explore(board: Board) -> None:
        key = board.key()
        if key in visited:
            return
        visited.add(key)

        for player_move in sorted(board.legal_moves):
            board.place(player_move, Mark.PLAYER)
            state = board.state()
            assert state is not ThreeInRowState.PLAYER_WON
            if state is ThreeInRowState.PLAYING:
                computer_move = strategy.choose_move(board)
                board.place(computer_move, Mark.COMPUTER)
                state = board.state()
                assert state is not ThreeInRowState.PLAYER_WON
                if state is ThreeInRowState.PLAYING:
                    explore(board)
                board.undo(computer_move)
            board.undo(player_move)

    explore(Board())
    assert visited

