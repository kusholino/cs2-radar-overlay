"""Application entry point for the radar overlay prototype."""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication

from radar_overlay.capture import ScreenCapture
from radar_overlay.config import AppConfig, DEFAULT_CONFIG, calculate_scaled_dimensions, load_config
from radar_overlay.overlay import OverlayWindow
from radar_overlay.performance import PerformanceTracker


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purely visual Windows radar relocation overlay.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"), help="Path to the TOML config file")
    return parser.parse_args()


def build_app(config: AppConfig | None = None) -> tuple[QApplication, ScreenCapture, OverlayWindow, PerformanceTracker, QTimer]:
    app = QApplication(sys.argv)
    runtime_config = config or DEFAULT_CONFIG
    capture = ScreenCapture(runtime_config.capture)
    overlay = OverlayWindow(runtime_config.overlay)
    tracker = PerformanceTracker()
    timer = QTimer()
    timer.setTimerType(0)

    def on_tick() -> None:
        tracker.begin_capture()
        frame = capture.capture_region()
        tracker.end_capture()
        tracker.begin_render()

        render_width, render_height = calculate_scaled_dimensions(
            frame.image.width,
            frame.image.height,
            runtime_config.overlay.width,
            runtime_config.overlay.height,
            preserve_aspect_ratio=True,
        )
        overlay.resize(render_width, render_height)
        overlay.update_image(frame.image.resize((render_width, render_height), resample=None))
        tracker.end_render()

    timer.timeout.connect(on_tick)
    interval_ms = max(1, int(1000 / runtime_config.performance.target_fps))
    timer.start(interval_ms)
    return app, capture, overlay, tracker, timer


def main() -> int:
    args = parse_args()
    try:
        config = load_config(args.config)
    except FileNotFoundError:
        config = DEFAULT_CONFIG

    app, _, overlay, _, _ = build_app(config)
    overlay.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
