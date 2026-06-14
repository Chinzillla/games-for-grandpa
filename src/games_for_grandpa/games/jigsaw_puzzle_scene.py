from __future__ import annotations

import math

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.jigsaw_puzzle import (
    GRID_OPTIONS,
    JigsawPuzzleModel,
    JigsawState,
)
from games_for_grandpa.ui import Button, GameHud, ResultActions

BOARD_RECT = pygame.Rect(120, 110, 520, 520)
SIDE_PANEL = pygame.Rect(700, 110, 510, 520)
TRAY_RECT = pygame.Rect(735, 306, 440, 292)
TRAY_GAP = 12


class JigsawPuzzleScene(Scene):
    GAME_ID = "jigsaw_puzzle"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = JigsawPuzzleModel()
        self.image = self._default_image()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.elapsed = 0.0
        self.drag_piece: int | None = None
        self.drag_position = (0, 0)
        self.drag_offset = (0, 0)
        self.choose_button = Button(
            pygame.Rect(SIDE_PANEL.x + 42, SIDE_PANEL.y + 62, 180, 58),
            "Choose Photo",
            self._choose_photo,
            accent=theme.SKY,
        )
        self.shuffle_button = Button(
            pygame.Rect(SIDE_PANEL.x + 288, SIDE_PANEL.y + 62, 150, 58),
            "Restart",
            self._restart,
            accent=theme.GREEN,
        )
        self.grid_buttons = [
            Button(
                pygame.Rect(SIDE_PANEL.x + 44 + index * 144, SIDE_PANEL.y + 122, 116, 52),
                f"{size} x {size}",
                lambda grid=size: self._change_grid(grid),
                accent=theme.SKY,
            )
            for index, size in enumerate(GRID_OPTIONS)
        ]

    def _restart(self) -> None:
        self.model.reset()
        self.drag_piece = None
        self.controller.play_sound("click")

    def _change_grid(self, grid_size: int) -> None:
        self.model.reset(grid_size)
        self.drag_piece = None
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
            or any(button.handle_event(event) for button in self.grid_buttons)
        ):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._start_drag(event.pos)
        elif event.type == pygame.MOUSEMOTION and self.drag_piece is not None:
            self.drag_position = event.pos
        elif (
            event.type == pygame.MOUSEBUTTONUP and event.button == 1 and self.drag_piece is not None
        ):
            self._finish_drag(event.pos)

    def _start_drag(self, position: tuple[int, int]) -> None:
        for piece_id, rect in reversed(self._tray_rects()):
            if rect.collidepoint(position):
                self.drag_piece = piece_id
                self.drag_position = position
                self.drag_offset = (position[0] - rect.x, position[1] - rect.y)
                self.controller.play_sound("click")
                return

    def _finish_drag(self, position: tuple[int, int]) -> None:
        assert self.drag_piece is not None
        slot = self._slot_at(position)
        if slot is None:
            self.controller.play_sound("point")
        else:
            result = self.model.place_piece(self.drag_piece, slot)
            if result.placed:
                self.controller.play_sound("success")
                if self.model.state is JigsawState.COMPLETE:
                    self.controller.record_score(self.GAME_ID, self.model.piece_count)
                    self.controller.play_sound("complete")
            else:
                self.controller.play_sound("point")
        self.drag_piece = None

    def _slot_at(self, position: tuple[int, int]) -> int | None:
        if not BOARD_RECT.collidepoint(position):
            return None
        piece_size = BOARD_RECT.width // self.model.grid_size
        column = min(self.model.grid_size - 1, (position[0] - BOARD_RECT.x) // piece_size)
        row = min(self.model.grid_size - 1, (position[1] - BOARD_RECT.y) // piece_size)
        return row * self.model.grid_size + column

    def update(self, dt: float) -> None:
        self.elapsed += dt

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#FFE6A7"), pygame.Color("#F9FAFB"))
        self._draw_board(surface)
        self._draw_side_panel(surface)
        if self.model.state is JigsawState.COMPLETE:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_board(self, surface: pygame.Surface) -> None:
        theme.draw_card(
            surface, BOARD_RECT.inflate(28, 28), color=theme.CREAM, shadow_offset=10, radius=30
        )
        piece_size = BOARD_RECT.width // self.model.grid_size
        preview = self.image.copy()
        preview.set_alpha(55)
        surface.blit(preview, BOARD_RECT)
        for slot, piece_id in enumerate(self.model.slots):
            row, column = divmod(slot, self.model.grid_size)
            dest = pygame.Rect(
                BOARD_RECT.x + column * piece_size,
                BOARD_RECT.y + row * piece_size,
                piece_size,
                piece_size,
            )
            pygame.draw.rect(surface, pygame.Color("#FFFFFF88"), dest, width=2)
            if piece_id is not None:
                self._draw_piece(surface, piece_id, dest, on_board=True)

    def _draw_side_panel(self, surface: pygame.Surface) -> None:
        theme.draw_card(surface, SIDE_PANEL, color=theme.WHITE, shadow_offset=8, radius=28)
        theme.draw_text(
            surface,
            "Puzzle Pieces",
            33,
            theme.INK,
            (SIDE_PANEL.centerx, SIDE_PANEL.y + 34),
            bold=True,
        )
        self.choose_button.draw(surface)
        self.shuffle_button.draw(surface)
        for button, size in zip(self.grid_buttons, GRID_OPTIONS, strict=True):
            button.primary = size == self.model.grid_size
            button.draw(surface)
        pygame.draw.rect(surface, pygame.Color("#F2F6FF"), TRAY_RECT, border_radius=22)
        pygame.draw.rect(surface, pygame.Color("#CAD7F5"), TRAY_RECT, width=3, border_radius=22)
        for piece_id, rect in self._tray_rects():
            if piece_id != self.drag_piece:
                self._draw_piece(surface, piece_id, rect, on_board=False)
        if self.drag_piece is not None:
            drag_rect = self._drag_rect()
            self._draw_piece(surface, self.drag_piece, drag_rect, on_board=False, dragging=True)

    def _tray_rects(self) -> list[tuple[int, pygame.Rect]]:
        count = max(1, len(self.model.tray))
        columns = 5 if count <= 16 else 7
        rows = math.ceil(count / columns)
        size = min(
            74,
            (TRAY_RECT.width - 34 - TRAY_GAP * (columns - 1)) // columns,
            (TRAY_RECT.height - 48 - TRAY_GAP * (rows - 1)) // rows,
        )
        start_x = TRAY_RECT.x + (TRAY_RECT.width - (columns * size + (columns - 1) * TRAY_GAP)) // 2
        start_y = TRAY_RECT.y + 24
        rects: list[tuple[int, pygame.Rect]] = []
        # DSA: The tray is the shuffled piece list; row/column math turns it into hit boxes.
        for index, piece_id in enumerate(self.model.tray):
            row, column = divmod(index, columns)
            rects.append(
                (
                    piece_id,
                    pygame.Rect(
                        start_x + column * (size + TRAY_GAP),
                        start_y + row * (size + TRAY_GAP),
                        size,
                        size,
                    ),
                )
            )
        return rects

    def _drag_rect(self) -> pygame.Rect:
        tray_size = self._tray_rects()[0][1].width if self.model.tray else 74
        x = self.drag_position[0] - self.drag_offset[0]
        y = self.drag_position[1] - self.drag_offset[1]
        return pygame.Rect(x, y, tray_size + 10, tray_size + 10)

    def _draw_piece(
        self,
        surface: pygame.Surface,
        piece_id: int,
        rect: pygame.Rect,
        *,
        on_board: bool,
        dragging: bool = False,
    ) -> None:
        source = self._source_rect(piece_id)
        piece = pygame.Surface(source.size, pygame.SRCALPHA)
        piece.blit(self.image, (0, 0), source)
        piece = pygame.transform.smoothscale(piece, rect.size)
        shadow = rect.move(0, 8 if dragging else 4)
        pygame.draw.rect(surface, theme.SHADOW, shadow, border_radius=12)
        surface.blit(piece, rect)
        pygame.draw.rect(surface, theme.WHITE, rect, width=4 if on_board else 3, border_radius=8)
        self._draw_jigsaw_marks(surface, rect)

    def _source_rect(self, piece_id: int) -> pygame.Rect:
        size = BOARD_RECT.width // self.model.grid_size
        row, column = divmod(piece_id, self.model.grid_size)
        return pygame.Rect(column * size, row * size, size, size)

    @staticmethod
    def _draw_jigsaw_marks(surface: pygame.Surface, rect: pygame.Rect) -> None:
        radius = max(5, rect.width // 12)
        pygame.draw.circle(surface, theme.WHITE, (rect.centerx, rect.top), radius, width=2)
        pygame.draw.circle(surface, theme.WHITE, (rect.right, rect.centery), radius, width=2)
        pygame.draw.circle(surface, theme.WHITE, (rect.centerx, rect.bottom), radius, width=2)
        pygame.draw.circle(surface, theme.WHITE, (rect.left, rect.centery), radius, width=2)

    @staticmethod
    def _default_image() -> pygame.Surface:
        image = pygame.Surface(BOARD_RECT.size)
        theme.vertical_gradient(image, pygame.Color("#60A5FA"), pygame.Color("#34D399"))
        pygame.draw.circle(image, theme.YELLOW, (410, 95), 56)
        pygame.draw.circle(image, pygame.Color("#FDE68A"), (430, 82), 16)
        pygame.draw.polygon(image, pygame.Color("#8B5E34"), [(40, 430), (190, 190), (340, 430)])
        pygame.draw.polygon(image, pygame.Color("#6B7280"), [(230, 430), (350, 250), (490, 430)])
        pygame.draw.ellipse(image, pygame.Color("#14532D"), pygame.Rect(-80, 390, 680, 180))
        for index in range(13):
            x = 35 + index * 38
            y = 392 + round(math.sin(index) * 18)
            pygame.draw.circle(image, theme.PINK, (x, y), 11)
            pygame.draw.circle(image, theme.YELLOW, (x, y), 5)
        return image

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "Puzzle complete!", 48, theme.INK, (640, 300), bold=True)
        theme.draw_text(
            surface,
            f"{self.model.piece_count} pieces placed.",
            30,
            theme.INK_SOFT,
            (640, 355),
        )
