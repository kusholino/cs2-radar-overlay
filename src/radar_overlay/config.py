"""Configuration loading and validation for the radar overlay prototype."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Any


@dataclass(frozen=True)
class CaptureSettings:
    """Defines the source region captured from the Windows desktop."""

    x: int
    y: int
    width: int
    height: int


@dataclass(frozen=True)
class OverlaySettings:
    """Defines the destination overlay window geometry and behavior."""

    x: int
    y: int
    width: int
    height: int
    opacity: float = 1.0
    click_through: bool = True
    always_on_top: bool = True
    preserve_aspect_ratio: bool = True


@dataclass(frozen=True)
class PerformanceSettings:
    """Capture/update performance configuration."""

    target_fps: int = 240


@dataclass(frozen=True)
class AppConfig:
    """Top-level configuration for the application."""

    capture: CaptureSettings
    overlay: OverlaySettings
    performance: PerformanceSettings


def validate_capture_region(
    x: int,
    y: int,
    width: int,
    height: int,
    virtual_width: int | None = None,
    virtual_height: int | None = None,
) -> tuple[int, int, int, int]:
    """Validate geometry for a desktop capture region."""

    if x < 0 or y < 0:
        raise ValueError("Capture coordinates must be non-negative.")
    if width <= 0 or height <= 0:
        raise ValueError("Capture width and height must be greater than zero.")
    if virtual_width is not None and x + width > virtual_width:
        raise ValueError("Capture region exceeds the available virtual screen width.")
    if virtual_height is not None and y + height > virtual_height:
        raise ValueError("Capture region exceeds the available virtual screen height.")
    return (x, y, width, height)


def validate_overlay_geometry(
    x: int,
    y: int,
    width: int,
    height: int,
    opacity: float,
) -> tuple[int, int, int, int, float]:
    """Validate destination overlay geometry and opacity."""

    if x < 0 or y < 0:
        raise ValueError("Overlay coordinates must be non-negative.")
    if width <= 0 or height <= 0:
        raise ValueError("Overlay width and height must be greater than zero.")
    if not 0.0 <= opacity <= 1.0:
        raise ValueError("Overlay opacity must be between 0.0 and 1.0 inclusive.")
    return (x, y, width, height, opacity)


def calculate_scaled_dimensions(
    source_width: int,
    source_height: int,
    target_width: int,
    target_height: int,
    preserve_aspect_ratio: bool = True,
) -> tuple[int, int]:
    """Compute output dimensions from a source image and target box."""

    if source_width <= 0 or source_height <= 0:
        raise ValueError("Source dimensions must be greater than zero.")
    if target_width <= 0 or target_height <= 0:
        raise ValueError("Target dimensions must be greater than zero.")

    if not preserve_aspect_ratio:
        return (target_width, target_height)

    scale = min(target_width / source_width, target_height / source_height)
    width = max(1, int(round(source_width * scale)))
    height = max(1, int(round(source_height * scale)))
    return (width, height)


def load_config(path: str | Path = "config.toml") -> AppConfig:
    """Load the application configuration from a TOML file."""

    config_path = Path(path)
    with config_path.open("rb") as handle:
        data: dict[str, Any] = tomllib.load(handle)

    capture_data = data.get("capture", {})
    overlay_data = data.get("overlay", {})
    performance_data = data.get("performance", {})

    capture = CaptureSettings(
        x=int(capture_data.get("x", 0)),
        y=int(capture_data.get("y", 0)),
        width=int(capture_data.get("width", 300)),
        height=int(capture_data.get("height", 300)),
    )
    overlay = OverlaySettings(
        x=int(overlay_data.get("x", 0)),
        y=int(overlay_data.get("y", 0)),
        width=int(overlay_data.get("width", capture.width)),
        height=int(overlay_data.get("height", capture.height)),
        opacity=float(overlay_data.get("opacity", 1.0)),
        click_through=bool(overlay_data.get("click_through", True)),
        always_on_top=bool(overlay_data.get("always_on_top", True)),
    )
    performance = PerformanceSettings(target_fps=int(performance_data.get("target_fps", 240)))

    if performance.target_fps <= 0:
        raise ValueError("target_fps must be greater than zero.")
    validate_capture_region(capture.x, capture.y, capture.width, capture.height)
    validate_overlay_geometry(
        overlay.x,
        overlay.y,
        overlay.width,
        overlay.height,
        overlay.opacity,
    )
    return AppConfig(capture=capture, overlay=overlay, performance=performance)


DEFAULT_CONFIG = AppConfig(
    capture=CaptureSettings(x=0, y=0, width=300, height=300),
    overlay=OverlaySettings(x=0, y=0, width=300, height=300, opacity=1.0, click_through=True, always_on_top=True, preserve_aspect_ratio=True),
    performance=PerformanceSettings(target_fps=240),
)
