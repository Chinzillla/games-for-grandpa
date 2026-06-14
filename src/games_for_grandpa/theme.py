from __future__ import annotations

from functools import lru_cache

import pygame

BACKGROUND = pygame.Color("#102A43")
PANEL = pygame.Color("#243B53")
PANEL_LIGHT = pygame.Color("#334E68")
PRIMARY = pygame.Color("#F6C85F")
PRIMARY_HOVER = pygame.Color("#FFD978")
ACCENT = pygame.Color("#4FD1C5")
TEXT = pygame.Color("#F7FAFC")
MUTED_TEXT = pygame.Color("#D9E2EC")
DANGER = pygame.Color("#FF8A80")
SUCCESS = pygame.Color("#7EE787")
BLACK = pygame.Color("#000000")


@lru_cache(maxsize=32)
def font(size: int, *, bold: bool = False) -> pygame.font.Font:
    result = pygame.font.Font(None, size)
    result.bold = bold
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

