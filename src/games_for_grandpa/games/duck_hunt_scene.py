from __future__ import annotations

import math

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.duck_hunt import (
    DUCKS_TO_COMPLETE,
    DuckHuntModel,
    DuckHuntState,
)
from games_for_grandpa.ui import GameHud


class DuckHuntScene(Scene):
    GAME_ID = "target_tap"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = DuckHuntModel(controller.settings.difficulty_for(self.GAME_ID))
        self.crosshair = (640, 360)
        self.animation_time = 0.0
        self.hud = GameHud(
            controller,
            self.GAME_ID,
            on_restart=self._restart,
            on_difficulty=self._restart,
        )

    def _restart(self) -> None:
        self.model.reset(self.controller.settings.difficulty_for(self.GAME_ID))
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.hud.handle_event(event):
            return
        if hasattr(event, "pos"):
            self.crosshair = event.pos
        if (
            self.hud.paused
            or self.model.state is DuckHuntState.COMPLETE
            or event.type != pygame.MOUSEBUTTONDOWN
            or event.button != 1
        ):
            return
        if self.model.shoot(event.pos):
            if self.model.state is DuckHuntState.COMPLETE:
                self.controller.record_score(self.GAME_ID, self.model.score)
                self.controller.play_sound("complete")
            else:
                self.controller.play_sound("success")
        else:
            self.controller.play_sound("point")

    def update(self, dt: float) -> None:
        if self.hud.paused:
            return
        self.animation_time += dt
        self.model.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_world(surface)
        if self.model.state is DuckHuntState.PLAYING:
            self._draw_duck(surface)
            self._draw_rifle(surface)
            self._draw_crosshair(surface)
        else:
            self._draw_complete(surface)
        self._draw_score(surface)
        self.hud.draw(surface)

    def _draw_world(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, theme.SKY, theme.SKY_LIGHT)
        pygame.draw.circle(surface, theme.YELLOW, (1070, 105), 55)
        self._draw_cloud(surface, (250, 120), 1.0)
        self._draw_cloud(surface, (780, 185), 0.8)
        pygame.draw.ellipse(surface, theme.GRASS_DARK, pygame.Rect(-80, 520, 1440, 250))
        pygame.draw.ellipse(surface, theme.GRASS, pygame.Rect(-100, 555, 1480, 240))
        for x in range(0, 1280, 55):
            height = 24 + (x * 17) % 36
            pygame.draw.line(surface, theme.GREEN_DARK, (x, 650), (x + 9, 650 - height), 5)

    @staticmethod
    def _draw_cloud(
        surface: pygame.Surface,
        center: tuple[int, int],
        scale: float,
    ) -> None:
        x, y = center
        pygame.draw.circle(surface, theme.WHITE, (x, y), round(40 * scale))
        pygame.draw.circle(
            surface,
            theme.WHITE,
            (x + round(45 * scale), y - round(15 * scale)),
            round(50 * scale),
        )
        pygame.draw.circle(surface, theme.WHITE, (x + round(95 * scale), y), round(38 * scale))
        pygame.draw.ellipse(
            surface,
            theme.WHITE,
            pygame.Rect(x - round(30 * scale), y, round(165 * scale), round(50 * scale)),
        )

    def _draw_duck(self, surface: pygame.Surface) -> None:
        x = round(self.model.duck.x)
        y = round(self.model.duck.y)
        facing = 1 if self.model.duck.vx >= 0 else -1
        wing_lift = round(math.sin(self.animation_time * 10) * 14)
        pygame.draw.ellipse(surface, theme.SHADOW, pygame.Rect(x - 58, y + 38, 118, 24))
        pygame.draw.ellipse(surface, theme.BROWN, pygame.Rect(x - 55, y - 28, 100, 62))
        pygame.draw.circle(surface, theme.GREEN_DARK, (x + facing * 43, y - 16), 32)
        beak_x = x + facing * 72
        pygame.draw.polygon(
            surface,
            theme.YELLOW,
            [(x + facing * 65, y - 20), (beak_x, y - 11), (x + facing * 65, y - 3)],
        )
        eye_x = x + facing * 50
        pygame.draw.circle(surface, theme.WHITE, (eye_x, y - 25), 7)
        pygame.draw.circle(surface, theme.BLACK, (eye_x + facing * 2, y - 25), 3)
        wing_rect = pygame.Rect(x - 34, y - 55 - wing_lift, 68, 50)
        pygame.draw.ellipse(surface, theme.CREAM, wing_rect)
        pygame.draw.ellipse(surface, theme.CREAM, pygame.Rect(x - 22, y + 3 + wing_lift, 65, 44))
        pygame.draw.line(surface, theme.YELLOW_DARK, (x - 18, y + 28), (x - 28, y + 48), 5)
        pygame.draw.line(surface, theme.YELLOW_DARK, (x + 8, y + 28), (x + 18, y + 48), 5)

    def _draw_rifle(self, surface: pygame.Surface) -> None:
        origin = pygame.Vector2(500, 670)
        target = pygame.Vector2(self.crosshair)
        direction = target - origin
        if direction.length_squared() == 0:
            direction = pygame.Vector2(0, -1)
        direction = direction.normalize()
        barrel_end = origin + direction * 205
        side = pygame.Vector2(-direction.y, direction.x)
        pygame.draw.line(surface, theme.BLACK, origin, barrel_end, 24)
        pygame.draw.line(surface, theme.INK_SOFT, origin, barrel_end, 13)
        stock = [
            origin + side * 34,
            origin - side * 27,
            origin - side * 20 - direction * 115,
            origin + side * 27 - direction * 105,
        ]
        pygame.draw.polygon(surface, theme.BROWN, stock)
        pygame.draw.polygon(
            surface,
            theme.BROWN,
            [
                origin - direction * 18,
                origin - direction * 68,
                origin - direction * 58 + side * 42,
                origin - direction * 8 + side * 20,
            ],
        )
        pygame.draw.circle(surface, theme.BLACK, barrel_end, 13)

    def _draw_crosshair(self, surface: pygame.Surface) -> None:
        x, y = self.crosshair
        pygame.draw.circle(surface, theme.CORAL, (x, y), 27, width=4)
        pygame.draw.line(surface, theme.CORAL, (x - 40, y), (x + 40, y), 4)
        pygame.draw.line(surface, theme.CORAL, (x, y - 40), (x, y + 40), 4)
        pygame.draw.circle(surface, theme.WHITE, (x, y), 4)

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 22, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Ducks  {self.model.score} / {DUCKS_TO_COMPLETE}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    def _draw_complete(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 280)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "Great shooting!", 52, theme.INK, (640, 290), bold=True)
        theme.draw_text(surface, "You found all 10 ducks.", 30, theme.INK_SOFT, (640, 365))
        theme.draw_text(
            surface,
            "Open Menu to play again.",
            25,
            theme.BLUE_DARK,
            (640, 425),
            bold=True,
        )
