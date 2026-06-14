from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Difficulty, Scene
from games_for_grandpa.games.paddle_rally import (
    PLAY_BOTTOM,
    PLAY_LEFT,
    PLAY_RIGHT,
    PLAY_TOP,
    Paddle,
    PaddleRallyModel,
    RallyEvent,
    RallyState,
)
from games_for_grandpa.ui import GameHud, ResultActions


class PaddleRallyScene(Scene):
    GAME_ID = "paddle_rally"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.model = PaddleRallyModel(Difficulty.EASY)
        self.hud = GameHud(controller)
        self.result_actions = ResultActions(controller, self._restart)

    def _restart(self) -> None:
        self.model.reset(Difficulty.EASY)
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.model.state is not RallyState.PLAYING:
            self.result_actions.handle_event(event)
            return
        if self.hud.handle_event(event):
            return
        if event.type in {pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN}:
            self.model.move_player(event.pos[1])

    def update(self, dt: float) -> None:
        events = self.model.update(dt)
        if RallyEvent.COMPLETE in events:
            self.controller.record_score(self.GAME_ID, self.model.player_score)
            self.controller.play_sound("complete")
        elif RallyEvent.POINT in events:
            self.controller.play_sound("point")
        elif RallyEvent.PADDLE_HIT in events:
            self.controller.play_sound("success")

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, theme.INK, pygame.Color("#283A67"))
        self._draw_play_area(surface)
        if self.model.state is not RallyState.PLAYING:
            self._draw_complete(surface)
            self.result_actions.draw(surface)
        else:
            self.hud.draw(surface)

    def _draw_play_area(self, surface: pygame.Surface) -> None:
        play_rect = pygame.Rect(
            round(PLAY_LEFT),
            round(PLAY_TOP),
            round(PLAY_RIGHT - PLAY_LEFT),
            round(PLAY_BOTTOM - PLAY_TOP),
        )
        pygame.draw.rect(surface, pygame.Color("#15213C"), play_rect, border_radius=24)
        pygame.draw.rect(surface, pygame.Color("#7D8DB5"), play_rect, width=3, border_radius=24)
        for y in range(round(PLAY_TOP) + 15, round(PLAY_BOTTOM), 42):
            pygame.draw.line(surface, pygame.Color("#51658F"), (640, y), (640, y + 22), width=5)

        score_panel = pygame.Rect(510, 24, 260, 62)
        pygame.draw.rect(surface, theme.WHITE, score_panel, border_radius=31)
        theme.draw_text(
            surface,
            f"{self.model.player_score}   :   {self.model.computer_score}",
            34,
            theme.INK,
            score_panel.center,
            bold=True,
        )
        self._draw_paddle(surface, self.model.player, theme.CORAL)
        self._draw_paddle(surface, self.model.computer, theme.GREEN)
        pygame.draw.circle(
            surface,
            theme.YELLOW,
            (round(self.model.ball.x), round(self.model.ball.y)),
            round(self.model.ball.radius + 4),
        )
        pygame.draw.circle(
            surface,
            theme.WHITE,
            (round(self.model.ball.x - 5), round(self.model.ball.y - 5)),
            5,
        )

    @staticmethod
    def _draw_paddle(
        surface: pygame.Surface,
        paddle: Paddle,
        color: pygame.Color,
    ) -> None:
        rect = pygame.Rect(
            round(paddle.left),
            round(paddle.top),
            round(paddle.width),
            round(paddle.height),
        )
        shadow = rect.move(5, 7)
        pygame.draw.rect(surface, theme.SHADOW, shadow, border_radius=14)
        pygame.draw.rect(surface, color, rect, border_radius=14)

    def _draw_complete(self, surface: pygame.Surface) -> None:
        panel = pygame.Rect(350, 230, 580, 270)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=32)
        message = "You won!" if self.model.state is RallyState.PLAYER_WON else "Good game!"
        theme.draw_text(surface, message, 52, theme.INK, (640, 315), bold=True)
