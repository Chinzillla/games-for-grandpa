from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from enum import Enum

MAZE = (
    "###############",
    "#.............#",
    "#.###.###.###.#",
    "#.............#",
    "###.#.#####.#.#",
    "#...#...#...#.#",
    "#.#####.#.###.#",
    "#.............#",
    "#.###.###.###.#",
    "#.............#",
    "###############",
)
ROWS = len(MAZE)
COLUMNS = len(MAZE[0])


class MazeState(Enum):
    PLAYING = "playing"
    COMPLETE = "complete"
    CAUGHT = "caught"


@dataclass(frozen=True, slots=True)
class Cell:
    row: int
    column: int


class MazeChaseModel:
    def __init__(self) -> None:
        self.player = Cell(1, 1)
        self.enemy = Cell(9, 13)
        self.path: deque[Cell] = deque()
        self.pellets: set[Cell] = set()
        self.move_timer = 0.0
        self.enemy_timer = 0.0
        self.state = MazeState.PLAYING
        self.reset()

    def reset(self) -> None:
        self.player = Cell(1, 1)
        self.enemy = Cell(9, 13)
        self.path = deque()
        # DSA: A set gives O(1) average pellet removal by grid coordinate.
        self.pellets = {
            Cell(row, column)
            for row, line in enumerate(MAZE)
            for column, value in enumerate(line)
            if value == "."
        }
        self.pellets.discard(self.player)
        self.move_timer = 0.0
        self.enemy_timer = 0.0
        self.state = MazeState.PLAYING

    def click_cell(self, cell: Cell) -> bool:
        if self.state is not MazeState.PLAYING or not self.walkable(cell):
            return False
        path = self._shortest_path(self.player, cell)
        if not path:
            return False
        self.path = deque(path[1:])
        return True

    def update(self, dt: float) -> None:
        if self.state is not MazeState.PLAYING:
            return
        self.move_timer -= dt
        self.enemy_timer -= dt
        if self.move_timer <= 0 and self.path:
            self.player = self.path.popleft()
            self.pellets.discard(self.player)
            self.move_timer = 0.17
        if self.enemy_timer <= 0:
            path = self._shortest_path(self.enemy, self.player)
            if len(path) > 1:
                self.enemy = path[1]
            self.enemy_timer = 0.55
        if self.enemy == self.player:
            self.state = MazeState.CAUGHT
        elif not self.pellets:
            self.state = MazeState.COMPLETE

    @staticmethod
    def walkable(cell: Cell) -> bool:
        return (
            0 <= cell.row < ROWS
            and 0 <= cell.column < COLUMNS
            and MAZE[cell.row][cell.column] != "#"
        )

    def _shortest_path(self, start: Cell, goal: Cell) -> list[Cell]:
        # DSA: Breadth-first search finds the shortest path in an unweighted grid.
        queue: deque[Cell] = deque([start])
        previous: dict[Cell, Cell | None] = {start: None}
        while queue:
            current = queue.popleft()
            if current == goal:
                break
            for neighbor in self._neighbors(current):
                if neighbor not in previous:
                    previous[neighbor] = current
                    queue.append(neighbor)
        if goal not in previous:
            return []
        path: list[Cell] = []
        current: Cell | None = goal
        while current is not None:
            path.append(current)
            current = previous[current]
        path.reverse()
        return path

    def _neighbors(self, cell: Cell) -> list[Cell]:
        candidates = (
            Cell(cell.row - 1, cell.column),
            Cell(cell.row + 1, cell.column),
            Cell(cell.row, cell.column - 1),
            Cell(cell.row, cell.column + 1),
        )
        return [candidate for candidate in candidates if self.walkable(candidate)]
