"""Simple CLI helpers to pick a map and preview waves."""

from __future__ import annotations

from typing import Iterable, List

from .game import build_campaign
from .loader import load_map_definitions, load_wave_blueprints
from .models import MapDefinition


def list_available_maps() -> List[MapDefinition]:
    return load_map_definitions()


def prompt_map_selection(maps: Iterable[MapDefinition]) -> MapDefinition:
    mapping = list(maps)
    if not mapping:
        raise ValueError("No hay mapas disponibles para seleccionar.")

    print("Selecciona un mapa para iniciar la partida:\n")
    for idx, map_def in enumerate(mapping, start=1):
        print(f"  {idx}. {map_def.name} — {map_def.description}")

    while True:
        raw = input("\nIngresa el número del mapa: ").strip()
        if not raw.isdigit():
            print("Debes ingresar un número válido.")
            continue
        selection = int(raw)
        if 1 <= selection <= len(mapping):
            return mapping[selection - 1]
        print("La opción seleccionada no existe, intenta nuevamente.")


def preview_campaign(map_definition: MapDefinition) -> None:
    blueprints = load_wave_blueprints(map_definition.id)
    campaign = build_campaign(map_definition, blueprints)
    print(f"\nResumen de oleadas para {map_definition.name}:\n")
    for wave in campaign["waves"]:
        tags = ", ".join(wave.difficulty_tags)
        tags_display = f" [{tags}]" if tags else ""
        print(
            f"Oleada {wave.wave}: {wave.count}x {wave.enemy_type} — "
            f"Vida {wave.health}, Velocidad {wave.speed}{tags_display}"
        )


def main() -> None:
    maps = list_available_maps()
    chosen = prompt_map_selection(maps)
    preview_campaign(chosen)


if __name__ == "__main__":
    main()
