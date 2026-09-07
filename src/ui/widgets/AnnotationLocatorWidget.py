import math
from typing import Optional

from PyQt6.QtCore import QEasingCurve, QPointF, QRectF, QVariantAnimation, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QMouseEvent, QPaintEvent, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import QSizePolicy, QWidget

class AnnotationLocatorWidget(QWidget):
    """
    A 2D proxy canvas that visually represents the 0.0 to 1.0 coordinate space
    of a Matplotlib canvas.
    Used to position text annotations and pointer arrows.
    """

    textPositionChanged = pyqtSignal(float, float)
    targetPositionChanged = pyqtSignal(float, float)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("AnnotationLocatorWidget")

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(200)
        self.setCursor(Qt.CursorShape.CrossCursor)

        self._aspect_ratio: float = 1.0

        self.text_pos = QPointF(0.5, 0.5)
        self.target_pos = QPointF(0.5, 0.4)

        self.has_arrow: bool = False
        self.arrow_preset: str = "Subtle Pointer"
        self.text_color: QColor = QColor("black")

        self._dragged_node: str | None = None
        self._text_animation: QVariantAnimation | None = None
        self._target_animation: QVariantAnimation | None = None
        self._animation_duration: int = 250

    #####
    # Public setters that triggers the points moving animation
    #####

    def set_arrow_enabled(self, enabled: bool) -> None:
        """Toggles the rendering of the secondary target node and the connection line"""
        if self.has_arrow != enabled:
            self.has_arrow = enabled
            self.update()

    def set_arrow_preset(self, preset: str) -> None:
        """Updates the visual representation of the pointer arrow to match the selected arrow preset"""
        if self.arrow_preset != preset:
            self.arrow_preset = preset
            self.update()

    def set_text_color(self, color: QColor) -> None:
        """Updates the text node color to match the chosen font color"""
        if self.text_color != color:
            self.text_color = color
            self.update()

    def set_canvas_dimensions(self, width: float, height: float) -> None:
        """
        Updates the proxy canvas dimensions to match the target figure's aspect ratio
        """
        if width <= 0 or height <= 0:
            return

        self._aspect_ratio = width / height
        self.update()

    def _get_canvas_rect(self) -> QRectF:
        """Calculates the centered active canvas area based on the current aspect ratio"""
        widget_width, widget_height = self.width(), self.height()

        target_height = widget_height
        target_width = target_height * self._aspect_ratio

        if target_width > widget_width:
            target_width = widget_width
            target_height = target_width / self._aspect_ratio

        x = (widget_width - target_width) / 2.0
        y = (widget_height - target_height) / 2.0

        return QRectF(x, y, target_width, target_height)

    def set_text_pos(self, x: float, y: float) -> None:
        """Sets the text origin and animates to a new position if changed"""
        if self._dragged_node == "text":
            return

        new_pos = QPointF(x, y)
        if self.text_pos == new_pos:
            return

        if self._text_animation and self._text_animation.state() == QVariantAnimation.State.Running:
            self._text_animation.stop()

        self._text_animation = QVariantAnimation(self)
        self._text_animation.setStartValue(self.text_pos)
        self._text_animation.setEndValue(new_pos)
        self._text_animation.setDuration(self._animation_duration)
        self._text_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._text_animation.valueChanged.connect(self._on_text_animation_step)
        self._text_animation.start()

    def set_target_pos(self, x: float, y: float) -> None:
        """Sets the arrow target and animates to the new position if changed"""
        if self._dragged_node == "target":
            return

        new_pos = QPointF(x, y)
        if self.target_pos == new_pos:
            return

        if self._target_animation and self._target_animation.state() == QVariantAnimation.State.Running:
            self._target_animation.stop()

        self._target_animation = QVariantAnimation(self)
        self._target_animation.setStartValue(self.target_pos)
        self._target_animation.setEndValue(new_pos)
        self._target_animation.setDuration(self._animation_duration)
        self._target_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._target_animation.valueChanged.connect(self._on_target_animation_step)
        self._target_animation.start()

    def _on_text_animation_step(self, value: QPointF) -> None:
        self.text_pos = value
        self.update()

    def _on_target_animation_step(self, value: QPointF) -> None:
        self.target_pos = value
        self.update()

    #####
    # Mouse Event Handlers
    ## Handles the mouse Press, the move and the release of a point
    ## Hit Detection and dragging events
    #####

    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Detects a click on a node to being a drag operation"""
        if event.button() != Qt.MouseButton.LeftButton:
            return

        if self._text_animation and self._text_animation.state() == QVariantAnimation.State.Running:
            self._text_animation.stop()
        if self._target_animation and self._target_animation.state() == QVariantAnimation.State.Running:
            self._target_animation.stop()

        local_pos = self.mapFromGlobal(event.globalPosition().toPoint())
        click_pos = QPointF(local_pos.x(), local_pos.y())

        rect = self._get_canvas_rect()
        p_text = self._to_px(self.text_pos, rect)
        p_target = self._to_px(self.target_pos, rect)

        # Give priority to arrow target node
        if self.has_arrow:
            dist_target = math.hypot(click_pos.x() - p_target.x(), click_pos.y() - p_target.y())
            if dist_target < 15:
                self._dragged_node = "target"
                return

        dist_text = math.hypot(click_pos.x() - p_text.x(), click_pos.y() - p_text.y())
        if dist_text < 15:
            self._dragged_node = "text"
            return

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Updates the internal coordinates and emits signal while dragging nodes"""
        if not self._dragged_node:
            return

        local_pos = self.mapFromGlobal(event.globalPosition().toPoint())
        px = QPointF(local_pos.x(), local_pos.y())
        new_pos = self._to_pos(px)
        # Clamping to a 0.0-1.0 to not lose nodes outside canvas
        clamped_x = max(0.0, min(1.0, new_pos.x()))
        clamped_y = max(0.0, min(1.0, new_pos.y()))
        clamped_pos = QPointF(clamped_x, clamped_y)

        if self._dragged_node == "text":
            self.text_pos = clamped_pos
            self.textPositionChanged.emit(clamped_x, clamped_y)
        elif self._dragged_node == "target":
            self.target_pos = clamped_pos
            self.targetPositionChanged.emit(clamped_x, clamped_y)

        self.update()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Releases the currently grabbed node"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._dragged_node = None

    #####
    # Coordinate mapping and rendering
    ## Rendering paintEvent
    ####

    def _to_px(self, pos: QPointF, canvas_rect: Optional[QRectF] = None) -> QPointF:
        """Maps 0-1 Matplotlib space to pixel space"""
        rect = canvas_rect if canvas_rect is not None else self._get_canvas_rect()
        px_x = rect.x() + (pos.x() * rect.width())
        px_y = rect.y() + (rect.height() - (pos.y() * rect.height()))
        return QPointF(px_x, px_y)

    def _to_pos(self, px: QPointF, canvas_rect: Optional[QRectF] = None) -> QPointF:
        """Maps pixel space to 0-1 Matplotlib space"""
        rect = canvas_rect if canvas_rect is not None else self._get_canvas_rect()
        if rect.width() == 0 or rect.height() == 0:
            return QPointF(0, 0)

        x = (px.x() - rect.x()) / rect.width()
        y = (rect.bottom() - px.y()) / rect.height()
        return QPointF(x, y)

    def paintEvent(self, event: QPaintEvent) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self._get_canvas_rect()

        painter.fillRect(self.rect(), QColor(100, 100, 100, 15))
        painter.fillRect(rect, QColor(128, 128, 128, 40))

        border_pen = QPen(QColor(150, 150, 150), 1)
        painter.setPen(border_pen)
        painter.drawRect(rect)

        grid_pen = QPen(QColor(150, 150, 150, 80))
        grid_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(grid_pen)

        rx, ry = rect.x(), rect.y()
        rw, rh = rect.width(), rect.height()
        r_bottom, r_right = rect.bottom(), rect.right()

        for i in [1, 2, 3]:
            vx = rx * (rw * (i / 4.0))
            painter.drawLine(QPointF(vx, ry), QPointF(vx, r_bottom))
            vy = ry * (rh * (i / 4.0))
            painter.drawLine(QPointF(rx, vy), QPointF(r_right, vy))

        p_text = self._to_px(self.text_pos)

        if self.has_arrow:
            p_target = self._to_px(self.target_pos, rect)
            dx = p_target.x() - p_text.x()
            dy = p_target.y() - p_text.y()
            angle = math.atan2(dy, dx)

            line_color = QColor(150, 150, 150)
            if self.arrow_preset == "Aggressive Red Arrow":
                line_color = QColor(220, 50, 50, 200)
            elif self.arrow_preset == "Curved Highlight":
                line_color = QColor(50, 100, 220, 200)
            elif self.arrow_preset == "Straight Line":
                line_color = QColor(50, 50, 50, 200)

            painter.setPen(QPen(line_color, 2))

            if self.arrow_preset == "Curved Highlight":
                path = QPainterPath()
                path.moveTo(p_text)
                path.quadTo(p_text.x() + dx * 0.5, p_text.y(), p_target.x(), p_target.y())
                painter.drawPath(path)

                curve_dx = p_target.x() - (p_text.x() + dx * 0.5)
                curve_dy = p_target.y() - p_text.y()
                angle = math.atan2(curve_dy, curve_dx)
            else:
                painter.drawLine(p_text, p_target)

            if self.arrow_preset != "Straight Line":
                arrow_size = 10.0
                p1 = QPointF(p_target.x() - arrow_size * math.cos(angle - math.pi / 6),
                             p_target.y() - arrow_size * math.sin(angle - math.pi / 6))
                p2 = QPointF(p_target.x() - arrow_size * math.cos(angle + math.pi / 6),
                             p_target.y() - arrow_size * math.sin(angle + math.pi / 6))

                painter.setBrush(QBrush(line_color))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawPolygon(QPolygonF([p_target, p1, p2]))

            painter.setBrush(QBrush(QColor(255, 255, 255, 150)))
            painter.setPen(QPen(line_color, 1))
            painter.drawEllipse(p_target, 4, 4)

        painter.setBrush(QBrush(self.text_color))
        painter.setPen(QPen(QColor(255, 255, 255, 200), 1.5))
        painter.drawEllipse(p_text, 7, 7)

        t_color = Qt.GlobalColor.black if self.text_color.lightness() > 150 else Qt.GlobalColor.white
        painter.setPen(QPen(t_color))

        font = painter.font()
        font.setPixelSize(10)
        font.setBold(True)
        painter.setFont(font)

        text_rect = QRectF(p_text.x() - 7, p_text.y() - 7, 14, 14)
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignCenter, "T")
