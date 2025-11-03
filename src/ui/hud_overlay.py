"""Heads-up display utilities for the tower defence sample game.

This module centralises the drawing logic for the money, lives and wave
counters as well as the interactive tower buttons used when building new
structures.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Tuple

import pygame


Color = Tuple[int, int, int]
Point = Tuple[int, int]


@dataclass
class TowerButton:
    """Interactive element that allows selecting a tower to build.

    Parameters
    ----------
    name:
        Display name used in the button label.
    cost:
        Tower price. The HUD paints the button red when the player cannot
        afford it and green otherwise.
    icon:
        Optional surface drawn on the left side of the text. Passing ``None``
        skips the icon.
    position:
        Top-left corner of the button in screen coordinates.
    size:
        Button size in pixels.
    """

    name: str
    cost: int
    icon: Optional[pygame.Surface]
    position: Point
    size: Point
    base_color: Color = (80, 80, 80)
    text_color: Color = (240, 240, 240)
    affordable_color: Color = (60, 140, 60)
    unaffordable_color: Color = (170, 55, 55)
    selected_border_color: Color = (250, 210, 0)
    rect: pygame.Rect = field(init=False)

    def __post_init__(self) -> None:
        self.rect = pygame.Rect(self.position, self.size)

    def contains_point(self, point: Point) -> bool:
        """Return ``True`` when ``point`` is inside the button rectangle."""

        return self.rect.collidepoint(point)

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font,
        is_selected: bool,
        is_affordable: bool,
    ) -> None:
        """Render the button on ``surface``.

        The background turns green when ``is_affordable`` is ``True`` and red
        otherwise. A yellow border highlights the currently selected tower.
        """

        background = self.affordable_color if is_affordable else self.unaffordable_color
        pygame.draw.rect(surface, self.base_color, self.rect)
        inner_rect = self.rect.inflate(-6, -6)
        pygame.draw.rect(surface, background, inner_rect)

        if is_selected:
            pygame.draw.rect(surface, self.selected_border_color, inner_rect, width=3)

        text = font.render(f"{self.name} (${self.cost})", True, self.text_color)

        text_rect = text.get_rect()
        text_rect.centery = self.rect.centery
        padding_x = 10

        if self.icon is not None:
            icon_rect = self.icon.get_rect()
            icon_rect.centery = self.rect.centery
            icon_rect.left = inner_rect.left + padding_x
            surface.blit(self.icon, icon_rect)
            padding_x += icon_rect.width + 8

        text_rect.left = inner_rect.left + padding_x
        surface.blit(text, text_rect)


class HUD:
    """Draws a semi-transparent panel containing game information."""

    def __init__(
        self,
        font: pygame.font.Font,
        small_font: Optional[pygame.font.Font] = None,
        panel_color: Color = (30, 30, 30),
        panel_alpha: int = 180,
        text_color: Color = (245, 245, 245),
        padding: int = 16,
    ) -> None:
        self.font = font
        self.small_font = small_font or font
        self.panel_color = panel_color
        self.panel_alpha = panel_alpha
        self.text_color = text_color
        self.padding = padding
        self.tower_buttons: List[TowerButton] = []

    def set_tower_buttons(self, buttons: Iterable[TowerButton]) -> None:
        self.tower_buttons = list(buttons)

    def _draw_background(self, surface: pygame.Surface) -> pygame.Surface:
        panel = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        panel.fill((*self.panel_color, self.panel_alpha))
        return panel

    def render(
        self,
        surface: pygame.Surface,
        money: int,
        lives: int,
        wave: int,
        selected_button: Optional[TowerButton],
    ) -> None:
        """Render the HUD on ``surface``.

        Parameters
        ----------
        surface:
            Target surface.
        money, lives, wave:
            Values displayed on the HUD panel.
        selected_button:
            Reference to the currently selected tower button. It can be ``None``
            when the player is not placing any tower.
        """

        panel = self._draw_background(surface)
        surface.blit(panel, (0, 0))

        y = self.padding
        surface.blit(
            self.font.render(f"Dinero: ${money}", True, self.text_color),
            (self.padding, y),
        )
        y += self.font.get_height() + 4
        surface.blit(
            self.font.render(f"Vidas: {lives}", True, self.text_color),
            (self.padding, y),
        )
        y += self.font.get_height() + 4
        surface.blit(
            self.font.render(f"Oleada: {wave}", True, self.text_color),
            (self.padding, y),
        )
        y += self.font.get_height() + 16

        if self.tower_buttons:
            label = self.small_font.render("Torres", True, self.text_color)
            surface.blit(label, (self.padding, y))
            y += label.get_height() + 8

        for button in self.tower_buttons:
            affordable = money >= button.cost
            button.draw(surface, self.small_font, button is selected_button, affordable)

    def handle_click(self, pos: Point, money: int) -> Optional[TowerButton]:
        """Return the tower button that contains ``pos`` and is affordable."""

        for button in self.tower_buttons:
            if button.contains_point(pos) and money >= button.cost:
                return button
        return None
