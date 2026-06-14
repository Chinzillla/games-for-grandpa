from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

GRID_SIZE = 3
PIECE_COUNT = GRID_SIZE * GRID_SIZE


class JigsawState(Enum):
    PLAYING = "playing"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class Swap:
    first: int
    second: int


class JigsawPuzzleModel:
    def __init__(self, *, rng: random.Random | None = None) -> None:
        self.rng = rng or random.Random()
        self.positions = list(range(PIECE_COUNT))
        self.selected: int | None = None
        self.state = JigsawState.PLAYING
        self.shuffle()

    def shuffle(self) -> None:
        # DSA: A permutation list maps each visible slot to the source tile in O(1).
        self.positions = list(range(PIECE_COUNT))
        while self.positions == list(range(PIECE_COUNT)):
            self.rng.shuffle(self.positions)
        self.selected = None
        self.state = JigsawState.PLAYING

    def click(self, index: int) -> Swap | None:
        if self.state is JigsawState.COMPLETE or not 0 <= index < PIECE_COUNT:
            return None
        if self.selected is None:
            self.selected = index
            return None
        first = self.selected
        second = index
        self.selected = None
        # DSA: Swapping two list entries is O(1); solved detection scans only 9 pieces.
        self.positions[first], self.positions[second] = (
            self.positions[second],
            self.positions[first],
        )
        if self.positions == list(range(PIECE_COUNT)):
            self.state = JigsawState.COMPLETE
        return Swap(first, second)
