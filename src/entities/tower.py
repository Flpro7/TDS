"""Tower entity that can rotate to track targets."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import pygame

from .base import AnimatedEntity
from .projectile import Projectile


@dataclass
class Tower(AnimatedEntity):
    """Tower capable of aiming and firing projectiles."""

    rotation: float = 0.0
    cooldown: float = 0.5
    _cooldown_timer: float = 0.0
    projectile_speed: float = 200.0
    projectile_surface: Optional[pygame.Surface] = None

    def aim_at(self, target: pygame.Vector2) -> None:
        """Rotate the tower so it faces ``target``."""

        direction = target - self.position
        if direction.length_squared() == 0:
            return
        # Pygame's rotation uses degrees counter-clockwise; atan2 returns the
        # angle from the x-axis in radians.  We invert to keep the sprite facing
        # the target when ``rotate`` is applied.
        self.rotation = -pygame.Vector2(1, 0).angle_to(direction)

    def can_fire(self) -> bool:
        """Return ``True`` if the tower is ready to fire another projectile."""

        return self._cooldown_timer <= 0.0

    def update(self, delta: float) -> None:
        """Update the animation state and cooldown timer."""

        self.update_animation(delta)
        if self._cooldown_timer > 0.0:
            self._cooldown_timer -= delta

    def fire(self, target: pygame.Vector2) -> Optional[Projectile]:
        """Create a projectile heading towards ``target`` if possible."""

        if not self.can_fire():
            return None

        direction = (target - self.position)
        if direction.length_squared() == 0:
            return None

        velocity = direction.normalize() * self.projectile_speed
        projectile = Projectile(
            frames=[self.projectile_surface or self.current_frame],
            position=self.position.copy(),
            velocity=velocity,
        )
        projectile.aim_at(target)
        self._cooldown_timer = self.cooldown
        return projectile

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the tower applying the current rotation."""

        base_frame = self.current_frame
        rotated = pygame.transform.rotate(base_frame, self.rotation)
        rect = rotated.get_rect(center=self.position)
        surface.blit(rotated, rect)
