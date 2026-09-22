"""Application entry point for the radar overlay prototype."""

from __future__ import annotations

import argparse
import signal
import sys
from pathlib import Path

from PySide6.QtCore import QTimer, Qt
from PySide6.QtWidgets import QApplication

from radar_overlay.calibration import run_calibration
from radar_overlay.capture import ScreenCapture
from radar_overlay.config import (
    AppConfig,
    CaptureSettings,
    DEFAULT_CONFIG,
    OverlaySettings,
    calculate_scaled_dimensions,
    load_config,
    preset_path,
    save_config,
)
from radar_overlay.overlay import OverlayWindow
from radar_overlay.performance import PerformanceTracker
from radar_overlay.hotkeys import GlobalHotkeys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Purely visual Windows radar relocation overlay.")
    parser.add_argument("--config", type=Path, default=Path("config.toml"), help="Path to the TOML config file")
    parser.add_argument("--preset", help="Load a named preset from the presets directory")
    parser.add_argument(
        "--edit",
        action="store_true",
        help="Edit the existing source and destination regions without selecting them again",
    )
    parser.add_argument(
        "--calibrate",
        action="store_true",
        help="Select the source and destination rectangles with the mouse and save them",
    )
    parser.add_argument(
        "--shape",
        choices=("rectangle", "circle"),
        default=None,
        help="Overlay shape to save during calibration",
    )
    return parser.parse_args()


def build_app(config: AppConfig | None = None) -> tuple[QApplication, ScreenCapture, OverlayWindow, PerformanceTracker, QTimer]:
    app = QApplication(sys.argv)
    runtime_config = config or DEFAULT_CONFIG
    capture = ScreenCapture(runtime_config.capture)
    overlay = OverlayWindow(runtime_config.overlay)
    tracker = PerformanceTracker()
    timer = QTimer()
    timer.setTimerType(Qt.TimerType.PreciseTimer)
    hotkeys = GlobalHotkeys(overlay.toggle_hud, overlay.toggle_lock, app.quit)
    app.installNativeEventFilter(hotkeys)
    hotkeys.register()

    def cleanup_hotkeys() -> None:
        hotkeys.unregister()
        app.removeNativeEventFilter(hotkeys)

    app.aboutToQuit.connect(cleanup_hotkeys)

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
            preserve_aspect_ratio=runtime_config.overlay.preserve_aspect_ratio,
        )

        if overlay.width() != render_width or overlay.height() != render_height:
            overlay.resize(render_width, render_height)

        display_image = frame.image
        if display_image.size != (render_width, render_height):
            display_image = display_image.resize((render_width, render_height), resample=None)
        overlay.update_image(display_image)
        tracker.end_render()
        overlay.update_stats(tracker.snapshot())

    def stop_app() -> None:
        timer.stop()
        app.quit()

    timer.timeout.connect(on_tick)
    interval_ms = max(1, int(1000 / runtime_config.performance.target_fps))
    timer.start(interval_ms)

    signal.signal(signal.SIGINT, lambda *_: stop_app())
    return app, capture, overlay, tracker, timer


def main() -> int:
    args = parse_args()
    config_path = preset_path(args.preset) if args.preset else args.config
    if args.calibrate or args.edit:
        def on_complete(source: tuple[int, int, int, int], destination: tuple[int, int, int, int]) -> None:
            current = load_config(config_path) if config_path.exists() else DEFAULT_CONFIG
            save_config(
                AppConfig(
                    capture=CaptureSettings(*source),
                    overlay=OverlaySettings(
                        x=destination[0],
                        y=destination[1],
                        width=destination[2],
                        height=destination[3],
                        opacity=current.overlay.opacity,
                        click_through=True,
                        always_on_top=current.overlay.always_on_top,
                        preserve_aspect_ratio=False,
                        shape=args.shape or current.overlay.shape,
                        show_fps=current.overlay.show_fps,
                        show_refresh_hz=current.overlay.show_refresh_hz,
                        show_capture_ms=current.overlay.show_capture_ms,
                        show_render_ms=current.overlay.show_render_ms,
                    ),
                    performance=current.performance,
                ),
                config_path,
            )

        current_shape = args.shape
        current = load_config(config_path) if config_path.exists() else DEFAULT_CONFIG
        if current_shape is None:
            current_shape = current.overlay.shape
        initial_source = current.capture if args.edit else None
        initial_destination = (
            (current.overlay.x, current.overlay.y, current.overlay.width, current.overlay.height)
            if args.edit
            else None
        )
        return run_calibration(
            on_complete,
            shape=current_shape or "rectangle",
            initial_source=(initial_source.x, initial_source.y, initial_source.width, initial_source.height)
            if initial_source
            else None,
            initial_destination=initial_destination,
        )

    try:
        config = load_config(config_path)
    except FileNotFoundError:
        config = DEFAULT_CONFIG

    app, _, overlay, _, _ = build_app(config)
    overlay.show()
    exit_code = app.exec()
    overlay.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
