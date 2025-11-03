"""Helpers to manage waypoint-based enemy movement."""
from __future__ import annotations

import math
from typing import Optional, Sequence, Tuple

Point = Tuple[float, float]


def get_next_waypoint(path: Sequence[Point], current_index: int) -> Optional[Point]:
    """Return the next waypoint from ``path`` relative to ``current_index``."""

    next_index = current_index + 1
    if 0 <= next_index < len(path):
        return path[next_index]
    return None


def get_next_waypoint_index(path: Sequence[Point], current_index: int) -> Optional[int]:
    """Return the index of the next waypoint or ``None`` if finished."""

    next_index = current_index + 1
    if next_index < len(path):
        return next_index
    return None


def direction_between(start: Point, end: Point) -> Point:
    """Return the normalized direction vector from ``start`` to ``end``."""

    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    if length == 0:
        return (0.0, 0.0)
    return (dx / length, dy / length)


def advance_along_path(
    position: Point,
    path: Sequence[Point],
    current_index: int,
    speed: float,
    dt: float,
    arrival_threshold: float = 4.0,
) -> Tuple[Point, int]:
    """Move ``position`` along ``path`` using ``speed`` and ``dt``.

    Parameters
    ----------
    position:
        Current world position of the entity.
    path:
        Sequence of waypoints in world coordinates.
    current_index:
        Index of the waypoint that the entity has most recently reached.
    speed:
        Movement speed in pixels per second.
    dt:
        Time delta (seconds) since the previous update.
    arrival_threshold:
        Radius around the target waypoint considered "reached".

    Returns
    -------
    tuple[Point, int]
        Updated position and the index of the waypoint that was last reached.
    """

    x, y = position
    index = current_index
    remaining_distance = speed * dt

    while True:
        next_index = get_next_waypoint_index(path, index)
        if next_index is None:
            return (x, y), index
        target = path[next_index]
        dx = target[0] - x
        dy = target[1] - y
        distance = math.hypot(dx, dy)

        if distance <= arrival_threshold:
            x, y = target
            index = next_index
            continue

        if remaining_distance <= 0:
            return (x, y), index

        step = min(remaining_distance, distance)
        if distance != 0:
            ratio = step / distance
            x += dx * ratio
            y += dy * ratio
        remaining_distance -= step

        if step < distance:
            return (x, y), index
        else:
            index = next_index

