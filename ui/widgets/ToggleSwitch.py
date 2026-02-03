from PyQt6.QtCore import (
    Qt, 
    QSize, 
    QRectF, 
    QEasingCurve, 
    QPropertyAnimation,
    pyqtProperty
    )
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from PyQt6.QtWidgets import QCheckBox

from ui.theme import ThemeColors
from ui.widgets.mixins import HoverFocusAnimationMixin

class DataPlotStudioToggleSwitch(HoverFocusAnimationMixin, QCheckBox):
    """A toggle switch widget"""
    
    def __init__(self, parent=None):
        QCheckBox.__init__(self, parent)
        
        HoverFocusAnimationMixin.__init__(self)
        
        self._track_height = 22
        self._track_width = 40
        self._margin = 4
        self._spacing = 8
        
        self._handle_position = 1.0 if self.isChecked() else 0.0
        
        self._handle_animation = QPropertyAnimation(self, b"handle_position", self)
        self._handle_animation.setDuration(200)
        self._handle_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        
        self.toggled.connect(self._on_toggled)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
    
    @pyqtProperty(float)
    def handle_position(self) -> float:
        return self._handle_position
    
    @handle_position.setter
    def handle_position(self, pos: float) -> None:
        self._handle_position = pos
        self.update()
    
    def _on_toggled(self, checked: bool) -> None:
        start = self._handle_position
        end = 1.0 if checked else 0.0
        
        self._handle_animation.stop()
        self._handle_animation.setStartValue(start)
        self._handle_animation.setEndValue(end)
        self._handle_animation.start()
    
    def _update_stylesheet(self, color: QColor) -> None:
        self.update()
    
    def sizeHint(self) -> QSize:
        size = QSize(self._track_width, self._track_height)
        text = self.text()
        if text:
            font_metric = self.fontMetrics()
            width = self._track_width + self._spacing + font_metric.horizontalAdvance(text)
            height = max(self._track_height, font_metric.height())
            size = QSize(width, height)
        return size
    
    def hitButton(self, pos) -> bool:
        return self.contentsRect().contains(pos)

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        if not self.isEnabled():
            track_color = ThemeColors.BORDER_BASE
            handle_color = ThemeColors.BG_WHITE
            opacity = 0.5
            text_color = ThemeColors.TEXT_DISABLED
        else:
            opacity = 1.0
            handle_color = ThemeColors.BG_WHITE
            text_color = ThemeColors.TEXT_PRIMARY
            
            color_off = ThemeColors.BORDER_BASE
            color_on = ThemeColors.ACCENT_COLOR
            
            red = color_off.red() + (color_on.red() - color_off.red()) * self._handle_position
            green = color_off.green() + (color_off.green() - color_off.green()) * self._handle_position
            blue = color_off.blue() + (color_off.blue() - color_off.blue()) * self._handle_position
            track_color = QColor(int(red), int(green), int(blue))
            
        painter.setOpacity(opacity)
        
        # Calculation of geometry
        content_rect = self.contentsRect()
        
        y_offset = content_rect.top() + round((content_rect.height() - self._track_height) / 2)
        x_offset = content_rect.left()
        
        track_rect = QRectF(x_offset, y_offset, self._track_width, self._track_height)
        radius = self._track_height / 2
        
        # Draw main track
        painter.setBrush(QBrush(track_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(track_rect, radius, radius)
        
        if self.hasFocus():
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(self.animated_border_color, 2))
            painter.drawRoundedRect(track_rect.adjusted(1, 1, -1, -1), radius - 1, radius - 1)
        
        handle_diameter = self._track_height - (2 * self._margin)
        available_width = self._track_width - (2 * self._margin) - handle_diameter
        
        current_offset = available_width * self._handle_position
        
        handle_x = x_offset + self._margin + current_offset
        handle_y = y_offset + self._margin
        
        handle_rect = QRectF(handle_x, handle_y, handle_diameter, handle_diameter)
        
        painter.setBrush(QBrush(handle_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(handle_rect)
        
        if self.text():
            text_rect = QRectF(content_rect)
            text_start_x = x_offset + self._track_width + self._spacing
            text_rect.setLeft(text_start_x)
            
            painter.setPen(text_color)
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, self.text())
        
        painter.end()