"""Utility classes to manage tile based tower-defense style maps."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

import pygame

TileCoord = Tuple[int, int]
Point = Tuple[float, float]


def load_tile_sheet(
    image_path: str | Path,
    tile_width: int,
    tile_height: Optional[int] = None,
) -> List[pygame.Surface]:
    """Load a sprite sheet and split it into equally-sized tiles.

    Parameters
    ----------
    image_path:
        Path to the sprite sheet image.
    tile_width, tile_height:
        Dimensions of each tile to extract. ``tile_height`` defaults to
        ``tile_width`` for square tiles.

    Returns
    -------
    list[pygame.Surface]
        A list of tile images cropped from the sprite sheet ordered from left
        to right, top to bottom.
    """

    tile_height = tile_height or tile_width
    sheet = pygame.image.load(str(image_path)).convert_alpha()
    sheet_width, sheet_height = sheet.get_size()
    tiles: List[pygame.Surface] = []
    for y in range(0, sheet_height, tile_height):
        for x in range(0, sheet_width, tile_width):
            rect = pygame.Rect(x, y, tile_width, tile_height)
            tile = sheet.subsurface(rect).copy()
            tiles.append(tile)
    return tiles


@dataclass
class TileMap:
    """Store the tile layout and helper surfaces required to render a map."""

    layout: List[List[int]]
    tile_size: Tuple[int, int]
    tiles: List[pygame.Surface]
    path: List[TileCoord]
    background: Optional[pygame.Surface] = None

    def __init__(
        self,
        layout: Sequence[Sequence[int]],
        tile_size: Tuple[int, int] | int,
        tiles: Sequence[pygame.Surface],
        path: Optional[Sequence[TileCoord]] = None,
        background: Optional[pygame.Surface] = None,
    ) -> None:
        if isinstance(tile_size, int):
            tile_size = (tile_size, tile_size)
        self.tile_size = (int(tile_size[0]), int(tile_size[1]))
        self.layout = [list(row) for row in layout]
        self.tiles = [self._ensure_tile_size(tile) for tile in tiles]
        self.path = list(path) if path else []
        self.background = background

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _ensure_tile_size(self, tile: pygame.Surface) -> pygame.Surface:
        if tile.get_size() == self.tile_size:
            return tile
        return pygame.transform.smoothscale(tile, self.tile_size)

    @property
    def width(self) -> int:
        return len(self.layout[0]) if self.layout else 0

    @property
    def height(self) -> int:
        return len(self.layout)

    @property
    def pixel_size(self) -> Tuple[int, int]:
        return self.width * self.tile_size[0], self.height * self.tile_size[1]

    def set_background(self, surface: pygame.Surface) -> None:
        """Assign a background sprite for the map."""

        self.background = surface

    def tile_to_world(self, coord: TileCoord) -> Point:
        """Return the pixel center for a tile coordinate."""

        tx, ty = coord
        return (
            tx * self.tile_size[0] + self.tile_size[0] / 2,
            ty * self.tile_size[1] + self.tile_size[1] / 2,
        )

    def world_path(self) -> List[Point]:
        """Project the tile based path into pixel coordinates."""

        return [self.tile_to_world(step) for step in self.path]

    def iter_tiles(self) -> Iterable[Tuple[int, int, pygame.Surface]]:
        """Yield ``(x, y, tile_surface)`` triples for every tile in the map."""

        for row_index, row in enumerate(self.layout):
            for col_index, tile_id in enumerate(row):
                if tile_id < 0 or tile_id >= len(self.tiles):
                    continue
                yield col_index, row_index, self.tiles[tile_id]

    # ------------------------------------------------------------------
    # Drawing
    # ------------------------------------------------------------------
    def draw(self, surface: pygame.Surface, offset: Tuple[int, int] = (0, 0)) -> None:
        """Render the background (if any) and every tile to ``surface``."""

        if self.background:
            bg = self.background
            if bg.get_size() != surface.get_size():
                bg = pygame.transform.smoothscale(bg, surface.get_size())
            surface.blit(bg, (0, 0))

        ox, oy = offset
        for x, y, tile in self.iter_tiles():
            dest = (x * self.tile_size[0] + ox, y * self.tile_size[1] + oy)
            surface.blit(tile, dest)

    def draw_path(
        self,
        surface: pygame.Surface,
        color: Tuple[int, int, int] = (255, 0, 0),
        width: int = 3,
    ) -> None:
        """Draw the defined path as a polyline for visual debugging."""

        points = self.world_path()
        if len(points) >= 2:
            pygame.draw.lines(surface, color, False, points, width)

    # ------------------------------------------------------------------
    # Construction helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_indices(
        cls,
        indices: Sequence[Sequence[int]],
        tiles: Sequence[pygame.Surface],
        tile_size: Tuple[int, int] | int,
        path: Optional[Sequence[TileCoord]] = None,
        background: Optional[pygame.Surface] = None,
    ) -> "TileMap":
        return cls(indices, tile_size, tiles, path=path, background=background)

    @classmethod
    def from_sprite_sheet(
        cls,
        indices: Sequence[Sequence[int]],
        sheet_path: str | Path,
        tile_width: int,
        tile_height: Optional[int] = None,
        path: Optional[Sequence[TileCoord]] = None,
        background_path: Optional[str | Path] = None,
    ) -> "TileMap":
        """Helper constructor to load everything from disk."""

        tiles = load_tile_sheet(sheet_path, tile_width, tile_height)
        tile_size = (tile_width, tile_height or tile_width)
        background = None
        if background_path:
            background = pygame.image.load(str(background_path)).convert()
        return cls(indices, tile_size, tiles, path=path, background=background)
