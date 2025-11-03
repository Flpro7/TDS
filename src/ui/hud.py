"""Heads-up display helpers built on top of pygame."""

from __future__ import annotations

from typing import Optional

import pygame

from economy.player_stats import PlayerStats
from waves.wave_manager import WaveManager

BUTTON_COLOR = (40, 120, 200)
BUTTON_COLOR_HOVER = (60, 150, 230)
BUTTON_TEXT_COLOR = (240, 240, 240)
TEXT_COLOR = (255, 255, 255)


class HUD:
    """Render the current player stats and a start wave control."""

    def __init__(
        self,
        player_stats: PlayerStats,
        wave_manager: WaveManager,
        *,
        font: Optional[pygame.font.Font] = None,
        button_rect: Optional[pygame.Rect] = None,
    ) -> None:
        self.player_stats = player_stats
        self.wave_manager = wave_manager
        self.font = font or pygame.font.SysFont("arial", 24)
        self.button_rect = button_rect or pygame.Rect(20, 90, 260, 48)

    def draw(self, surface: pygame.Surface) -> None:
        money_surface = self.font.render(f"Dinero: {self.player_stats.money}", True, TEXT_COLOR)
        lives_surface = self.font.render(f"Vidas: {self.player_stats.lives}", True, TEXT_COLOR)

        wave_number = self.wave_manager.current_wave_number or self.player_stats.current_wave
        wave_state = "En curso" if self.wave_manager.wave_in_progress else "Listo"
        wave_surface = self.font.render(f"Oleada: {wave_number} ({wave_state})", True, TEXT_COLOR)

        surface.blit(money_surface, (20, 20))
        surface.blit(lives_surface, (20, 50))
        surface.blit(wave_surface, (20, 120))

        mouse_pos = pygame.mouse.get_pos()
        hovering = self.button_rect.collidepoint(mouse_pos)
        color = BUTTON_COLOR_HOVER if hovering else BUTTON_COLOR
        pygame.draw.rect(surface, color, self.button_rect, border_radius=6)

        label = "Iniciar Oleada" if not self.wave_manager.wave_in_progress else "Oleada en curso"
        label_surface = self.font.render(label + " (Espacio)", True, BUTTON_TEXT_COLOR)
        label_rect = label_surface.get_rect(center=self.button_rect.center)
        surface.blit(label_surface, label_rect)

    def wants_to_start_wave(self, event: pygame.event.Event) -> bool:
        if self.wave_manager.wave_in_progress:
            return False

        if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.button_rect.collidepoint(event.pos):
                return True
        if event.type == pygame.KEYUP and event.key == pygame.K_SPACE:
            return True
        return False
