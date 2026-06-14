from __future__ import annotations

from games_for_grandpa.games.fishing_game import FishingModel, FishingState


def test_lowering_and_reeling_moves_hook() -> None:
    model = FishingModel()

    model.set_lowering(True)
    model.update(0.5)
    lowered = model.hook_depth
    model.set_reeling(True)
    model.update(0.5)

    assert lowered > 90
    assert model.hook_depth < lowered


def test_hooking_fish_enters_hooked_state() -> None:
    model = FishingModel()
    model.rod_x = model.fish.x
    model.hook_depth = model.fish.y

    model.update(0.1)

    assert model.state is FishingState.HOOKED


def test_too_much_tension_breaks_line_and_respawns() -> None:
    model = FishingModel()
    model.state = FishingState.HOOKED
    model.tension = 99
    model.set_reeling(True)

    model.update(1.0)

    assert model.state is FishingState.PLAYING
    assert model.tension == 0
