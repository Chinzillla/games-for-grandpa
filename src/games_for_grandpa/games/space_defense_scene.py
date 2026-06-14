from __future__ import annotations

import math
from dataclasses import dataclass

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.space_defense import ENEMY_COUNT, SpaceDefenseModel, SpaceState
from games_for_grandpa.ui import GameHud, ResultActions


@dataclass(slots=True)
class Explosion:
    x: float
    y: float
    timer: float = 0.35


class SpaceDefenseScene(Scene):
    GAME_ID = "space_defense"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = SpaceDefenseModel()
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)
        self.finished_recorded = False
        self.elapsed = 0.0
        self.explosions: list[Explosion] = []

    def _restart(self) -> None:
        self.model.reset()
        self.finished_recorded = False
        self.elapsed = 0.0
        self.explosions.clear()
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
        alive_before = {index for index, enemy in enumerate(self.model.enemies) if enemy.alive}
        self.elapsed += dt
        self.model.update(dt)
        alive_after = {index for index, enemy in enumerate(self.model.enemies) if enemy.alive}
        for index in alive_before - alive_after:
            enemy = self.model.enemies[index]
            self.explosions.append(Explosion(enemy.x, enemy.y))
        for explosion in self.explosions:
            explosion.timer -= dt
        self.explosions = [explosion for explosion in self.explosions if explosion.timer > 0]
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
                bob = round(math.sin(self.elapsed * 5.0 + enemy.x * 0.03) * 6)
                self._draw_enemy(surface, round(enemy.x), round(enemy.y + bob), enemy.kind)
        for explosion in self.explosions:
            self._draw_explosion(surface, explosion)
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
    def _draw_enemy(surface: pygame.Surface, x: int, y: int, kind: int) -> None:
        if kind == 0:
            color = pygame.Color("#A78BFA")
            pygame.draw.polygon(
                surface,
                color,
                [
                    (x, y - 28),
                    (x - 38, y + 12),
                    (x - 18, y + 28),
                    (x, y + 12),
                    (x + 18, y + 28),
                    (x + 38, y + 12),
                ],
            )
            pygame.draw.circle(surface, theme.WHITE, (x, y), 8)
        elif kind == 1:
            color = pygame.Color("#7CFF6B")
            pygame.draw.ellipse(surface, color, pygame.Rect(x - 38, y - 22, 76, 40))
            pygame.draw.rect(surface, color, pygame.Rect(x - 24, y + 5, 48, 20), border_radius=8)
            pygame.draw.circle(surface, theme.BLACK, (x - 15, y - 3), 5)
            pygame.draw.circle(surface, theme.BLACK, (x + 15, y - 3), 5)
        else:
            color = pygame.Color("#67E8F9")
            pygame.draw.rect(
                surface,
                color,
                pygame.Rect(x - 30, y - 20, 60, 34),
                border_radius=10,
            )
            pygame.draw.polygon(
                surface,
                color,
                [(x - 30, y + 4), (x - 52, y + 24), (x - 18, y + 18)],
            )
            pygame.draw.polygon(
                surface,
                color,
                [(x + 30, y + 4), (x + 52, y + 24), (x + 18, y + 18)],
            )
            pygame.draw.circle(surface, theme.BLACK, (x - 13, y - 4), 4)
            pygame.draw.circle(surface, theme.BLACK, (x + 13, y - 4), 4)

    @staticmethod
    def _draw_explosion(surface: pygame.Surface, explosion: Explosion) -> None:
        progress = 1 - explosion.timer / 0.35
        radius = round(12 + 52 * progress)
        alpha = max(0, round(220 * (1 - progress)))
        layer = pygame.Surface((radius * 2 + 8, radius * 2 + 8), pygame.SRCALPHA)
        center = (layer.get_width() // 2, layer.get_height() // 2)
        pygame.draw.circle(layer, pygame.Color(255, 209, 102, alpha), center, radius, width=6)
        pygame.draw.circle(layer, pygame.Color(255, 107, 94, alpha), center, max(5, radius // 2))
        surface.blit(layer, layer.get_rect(center=(round(explosion.x), round(explosion.y))))

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
