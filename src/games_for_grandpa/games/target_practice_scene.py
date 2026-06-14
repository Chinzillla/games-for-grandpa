from __future__ import annotations

from importlib.resources import files

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.target_practice import (
    TARGETS_TO_WIN,
    TargetPracticeModel,
    TargetPracticeState,
)
from games_for_grandpa.ui import GameHud, ResultActions


class TargetPracticeScene(Scene):
    GAME_ID = "target_practice"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = TargetPracticeModel()
        duck_path = files("games_for_grandpa.assets").joinpath("duck.png")
        duck_source = pygame.image.load(str(duck_path)).convert_alpha()
        self.duck_sprite = pygame.transform.smoothscale(duck_source, (180, 140))
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)

    def _restart(self) -> None:
        self.model.reset()
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is TargetPracticeState.COMPLETE:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.controller.play_sound("gunshot")
            if self.model.shoot(event.pos):
                self.controller.play_sound("quack")
                if self.model.state is TargetPracticeState.COMPLETE:
                    self.controller.record_score(self.GAME_ID, self.model.score)
                    self.controller.play_sound("complete")

    def update(self, dt: float) -> None:
        self.model.update(dt)

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#A7F3D0"), pygame.Color("#ECFCCB"))
        self._draw_score(surface)
        pygame.draw.rect(
            surface,
            pygame.Color("#7C3AED"),
            pygame.Rect(980, 230, 130, 260),
            border_radius=18,
        )
        pygame.draw.circle(surface, theme.WHITE, (1045, 360), 54)
        pygame.draw.circle(surface, theme.CORAL, (1045, 360), 34)
        pygame.draw.circle(surface, theme.YELLOW, (1045, 360), 15)
        sprite = (
            self.duck_sprite
            if self.model.target.vx >= 0
            else pygame.transform.flip(self.duck_sprite, True, False)
        )
        surface.blit(
            sprite,
            sprite.get_rect(center=(round(self.model.target.x), round(self.model.target.y))),
        )
        if self.model.state is TargetPracticeState.COMPLETE:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Hits  {self.model.score} / {TARGETS_TO_WIN}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "Target cleared!", 48, theme.INK, (640, 310), bold=True)
