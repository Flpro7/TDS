"""Projectile entity."""
from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from .base import AnimatedEntity


@dataclass
class Projectile(AnimatedEntity):
    """Projectile fired by towers."""

    velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))
    rotation: float = 0.0

    def aim_at(self, target: pygame.Vector2) -> None:
        """Rotate the projectile to face ``target``."""

        direction = target - self.position
        if direction.length_squared() == 0:
            return
        self.rotation = -pygame.Vector2(1, 0).angle_to(direction)

    def update(self, delta: float) -> None:
        """Move the projectile and update its animation."""

        self.position += self.velocity * delta
        self.update_animation(delta)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the projectile using the cached rotation."""

        frame = self.current_frame
        rotated = pygame.transform.rotate(frame, self.rotation)
        rect = rotated.get_rect(center=self.position)
        surface.blit(rotated, rect)
