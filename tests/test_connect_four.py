from __future__ import annotations

from games_for_grandpa.games.connect_four import ConnectFourModel, ConnectState, Piece


def test_player_drop_places_piece_in_lowest_row() -> None:
    model = ConnectFourModel()

    assert model.player_move(0)

    assert model.piece_at(5, 0) is Piece.PLAYER


def test_computer_blocks_immediate_vertical_threat() -> None:
    model = ConnectFourModel()
    for _ in range(3):
        model._drop(2, Piece.PLAYER)

    assert model._choose_computer_column() == 2


def test_computer_takes_winning_move() -> None:
    model = ConnectFourModel()
    for _ in range(3):
        model._drop(3, Piece.COMPUTER)

    assert model._choose_computer_column() == 3


def test_four_connected_pieces_win() -> None:
    model = ConnectFourModel()
    for column in range(4):
        model._drop(column, Piece.PLAYER)

    assert model._state_after_move() is ConnectState.PLAYER_WON
