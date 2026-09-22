"""PySide6 overlay window implementation."""

from __future__ import annotations

from typing import Any

from PIL import Image
from PySide6.QtCore import Qt
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

from radar_overlay.config import OverlaySettings


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
        self.resize(settings.width, settings.height)
        self.move(settings.x, settings.y)
        self.setWindowOpacity(settings.opacity)
        self.set_click_through(settings.click_through)

    def set_click_through(self, enabled: bool) -> None:
        """Enable or disable mouse interaction with the overlay."""

        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, enabled)

    def update_image(self, image: Image.Image) -> None:
        """Render the captured image into the overlay."""

        rgba = image.convert("RGBA")
        data = rgba.tobytes("raw", "RGBA")
        qimage = QImage(data, rgba.width, rgba.height, QImage.Format.Format_RGBA8888)
        pixmap = QPixmap.fromImage(qimage)
        self._label.setPixmap(pixmap)
        self._label.resize(rgba.width, rgba.height)
        self.resize(rgba.width, rgba.height)


__all__ = ["OverlayWindow"]
