from __future__ import annotations

from games_for_grandpa.games.maze_chase import Cell, MazeChaseModel, MazeState


def test_clicking_walkable_cell_creates_shortest_path() -> None:
    model = MazeChaseModel()

    assert model.click_cell(Cell(1, 5))

    assert list(model.path)[-1] == Cell(1, 5)


def test_clicking_wall_is_ignored() -> None:
    model = MazeChaseModel()

    assert not model.click_cell(Cell(0, 0))
    assert not model.path


def test_enemy_can_catch_player() -> None:
    model = MazeChaseModel()
    model.enemy = model.player

    model.update(0.1)

    assert model.state is MazeState.CAUGHT
