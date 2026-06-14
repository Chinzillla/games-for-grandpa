from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.fishing_game import FISH_TO_WIN, FishingModel, FishingState
from games_for_grandpa.ui import GameHud, ResultActions


class FishingGameScene(Scene):
    GAME_ID = "fishing_game"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = FishingModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.finished_recorded = False

    def _restart(self) -> None:
        self.model.reset()
        self.finished_recorded = False
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is FishingState.COMPLETE:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if hasattr(event, "pos"):
            self.model.move_rod(event.pos[0])
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.model.set_lowering(True)
            elif event.button == 3:
                self.model.set_reeling(True)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.model.set_lowering(False)
            elif event.button == 3:
                self.model.set_reeling(False)

    def update(self, dt: float) -> None:
        previous_score = self.model.score
        self.model.update(dt)
        if self.model.score > previous_score:
            self.controller.play_sound("success")
        if self.model.state is FishingState.COMPLETE and not self.finished_recorded:
            self.finished_recorded = True
            self.controller.record_score(self.GAME_ID, self.model.score)
            self.controller.play_sound("complete")

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, theme.SKY, theme.SKY_LIGHT)
        pygame.draw.rect(surface, pygame.Color("#2563EB"), pygame.Rect(0, 210, 1280, 510))
        pygame.draw.rect(surface, pygame.Color("#1D4ED8"), pygame.Rect(0, 295, 1280, 425))
        self._draw_score(surface)
        self._draw_fish(surface)
        self._draw_rod(surface)
        self._draw_tension(surface)
        if self.model.state is FishingState.COMPLETE:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Fish  {self.model.score} / {FISH_TO_WIN}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    def _draw_rod(self, surface: pygame.Surface) -> None:
        x = round(self.model.rod_x)
        pygame.draw.line(surface, pygame.Color("#7C4A21"), (x - 80, 125), (x, 105), 10)
        pygame.draw.line(surface, theme.WHITE, (x, 105), (x, round(self.model.hook_depth)), 3)
        pygame.draw.circle(surface, theme.YELLOW, (x, round(self.model.hook_depth)), 10)

    def _draw_fish(self, surface: pygame.Surface) -> None:
        fish = self.model.fish
        width = round(58 * fish.size)
        height = round(28 * fish.size)
        pygame.draw.ellipse(
            surface,
            theme.CORAL,
            pygame.Rect(fish.x - width // 2, fish.y - height // 2, width, height),
        )
        tail = [
            (fish.x - width // 2, fish.y),
            (fish.x - width, fish.y - height // 2),
            (fish.x - width, fish.y + height // 2),
        ]
        pygame.draw.polygon(surface, theme.YELLOW, tail)

    def _draw_tension(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(410, 625, 460, 38)
        pygame.draw.rect(surface, theme.WHITE, panel, border_radius=19)
        fill = pygame.Rect(
            panel.x + 5,
            panel.y + 5,
            round((panel.width - 10) * self.model.tension / 100),
            panel.height - 10,
        )
        color = theme.CORAL if self.model.tension > 75 else theme.GREEN
        pygame.draw.rect(surface, color, fill, border_radius=14)
        theme.draw_text(surface, "Line strain", 20, theme.INK, panel.center, bold=True)

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        theme.draw_text(surface, "Fish caught!", 52, theme.INK, (640, 310), bold=True)
