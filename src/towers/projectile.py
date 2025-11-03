"""Projectile implementation used by towers."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple


class TargetLike:
    """Protocol-lite describing the minimal behaviour expected from a target."""

    @property
    def position(self) -> Tuple[float, float]:  # pragma: no cover - attribute contract
        ...

    def is_alive(self) -> bool:  # pragma: no cover - attribute contract
        ...

    def take_damage(self, amount: float) -> None:  # pragma: no cover - attribute contract
        ...


@dataclass
class Projectile:
    """Simple projectile travelling in a straight line towards its target."""

    position: Tuple[float, float]
    target: TargetLike
    speed: float
    damage: float

    finished: bool = False

    def update(self, dt: float) -> None:
        """Advance the projectile and deal damage when reaching the target."""

        if self.finished:
            return

        if not self.target.is_alive():
            self.finished = True
            return

        tx, ty = self.target.position
        x, y = self.position
        dx = tx - x
        dy = ty - y
        distance = (dx ** 2 + dy ** 2) ** 0.5

        if distance == 0:
            self._hit_target()
            return

        travel_distance = self.speed * dt
        if travel_distance >= distance:
            self.position = (tx, ty)
            self._hit_target()
            return

        ratio = travel_distance / distance
        self.position = (x + dx * ratio, y + dy * ratio)

    def _hit_target(self) -> None:
        if not self.target.is_alive():
            self.finished = True
            return

        self.target.take_damage(self.damage)
        self.finished = True


__all__ = ["Projectile"]
