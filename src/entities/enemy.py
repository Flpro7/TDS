"""Enemy entity implementation."""
from __future__ import annotations

from dataclasses import dataclass, field

import pygame

from .base import AnimatedEntity


@dataclass
class Enemy(AnimatedEntity):
    """Simple walking enemy that follows a straight velocity vector."""

    velocity: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))

    def update(self, delta: float) -> None:
        """Advance the enemy state by ``delta`` seconds."""

        self.position += self.velocity * delta
        self.update_animation(delta)
