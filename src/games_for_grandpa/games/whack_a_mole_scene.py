from __future__ import annotations

import math
from importlib.resources import files

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.whack_a_mole import (
    HIT_FEEDBACK_SECONDS,
    HOLE_COUNT,
    MOLES_TO_WIN,
    WhackAMoleModel,
    WhackState,
)
from games_for_grandpa.ui import GameHud, ResultActions

HOLE_RECTS = [
    pygame.Rect(350 + column * 200, 180 + row * 145, 130, 90)
    for row in range(3)
    for column in range(3)
]


class WhackAMoleScene(Scene):
    GAME_ID = "whack_a_mole"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = WhackAMoleModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.elapsed = 0.0
        self.hammer_timer = 0.0
        self.hammer_position = (640, 360)

        mole_source = pygame.image.load(
            str(files("games_for_grandpa.assets").joinpath("mole.png"))
        ).convert_alpha()
        dizzy_source = pygame.image.load(
            str(files("games_for_grandpa.assets").joinpath("mole_dizzy.png"))
        ).convert_alpha()
        hammer_source = pygame.image.load(
            str(files("games_for_grandpa.assets").joinpath("hammer.png"))
        ).convert_alpha()
        self.mole_sprite = pygame.transform.smoothscale(mole_source, (150, 132))
        self.dizzy_sprite = pygame.transform.smoothscale(dizzy_source, (168, 136))
        self.hammer_sprite = pygame.transform.smoothscale(hammer_source, (178, 188))

    def _restart(self) -> None:
        self.model.reset()
        self.elapsed = 0.0
        self.hammer_timer = 0.0
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is WhackState.COMPLETE:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return
        self.hammer_position = event.pos
        self.hammer_timer = 0.22
        for index, rect in enumerate(HOLE_RECTS):
            if rect.collidepoint(event.pos):
                if self.model.whack(index):
                    self.controller.play_sound("success")
                    if self.model.state is WhackState.COMPLETE:
                        self.controller.record_score(self.GAME_ID, self.model.score)
                        self.controller.play_sound("complete")
                return

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.hammer_timer = max(0.0, self.hammer_timer - dt)
        self.model.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#7ED957"), pygame.Color("#C6F6A8"))
        self._draw_score(surface)
        for rect in HOLE_RECTS:
            self._draw_hole(surface, rect)
        if self.model.hit_hole is not None:
            self._draw_hit_feedback(surface)
        if self.model.state is not WhackState.COMPLETE:
            self._draw_mole(surface, HOLE_RECTS[self.model.active_hole], self.mole_sprite)
        if self.hammer_timer > 0:
            self._draw_hammer(surface)
        if self.model.state is WhackState.COMPLETE:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Moles  {self.model.score} / {MOLES_TO_WIN}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    def _draw_hole(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        pygame.draw.ellipse(surface, pygame.Color("#5A3B1B"), rect)
        pygame.draw.ellipse(surface, pygame.Color("#2F2218"), rect.inflate(-18, -18))

    def _draw_mole(
        self, surface: pygame.Surface, rect: pygame.Rect, sprite: pygame.Surface
    ) -> None:
        bob = round(math.sin(self.elapsed * 10.0) * 6)
        target = sprite.get_rect(center=(rect.centerx, rect.centery - 44 + bob))
        surface.blit(sprite, target)

    def _draw_hit_feedback(self, surface: pygame.Surface) -> None:
        assert self.model.hit_hole is not None
        rect = HOLE_RECTS[self.model.hit_hole]
        progress = self.model.hit_timer / HIT_FEEDBACK_SECONDS
        target = self.dizzy_sprite.get_rect(center=(rect.centerx, rect.centery - 46))
        surface.blit(self.dizzy_sprite, target)
        radius = round(76 * progress)
        center = (rect.centerx, rect.centery - 68)
        for angle in range(0, 360, 60):
            x = center[0] + round(math.cos(math.radians(angle)) * radius)
            y = center[1] + round(math.sin(math.radians(angle)) * radius)
            pygame.draw.circle(surface, theme.YELLOW, (x, y), 10)

    def _draw_hammer(self, surface: pygame.Surface) -> None:
        progress = self.hammer_timer / 0.22
        angle = -26 - 42 * progress
        sprite = pygame.transform.rotozoom(self.hammer_sprite, angle, 1.0)
        x, y = self.hammer_position
        offset = round(34 * progress)
        surface.blit(sprite, sprite.get_rect(center=(x + 48, y - 56 + offset)))

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "Great job!", 52, theme.INK, (640, 290), bold=True)
        theme.draw_text(
            surface,
            f"{HOLE_COUNT} holes, {MOLES_TO_WIN} moles.",
            30,
            theme.INK_SOFT,
            (640, 350),
        )
