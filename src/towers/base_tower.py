"""Base tower logic and upgrade management for the tower defence game."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Protocol, Tuple

from .projectile import Projectile


class Target(Protocol):
    """Protocol describing the minimal interface required for tower targets."""

    @property
    def position(self) -> Tuple[float, float]:
        """Return the current (x, y) position of the target."""

    def is_alive(self) -> bool:
        """Return ``True`` when the target can still take damage."""

    def take_damage(self, amount: float) -> None:
        """Apply ``amount`` damage to the target."""


@dataclass
class TowerUpgrade:
    """Simple structure describing an upgrade level for a tower."""

    cost: int
    range_bonus: float = 0.0
    fire_rate_bonus: float = 0.0
    damage_bonus: float = 0.0


@dataclass
class BaseTower:
    """Base functionality shared between all towers.

    The class is intentionally lightweight so that specialised towers can
    extend and customise the behaviour while keeping the core logic in a
    single place.  The tower keeps track of its firing cadence via
    ``cooldown``; when the cooldown reaches zero the tower is able to fire
    again.
    """

    position: Tuple[float, float]
    range: float
    fire_rate: float
    damage: float
    cost: int
    projectile_speed: float = 400.0
    upgrades: List[TowerUpgrade] = field(default_factory=list)

    target: Optional[Target] = field(default=None, init=False)
    cooldown: float = field(default=0.0, init=False)
    level: int = field(default=1, init=False)
    projectiles: List[Projectile] = field(default_factory=list, init=False)

    def distance_to(self, target: Target) -> float:
        tx, ty = target.position
        x, y = self.position
        return ((tx - x) ** 2 + (ty - y) ** 2) ** 0.5

    def select_target(self, enemies: Iterable[Target]) -> Optional[Target]:
        """Select the closest enemy in range."""

        closest: Optional[Target] = None
        closest_distance = float("inf")
        for enemy in enemies:
            if not enemy.is_alive():
                continue
            distance = self.distance_to(enemy)
            if distance <= self.range and distance < closest_distance:
                closest = enemy
                closest_distance = distance
        return closest

    def shoot(self, target: Target) -> None:
        projectile = Projectile(
            position=self.position,
            target=target,
            speed=self.projectile_speed,
            damage=self.damage,
        )
        self.projectiles.append(projectile)
        self.cooldown = 1.0 / self.fire_rate if self.fire_rate > 0 else 0.0

    def update_projectiles(self, dt: float) -> None:
        """Advance active projectiles and remove the ones that have finished."""

        still_active: List[Projectile] = []
        for projectile in self.projectiles:
            projectile.update(dt)
            if not projectile.finished:
                still_active.append(projectile)
        self.projectiles = still_active

    def update(self, dt: float, enemies: Iterable[Target]) -> None:
        """Update the tower state.

        This method performs three actions:

        * decrease the current cooldown timer;
        * update existing projectiles;
        * acquire and shoot at a target if one is available and the cooldown
          has expired.
        """

        if self.cooldown > 0:
            self.cooldown = max(0.0, self.cooldown - dt)

        self.update_projectiles(dt)

        if self.target is None or not self.target.is_alive() or self.distance_to(self.target) > self.range:
            self.target = self.select_target(enemies)

        if self.target and self.cooldown <= 0:
            self.shoot(self.target)

    # ------------------------------------------------------------------
    # Upgrade logic
    # ------------------------------------------------------------------
    def can_upgrade(self) -> bool:
        """Return ``True`` when another upgrade level is available."""

        return self.level - 1 < len(self.upgrades)

    def upgrade_cost(self) -> Optional[int]:
        """Return the cost of the next upgrade, ``None`` if none available."""

        if not self.can_upgrade():
            return None
        return self.upgrades[self.level - 1].cost

    def apply_upgrade(self) -> bool:
        """Apply the next upgrade and return ``True`` on success."""

        if not self.can_upgrade():
            return False

        upgrade = self.upgrades[self.level - 1]
        self.range += upgrade.range_bonus
        self.fire_rate += upgrade.fire_rate_bonus
        self.damage += upgrade.damage_bonus
        self.level += 1
        return True


__all__ = ["BaseTower", "TowerUpgrade", "Target"]
