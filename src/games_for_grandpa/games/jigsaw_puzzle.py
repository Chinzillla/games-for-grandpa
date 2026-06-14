from __future__ import annotations

import random
from dataclasses import dataclass
from enum import Enum

DEFAULT_GRID_SIZE = 3
GRID_OPTIONS = (3, 4, 5)
GRID_SIZE = DEFAULT_GRID_SIZE
PIECE_COUNT = GRID_SIZE * GRID_SIZE


class JigsawState(Enum):
    PLAYING = "playing"
    COMPLETE = "complete"


@dataclass(frozen=True, slots=True)
class DropResult:
    piece_id: int
    slot: int
    placed: bool


class JigsawPuzzleModel:
    def __init__(
        self,
        *,
        rng: random.Random | None = None,
        grid_size: int = DEFAULT_GRID_SIZE,
    ) -> None:
        self.rng = rng or random.Random()
        self.grid_size = self._validate_grid_size(grid_size)
        self.tray: list[int] = []
        self.slots: list[int | None] = []
        self.state = JigsawState.PLAYING
        self.reset()

    @property
    def piece_count(self) -> int:
        return self.grid_size * self.grid_size

    def reset(self, grid_size: int | None = None) -> None:
        if grid_size is not None:
            self.grid_size = self._validate_grid_size(grid_size)
        self.slots = [None] * self.piece_count
        self.tray = list(range(self.piece_count))
        self.rng.shuffle(self.tray)
        if self.tray == list(range(self.piece_count)):
            self.tray.reverse()
        self.state = JigsawState.PLAYING

    def place_piece(self, piece_id: int, slot: int) -> DropResult:
        if (
            self.state is JigsawState.COMPLETE
            or piece_id not in self.tray
            or not 0 <= slot < self.piece_count
        ):
            return DropResult(piece_id, slot, False)

        # DSA: A list maps board slots to source piece IDs, making solved checks O(n).
        placed = piece_id == slot and self.slots[slot] is None
        if placed:
            self.tray.remove(piece_id)
            self.slots[slot] = piece_id
            if all(piece is not None for piece in self.slots):
                self.state = JigsawState.COMPLETE
        return DropResult(piece_id, slot, placed)

    @staticmethod
    def _validate_grid_size(grid_size: int) -> int:
        if grid_size not in GRID_OPTIONS:
            raise ValueError(f"unsupported jigsaw grid size: {grid_size}")
        return grid_size
