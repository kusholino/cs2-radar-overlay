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

try:  # pragma: no cover - environment-specific import
    import mss
except ImportError:  # pragma: no cover - fallback if mss is not installed
    mss = None


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
        self._mss = None
        self._virtual_screen_bounds: tuple[int, int, int, int] | None = None

        if dxcam is not None:  # pragma: no cover - optional runtime dependency
            try:
                self._dxcam = dxcam.create(device_idx=0)
            except Exception:  # pragma: no cover - fall back cleanly if unsupported
                self._dxcam = None

        if self._dxcam is None and mss is not None:  # pragma: no cover - Windows-only backend
            try:
                self._mss = mss.mss()
            except Exception:
                self._mss = None

    def get_virtual_screen_bounds(self) -> tuple[int, int, int, int]:
        """Return the current virtual desktop boundaries."""

        if self._virtual_screen_bounds is None:
            if self._mss is not None:
                monitor = self._mss.monitors[0]
                self._virtual_screen_bounds = (
                    monitor["left"],
                    monitor["top"],
                    monitor["width"],
                    monitor["height"],
                )
            else:
                width, height = ImageGrab.grab(all_screens=True).size
                self._virtual_screen_bounds = (0, 0, width, height)
        return self._virtual_screen_bounds

    def capture_region(self) -> CaptureFrame:
        """Capture and return the configured rectangle."""

        x, y, width, height = validate_capture_region(
            self.settings.x,
            self.settings.y,
            self.settings.width,
            self.settings.height,
            self.get_virtual_screen_bounds()[2],
            self.get_virtual_screen_bounds()[3],
            virtual_left=self.get_virtual_screen_bounds()[0],
            virtual_top=self.get_virtual_screen_bounds()[1],
        )

        if self._dxcam is not None and hasattr(self._dxcam, "grab"):
            region = self._dxcam.grab(region=(x, y, x + width, y + height))
            if region is not None:
                image = Image.fromarray(region)
                return CaptureFrame(image=image, captured_at=0.0)

        if self._mss is not None:
            region = self._mss.grab({"left": x, "top": y, "width": width, "height": height})
            image = Image.frombytes("RGB", region.size, region.rgb)
            return CaptureFrame(image=image, captured_at=0.0)

        image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
        return CaptureFrame(image=image, captured_at=0.0)


__all__ = ["CaptureFrame", "ScreenCapture"]
