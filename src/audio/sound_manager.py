"""Utility for handling in-game sound effects.

This module centralises the configuration and loading of sound effects used
throughout the project.  The :class:`SoundManager` lazily initialises the
``pygame`` mixer, loads each sound from ``assets/audio`` and exposes a handful
of convenience methods (``play_shot``, ``play_hit`` and
``play_wave_complete``) to make it easy for gameplay code to trigger the
appropriate feedback when important events occur.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Dict

try:  # pragma: no cover - optional dependency
    import pygame
except ImportError:  # pragma: no cover - optional dependency
    pygame = None  # type: ignore

_LOGGER = logging.getLogger(__name__)


class SoundManager:
    """Load and play the sound effects used by the game.

    The manager handles the lifetime of the ``pygame`` mixer to ensure that
    sound playback is only attempted when audio support is available.  When
    running in environments without ``pygame`` (for example during automated
    tests) all methods degrade gracefully into no-ops while logging a helpful
    message so developers know why no audio is heard.
    """

    _SOUND_FILES = {
        "shot": "shot.wav",
        "hit": "hit.wav",
        "wave_complete": "wave_complete.wav",
    }

    def __init__(self) -> None:
        self._sounds: Dict[str, "pygame.mixer.Sound"] = {}
        self._available = False
        self._audio_root = Path(__file__).resolve().parents[2] / "assets" / "audio"
        self._initialise()

    def _initialise(self) -> None:
        """Initialise the mixer and load all known sound effects."""
        if pygame is None:
            _LOGGER.warning("pygame is not installed; sound effects will be disabled.")
            return

        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
        except pygame.error as exc:  # pragma: no cover - depends on system audio
            _LOGGER.warning("Unable to initialise audio mixer: %s", exc)
            return

        for key, filename in self._SOUND_FILES.items():
            path = self._audio_root / filename
            if not path.exists():
                _LOGGER.warning("Sound file not found: %s", path)
                continue

            try:
                self._sounds[key] = pygame.mixer.Sound(str(path))
            except pygame.error as exc:  # pragma: no cover - depends on pygame
                _LOGGER.warning("Could not load sound '%s': %s", path, exc)

        if self._sounds:
            self._available = True
        else:
            _LOGGER.warning("No sound effects were loaded; audio playback disabled.")

    def _play(self, key: str) -> None:
        if not self._available:
            return

        sound = self._sounds.get(key)
        if sound is None:
            _LOGGER.debug("Requested sound '%s' is not loaded.", key)
            return

        try:
            sound.play()
        except pygame.error as exc:  # pragma: no cover - depends on pygame
            _LOGGER.warning("Failed to play sound '%s': %s", key, exc)

    def play_shot(self) -> None:
        """Play the tower shooting sound effect."""

        self._play("shot")

    def play_hit(self) -> None:
        """Play the sound for hitting an enemy."""

        self._play("hit")

    def play_wave_complete(self) -> None:
        """Play the sound signalling that the wave has been cleared."""

        self._play("wave_complete")

    def stop_all(self) -> None:
        """Stop any currently playing sound effects."""

        if not self._available:
            return

        try:
            pygame.mixer.stop()
        except pygame.error as exc:  # pragma: no cover - depends on pygame
            _LOGGER.warning("Failed to stop mixer playback: %s", exc)

    def set_volume(self, volume: float) -> None:
        """Set the playback volume for all known sound effects.

        ``volume`` must be in the range ``0.0`` (muted) to ``1.0`` (full
        volume).  Values outside this range are clamped.
        """

        if not self._available:
            return

        volume = max(0.0, min(1.0, volume))
        for sound in self._sounds.values():
            sound.set_volume(volume)
