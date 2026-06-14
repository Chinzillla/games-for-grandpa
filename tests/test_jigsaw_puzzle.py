from __future__ import annotations

import random

from games_for_grandpa.games.jigsaw_puzzle import JigsawPuzzleModel, JigsawState


def test_jigsaw_starts_with_shuffled_tray_and_empty_board() -> None:
    model = JigsawPuzzleModel(rng=random.Random(1))

    assert sorted(model.tray) == list(range(model.piece_count))
    assert model.tray != list(range(model.piece_count))
    assert model.slots == [None] * model.piece_count


def test_wrong_jigsaw_drop_stays_in_tray() -> None:
    model = JigsawPuzzleModel(rng=random.Random(2))
    piece_id = model.tray[0]
    wrong_slot = (piece_id + 1) % model.piece_count

    result = model.place_piece(piece_id, wrong_slot)

    assert not result.placed
    assert piece_id in model.tray
    assert model.slots[wrong_slot] is None


def test_correct_jigsaw_drop_snaps_piece_to_board() -> None:
    model = JigsawPuzzleModel(rng=random.Random(3))
    piece_id = model.tray[0]

    result = model.place_piece(piece_id, piece_id)

    assert result.placed
    assert piece_id not in model.tray
    assert model.slots[piece_id] == piece_id


def test_jigsaw_completes_when_all_pieces_are_placed() -> None:
    model = JigsawPuzzleModel(rng=random.Random(4), grid_size=3)

    for piece_id in list(model.tray):
        model.place_piece(piece_id, piece_id)

    assert model.state is JigsawState.COMPLETE


def test_jigsaw_grid_size_can_change() -> None:
    model = JigsawPuzzleModel(rng=random.Random(5))

    model.reset(5)

    assert model.grid_size == 5
    assert model.piece_count == 25
    assert len(model.tray) == 25
