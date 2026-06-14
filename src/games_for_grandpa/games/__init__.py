from __future__ import annotations

from games_for_grandpa.core import Difficulty, GameDefinition
from games_for_grandpa.games.connect_four_scene import ConnectFourScene
from games_for_grandpa.games.duck_hunt_scene import DuckHuntScene
from games_for_grandpa.games.fishing_game_scene import FishingGameScene
from games_for_grandpa.games.jigsaw_puzzle_scene import JigsawPuzzleScene
from games_for_grandpa.games.maze_chase_scene import MazeChaseScene
from games_for_grandpa.games.memory_cards_scene import MemoryCardsScene
from games_for_grandpa.games.paddle_rally_scene import PaddleRallyScene
from games_for_grandpa.games.space_defense_scene import SpaceDefenseScene
from games_for_grandpa.games.target_practice_scene import TargetPracticeScene
from games_for_grandpa.games.three_in_row_scene import ThreeInRowScene
from games_for_grandpa.games.whack_a_mole_scene import WhackAMoleScene


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
            game_id="connect_four",
            title="Connect Four",
            description="",
            scene_factory=ConnectFourScene,
            difficulties=(Difficulty.NORMAL,),
        ),
        GameDefinition(
            game_id="paddle_rally",
            title="Pong",
            description="",
            scene_factory=PaddleRallyScene,
            difficulties=(Difficulty.EASY,),
        ),
        GameDefinition(
            game_id="space_defense",
            title="Space Defense",
            description="",
            scene_factory=SpaceDefenseScene,
            difficulties=(Difficulty.EASY,),
        ),
        GameDefinition(
            game_id="maze_chase",
            title="Maze Chase",
            description="",
            scene_factory=MazeChaseScene,
            difficulties=(Difficulty.EASY,),
        ),
        GameDefinition(
            game_id="whack_a_mole",
            title="Whack-a-Mole",
            description="",
            scene_factory=WhackAMoleScene,
            difficulties=(Difficulty.EASY,),
        ),
        GameDefinition(
            game_id="target_practice",
            title="Target Practice",
            description="",
            scene_factory=TargetPracticeScene,
            difficulties=(Difficulty.EASY,),
        ),
        GameDefinition(
            game_id="memory_cards",
            title="Memory Cards",
            description="",
            scene_factory=MemoryCardsScene,
            difficulties=(Difficulty.EASY,),
        ),
        GameDefinition(
            game_id="jigsaw_puzzle",
            title="Jigsaw Puzzle",
            description="",
            scene_factory=JigsawPuzzleScene,
            difficulties=(Difficulty.EASY,),
        ),
        GameDefinition(
            game_id="fishing_game",
            title="Fishing",
            description="",
            scene_factory=FishingGameScene,
            difficulties=(Difficulty.EASY,),
        ),
    )
    # DSA: A dictionary gives average O(1) lookup from a stable game ID.
    return {definition.game_id: definition for definition in definitions}
