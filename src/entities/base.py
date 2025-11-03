"""Entity primitives used by the tower defence sample."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import pygame


@dataclass
class AnimatedEntity:
    """Base class that manages animation state.

    Parameters
    ----------
    frames:
        Sequence of :class:`pygame.Surface` objects forming the animation.
    frame_time:
        Duration of each frame in seconds.
    position:
        Cartesian coordinates where the entity should be drawn.
    """

    frames: Sequence[pygame.Surface]
    frame_time: float = 0.1
    position: pygame.Vector2 = field(default_factory=lambda: pygame.Vector2(0, 0))
    animation_index: int = 0
    animation_time: float = 0.0

    def update_animation(self, delta: float) -> None:
        """Advance the animation by ``delta`` seconds.

        The method accumulates time and switches to the next frame when enough
        time has passed.  The index loops around to allow continuous playback.
        """

        if not self.frames:
            return

        self.animation_time += delta
        while self.animation_time >= self.frame_time:
            self.animation_time -= self.frame_time
            self.animation_index = (self.animation_index + 1) % len(self.frames)

    @property
    def current_frame(self) -> pygame.Surface:
        """Return the current animation frame."""

        if not self.frames:
            raise ValueError("AnimatedEntity requires at least one frame")
        return self.frames[self.animation_index]

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the entity at its current position."""

        rect = self.current_frame.get_rect(center=self.position)
        surface.blit(self.current_frame, rect)
