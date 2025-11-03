"""Wave management utilities for spawning enemies over time.

This module exposes :class:`WaveManager`, a simple timer-driven controller that
reads a declarative wave description and executes spawn callbacks at the
appropriate moment.  It is intentionally lightweight so it can be reused inside
sample games or tests without bringing any framework specific baggage.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Sequence, Tuple

EnemySpawn = Tuple[str, float]
WaveDefinition = Sequence[EnemySpawn]
SpawnCallback = Callable[[str], None]


@dataclass
class WaveState:
    """Runtime bookkeeping for the current wave."""

    spawns: List[EnemySpawn]
    elapsed: float = 0.0


class WaveManager:
    """Spawn enemies for a sequence of waves using a timer.

    Parameters
    ----------
    waves:
        A list containing the individual waves.  Each wave must be an iterable
        of ``(enemy_type, spawn_time)`` tuples.  ``spawn_time`` is measured in
        seconds relative to the beginning of the wave.
    spawn_callback:
        Callable invoked every time an enemy should be created.  The callback
        receives the ``enemy_type`` string so the callee can instantiate the
        concrete enemy object.
    loop_waves:
        When ``True`` the manager restarts at the first wave after the last wave
        finishes.  The default (``False``) is to stop after the final wave.
    """

    def __init__(
        self,
        waves: Iterable[WaveDefinition],
        spawn_callback: SpawnCallback,
        *,
        loop_waves: bool = False,
    ) -> None:
        self._waves: List[List[EnemySpawn]] = [
            sorted([(enemy, float(time)) for enemy, time in wave], key=lambda item: item[1])
            for wave in waves
        ]
        self._spawn_callback = spawn_callback
        self._loop_waves = loop_waves

        self._current_index: int = -1
        self._state: WaveState | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def current_wave_index(self) -> int:
        """0-based index of the active wave or ``-1`` when idle."""

        return self._current_index

    @property
    def current_wave_number(self) -> int:
        """Human friendly 1-based wave number (``0`` when idle)."""

        return self._current_index + 1 if self._state else 0

    @property
    def wave_in_progress(self) -> bool:
        """Whether a wave is currently being spawned."""

        return self._state is not None

    @property
    def total_waves(self) -> int:
        return len(self._waves)

    def start_next_wave(self) -> bool:
        """Start the next wave if available.

        Returns ``True`` when a wave starts.  If a wave is already running or no
        additional waves exist the method returns ``False``.
        """

        if self._state is not None:
            return False

        next_index = self._current_index + 1
        if next_index >= len(self._waves):
            if self._loop_waves and self._waves:
                next_index = 0
            else:
                return False

        self._current_index = next_index
        self._state = WaveState(spawns=list(self._waves[next_index]))
        return True

    def reset(self) -> None:
        """Return to the idle state and forget progress."""

        self._current_index = -1
        self._state = None

    def update(self, delta_time: float) -> None:
        """Advance the internal timer and spawn due enemies."""

        if self._state is None:
            return

        self._state.elapsed += delta_time
        while self._state.spawns and self._state.spawns[0][1] <= self._state.elapsed:
            enemy_type, _ = self._state.spawns.pop(0)
            self._spawn_callback(enemy_type)

        if not self._state.spawns:
            self._state = None

    def is_finished(self) -> bool:
        """Whether all configured waves have been completed."""

        return not self._loop_waves and self._current_index >= len(self._waves) - 1 and self._state is None

    # Convenience helpers -------------------------------------------------
    def remaining_waves(self) -> int:
        """Number of waves left to play (including the active one)."""

        if self._loop_waves:
            return float("inf")  # type: ignore[return-value]

        if self._state is None:
            return max(0, len(self._waves) - (self._current_index + 1))
        return max(0, len(self._waves) - self._current_index)

    def serialize_progress(self) -> dict:
        """Create a JSON-serialisable snapshot of the current state."""

        return {
            "current_index": self._current_index,
            "wave_in_progress": self.wave_in_progress,
            "remaining_spawns": list(self._state.spawns) if self._state else [],
            "elapsed": self._state.elapsed if self._state else 0.0,
        }

    def load_progress(self, data: dict) -> None:
        """Restore the manager from :meth:`serialize_progress` output."""

        index = int(data.get("current_index", -1))
        if index < -1 or index >= len(self._waves):
            raise ValueError("Invalid wave index in progress data")

        self._current_index = index
        if data.get("wave_in_progress") and 0 <= index < len(self._waves):
            remaining = [tuple(item) for item in data.get("remaining_spawns", [])]
            self._state = WaveState(spawns=list(remaining), elapsed=float(data.get("elapsed", 0.0)))
        else:
            self._state = None
