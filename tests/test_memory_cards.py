from __future__ import annotations

import random

from games_for_grandpa.games.memory_cards import MemoryCardsModel, MemoryState


def test_matching_pair_stays_face_up() -> None:
    model = MemoryCardsModel(rng=random.Random(4))
    first_pair = model.cards[0].pair_id
    second_index = next(
        index for index, card in enumerate(model.cards[1:], start=1) if card.pair_id == first_pair
    )

    assert model.flip(0)
    assert model.flip(second_index)

    assert model.cards[0].matched
    assert model.cards[second_index].matched
    assert model.matches == 1


def test_mismatched_pair_hides_after_delay() -> None:
    model = MemoryCardsModel(rng=random.Random(5))
    first_pair = model.cards[0].pair_id
    second_index = next(
        index for index, card in enumerate(model.cards[1:], start=1) if card.pair_id != first_pair
    )

    assert model.flip(0)
    assert model.flip(second_index)
    assert model.state is MemoryState.SHOWING_MISMATCH

    model.update(1.0)

    assert model.state is MemoryState.PLAYING
    assert not model.cards[0].face_up
    assert not model.cards[second_index].face_up


def test_all_pairs_complete_game() -> None:
    model = MemoryCardsModel(rng=random.Random(6))
    for index in range(0, len(model.cards), 2):
        model.cards[index].pair_id = index
        model.cards[index + 1].pair_id = index

    for index in range(0, len(model.cards), 2):
        assert model.flip(index)
        assert model.flip(index + 1)

    assert model.state is MemoryState.COMPLETE


def test_memory_grid_size_can_change() -> None:
    model = MemoryCardsModel(rng=random.Random(7), grid_size=(2, 3))

    assert model.card_count == 6
    assert model.pair_count == 3

    model.reset((4, 4))

    assert model.card_count == 16
    assert model.pair_count == 8
    assert len(model.cards) == 16

    model.reset((6, 6))

    assert model.card_count == 36
    assert model.pair_count == 18
    assert len(model.cards) == 36


def test_memory_rejects_grids_larger_than_icon_set() -> None:
    model = MemoryCardsModel(rng=random.Random(8))

    try:
        model.reset((6, 8))
    except ValueError as error:
        assert "unsupported memory grid" in str(error)
    else:
        raise AssertionError("unsupported memory grid should fail")
