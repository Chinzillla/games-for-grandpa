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
    def __init__(
        self,
        controller: AppController,
        game_id: str,
        *,
        on_restart: Callable[[], None],
        on_difficulty: Callable[[], None],
    ) -> None:
        self.controller = controller
        self.game_id = game_id
        self.on_restart = on_restart
        self.on_difficulty = on_difficulty
        self.menu_open = False
        self.home_button = Button(
            pygame.Rect(28, 24, 116, 54),
            "Home",
            controller.go_home,
        )
        self.menu_button = Button(
            pygame.Rect(1136, 24, 116, 54),
            "Menu",
            self._open_menu,
        )
        self.menu_buttons = [
            Button(
                pygame.Rect(440, 245, 400, 62),
                "Continue",
                self._close_menu,
                accent=theme.GREEN,
            ),
            Button(
                pygame.Rect(440, 325, 400, 62),
                "Restart",
                self._restart,
                accent=theme.YELLOW,
            ),
            Button(
                pygame.Rect(440, 405, 400, 62),
                "Difficulty  Easy",
                self._cycle_difficulty,
                accent=theme.SKY,
            ),
            Button(
                pygame.Rect(440, 485, 400, 62),
                "Sound  On",
                self._toggle_sound,
                accent=pygame.Color("#EFEAFF"),
            ),
        ]

    @property
    def paused(self) -> bool:
        return self.menu_open

    def _open_menu(self) -> None:
        self.menu_open = True
        self.controller.play_sound("click")

    def _close_menu(self) -> None:
        self.menu_open = False
        self.controller.play_sound("click")

    def _restart(self) -> None:
        self.menu_open = False
        self.on_restart()

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
        if self.menu_open:
            return any(button.handle_event(event) for button in self.menu_buttons)
        return self.home_button.handle_event(event) or self.menu_button.handle_event(event)

    def draw(self, surface: pygame.Surface) -> None:
        self.home_button.draw(surface)
        self.menu_button.draw(surface)
        if not self.menu_open:
            return

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((23, 33, 58, 170))
        surface.blit(overlay, (0, 0))
        panel = pygame.Rect(390, 135, 500, 485)
        theme.draw_card(surface, panel, color=theme.CREAM, shadow_offset=10, radius=32)
        theme.draw_text(surface, "Game Menu", 44, theme.INK, (640, 190), bold=True)
        sound = "On" if self.controller.settings.sound_enabled else "Off"
        difficulty = self.controller.settings.difficulty_for(self.game_id)
        self.menu_buttons[2].label = f"Difficulty  {difficulty.value}"
        self.menu_buttons[3].label = f"Sound  {sound}"
        for button in self.menu_buttons:
            button.draw(surface)
