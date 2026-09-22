"""PySide6 overlay window implementation."""

from __future__ import annotations

from typing import Any

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QLabel, QMainWindow

from radar_overlay.config import OverlaySettings
from radar_overlay.performance import PerformanceStats


class OverlayWindow(QMainWindow):
    """Transparent window used to display the captured radar pixels."""

    def __init__(self, settings: OverlaySettings) -> None:
        super().__init__()
        self.settings = settings

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_AlwaysStackOnTop, settings.always_on_top)
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.Tool
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.WindowDoesNotAcceptFocus
        )

        self._label = QLabel(self)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self._label.setStyleSheet("background: transparent; border: none;")
        self._label.setMinimumSize(1, 1)
        self._label.setScaledContents(True)
        self._stats_label = QLabel(self)
        self._stats_label.setStyleSheet(
            "color: white; background: rgba(0, 0, 0, 170); "
            "padding: 4px; border: none;"
        )
        self._stats_label.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._stats_label.setText("FPS: --\nRefresh: -- Hz")
        self._stats_label.adjustSize()
        self._stats_label.raise_()
        self.resize(settings.width, settings.height)
        self.move(settings.x, settings.y)
        self.setWindowOpacity(settings.opacity)
        self.set_click_through(settings.click_through)

    def set_click_through(self, enabled: bool) -> None:
        """Enable or disable mouse interaction with the overlay."""

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, enabled)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        """Handle keyboard shortcuts for stopping the overlay cleanly."""

        if event.key() == Qt.Key.Key_Escape:
            self.close()
        super().keyPressEvent(event)

    def update_image(self, image: Image.Image) -> None:
        """Render the captured image into the overlay."""

        rgba = image.convert("RGBA")
        data = rgba.tobytes("raw", "RGBA")
        qimage = QImage(data, rgba.width, rgba.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)
        self._label.setPixmap(pixmap)
        self._label.resize(rgba.width, rgba.height)
        if self.width() != rgba.width or self.height() != rgba.height:
            self.resize(rgba.width, rgba.height)

    def update_stats(self, stats: PerformanceStats) -> None:
        """Display live desktop capture and render timing information."""

        refresh_fps = 1000.0 / stats.frame_interval_ms if stats.frame_interval_ms > 0.0 else 0.0
        self._stats_label.setText(
            f"FPS:     {refresh_fps:5.0f}\n"
            f"Refresh: {refresh_fps:5.1f} Hz\n"
            f"Capture: {stats.capture_time_ms:5.1f} ms\n"
            f"Render:  {stats.render_time_ms:5.1f} ms"
        )
        self._stats_label.adjustSize()
        self._stats_label.raise_()


__all__ = ["OverlayWindow"]
