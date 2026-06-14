from __future__ import annotations

from functools import lru_cache

import pygame

INK = pygame.Color("#17213A")
INK_SOFT = pygame.Color("#344263")
CREAM = pygame.Color("#FFF8E8")
WHITE = pygame.Color("#FFFFFF")
SKY = pygame.Color("#71CDF4")
SKY_LIGHT = pygame.Color("#DDF5FF")
BLUE = pygame.Color("#3B82F6")
BLUE_DARK = pygame.Color("#2457B8")
CORAL = pygame.Color("#FF6B5E")
CORAL_DARK = pygame.Color("#D94B43")
YELLOW = pygame.Color("#FFD166")
YELLOW_DARK = pygame.Color("#E3A821")
GREEN = pygame.Color("#42C98A")
GREEN_DARK = pygame.Color("#24865E")
PURPLE = pygame.Color("#806CE8")
PURPLE_DARK = pygame.Color("#5644B8")
PINK = pygame.Color("#FF8FB4")
GRASS = pygame.Color("#75C94D")
GRASS_DARK = pygame.Color("#34894A")
BROWN = pygame.Color("#8C5A3C")
BLACK = pygame.Color("#101522")
SHADOW = pygame.Color(20, 35, 60, 80)

# Compatibility names used by game logic and drawing code.
BACKGROUND = CREAM
PANEL = WHITE
PANEL_LIGHT = SKY_LIGHT
PRIMARY = YELLOW
PRIMARY_HOVER = pygame.Color("#FFE08A")
ACCENT = BLUE
TEXT = INK
MUTED_TEXT = INK_SOFT
DANGER = CORAL
SUCCESS = GREEN


@lru_cache(maxsize=32)
def font(size: int, *, bold: bool = False) -> pygame.font.Font:
    """Return a native TrueType font instead of pygame's blurry bitmap default."""
    preferred = ("segoeui", "arial", "dejavusans")
    path = None
    for family in preferred:
        path = pygame.font.match_font(family, bold=bold)
        if path:
            break
    result = pygame.font.Font(path, size)
    result.set_bold(bold and path is None)
    return result


def draw_text(
    surface: pygame.Surface,
    text: str,
    size: int,
    color: pygame.Color,
    center: tuple[int, int],
    *,
    bold: bool = False,
) -> pygame.Rect:
    image = font(size, bold=bold).render(text, True, color)
    rect = image.get_rect(center=center)
    surface.blit(image, rect)
    return rect


def draw_left_text(
    surface: pygame.Surface,
    text: str,
    size: int,
    color: pygame.Color,
    position: tuple[int, int],
    *,
    bold: bool = False,
) -> pygame.Rect:
    image = font(size, bold=bold).render(text, True, color)
    rect = image.get_rect(topleft=position)
    surface.blit(image, rect)
    return rect


def vertical_gradient(
    surface: pygame.Surface,
    top: pygame.Color,
    bottom: pygame.Color,
    rect: pygame.Rect | None = None,
) -> None:
    area = rect or surface.get_rect()
    height = max(1, area.height - 1)
    for offset in range(area.height):
        ratio = offset / height
        color = (
            round(top.r + (bottom.r - top.r) * ratio),
            round(top.g + (bottom.g - top.g) * ratio),
            round(top.b + (bottom.b - top.b) * ratio),
        )
        pygame.draw.line(
            surface,
            color,
            (area.left, area.top + offset),
            (area.right - 1, area.top + offset),
        )


def draw_card(
    surface: pygame.Surface,
    rect: pygame.Rect,
    *,
    color: pygame.Color = WHITE,
    shadow_offset: int = 8,
    radius: int = 28,
) -> None:
    shadow = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(shadow, SHADOW, shadow.get_rect(), border_radius=radius)
    surface.blit(shadow, (rect.x, rect.y + shadow_offset))
    pygame.draw.rect(surface, color, rect, border_radius=radius)

