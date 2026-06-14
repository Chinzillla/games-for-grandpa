from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.maze_chase import MAZE, Cell, MazeChaseModel, MazeState
from games_for_grandpa.ui import GameHud, ResultActions

CELL_SIZE = 46
BOARD_X = 295
BOARD_Y = 118


class MazeChaseScene(Scene):
    GAME_ID = "maze_chase"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = MazeChaseModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.finished_recorded = False

    def _restart(self) -> None:
        self.model.reset()
        self.finished_recorded = False
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is not MazeState.PLAYING:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        column = (event.pos[0] - BOARD_X) // CELL_SIZE
        row = (event.pos[1] - BOARD_Y) // CELL_SIZE
        if self.model.click_cell(Cell(row, column)):
            self.controller.play_sound("click")

    def update(self, dt: float) -> None:
        self.model.update(dt)
        if self.model.state is MazeState.COMPLETE and not self.finished_recorded:
            self.finished_recorded = True
            self.controller.record_score(self.GAME_ID, 1)
            self.controller.play_sound("complete")

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#111827"), pygame.Color("#312E81"))
        self._draw_score(surface)
        for row, line in enumerate(MAZE):
            for column, value in enumerate(line):
                rect = pygame.Rect(
                    BOARD_X + column * CELL_SIZE,
                    BOARD_Y + row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )
                if value == "#":
                    pygame.draw.rect(surface, pygame.Color("#4F46E5"), rect, border_radius=6)
                else:
                    pygame.draw.rect(surface, pygame.Color("#0B1026"), rect)
        for pellet in self.model.pellets:
            pygame.draw.circle(surface, theme.WHITE, self._cell_center(pellet), 5)
        pygame.draw.circle(surface, theme.YELLOW, self._cell_center(self.model.player), 17)
        pygame.draw.circle(surface, theme.CORAL, self._cell_center(self.model.enemy), 18)
        if self.model.state is not MazeState.PLAYING:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        total = sum(line.count(".") for line in MAZE)
        theme.draw_text(
            surface,
            f"Dots  {total - len(self.model.pellets)} / {total}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    @staticmethod
    def _cell_center(cell: Cell) -> tuple[int, int]:
        return (
            BOARD_X + cell.column * CELL_SIZE + CELL_SIZE // 2,
            BOARD_Y + cell.row * CELL_SIZE + CELL_SIZE // 2,
        )

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        title = "You win!" if self.model.state is MazeState.COMPLETE else "Caught!"
        theme.draw_text(surface, title, 52, theme.INK, (640, 310), bold=True)
