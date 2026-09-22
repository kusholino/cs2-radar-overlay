"""Interactive screen-region calibration for the desktop overlay."""

from __future__ import annotations

from collections.abc import Callable

from PIL import ImageGrab
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtGui import QColor, QImage, QPainter, QPen, QPixmap, QRegion
from PySide6.QtWidgets import QApplication, QLabel, QRubberBand, QWidget


class RegionSelector(QWidget):
    """Snipping-tool style selector that collects source and destination regions."""

    def __init__(
        self,
        on_complete: Callable[[tuple[int, int, int, int], tuple[int, int, int, int]], None],
        shape: str = "rectangle",
        initial_source: tuple[int, int, int, int] | None = None,
        initial_destination: tuple[int, int, int, int] | None = None,
    ) -> None:
        super().__init__()
        self._on_complete = on_complete
        self._shape = shape
        virtual_geometry = QApplication.primaryScreen().virtualGeometry()
        self._virtual_origin = QPoint(virtual_geometry.left(), virtual_geometry.top())
        self._stage = 2 if initial_source and initial_destination else 0
        self._source = initial_source
        self._destination = initial_destination
        self._current_rect: QRect | None = None
        self._active_region: str | None = None
        self._drag_mode: str | None = None
        self._drag_start = QPoint()
        self._drag_rect = QRect()
        self._origin = QPoint()
        self._rubber_band = QRubberBand(QRubberBand.Shape.Rectangle, self)
        self._background = QLabel(self)
        screenshot = ImageGrab.grab(all_screens=True)
        screenshot_data = screenshot.convert("RGB").tobytes("raw", "RGB")
        screenshot_image = QImage(
            screenshot_data,
            screenshot.width,
            screenshot.height,
            QImage.Format.Format_RGB888,
        )
        self._background_pixmap = QPixmap.fromImage(screenshot_image)
        self._background.setPixmap(self._background_pixmap)
        self._background.setGeometry(0, 0, screenshot.width, screenshot.height)
        self._background.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._background.lower()
        self._background.hide()
        self._preview = QLabel(self)
        preview_style = "border: 3px solid #00e5ff; background: transparent;"
        if self._shape == "circle":
            preview_style = "border: 3px solid #00e5ff; border-radius: 9999px; background: transparent;"
        self._preview.setStyleSheet(preview_style)
        self._preview.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)
        self._preview.hide()
        self._hint = QLabel(self)
        self._hint.setStyleSheet(
            "color: white; background: rgba(0, 0, 0, 190); padding: 8px;"
        )
        selection_name = "Kreis" if self._shape == "circle" else "Rechteck"
        self._hint.setText(f"1/2: Ziehe ein {selection_name} um die CS2-Minimap")
        self._hint.adjustSize()
        self._hint.raise_()
        self.setCursor(Qt.CursorShape.CrossCursor)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setGeometry(virtual_geometry)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMouseTracking(True)
        if self._stage == 2:
            self._refresh_preview()
            self._hint.setText(
                "Bestehende Config bearbeiten: Ziehen = verschieben, Kanten/Ecken = Größe ändern | "
                "Enter = speichern | R = neu | Esc = abbrechen"
            )
            self._hint.adjustSize()

    def _draw_region(self, painter: QPainter, region: tuple[int, int, int, int]) -> None:
        rectangle = self._to_local_rect(QRect(*region))
        if self._shape == "circle":
            painter.drawEllipse(rectangle)
        else:
            painter.drawRect(rectangle)

    def _region_rect(self, name: str) -> QRect:
        region = self._source if name == "source" else self._destination
        return self._to_local_rect(QRect(*(region or (0, 0, 0, 0))))

    def _to_local_rect(self, rectangle: QRect) -> QRect:
        return rectangle.translated(-self._virtual_origin)

    def _hit_test(self, position: QPoint, name: str) -> str | None:
        rectangle = self._region_rect(name)
        if not rectangle.contains(position):
            return None
        margin = 12
        left = abs(position.x() - rectangle.left()) <= margin
        right = abs(position.x() - rectangle.right()) <= margin
        top = abs(position.y() - rectangle.top()) <= margin
        bottom = abs(position.y() - rectangle.bottom()) <= margin
        horizontal = "l" if left else "r" if right else ""
        vertical = "t" if top else "b" if bottom else ""
        return vertical + horizontal or "move"

    def _update_region(self, name: str, rectangle: QRect) -> None:
        rectangle = rectangle.normalized()
        rectangle.setWidth(max(2, rectangle.width()))
        rectangle.setHeight(max(2, rectangle.height()))
        selected = (rectangle.x(), rectangle.y(), rectangle.width(), rectangle.height())
        selected = (selected[0] + self._virtual_origin.x(), selected[1] + self._virtual_origin.y(), selected[2], selected[3])
        if name == "source":
            self._source = selected
        else:
            self._destination = selected

    def _refresh_preview(self) -> None:
        if self._source is None or self._destination is None:
            return
        source_rect = self._to_local_rect(QRect(*self._source))
        destination_rect = self._to_local_rect(QRect(*self._destination))
        preview = self._background_pixmap.copy(source_rect)
        self._preview.setPixmap(preview.scaled(
            destination_rect.width(),
            destination_rect.height(),
            Qt.AspectRatioMode.IgnoreAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        ))
        self._preview.setGeometry(destination_rect)
        if self._shape == "circle":
            self._preview.setMask(QRegion(self._preview.rect(), QRegion.RegionType.Ellipse))
        else:
            self._preview.clearMask()
        self._preview.show()
        self._preview.raise_()

    def paintEvent(self, event) -> None:  # type: ignore[override]
        painter = QPainter(self)
        painter.drawPixmap(0, 0, self._background_pixmap)
        painter.setPen(QPen(Qt.GlobalColor.white, 1, Qt.PenStyle.DashLine))
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))
        if self._source is not None:
            painter.setBrush(QColor(40, 220, 100, 55))
            painter.setPen(QPen(Qt.GlobalColor.green, 3))
            self._draw_region(painter, self._source)
        if self._destination is not None:
            painter.setBrush(QColor(0, 210, 255, 45))
            painter.setPen(QPen(Qt.GlobalColor.cyan, 3))
            self._draw_region(painter, self._destination)
        if self._current_rect is not None:
            painter.setBrush(QColor(255, 220, 0, 65))
            painter.setPen(QPen(Qt.GlobalColor.yellow, 2, Qt.PenStyle.DashLine))
            if self._shape == "circle":
                painter.drawEllipse(self._current_rect)
            else:
                painter.drawRect(self._current_rect)

    def mousePressEvent(self, event) -> None:  # type: ignore[override]
        if event.button() == Qt.MouseButton.LeftButton:
            if self._stage == 2:
                position = event.position().toPoint()
                self._active_region = "destination" if self._destination and self._hit_test(position, "destination") else "source"
                self._drag_mode = self._hit_test(position, self._active_region)
                if self._drag_mode is None:
                    self._active_region = None
                    return
                self._drag_start = position
                self._drag_rect = self._region_rect(self._active_region)
                return
            self._origin = event.position().toPoint()
            self._rubber_band.setGeometry(QRect(self._origin, self._origin))
            self._current_rect = QRect(self._origin, self._origin)
            self.update()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[override]
        if self._stage == 2 and self._active_region and self._drag_mode:
            position = event.position().toPoint()
            delta = position - self._drag_start
            rectangle = QRect(self._drag_rect)
            if self._drag_mode == "move":
                rectangle.translate(delta)
            else:
                if "l" in self._drag_mode:
                    rectangle.setLeft(self._drag_rect.left() + delta.x())
                if "r" in self._drag_mode:
                    rectangle.setRight(self._drag_rect.right() + delta.x())
                if "t" in self._drag_mode:
                    rectangle.setTop(self._drag_rect.top() + delta.y())
                if "b" in self._drag_mode:
                    rectangle.setBottom(self._drag_rect.bottom() + delta.y())
            self._update_region(self._active_region, rectangle)
            self._refresh_preview()
            self.update()
            return
        if self._current_rect is not None:
            self._current_rect = QRect(self._origin, event.position().toPoint()).normalized()
            self.update()

    def mouseReleaseEvent(self, event) -> None:  # type: ignore[override]
        if event.button() != Qt.MouseButton.LeftButton:
            return
        if self._stage == 2:
            self._active_region = None
            self._drag_mode = None
            return
        rectangle = self._rubber_band.geometry().normalized()
        if self._current_rect is not None:
            rectangle = self._current_rect.normalized()
        self._current_rect = None
        if rectangle.width() < 2 or rectangle.height() < 2:
            return

        selected = (
            rectangle.x() + self._virtual_origin.x(),
            rectangle.y() + self._virtual_origin.y(),
            rectangle.width(),
            rectangle.height(),
        )
        if self._stage == 0:
            self._source = selected
            self._stage = 1
            self._hint.setText("2/2: Ziehe die gewünschte Zielgröße und Position")
            self._hint.adjustSize()
        elif self._source is not None:
            self._destination = selected
            self._stage = 2
            self._refresh_preview()
            self._hint.setText("Ziehen = verschieben, Kanten/Ecken = Größe ändern | Enter = speichern | R = neu | Esc = abbrechen")
            self._hint.adjustSize()
            self.update()

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if event.key() == Qt.Key.Key_Escape:
            self.close()
        elif event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter) and self._stage == 2:
            if self._source is not None and self._destination is not None:
                self._on_complete(self._source, self._destination)
                self.close()
        elif event.key() == Qt.Key.Key_R and self._stage == 2:
            self._stage = 0
            self._source = None
            self._destination = None
            self._current_rect = None
            self._preview.clear()
            self._preview.clearMask()
            self._preview.hide()
            selection_name = "Kreis" if self._shape == "circle" else "Rechteck"
            self._hint.setText(f"1/2: Ziehe ein {selection_name} um die CS2-Minimap")
            self._hint.adjustSize()
            self.update()
        super().keyPressEvent(event)

    def closeEvent(self, event) -> None:  # type: ignore[override]
        QApplication.instance().quit()
        super().closeEvent(event)


def run_calibration(
    on_complete: Callable[[tuple[int, int, int, int], tuple[int, int, int, int]], None],
    shape: str = "rectangle",
    initial_source: tuple[int, int, int, int] | None = None,
    initial_destination: tuple[int, int, int, int] | None = None,
) -> int:
    """Run the interactive selector and return its Qt exit code."""

    app = QApplication.instance() or QApplication([])
    def finish(source: tuple[int, int, int, int], destination: tuple[int, int, int, int]) -> None:
        on_complete(source, destination)
        app.quit()

    selector = RegionSelector(
        finish,
        shape=shape,
        initial_source=initial_source,
        initial_destination=initial_destination,
    )
    selector.show()
    return app.exec()


__all__ = ["run_calibration"]
