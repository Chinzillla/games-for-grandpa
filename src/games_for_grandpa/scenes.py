from __future__ import annotations

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import AppController, GameDefinition, Scene
from games_for_grandpa.ui import Button, GameToolbar


class HomeScene(Scene):
    def __init__(
        self,
        controller: AppController,
        registry: dict[str, GameDefinition],
    ) -> None:
        self.controller = controller
        self.registry = registry
        self.sound_button = Button(
            pygame.Rect(1040, 28, 200, 62),
            "Sound: On",
            self._toggle_sound,
        )
        self.game_buttons: list[Button] = []
        for index, definition in enumerate(registry.values()):
            x = 90 + index * 400
            self.game_buttons.append(
                Button(
                    pygame.Rect(x + 45, 510, 250, 76),
                    "Play",
                    lambda game_id=definition.game_id: self._start(game_id),
                    primary=True,
                )
            )

    def _toggle_sound(self) -> None:
        self.controller.settings.sound_enabled = not self.controller.settings.sound_enabled
        self.controller.save_settings()
        self.controller.play_sound("click")

    def _start(self, game_id: str) -> None:
        self.controller.play_sound("click")
        self.controller.start_game(game_id)

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.sound_button.handle_event(event):
            return
        for button in self.game_buttons:
            if button.handle_event(event):
                return

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.BACKGROUND)
        theme.draw_left_text(
            surface,
            "Games for Grandpa",
            58,
            theme.TEXT,
            (48, 28),
            bold=True,
        )
        self.sound_button.label = (
            "Sound: On" if self.controller.settings.sound_enabled else "Sound: Off"
        )
        self.sound_button.draw(surface)
        theme.draw_text(
            surface,
            "Choose a game",
            42,
            theme.MUTED_TEXT,
            (640, 142),
        )

        for index, definition in enumerate(self.registry.values()):
            x = 90 + index * 400
            card = pygame.Rect(x, 190, 340, 420)
            pygame.draw.rect(surface, theme.PANEL, card, border_radius=24)
            pygame.draw.rect(surface, theme.ACCENT, card, width=4, border_radius=24)
            theme.draw_text(
                surface,
                definition.title,
                42,
                theme.TEXT,
                (card.centerx, 270),
                bold=True,
            )
            lines = definition.description.split("\n")
            for line_index, line in enumerate(lines):
                theme.draw_text(
                    surface,
                    line,
                    30,
                    theme.MUTED_TEXT,
                    (card.centerx, 360 + line_index * 42),
                )
            self.game_buttons[index].draw(surface)

        theme.draw_text(
            surface,
            "Everything can be played with the mouse.",
            30,
            theme.MUTED_TEXT,
            (640, 668),
        )


class ComingSoonScene(Scene):
    def __init__(
        self,
        controller: AppController,
        game_id: str,
        title: str,
    ) -> None:
        self.controller = controller
        self.game_id = game_id
        self.title = title
        self.paused = False
        self.toolbar = GameToolbar(
            controller,
            game_id,
            on_pause=self._toggle_pause,
            on_restart=self._restart,
            on_difficulty=self._restart,
            is_paused=lambda: self.paused,
        )

    def _toggle_pause(self) -> None:
        self.paused = not self.paused

    def _restart(self) -> None:
        self.paused = False

    def handle_event(self, event: pygame.event.Event) -> None:
        self.toolbar.handle_event(event)

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        surface.fill(theme.BACKGROUND)
        self.toolbar.draw(surface)
        theme.draw_text(surface, self.title, 64, theme.TEXT, (640, 270), bold=True)
        message = "Paused" if self.paused else "This game is the next lesson."
        theme.draw_text(surface, message, 40, theme.MUTED_TEXT, (640, 380))
        theme.draw_text(
            surface,
            "Use Home to choose another game.",
            32,
            theme.MUTED_TEXT,
            (640, 455),
        )

