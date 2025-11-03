"""Sprite loading and caching utilities for the tower defence game.

This module centralises sprite loading so that the pygame image loader is
invoked only once per resource.  Subsequent calls return the cached instance
allowing animations to reuse surfaces without hitting the file-system again.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import pygame

# Internal cache that maps a tuple describing how the sprite was loaded to the
# pygame surface instance.  Using a dictionary keeps the implementation simple
# while guaranteeing O(1) lookups on average.
_SPRITE_CACHE: Dict[Tuple[Path, bool, Tuple[int, int, int] | None], pygame.Surface] = {}


def _normalise_path(path: str | Path) -> Path:
    """Return a normalised, absolute path for cache keys.

    The loader accepts either :class:`str` or :class:`~pathlib.Path` objects.
    Converting everything to an absolute :class:`Path` prevents duplicates such
    as ``"enemy.png"`` versus ``"./enemy.png"`` from resulting in two cache
    entries for the same sprite.
    """

    p = Path(path)
    return p if p.is_absolute() else (Path.cwd() / p).resolve()


def load_sprite(path: str | Path, *, convert_alpha: bool = True,
                colorkey: Tuple[int, int, int] | None = None) -> pygame.Surface:
    """Load a sprite from ``path`` using pygame and cache the surface.

    Parameters
    ----------
    path:
        Filesystem path to the sprite.
    convert_alpha:
        Whether to call :func:`pygame.Surface.convert_alpha`.  When ``False`` the
        image is converted without per-pixel alpha.
    colorkey:
        Optional colour that should be treated as transparent.

    Returns
    -------
    pygame.Surface
        The cached or newly loaded surface.
    """

    normalised = _normalise_path(path)
    cache_key = (normalised, convert_alpha, colorkey)
    if cache_key in _SPRITE_CACHE:
        return _SPRITE_CACHE[cache_key]

    image = pygame.image.load(str(normalised))

    # ``Surface.convert`` and ``Surface.convert_alpha`` require an initialised
    # display surface.  During unit tests the pygame display module is not
    # always set up which would raise an exception.  We therefore only convert
    # the surface when a display surface is present.
    if pygame.display.get_surface() is not None:
        if convert_alpha:
            image = image.convert_alpha()
        else:
            image = image.convert()

    if colorkey is not None:
        image.set_colorkey(colorkey)

    _SPRITE_CACHE[cache_key] = image
    return image


def load_sprite_sheet(paths: Iterable[str | Path], *, convert_alpha: bool = True,
                      colorkey: Tuple[int, int, int] | None = None) -> list[pygame.Surface]:
    """Load several sprites at once.

    This is a convenience wrapper used for animations.  Each path shares the
    same conversion settings, guaranteeing that consecutive frames are
    compatible with blitting operations.
    """

    return [
        load_sprite(path, convert_alpha=convert_alpha, colorkey=colorkey)
        for path in paths
    ]


def cache_sprite(path: str | Path, surface: pygame.Surface, *,
                 convert_alpha: bool = True,
                 colorkey: Tuple[int, int, int] | None = None) -> None:
    """Manually register ``surface`` for ``path`` in the loader cache.

    This can be helpful when sprites are generated procedurally at runtime.
    """

    normalised = _normalise_path(path)
    cache_key = (normalised, convert_alpha, colorkey)
    _SPRITE_CACHE[cache_key] = surface


def clear_cache() -> None:
    """Remove every cached sprite.

    Useful for test suites or when the game needs to release resources.
    """

    _SPRITE_CACHE.clear()
