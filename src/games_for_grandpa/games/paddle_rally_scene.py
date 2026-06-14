from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, Scene
from games_for_grandpa.games.paddle_rally import (
    PLAY_BOTTOM,
    PLAY_LEFT,
    PLAY_RIGHT,
    PLAY_TOP,
    WINNING_SCORE,
    Paddle,
    PaddleRallyModel,
    RallyEvent,
    RallyState,
)
from games_for_grandpa.ui import GameToolbar


class PaddleRallyScene(Scene):
    GAME_ID = "paddle_rally"

    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.paused = False
        self.model = PaddleRallyModel(controller.settings.difficulty_for(self.GAME_ID))
        self.toolbar = GameToolbar(
            controller,
            self.GAME_ID,
            on_pause=self._toggle_pause,
            on_restart=self._restart,
            on_difficulty=self._restart,
            is_paused=lambda: self.paused,
        )

    def _toggle_pause(self) -> None:
        self.paused = not self.paused
        self.controller.play_sound("click")

    def _restart(self) -> None:
        self.paused = False
        self.model.reset(self.controller.settings.difficulty_for(self.GAME_ID))
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.toolbar.handle_event(event):
            return
        if self.paused or self.model.state is not RallyState.PLAYING:
            return
        if event.type in {pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN}:
            self.model.move_player(event.pos[1])

    def update(self, dt: float) -> None:
        if self.paused:
            return
        events = self.model.update(dt)
        if RallyEvent.COMPLETE in events:
            self.controller.record_score(self.GAME_ID, self.model.player_score)
            self.controller.play_sound("complete")
        elif RallyEvent.POINT in events:
            self.controller.play_sound("point")
        elif RallyEvent.PADDLE_HIT in events:
            self.controller.play_sound("success")

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.BACKGROUND)
        self.toolbar.draw(surface)
        self._draw_play_area(surface)
        if self.model.state is not RallyState.PLAYING:
            self._draw_complete(surface)
        if self.paused:
            self._draw_paused(surface)

    def _draw_play_area(self, surface: pygame.Surface) -> None:
        play_rect = pygame.Rect(
            round(PLAY_LEFT),
            round(PLAY_TOP),
            round(PLAY_RIGHT - PLAY_LEFT),
            round(PLAY_BOTTOM - PLAY_TOP),
        )
        pygame.draw.rect(surface, theme.PANEL, play_rect, border_radius=18)
        pygame.draw.rect(surface, theme.MUTED_TEXT, play_rect, width=3, border_radius=18)
        for y in range(round(PLAY_TOP) + 16, round(PLAY_BOTTOM), 38):
            pygame.draw.line(surface, theme.PANEL_LIGHT, (640, y), (640, y + 20), width=5)

        theme.draw_text(
            surface,
            str(self.model.player_score),
            68,
            theme.PRIMARY,
            (520, 178),
            bold=True,
        )
        theme.draw_text(
            surface,
            str(self.model.computer_score),
            68,
            theme.ACCENT,
            (760, 178),
            bold=True,
        )
        theme.draw_text(
            surface,
            f"First to {WINNING_SCORE}",
            28,
            theme.MUTED_TEXT,
            (640, 174),
        )

        self._draw_paddle(surface, self.model.player, theme.PRIMARY)
        self._draw_paddle(surface, self.model.computer, theme.ACCENT)
        pygame.draw.circle(
            surface,
            theme.TEXT,
            (round(self.model.ball.x), round(self.model.ball.y)),
            round(self.model.ball.radius),
        )
        theme.draw_text(
            surface,
            "Move the mouse up and down to control the gold paddle.",
            30,
            theme.MUTED_TEXT,
            (640, 115),
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
        pygame.draw.rect(surface, color, rect, border_radius=12)

    def _draw_complete(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((760, 320), pygame.SRCALPHA)
        overlay.fill((36, 59, 83, 245))
        panel = overlay.get_rect(center=(380, 160))
        pygame.draw.rect(overlay, theme.SUCCESS, panel, width=5, border_radius=26)
        surface.blit(overlay, (260, 245))
        message = (
            "You won the rally!"
            if self.model.state is RallyState.PLAYER_WON
            else "Nice rally!"
        )
        theme.draw_text(surface, message, 62, theme.TEXT, (640, 350), bold=True)
        theme.draw_text(
            surface,
            "Choose Restart to play again.",
            36,
            theme.MUTED_TEXT,
            (640, 445),
        )

    def _draw_paused(self, surface: pygame.Surface) -> None:
        overlay = pygame.Surface((1280, 622), pygame.SRCALPHA)
        overlay.fill((16, 42, 67, 235))
        surface.blit(overlay, (0, 98))
        theme.draw_text(surface, "Paused", 76, theme.TEXT, (640, 350), bold=True)
        theme.draw_text(
            surface,
            "Choose Continue when you are ready.",
            38,
            theme.MUTED_TEXT,
            (640, 435),
        )
