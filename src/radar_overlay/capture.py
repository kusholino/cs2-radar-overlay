"""Desktop capture utilities used by the overlay prototype."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from PIL import Image, ImageGrab

from radar_overlay.config import CaptureSettings, validate_capture_region

try:  # pragma: no cover - environment-specific import
    import dxcam
except ImportError:  # pragma: no cover - fallback if dxcam is not installed
    dxcam = None


@dataclass
class CaptureFrame:
    """Container for a captured region."""

    image: Image.Image
    captured_at: float


class ScreenCapture:
    """Capture a rectangular region from the Windows desktop."""

    def __init__(self, settings: CaptureSettings):
        self.settings = settings
        self._dxcam = None

        if dxcam is not None:  # pragma: no cover - optional runtime dependency
            try:
                self._dxcam = dxcam.create(device_idx=0)
            except Exception:  # pragma: no cover - fall back cleanly if unsupported
                self._dxcam = None

    def get_virtual_screen_bounds(self) -> tuple[int, int, int, int]:
        """Return the current virtual desktop boundaries."""

        width, height = ImageGrab.grab().size
        return (0, 0, width, height)

    def capture_region(self) -> CaptureFrame:
        """Capture and return the configured rectangle."""

        x, y, width, height = validate_capture_region(
            self.settings.x,
            self.settings.y,
            self.settings.width,
            self.settings.height,
            *self.get_virtual_screen_bounds()[2:],
        )

        if self._dxcam is not None and hasattr(self._dxcam, "grab"):
            region = self._dxcam.grab(region=(x, y, x + width, y + height))
            if region is not None:
                image = Image.fromarray(region)
                return CaptureFrame(image=image, captured_at=0.0)

        image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        return CaptureFrame(image=image, captured_at=0.0)


__all__ = ["CaptureFrame", "ScreenCapture"]
