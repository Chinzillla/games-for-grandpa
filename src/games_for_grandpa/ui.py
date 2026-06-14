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
    accent: pygame.Color | None = None
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
            color = theme.SKY_LIGHT
            text_color = theme.MUTED_TEXT
        elif self.hovered:
            color = (
                theme.PRIMARY_HOVER
                if self.primary
                else self.accent or pygame.Color("#EEF5FF")
            )
            text_color = theme.BLACK if self.primary else theme.INK
        else:
            color = theme.PRIMARY if self.primary else self.accent or theme.WHITE
            text_color = theme.BLACK if self.primary else theme.INK
        shadow_rect = self.rect.move(0, 4)
        pygame.draw.rect(surface, theme.SHADOW, shadow_rect, border_radius=16)
        pygame.draw.rect(surface, color, self.rect, border_radius=14)
        theme.draw_text(
            surface,
            self.label,
            25,
            text_color,
            self.rect.center,
            bold=True,
        )


class GameHud:
    def __init__(self, controller: AppController) -> None:
        self.controller = controller
        self.home_button = Button(
            pygame.Rect(28, 24, 116, 54),
            "Home",
            controller.go_home,
        )
        self.sound_button = Button(
            pygame.Rect(1080, 24, 172, 54),
            "Sound On",
            self._toggle_sound,
        )

    def _toggle_sound(self) -> None:
        self.controller.settings.sound_enabled = not self.controller.settings.sound_enabled
        self.controller.save_settings()
        self.controller.play_sound("click")

    def handle_event(self, event: pygame.event.Event) -> bool:
        return self.home_button.handle_event(event) or self.sound_button.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        self.sound_button.label = (
            "Sound On" if self.controller.settings.sound_enabled else "Sound Off"
        )
        self.home_button.draw(surface)
        self.sound_button.draw(surface)


class ResultActions:
    def __init__(
        self,
        controller: AppController,
        on_restart: Callable[[], None],
    ) -> None:
        self.buttons = [
            Button(
                pygame.Rect(430, 390, 190, 68),
                "Home",
                controller.go_home,
                accent=theme.SKY,
            ),
            Button(
                pygame.Rect(660, 390, 190, 68),
                "Restart",
                on_restart,
                accent=theme.GREEN,
            ),
        ]

    def handle_event(self, event: pygame.event.Event) -> bool:
        return any(button.handle_event(event) for button in self.buttons)

    def draw(self, surface: pygame.Surface) -> None:
        for button in self.buttons:
            button.draw(surface)
