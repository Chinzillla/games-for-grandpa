from __future__ import annotations

from games_for_grandpa.core import Difficulty, GameDefinition
from games_for_grandpa.games.duck_hunt_scene import DuckHuntScene
from games_for_grandpa.games.paddle_rally_scene import PaddleRallyScene
from games_for_grandpa.games.three_in_row_scene import ThreeInRowScene


def build_game_registry() -> dict[str, GameDefinition]:
    definitions = (
        GameDefinition(
            game_id="target_tap",
            title="Duck Hunt",
            description="",
            scene_factory=DuckHuntScene,
            difficulties=(Difficulty.CHALLENGE,),
        ),
        GameDefinition(
            game_id="three_in_row",
            title="Tic Tac Toe",
            description="",
            scene_factory=ThreeInRowScene,
            difficulties=(Difficulty.NORMAL,),
        ),
        GameDefinition(
            game_id="paddle_rally",
            title="Pong",
            description="",
            scene_factory=PaddleRallyScene,
            difficulties=(Difficulty.EASY,),
        ),
    )
    # DSA: A dictionary gives average O(1) lookup from a stable game ID.
    return {definition.game_id: definition for definition in definitions}
