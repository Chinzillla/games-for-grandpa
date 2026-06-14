from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.jigsaw_puzzle import (
    GRID_SIZE,
    PIECE_COUNT,
    JigsawPuzzleModel,
    JigsawState,
)
from games_for_grandpa.ui import Button, GameHud, ResultActions

BOARD_RECT = pygame.Rect(415, 135, 450, 450)
PIECE_SIZE = BOARD_RECT.width // GRID_SIZE


class JigsawPuzzleScene(Scene):
    GAME_ID = "jigsaw_puzzle"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = JigsawPuzzleModel()
        self.image = self._default_image()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.choose_button = Button(
            pygame.Rect(80, 610, 210, 60),
            "Choose Photo",
            self._choose_photo,
            accent=theme.SKY,
        )
        self.shuffle_button = Button(
            pygame.Rect(990, 610, 170, 60),
            "Shuffle",
            self._restart,
            accent=theme.GREEN,
        )

    def _restart(self) -> None:
        self.model.shuffle()
        self.controller.play_sound("click")

    def _choose_photo(self) -> None:
        try:
            from tkinter import Tk, filedialog

            root = Tk()
            root.withdraw()
            path = filedialog.askopenfilename(filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp")])
            root.destroy()
            if path:
                loaded = pygame.image.load(path).convert()
                self.image = pygame.transform.smoothscale(loaded, BOARD_RECT.size)
                self._restart()
        except (OSError, pygame.error):
            self.controller.play_sound("point")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is JigsawState.COMPLETE:
            self.result_actions.handle_event(event)
            return
        if (
            self.hud.handle_event(event)
            or self.choose_button.handle_event(event)
            or self.shuffle_button.handle_event(event)
        ):
            return
        if (
            event.type != pygame.MOUSEBUTTONDOWN
            or event.button != 1
            or not BOARD_RECT.collidepoint(event.pos)
        ):
            return
        column = (event.pos[0] - BOARD_RECT.x) // PIECE_SIZE
        row = (event.pos[1] - BOARD_RECT.y) // PIECE_SIZE
        if self.model.click(row * GRID_SIZE + column):
            self.controller.play_sound("success")
            if self.model.state is JigsawState.COMPLETE:
                self.controller.record_score(self.GAME_ID, PIECE_COUNT)
                self.controller.play_sound("complete")

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#FFE6A7"), pygame.Color("#F9FAFB"))
        for board_index, source_index in enumerate(self.model.positions):
            row, column = divmod(board_index, GRID_SIZE)
            source_row, source_column = divmod(source_index, GRID_SIZE)
            dest = pygame.Rect(
                BOARD_RECT.x + column * PIECE_SIZE,
                BOARD_RECT.y + row * PIECE_SIZE,
                PIECE_SIZE,
                PIECE_SIZE,
            )
            source = pygame.Rect(
                source_column * PIECE_SIZE,
                source_row * PIECE_SIZE,
                PIECE_SIZE,
                PIECE_SIZE,
            )
            surface.blit(self.image, dest, source)
            pygame.draw.rect(surface, theme.WHITE, dest, width=4)
        if self.model.selected is not None:
            row, column = divmod(self.model.selected, GRID_SIZE)
            selected = pygame.Rect(
                BOARD_RECT.x + column * PIECE_SIZE,
                BOARD_RECT.y + row * PIECE_SIZE,
                PIECE_SIZE,
                PIECE_SIZE,
            )
            pygame.draw.rect(surface, theme.CORAL, selected, width=8)
        if self.model.state is JigsawState.COMPLETE:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.choose_button.draw(surface)
            self.shuffle_button.draw(surface)
            self.hud.draw(surface)

    @staticmethod
    def _default_image() -> pygame.Surface:
        image = pygame.Surface(BOARD_RECT.size)
        theme.vertical_gradient(image, pygame.Color("#60A5FA"), pygame.Color("#34D399"))
        pygame.draw.circle(image, theme.YELLOW, (355, 90), 52)
        pygame.draw.polygon(image, pygame.Color("#8B5E34"), [(50, 400), (190, 190), (330, 400)])
        pygame.draw.polygon(image, pygame.Color("#6B7280"), [(180, 400), (300, 240), (430, 400)])
        return image

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "Puzzle complete!", 48, theme.INK, (640, 310), bold=True)
