from __future__ import annotations

from dataclasses import dataclass

import pygame

from games_for_grandpa import theme
from games_for_grandpa.core import LOGICAL_SIZE, AppController, GameDefinition, Scene
from games_for_grandpa.ui import Button


@dataclass(slots=True)
class GameCard:
    rect: pygame.Rect
    game_id: str
    title: str
    hovered: bool = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if hasattr(event, "pos"):
            self.hovered = self.rect.collidepoint(event.pos)
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )


class HomeScene(Scene):
    CARD_COLORS = (
        theme.SKY_LIGHT,
        pygame.Color("#EFEAFF"),
        pygame.Color("#E7F8EF"),
        pygame.Color("#FFF2C9"),
        pygame.Color("#FFE0E0"),
        pygame.Color("#E0F2FE"),
        pygame.Color("#DCFCE7"),
        pygame.Color("#FCE7F3"),
        pygame.Color("#EDE9FE"),
        pygame.Color("#FEF3C7"),
        pygame.Color("#DBEAFE"),
    )

    def __init__(
        self,
        controller: AppController,
        registry: dict[str, GameDefinition],
    ) -> None:
        self.controller = controller
        self.registry = registry
        self.sound_button = Button(
            pygame.Rect(895, 34, 150, 54),
            "Sound On",
            self._toggle_sound,
        )
        self.exit_button = Button(
            pygame.Rect(1082, 34, 150, 54),
            "Exit",
            self.controller.request_exit,
            accent=theme.CORAL,
        )
        self.cards = [
            GameCard(
                self._card_rect(index),
                definition.game_id,
                definition.title,
            )
            for index, definition in enumerate(registry.values())
        ]
        self.previews = {
            definition.game_id: self._render_preview(definition) for definition in registry.values()
        }

    @staticmethod
    def _card_rect(index: int) -> pygame.Rect:
        column = index % 4
        row = index // 4
        return pygame.Rect(38 + column * 305, 126 + row * 184, 284, 164)

    def _toggle_sound(self) -> None:
        self.controller.settings.sound_enabled = not self.controller.settings.sound_enabled
        self.controller.save_settings()
        self.controller.play_sound("click")

    def _render_preview(self, definition: GameDefinition) -> pygame.Surface:
        snapshot = pygame.Surface(LOGICAL_SIZE)
        definition.scene_factory(self.controller).draw(snapshot)
        return pygame.transform.smoothscale(snapshot, (232, 100))

    def handle_event(self, event: pygame.event.Event) -> None:
        if self.sound_button.handle_event(event) or self.exit_button.handle_event(event):
            return
        for card in self.cards:
            if card.handle_event(event):
                self.controller.play_sound("click")
                self.controller.start_game(card.game_id)
                return

    def update(self, dt: float) -> None:
        del dt

    def draw(self, surface: pygame.Surface) -> None:
        theme.vertical_gradient(surface, theme.CREAM, pygame.Color("#FFEED9"))
        self._draw_header(surface)
        for index, card in enumerate(self.cards):
            color = self.CARD_COLORS[index % len(self.CARD_COLORS)]
            self._draw_card(surface, card, color)

    def _draw_header(self, surface: pygame.Surface) -> None:
        theme.draw_left_text(
            surface,
            "Gameroom",
            50,
            theme.INK,
            (48, 34),
            bold=True,
        )
        theme.draw_left_text(
            surface,
            "Pick a game",
            26,
            theme.INK_SOFT,
            (51, 96),
        )
        self.sound_button.label = (
            "Sound On" if self.controller.settings.sound_enabled else "Sound Off"
        )
        self.sound_button.draw(surface)
        self.exit_button.draw(surface)

    def _draw_card(
        self,
        surface: pygame.Surface,
        card: GameCard,
        color: pygame.Color,
    ) -> None:
        draw_rect = card.rect.move(0, -6 if card.hovered else 0)
        theme.draw_card(surface, draw_rect, color=color)
        preview_frame = pygame.Rect(
            draw_rect.x + 14,
            draw_rect.y + 12,
            draw_rect.width - 28,
            104,
        )
        pygame.draw.rect(surface, theme.WHITE, preview_frame, border_radius=20)
        preview = self.previews[card.game_id]
        preview_rect = preview.get_rect(center=preview_frame.center)
        surface.blit(preview, preview_rect)
        pygame.draw.rect(surface, theme.WHITE, preview_frame, width=5, border_radius=20)

        theme.draw_text(
            surface,
            card.title,
            23,
            theme.INK,
            (draw_rect.centerx, draw_rect.y + 130),
            bold=True,
        )
        best = self.controller.best_score(card.game_id)
        theme.draw_text(
            surface,
            f"Best {best}",
            17,
            theme.INK_SOFT,
            (draw_rect.centerx, draw_rect.y + 153),
        )
