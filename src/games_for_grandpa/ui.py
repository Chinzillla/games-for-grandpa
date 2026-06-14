from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController


@dataclass(slots=True)
class Button:
    rect: pygame.Rect
    label: str
    on_click: Callable[[], None]
    primary: bool = False
    enabled: bool = True
    hovered: bool = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if hasattr(event, "pos"):
            self.hovered = self.rect.collidepoint(event.pos)
        if (
            self.enabled
            and event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        ):
            self.on_click()
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.enabled:
            color = theme.PANEL_LIGHT
            text_color = theme.MUTED_TEXT
        elif self.hovered:
            color = theme.PRIMARY_HOVER if self.primary else theme.PANEL_LIGHT
            text_color = theme.BLACK if self.primary else theme.TEXT
        else:
            color = theme.PRIMARY if self.primary else theme.PANEL
            text_color = theme.BLACK if self.primary else theme.TEXT
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        pygame.draw.rect(surface, theme.MUTED_TEXT, self.rect, width=2, border_radius=14)
        theme.draw_text(
            surface,
            self.label,
            30,
            text_color,
            self.rect.center,
            bold=True,
        )


class GameToolbar:
    def __init__(
        self,
        controller: AppController,
        game_id: str,
        *,
        on_pause: Callable[[], None],
        on_restart: Callable[[], None],
        on_difficulty: Callable[[], None],
        is_paused: Callable[[], bool],
    ) -> None:
        self.controller = controller
        self.game_id = game_id
        self.on_difficulty = on_difficulty
        self.is_paused = is_paused
        self.buttons = [
            Button(pygame.Rect(20, 18, 150, 62), "Home", controller.go_home),
            Button(pygame.Rect(184, 18, 150, 62), "Pause", on_pause),
            Button(pygame.Rect(348, 18, 170, 62), "Restart", on_restart),
            Button(pygame.Rect(532, 18, 190, 62), "Sound: On", self._toggle_sound),
            Button(
                pygame.Rect(736, 18, 300, 62),
                "Difficulty: Easy",
                self._cycle_difficulty,
            ),
        ]

    def _toggle_sound(self) -> None:
        self.controller.settings.sound_enabled = not self.controller.settings.sound_enabled
        self.controller.save_settings()
        self.controller.play_sound("click")

    def _cycle_difficulty(self) -> None:
        current = self.controller.settings.difficulty_for(self.game_id)
        self.controller.settings.difficulties[self.game_id] = current.next()
        self.controller.save_settings()
        self.on_difficulty()
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> bool:
        return any(button.handle_event(event) for button in self.buttons)

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, theme.PANEL, pygame.Rect(0, 0, 1280, 98))
        self.buttons[1].label = "Continue" if self.is_paused() else "Pause"
        sound = "On" if self.controller.settings.sound_enabled else "Off"
        self.buttons[3].label = f"Sound: {sound}"
        difficulty = self.controller.settings.difficulty_for(self.game_id)
        self.buttons[4].label = f"Difficulty: {difficulty.value}"
        for button in self.buttons:
            button.draw(surface)

