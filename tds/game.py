"""Game helpers that apply difficulty scaling to wave blueprints."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, List, Sequence

from .models import MapDefinition, WaveBlueprint, WaveConfig


@dataclass
class DifficultyCurve:
    """Parameters that control the difficulty escalation per wave."""

    health_growth: float = 0.22
    speed_growth: float = 0.05
    count_growth: float = 0.08
    special_frequency: int = 3
    extra_specials: Sequence[str] = ("élite", "acorazado", "etéreo")

    def health_multiplier(self, wave_index: int) -> float:
        return (1 + self.health_growth) ** (wave_index - 1)

    def speed_multiplier(self, wave_index: int) -> float:
        return (1 + self.speed_growth) ** (wave_index - 1)

    def count_multiplier(self, wave_index: int) -> float:
        return (1 + self.count_growth) ** (wave_index - 1)

    def pick_special(self, wave_index: int) -> str:
        idx = (wave_index // self.special_frequency) - 1
        return self.extra_specials[idx % len(self.extra_specials)]


def apply_difficulty(
    blueprints: Iterable[WaveBlueprint], curve: DifficultyCurve | None = None
) -> List[WaveConfig]:
    """Convert raw *blueprints* into playable waves using *curve*."""

    curve = curve or DifficultyCurve()
    waves: List[WaveConfig] = []

    for bp in sorted(blueprints, key=lambda item: item.wave):
        health_multiplier = curve.health_multiplier(bp.wave)
        speed_multiplier = curve.speed_multiplier(bp.wave)
        count_multiplier = curve.count_multiplier(bp.wave)

        scaled_health = round(bp.base_health * health_multiplier, 2)
        scaled_speed = round(bp.base_speed * speed_multiplier, 2)
        scaled_count = max(1, math.ceil(bp.count * count_multiplier))

        tags: List[str] = []
        if health_multiplier > 1:
            tags.append(f"+vida {int((health_multiplier - 1) * 100)}%")
        if speed_multiplier > 1:
            tags.append(f"+velocidad {int((speed_multiplier - 1) * 100)}%")
        if scaled_count > bp.count:
            tags.append(f"+cantidad {scaled_count - bp.count}")

        special = bp.special
        if not special and bp.wave >= curve.special_frequency and bp.wave % curve.special_frequency == 0:
            special = curve.pick_special(bp.wave)
            tags.append(f"especial {special}")
        elif special:
            tags.append(f"especial {special}")

        waves.append(
            WaveConfig(
                wave=bp.wave,
                enemy_type=bp.enemy_type,
                count=scaled_count,
                health=scaled_health,
                speed=scaled_speed,
                special=special,
                difficulty_tags=tags,
            )
        )

    return waves


def build_campaign(
    map_definition: MapDefinition,
    blueprints: Iterable[WaveBlueprint],
    curve: DifficultyCurve | None = None,
) -> dict:
    """Compose a campaign dictionary for UI/preview purposes."""

    waves = apply_difficulty(blueprints, curve=curve)
    return {
        "map": map_definition,
        "waves": waves,
        "metadata": {
            "spawn_delay": map_definition.spawn_delay,
            "tileset": map_definition.tileset,
            "dificultad": {
                "crecimiento_vida": curve.health_growth if curve else DifficultyCurve().health_growth,
                "crecimiento_velocidad": curve.speed_growth if curve else DifficultyCurve().speed_growth,
                "crecimiento_cantidad": curve.count_growth if curve else DifficultyCurve().count_growth,
            },
        },
    }
