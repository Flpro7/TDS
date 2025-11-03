"""Tower build manager utilities."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Optional, Sequence, Set, Tuple

import pygame

from .hud_overlay import TowerButton

GridPosition = Tuple[int, int]
Color = Tuple[int, int, int]

# Coordinates (in tiles) that represent the enemy path.
BLOCKED_TILES: Sequence[GridPosition] = (
    (5, 0),
    (5, 1),
    (5, 2),
    (5, 3),
    (5, 4),
    (6, 4),
    (7, 4),
    (8, 4),
    (9, 4),
    (10, 4),
    (11, 4),
    (12, 4),
    (12, 5),
    (12, 6),
    (12, 7),
    (12, 8),
)

PREVIEW_OK_COLOR: Color = (80, 200, 120)
PREVIEW_FORBIDDEN_COLOR: Color = (210, 80, 80)


@dataclass
class BuildPreview:
    """Data describing the current build preview."""

    grid_position: GridPosition
    pixel_position: Tuple[int, int]
    color: Color
    can_build: bool


class BuildManager:
    """Orchestrates the state machine when placing new towers."""

    def __init__(
        self,
        tile_size: int,
        blocked_tiles: Optional[Iterable[GridPosition]] = None,
    ) -> None:
        self.tile_size = tile_size
        self.blocked_tiles: Set[GridPosition] = set(blocked_tiles or BLOCKED_TILES)
        self._selected_button: Optional[TowerButton] = None
        self.preview: Optional[BuildPreview] = None

    @property
    def is_building(self) -> bool:
        return self._selected_button is not None

    def begin_build(self, button: TowerButton, money: int) -> bool:
        """Start placing ``button`` if the player has enough ``money``."""

        if money < button.cost:
            return False
        self._selected_button = button
        self.preview = None
        return True

    def cancel(self) -> None:
        """Abort the current building operation."""

        self._selected_button = None
        self.preview = None

    def _snap_to_grid(self, position: Tuple[int, int]) -> GridPosition:
        return position[0] // self.tile_size, position[1] // self.tile_size

    def _can_place(self, grid_position: GridPosition, occupied: Set[GridPosition], money: int) -> bool:
        if self._selected_button is None:
            return False
        if money < self._selected_button.cost:
            return False
        if grid_position in self.blocked_tiles:
            return False
        return grid_position not in occupied

    def update_preview(
        self,
        mouse_position: Tuple[int, int],
        occupied_tiles: Iterable[GridPosition],
        money: int,
    ) -> Optional[BuildPreview]:
        """Update the preview rectangle according to ``mouse_position``."""

        if self._selected_button is None:
            self.preview = None
            return None

        grid_position = self._snap_to_grid(mouse_position)
        occupied_set = set(occupied_tiles)
        can_place = self._can_place(grid_position, occupied_set, money)
        color = PREVIEW_OK_COLOR if can_place else PREVIEW_FORBIDDEN_COLOR
        pixel_position = (
            grid_position[0] * self.tile_size,
            grid_position[1] * self.tile_size,
        )
        self.preview = BuildPreview(grid_position, pixel_position, color, can_place)
        return self.preview

    def confirm_build(
        self,
        occupied_tiles: Set[GridPosition],
        money: int,
    ) -> Optional[TowerButton]:
        """Finish the build if the preview is valid."""

        if self.preview is None or self._selected_button is None:
            return None
        if not self.preview.can_build:
            return None
        if money < self._selected_button.cost:
            return None

        occupied_tiles.add(self.preview.grid_position)
        button = self._selected_button
        self.cancel()
        return button

    def draw_preview(self, surface: pygame.Surface) -> None:
        """Render the preview rectangle in red/green according to validity."""

        if self.preview is None:
            return
        rect = pygame.Rect(self.preview.pixel_position, (self.tile_size, self.tile_size))
        pygame.draw.rect(surface, self.preview.color, rect, width=3)
        inner = rect.inflate(-6, -6)
        pygame.draw.rect(surface, self.preview.color, inner, width=1)
