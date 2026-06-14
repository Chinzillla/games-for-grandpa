from __future__ import annotations

from games_for_grandpa.core import AppController, GameDefinition
from games_for_grandpa.scenes import ComingSoonScene


def build_game_registry() -> dict[str, GameDefinition]:
    definitions = (
        _placeholder(
            "target_tap",
            "Target Tap",
            "Click 10 large targets.\nMissing never removes points.",
        ),
        _placeholder(
            "three_in_row",
            "Three in a Row",
            "Place three marks in a row.\nPlay a friendly computer.",
        ),
        _placeholder(
            "paddle_rally",
            "Paddle Rally",
            "Move the paddle with the mouse.\nKeep the ball in play.",
        ),
    )
    # DSA: A dictionary gives average O(1) lookup from a stable game ID.
    return {definition.game_id: definition for definition in definitions}


def _placeholder(game_id: str, title: str, description: str) -> GameDefinition:
    def factory(controller: AppController) -> ComingSoonScene:
        return ComingSoonScene(controller, game_id, title)

    return GameDefinition(
        game_id=game_id,
        title=title,
        description=description,
        scene_factory=factory,
    )
