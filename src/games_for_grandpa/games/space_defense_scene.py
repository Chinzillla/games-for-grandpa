from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.space_defense import ENEMY_COUNT, SpaceDefenseModel, SpaceState
from games_for_grandpa.ui import GameHud, ResultActions


class SpaceDefenseScene(Scene):
    GAME_ID = "space_defense"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = SpaceDefenseModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.finished_recorded = False

    def _restart(self) -> None:
        self.model.reset()
        self.finished_recorded = False
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is not SpaceState.PLAYING:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if event.type in {pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN}:
            self.model.move_player(event.pos[0])

    def update(self, dt: float) -> None:
        previous_score = self.model.score
        self.model.update(dt)
        if self.model.score > previous_score:
            self.controller.play_sound("success")
        if self.model.state is SpaceState.COMPLETE and not self.finished_recorded:
            self.finished_recorded = True
            self.controller.record_score(self.GAME_ID, self.model.score)
            self.controller.play_sound("complete")

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, pygame.Color("#0F172A"), pygame.Color("#273B7A"))
        self._draw_stars(surface)
        self._draw_score(surface)
        for bullet in self.model.bullets:
            pygame.draw.rect(
                surface,
                theme.YELLOW,
                pygame.Rect(bullet.x - 4, bullet.y - 18, 8, 24),
                border_radius=4,
            )
        for enemy in self.model.enemies:
            if enemy.alive:
                self._draw_enemy(surface, round(enemy.x), round(enemy.y))
        self._draw_ship(surface)
        if self.model.state is not SpaceState.PLAYING:
            self._draw_result(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    @staticmethod
    def _draw_stars(surface: pygame.Surface) -> None:
        for index in range(70):
            x = (index * 127) % 1280
            y = 95 + (index * 53) % 520
            pygame.draw.circle(surface, pygame.Color("#E0F2FE"), (x, y), 2)

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 24, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Ships  {self.model.score} / {ENEMY_COUNT}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    @staticmethod
    def _draw_enemy(surface: pygame.Surface, x: int, y: int) -> None:
        pygame.draw.ellipse(surface, pygame.Color("#7CFF6B"), pygame.Rect(x - 34, y - 22, 68, 44))
        pygame.draw.circle(surface, theme.BLACK, (x - 15, y - 3), 5)
        pygame.draw.circle(surface, theme.BLACK, (x + 15, y - 3), 5)

    def _draw_ship(self, surface: pygame.Surface) -> None:
        x = round(self.model.player_x)
        points = [(x, 610), (x - 46, 675), (x + 46, 675)]
        pygame.draw.polygon(surface, theme.CORAL, points)
        pygame.draw.polygon(surface, theme.WHITE, [(x, 625), (x - 16, 660), (x + 16, 660)])

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        title = "You win!" if self.model.state is SpaceState.COMPLETE else "Try again!"
        theme.draw_text(surface, title, 52, theme.INK, (640, 310), bold=True)
