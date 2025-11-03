"""Minimal Pygame demo showcasing the tile map and waypoint helpers."""
from __future__ import annotations

import sys
from pathlib import Path

import pygame

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from src.maps.tilemap import TileMap
from src.maps.waypoint import advance_along_path


def make_tile(size: tuple[int, int], fill_color: tuple[int, int, int], border_color: tuple[int, int, int]) -> pygame.Surface:
    tile = pygame.Surface(size)
    tile.fill(fill_color)
    pygame.draw.rect(tile, border_color, tile.get_rect(), width=2)
    return tile


def build_sample_map() -> TileMap:
    layout = [
        [1, 1, 1, 1, 1, 1, 2, 2, 2, 2],
        [0, 0, 0, 0, 0, 1, 0, 0, 0, 2],
        [0, 2, 2, 2, 0, 1, 0, 2, 0, 2],
        [0, 2, 0, 0, 0, 1, 0, 2, 0, 2],
        [0, 2, 0, 2, 2, 1, 0, 2, 0, 2],
        [0, 2, 0, 0, 0, 1, 0, 0, 0, 2],
        [0, 2, 2, 2, 2, 1, 1, 1, 1, 1],
    ]
    path = [
        (0, 0),
        (1, 0),
        (2, 0),
        (3, 0),
        (4, 0),
        (5, 0),
        (5, 1),
        (5, 2),
        (5, 3),
        (5, 4),
        (5, 5),
        (6, 5),
        (7, 5),
        (8, 5),
        (9, 5),
        (9, 6),
    ]

    tile_size = (32, 32)
    grass = make_tile(tile_size, (114, 176, 117), (90, 140, 94))
    path_tile = make_tile(tile_size, (196, 178, 152), (156, 138, 116))
    water = make_tile(tile_size, (108, 174, 214), (68, 138, 178))
    tiles = [grass, path_tile, water]

    map_width = len(layout[0]) * tile_size[0]
    map_height = len(layout) * tile_size[1]
    background = pygame.Surface((map_width, map_height))
    background.fill((194, 224, 255))

    return TileMap(layout, tile_size, tiles, path=path, background=background)


def main() -> None:
    pygame.init()
    tile_map = build_sample_map()
    window = pygame.display.set_mode(tile_map.pixel_size)
    pygame.display.set_caption("Tile map demo")
    clock = pygame.time.Clock()

    enemy_pos = tile_map.tile_to_world(tile_map.path[0])
    waypoint_index = 0
    path_points = tile_map.world_path()

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        tile_map.draw(window)
        tile_map.draw_path(window, color=(255, 0, 0))

        enemy_pos, waypoint_index = advance_along_path(
            enemy_pos,
            path_points,
            waypoint_index,
            speed=120.0,
            dt=dt,
        )
        pygame.draw.circle(
            window,
            (0, 0, 0),
            (int(enemy_pos[0]), int(enemy_pos[1])),
            8,
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
