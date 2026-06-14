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
