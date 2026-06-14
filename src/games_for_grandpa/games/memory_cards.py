from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

DEFAULT_GRID = (3, 4)
GRID_OPTIONS = ((2, 3), (3, 4), (4, 4))
CARD_COUNT = DEFAULT_GRID[0] * DEFAULT_GRID[1]
PAIR_COUNT = CARD_COUNT // 2
MISMATCH_SECONDS = 0.75


class MemoryState(Enum):
    PLAYING = "playing"
    SHOWING_MISMATCH = "showing_mismatch"
    COMPLETE = "complete"


@dataclass(slots=True)
class MemoryCard:
    pair_id: int
    face_up: bool = False
    matched: bool = False


class MemoryCardsModel:
    def __init__(
        self,
        *,
        rng: random.Random | None = None,
        grid_size: tuple[int, int] = DEFAULT_GRID,
    ) -> None:
        self.rng = rng or random.Random()
        self.rows, self.columns = self._validate_grid(grid_size)
        self.cards: list[MemoryCard] = []
        self.selected: list[int] = []
        self.matches = 0
        self.timer = 0.0
        self.state = MemoryState.PLAYING
        self.reset()

    @property
    def card_count(self) -> int:
        return self.rows * self.columns

    @property
    def pair_count(self) -> int:
        return self.card_count // 2

    def reset(self, grid_size: tuple[int, int] | None = None) -> None:
        if grid_size is not None:
            self.rows, self.columns = self._validate_grid(grid_size)
        pair_ids = [pair_id for pair_id in range(self.pair_count) for _ in range(2)]
        self.rng.shuffle(pair_ids)
        # DSA: A list gives O(1) card lookup by visible index for any selected grid size.
        self.cards = [MemoryCard(pair_id) for pair_id in pair_ids]
        self.selected = []
        self.matches = 0
        self.timer = 0.0
        self.state = MemoryState.PLAYING

    def update(self, dt: float) -> None:
        if self.state is not MemoryState.SHOWING_MISMATCH:
            return
        self.timer -= dt
        if self.timer <= 0:
            for index in self.selected:
                self.cards[index].face_up = False
            self.selected.clear()
            self.state = MemoryState.PLAYING

    def flip(self, index: int) -> bool:
        if self.state is not MemoryState.PLAYING or not 0 <= index < len(self.cards):
            return False
        card = self.cards[index]
        if card.face_up or card.matched:
            return False

        card.face_up = True
        self.selected.append(index)
        if len(self.selected) == 2:
            first, second = (self.cards[item] for item in self.selected)
            if first.pair_id == second.pair_id:
                first.matched = True
                second.matched = True
                self.selected.clear()
                self.matches += 1
                if self.matches == self.pair_count:
                    self.state = MemoryState.COMPLETE
            else:
                self.state = MemoryState.SHOWING_MISMATCH
                self.timer = MISMATCH_SECONDS
        return True

    @staticmethod
    def _validate_grid(grid_size: tuple[int, int]) -> tuple[int, int]:
        if grid_size not in GRID_OPTIONS:
            raise ValueError(f"unsupported memory grid: {grid_size}")
        rows, columns = grid_size
        if (rows * columns) % 2 != 0:
            raise ValueError("memory card grid must contain an even number of cards")
        return rows, columns
