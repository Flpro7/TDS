from __future__ import annotations

from tds.game import DifficultyCurve, apply_difficulty
from tds.loader import load_map_definitions, load_wave_blueprints


def test_maps_are_loaded():
    maps = load_map_definitions()
    assert {m.id for m in maps} == {"forest", "desert"}


def test_wave_scaling_increases_difficulty():
    blueprints = load_wave_blueprints("forest")
    waves = apply_difficulty(blueprints, DifficultyCurve())

    assert waves[0].health < waves[-1].health
    assert waves[0].speed < waves[-1].speed
    assert waves[0].count <= waves[-1].count

    special_waves = [w for w in waves if w.special]
    assert special_waves, "Al menos una oleada debería incluir enemigos especiales"

    tags_joined = " ".join(tag for wave in waves for tag in wave.difficulty_tags)
    assert "+vida" in tags_joined
    assert "+velocidad" in tags_joined
