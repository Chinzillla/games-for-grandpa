from __future__ import annotations

import math
from importlib.resources import files

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Difficulty, Scene
from games_for_grandpa.games.duck_hunt import (
    STARTING_LIVES,
    DuckHuntEvent,
    DuckHuntModel,
    DuckHuntState,
)
from games_for_grandpa.ui import GameHud, ResultActions


class DuckHuntScene(Scene):
    GAME_ID = "target_tap"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = DuckHuntModel(Difficulty.NORMAL)
        self.crosshair = (640, 360)

        duck_path = files("games_for_grandpa.assets").joinpath("duck.png")
        duck_source = pygame.image.load(str(duck_path)).convert_alpha()
        self.duck_sprite = pygame.transform.smoothscale(duck_source, (126, 98))

        hit_path = files("games_for_grandpa.assets").joinpath("duck_hit.png")
        hit_source = pygame.image.load(str(hit_path)).convert_alpha()
        self.duck_hit_sprite = pygame.transform.smoothscale(hit_source, (154, 92))

        shotgun_path = files("games_for_grandpa.assets").joinpath("first_person_shotgun.png")
        shotgun_source = pygame.image.load(str(shotgun_path)).convert_alpha()
        self.shotgun_sprite = pygame.transform.smoothscale(shotgun_source, (390, 242))
        self.elapsed = 0.0
        self.shot_flash_timer = 0.0

        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)

    def _finished(self) -> bool:
        return self.model.state is DuckHuntState.GAME_OVER

    def _duck_visible(self) -> bool:
        return self.model.state in (
            DuckHuntState.PLAYING,
            DuckHuntState.HIT,
        )

    def _restart(self) -> None:
        self.model.reset(Difficulty.NORMAL)
        self.elapsed = 0.0
        self.shot_flash_timer = 0.0
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._finished():
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if hasattr(event, "pos"):
            self.crosshair = event.pos
        if (
            self.model.state is not DuckHuntState.PLAYING
            or event.type != pygame.MOUSEBUTTONDOWN
            or event.button != 1
        ):
            return
        self.controller.play_sound("gunshot")
        self.shot_flash_timer = 0.12
        shot_position = self._friendly_hit_position(event.pos)
        if shot_position is not None and self.model.shoot(shot_position):
            self.controller.play_sound("quack")

    def update(self, dt: float) -> None:
        self.elapsed += dt
        self.shot_flash_timer = max(0.0, self.shot_flash_timer - dt)
        events = self.model.update(dt)
        if DuckHuntEvent.ESCAPED in events:
            self.controller.play_sound("point")
        if DuckHuntEvent.GAME_OVER in events:
            self.controller.record_score(self.GAME_ID, self.model.score)

    def draw(self, surface: pygame.Surface) -> None:
        self._draw_world(surface)
        if self._duck_visible():
            self._draw_duck(surface)
            self._draw_shotgun(surface)
            self._draw_crosshair(surface)
        else:
            self._draw_result(surface)

        if self._finished():
            self.result_actions.draw(surface)
        else:
            self._draw_score(surface)
            self._draw_hearts(surface)
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
        sprite = self.duck_hit_sprite if self.model.state is DuckHuntState.HIT else self.duck_sprite
        if self.model.duck.vx < 0:
            sprite = pygame.transform.flip(sprite, True, False)
        bob = (
            0
            if self.model.state is DuckHuntState.HIT
            else round(math.sin(self.elapsed * 9.0) * 8)
        )
        tilt = 0 if self.model.state is DuckHuntState.HIT else math.sin(self.elapsed * 7.0) * 7
        sprite = pygame.transform.rotozoom(sprite, tilt, 1.0)
        rect = sprite.get_rect(center=(round(self.model.duck.x), round(self.model.duck.y + bob)))
        surface.blit(sprite, rect)

    def _draw_shotgun(self, surface: pygame.Surface) -> None:
        aim_x = (self.crosshair[0] - 640) / 640
        aim_y = (self.crosshair[1] - 360) / 360
        # DSA: O(1) angle math maps cursor offset to a subtle first-person aim pose.
        angle = -math.degrees(math.atan2(aim_x, 9.5))
        rotated = pygame.transform.rotozoom(self.shotgun_sprite, angle, 1.0)
        center = (round(640 + aim_x * 34), round(658 + aim_y * 14))
        surface.blit(rotated, rotated.get_rect(center=center))
        if self.shot_flash_timer > 0:
            self._draw_muzzle_bang(surface, aim_x, aim_y)

    def _draw_muzzle_bang(self, surface: pygame.Surface, aim_x: float, aim_y: float) -> None:
        progress = self.shot_flash_timer / 0.12
        tip = (round(640 + aim_x * 62), round(525 + aim_y * 30))
        burst_radius = round(20 + 42 * progress)
        points: list[tuple[int, int]] = []
        for index in range(14):
            angle = -math.pi / 2 + index * math.pi / 7
            radius = burst_radius if index % 2 == 0 else round(burst_radius * 0.48)
            points.append(
                (
                    tip[0] + round(math.cos(angle) * radius),
                    tip[1] + round(math.sin(angle) * radius),
                )
            )
        pygame.draw.polygon(surface, theme.YELLOW, points)
        pygame.draw.circle(surface, theme.WHITE, tip, round(16 + 18 * progress))
        text_y = tip[1] - round(58 + 18 * progress)
        theme.draw_text(surface, "BANG!", 30, theme.CORAL_DARK, (tip[0], text_y), bold=True)

    def _draw_crosshair(self, surface: pygame.Surface) -> None:
        x, y = self.crosshair
        pygame.draw.circle(surface, theme.CORAL, (x, y), 27, width=4)
        pygame.draw.line(surface, theme.CORAL, (x - 40, y), (x + 40, y), 4)
        pygame.draw.line(surface, theme.CORAL, (x, y - 40), (x, y + 40), 4)
        pygame.draw.circle(surface, theme.WHITE, (x, y), 4)

    def _friendly_hit_position(self, position: tuple[int, int]) -> tuple[int, int] | None:
        duck_rect = self.duck_sprite.get_rect(
            center=(round(self.model.duck.x), round(self.model.duck.y))
        )
        if duck_rect.inflate(34, 34).collidepoint(position):
            return (round(self.model.duck.x), round(self.model.duck.y))
        return position

    def _draw_score(self, surface: pygame.Surface) -> None:
        badge = pygame.Rect(500, 22, 280, 58)
        pygame.draw.rect(surface, theme.WHITE, badge, border_radius=29)
        theme.draw_text(
            surface,
            f"Ducks  {self.model.score}",
            27,
            theme.INK,
            badge.center,
            bold=True,
        )

    def _draw_hearts(self, surface: pygame.Surface) -> None:
        start_x = 490
        for index in range(STARTING_LIVES):
            color = theme.CORAL if index < self.model.lives else pygame.Color("#E2E8F0")
            x = start_x + index * 33
            y = 98
            pygame.draw.circle(surface, color, (x - 7, y - 5), 8)
            pygame.draw.circle(surface, color, (x + 7, y - 5), 8)
            pygame.draw.polygon(surface, color, [(x - 16, y - 2), (x + 16, y - 2), (x, y + 18)])
            pygame.draw.polygon(surface, theme.WHITE, [(x - 6, y - 5), (x, y - 10), (x + 6, y - 5)])

    def _draw_result(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(330, 210, 620, 300)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=34)
        title = "Try again!"
        detail = f"You hit {self.model.score} ducks."
        theme.draw_text(surface, title, 52, theme.INK, (640, 290), bold=True)
        theme.draw_text(surface, detail, 30, theme.INK_SOFT, (640, 350))
