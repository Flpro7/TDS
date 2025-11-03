"""Core data models for the tower defense simulation helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple


Coordinate = Tuple[int, int]


@dataclass(frozen=True)
class MapDefinition:
    """Representation of a map layout and metadata."""

    id: str
    name: str
    tileset: str
    path: Sequence[Coordinate]
    spawn_delay: float
    description: str


@dataclass(frozen=True)
class WaveBlueprint:
    """Raw wave definition loaded from CSV data."""

    wave: int
    enemy_type: str
    count: int
    base_health: float
    base_speed: float
    special: Optional[str] = None


@dataclass(frozen=True)
class WaveConfig:
    """Wave configuration after applying difficulty adjustments."""

    wave: int
    enemy_type: str
    count: int
    health: float
    speed: float
    special: Optional[str]
    difficulty_tags: List[str]


__all__ = [
    "Coordinate",
    "MapDefinition",
    "WaveBlueprint",
    "WaveConfig",
]
