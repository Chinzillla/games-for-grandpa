from __future__ import annotations

from games_for_grandpa.core import GameDefinition
from games_for_grandpa.games.paddle_rally_scene import PaddleRallyScene
from games_for_grandpa.games.target_tap_scene import TargetTapScene
from games_for_grandpa.games.three_in_row_scene import ThreeInRowScene


def build_game_registry() -> dict[str, GameDefinition]:
    definitions = (
        GameDefinition(
            game_id="target_tap",
            title="Target Tap",
            description="Click 10 large targets.\nMissing never removes points.",
            scene_factory=TargetTapScene,
        ),
        GameDefinition(
            game_id="three_in_row",
            title="Three in a Row",
            description="Place three marks in a row.\nPlay a friendly computer.",
            scene_factory=ThreeInRowScene,
        ),
        GameDefinition(
            game_id="paddle_rally",
            title="Paddle Rally",
            description="Move the paddle with the mouse.\nKeep the ball in play.",
            scene_factory=PaddleRallyScene,
        ),
    )
    # DSA: A dictionary gives average O(1) lookup from a stable game ID.
    return {definition.game_id: definition for definition in definitions}
