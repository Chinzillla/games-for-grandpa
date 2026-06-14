from __future__ import annotations

import random

from games_for_grandpa.games.jigsaw_puzzle import JigsawPuzzleModel, JigsawState


def test_jigsaw_shuffle_is_not_solved() -> None:
    model = JigsawPuzzleModel(rng=random.Random(1))

    assert model.positions != list(range(len(model.positions)))


def test_clicking_two_pieces_swaps_them() -> None:
    model = JigsawPuzzleModel(rng=random.Random(2))
    before = model.positions.copy()

    model.click(0)
    swap = model.click(1)

    assert swap is not None
    assert model.positions[0] == before[1]
    assert model.positions[1] == before[0]


def test_solved_jigsaw_completes() -> None:
    model = JigsawPuzzleModel(rng=random.Random(3))
    model.positions = [1, 0, 2, 3, 4, 5, 6, 7, 8]

    model.click(0)
    model.click(1)

    assert model.state is JigsawState.COMPLETE
