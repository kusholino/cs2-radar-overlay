"""Utilities for measuring capture/render timing."""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter


@dataclass
class PerformanceStats:
    """Performance summary for a single frame interval."""

    capture_fps: float
    overlay_fps: float
    capture_time_ms: float
    render_time_ms: float
    frame_interval_ms: float


class PerformanceTracker:
    """Tracks capture and render timings for debug information."""

    def __init__(self) -> None:
        self._capture_start: float | None = None
        self._render_start: float | None = None
        self._last_tick: float | None = None
        self._capture_samples: list[float] = []
        self._render_samples: list[float] = []

    def begin_capture(self) -> None:
        self._capture_start = perf_counter()

    def end_capture(self) -> None:
        if self._capture_start is None:
            return
        duration = perf_counter() - self._capture_start
        self._capture_samples.append(duration)
        self._capture_start = None
        if len(self._capture_samples) > 60:
            self._capture_samples.pop(0)

    def begin_render(self) -> None:
        self._render_start = perf_counter()

    def end_render(self) -> None:
        if self._render_start is None:
            return
        duration = perf_counter() - self._render_start
        self._render_samples.append(duration)
        self._render_start = None
        if len(self._render_samples) > 60:
            self._render_samples.pop(0)

    def snapshot(self) -> PerformanceStats:
        """Return the current performance snapshot."""

        now = perf_counter()
        capture_time_ms = self.average_seconds(self._capture_samples) * 1000.0
        render_time_ms = self.average_seconds(self._render_samples) * 1000.0
        frame_interval_ms = 0.0
        if self._last_tick is not None:
            frame_interval_ms = (now - self._last_tick) * 1000.0
        self._last_tick = now

        capture_fps = 1000.0 / max(capture_time_ms, 1.0) if capture_time_ms > 0.0 else 0.0
        overlay_fps = 1000.0 / max(render_time_ms, 1.0) if render_time_ms > 0.0 else 0.0

        return PerformanceStats(
            capture_fps=capture_fps,
            overlay_fps=overlay_fps,
            capture_time_ms=capture_time_ms,
            render_time_ms=render_time_ms,
            frame_interval_ms=frame_interval_ms,
        )

    @staticmethod
    def average_seconds(items: list[float]) -> float:
        if not items:
            return 0.0
        return sum(items) / len(items)


__all__ = ["PerformanceStats", "PerformanceTracker"]
