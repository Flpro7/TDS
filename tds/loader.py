"""Utilities to load map and wave definitions from disk."""

from __future__ import annotations

import csv
import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable, List, Sequence

from .models import MapDefinition, WaveBlueprint


def _ensure_path(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el recurso requerido: {path}")
    return path


def load_map_definitions(directory: Path | str = Path("data/maps")) -> List[MapDefinition]:
    """Load all map definitions found inside *directory*."""

    dir_path = Path(directory)
    if not dir_path.exists():
        raise FileNotFoundError(
            f"No se encontró el directorio de mapas en '{dir_path}'."
        )

    maps: List[MapDefinition] = []
    for json_file in sorted(dir_path.glob("*.json")):
        with json_file.open("r", encoding="utf-8") as fh:
            data = json.load(fh)
        maps.append(
            MapDefinition(
                id=data["id"],
                name=data["name"],
                tileset=data["tileset"],
                path=[tuple(coord) for coord in data["path"]],
                spawn_delay=float(data["spawn_delay"]),
                description=data.get("description", ""),
            )
        )
    if not maps:
        raise ValueError(
            f"No se encontraron archivos de mapas en '{dir_path}'."
        )
    return maps


def load_wave_blueprints(
    map_id: str, directory: Path | str = Path("data/waves")
) -> List[WaveBlueprint]:
    """Load wave definitions for the given *map_id* from CSV."""

    dir_path = Path(directory)
    csv_file = dir_path / f"{map_id}.csv"
    _ensure_path(csv_file)

    blueprints: List[WaveBlueprint] = []
    with csv_file.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            blueprints.append(
                WaveBlueprint(
                    wave=int(row["wave"]),
                    enemy_type=row["enemy_type"],
                    count=int(row["count"]),
                    base_health=float(row["base_health"]),
                    base_speed=float(row["base_speed"]),
                    special=row.get("special") or None,
                )
            )

    if not blueprints:
        raise ValueError(
            f"No se definieron oleadas para el mapa '{map_id}'."
        )
    return blueprints


def dump_wave_configuration(
    waves: Sequence[WaveBlueprint], output: Path | str
) -> None:
    """Dump wave blueprints to CSV (useful for debugging/exports)."""

    out_path = Path(output)
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "wave",
                "enemy_type",
                "count",
                "base_health",
                "base_speed",
                "special",
            ],
        )
        writer.writeheader()
        for item in waves:
            writer.writerow(asdict(item))
