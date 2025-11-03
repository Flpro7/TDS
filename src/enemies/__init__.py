"""Enemy types available in the game."""

from __future__ import annotations

from .base_enemy import BaseEnemy


class FastEnemy(BaseEnemy):
    """Lightweight enemy that moves quickly but has low health."""

    def __init__(self, waypoints):
        super().__init__(
            waypoints,
            speed=120.0,
            health=50,
            animation_frames=("fast_1", "fast_2", "fast_3"),
            arrival_tolerance=2.0,
        )


class TankEnemy(BaseEnemy):
    """Slow but sturdy enemy type."""

    def __init__(self, waypoints):
        super().__init__(
            waypoints,
            speed=60.0,
            health=200,
            animation_frames=("tank_1", "tank_2"),
            arrival_tolerance=2.0,
        )


__all__ = ["BaseEnemy", "FastEnemy", "TankEnemy"]
