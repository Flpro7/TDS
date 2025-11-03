"""Base enemy implementation for the tower defence sample project.

The :class:`BaseEnemy` class concentrates the behaviour that is shared by all
enemy types in the game:

* Position and movement along a list of waypoints.
* Health and speed attributes.
* Simple sprite animation bookkeeping.
* Detection of when the enemy reaches the final waypoint (the player's base).

The class is intentionally framework agnostic – it only relies on the Python
standard library – which makes it straightforward to integrate with different
rendering or game-loop solutions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Optional, Sequence, Tuple


Vector = Tuple[float, float]


@dataclass
class AnimationState:
    """Book-keeping for simple frame-based animations."""

    frames: Sequence[str] = field(default_factory=tuple)
    frame_time: float = 0.1
    current_time: float = 0.0
    current_frame_index: int = 0

    def update(self, dt: float) -> None:
        if not self.frames:
            return

        self.current_time += dt
        while self.current_time >= self.frame_time:
            self.current_time -= self.frame_time
            self.current_frame_index = (self.current_frame_index + 1) % len(
                self.frames
            )

    @property
    def current_frame(self) -> Optional[str]:
        if not self.frames:
            return None
        return self.frames[self.current_frame_index]


class BaseEnemy:
    """Base class that handles movement, health and animation.

    Parameters
    ----------
    waypoints:
        A sequence of coordinates describing the path that the enemy must
        follow. Each waypoint is considered *reached* when the enemy is close
        enough to it (within ``arrival_tolerance``).
    speed:
        Movement speed expressed in map units per second.
    health:
        Starting health points for the enemy.
    animation_frames:
        Optional sequence describing the animation frames for the enemy. The
        class does not perform any rendering but keeps track of the current
        frame so that the main game can use it when drawing the sprite.
    arrival_tolerance:
        Distance threshold to consider a waypoint as reached.
    """

    def __init__(
        self,
        waypoints: Iterable[Vector],
        *,
        speed: float,
        health: int,
        animation_frames: Optional[Sequence[str]] = None,
        arrival_tolerance: float = 1.0,
    ) -> None:
        waypoint_list: List[Vector] = list(waypoints)
        if not waypoint_list:
            raise ValueError("At least one waypoint is required for an enemy path.")

        self._waypoints: List[Vector] = waypoint_list
        self._waypoint_index: int = 0
        self.position: Vector = waypoint_list[0]
        self.speed: float = speed
        self.health: int = health
        self.alive: bool = True
        self.arrival_tolerance: float = arrival_tolerance
        self.animation = AnimationState(animation_frames or ())
        self.reached_goal: bool = False

    @property
    def target_waypoint(self) -> Vector:
        return self._waypoints[self._waypoint_index]

    def take_damage(self, amount: int) -> None:
        if not self.alive:
            return
        self.health -= amount
        if self.health <= 0:
            self.alive = False

    def update(self, dt: float, *, player: "Player" | None = None) -> None:
        """Advance the enemy along the path.

        The method moves the enemy towards its current waypoint. When the
        waypoint is reached the next waypoint becomes the new target. Reaching
        the final waypoint marks the enemy as ``reached_goal`` and optionally
        subtracts one life from the provided ``player``.
        """

        if not self.alive or self.reached_goal:
            return

        self.animation.update(dt)

        remaining_distance = self.speed * dt

        while remaining_distance > 0 and not self.reached_goal:
            target_x, target_y = self.target_waypoint
            current_x, current_y = self.position
            diff_x = target_x - current_x
            diff_y = target_y - current_y
            distance_to_target = (diff_x**2 + diff_y**2) ** 0.5

            if distance_to_target <= self.arrival_tolerance:
                # Snap to the waypoint and advance to the next one.
                self.position = self.target_waypoint
                if self._waypoint_index + 1 >= len(self._waypoints):
                    self._on_goal_reached(player)
                    break
                self._waypoint_index += 1
                continue

            if distance_to_target <= remaining_distance:
                # We can reach the waypoint this frame.
                self.position = self.target_waypoint
                remaining_distance -= distance_to_target
                if self._waypoint_index + 1 >= len(self._waypoints):
                    self._on_goal_reached(player)
                    break
                self._waypoint_index += 1
            else:
                # Move proportionally towards the waypoint and finish the frame.
                ratio = remaining_distance / distance_to_target
                new_x = current_x + diff_x * ratio
                new_y = current_y + diff_y * ratio
                self.position = (new_x, new_y)
                remaining_distance = 0

    def _on_goal_reached(self, player: "Player" | None) -> None:
        self.reached_goal = True
        if player is not None:
            player.lose_life()


class Player:
    """Minimal player representation holding the remaining lives."""

    def __init__(self, lives: int) -> None:
        if lives <= 0:
            raise ValueError("Player must start with at least one life.")
        self.lives = lives

    def lose_life(self) -> None:
        if self.lives > 0:
            self.lives -= 1

    @property
    def is_alive(self) -> bool:
        return self.lives > 0
