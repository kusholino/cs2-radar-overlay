from pathlib import Path

import pytest

from radar_overlay.config import (
    AppConfig,
    CaptureSettings,
    OverlaySettings,
    PerformanceSettings,
    calculate_scaled_dimensions,
    load_config,
    validate_capture_region,
    validate_overlay_geometry,
)


def test_load_config_parses_toml(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[capture]
x = 100
y = 200
width = 300
height = 200

[overlay]
x = 800
y = 100
width = 600
height = 400
opacity = 0.8
click_through = true
always_on_top = true

[performance]
target_fps = 240
""".strip(),
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert isinstance(config, AppConfig)
    assert config.capture == CaptureSettings(100, 200, 300, 200)
    assert config.overlay == OverlaySettings(800, 100, 600, 400, 0.8, True, True)
    assert config.performance == PerformanceSettings(240)


def test_calculate_scaled_dimensions_preserves_aspect_ratio() -> None:
    width, height = calculate_scaled_dimensions(400, 200, 300, 300, preserve_aspect_ratio=True)
    assert (width, height) == (300, 150)

    width, height = calculate_scaled_dimensions(400, 200, 300, 300, preserve_aspect_ratio=False)
    assert (width, height) == (300, 300)


def test_validate_capture_region_rejects_invalid_dimensions() -> None:
    with pytest.raises(ValueError):
        validate_capture_region(0, 0, 0, 200, 1920, 1080)

    with pytest.raises(ValueError):
        validate_capture_region(0, 0, 100, 0, 1920, 1080)

    with pytest.raises(ValueError):
        validate_capture_region(-1, 0, 100, 100, 1920, 1080)

    assert validate_capture_region(10, 20, 300, 200, 1920, 1080) == (10, 20, 300, 200)


def test_validate_overlay_geometry_rejects_invalid_runtime_values() -> None:
    with pytest.raises(ValueError):
        validate_overlay_geometry(0, 0, 0, 200, 0.5)

    with pytest.raises(ValueError):
        validate_overlay_geometry(0, 0, 200, 200, -0.1)

    with pytest.raises(ValueError):
        validate_overlay_geometry(0, 0, 200, 200, 1.2)

    assert validate_overlay_geometry(50, 75, 250, 150, 0.8) == (50, 75, 250, 150, 0.8)


def test_load_config_rejects_invalid_runtime_values(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        """
[capture]
x = 0
y = 0
width = 100
height = 50

[overlay]
x = 100
y = 200
width = 300
height = 200
opacity = 1.5
click_through = true
always_on_top = true

[performance]
target_fps = 0
""".strip(),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        load_config(config_path)
