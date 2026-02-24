from typing import Optional

from PyQt6.QtCore import QRectF
from PyQt6.QtGui import QColor, QPainter, QPaintEvent, QPen
from PyQt6.QtWidgets import QSpinBox, QWidget
from ui.widgets.mixins import HoverFocusAnimationMixin


class DataPlotStudioSpinBox(HoverFocusAnimationMixin, QSpinBox):
    """A QSpinBox with animated border color on hover/focus."""
    
    _base_border_color: QColor
    _hover_border_color: QColor
    _focus_border_color: QColor
    _animated_color: QColor
    
    _BORDER_WIDTH: float = 1.5
    _BORDER_RADIUS: int = 3
    _PADDING_TOP: int = 1
    _PADDING_RIGHT: int = 4
    _PADDING_BOTTOM: int = 1
    _PADDING_LEFT: int = 3
    _MIN_WIDTH_EM: float = 2.0
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent=parent)

        self._current_border_color: QColor = self._base_border_color
        self._setup_static_stylesheet()

    def _setup_static_stylesheet(self) -> None:
        """
        Applies base styling during init
        """
        self.setStyleSheet(f"""
            QSpinBox {{
                border: none;
                border-radius: {self._BORDER_RADIUS}px;
                padding: {self._PADDING_TOP}px {self._PADDING_RIGHT}px {self._PADDING_BOTTOM}px {self._PADDING_LEFT}px;
                min-width: {self._MIN_WIDTH_EM}em;
                background-color: palette(base);
                color: palette(text);
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                border-width: 0px;
                background-color: palette(base);
                border-radius: 2px;
                margin: 1px;
            }}
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
                background-color: rgba(128, 128, 128, 0.15);
            }}
            QSpinBox::up-button:pressed, QSpinBox::down-button:pressed {{
                background-color: rgba(128, 128, 128, 0.3);
            }}
        """)
    
    def _update_stylesheet(self, color: QColor) -> None:
        """Applies new colors to stylesheet"""
        if not color.isValid():
            return
        self._current_border_color = color
        self.update()
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """Overrides the default paint event to render the spinbox"""
        # Render the native widget first
        super().paintEvent(event)
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        pen = QPen(self._current_border_color)
        pen.setWidthF(self._BORDER_WIDTH)
        painter.setPen(pen)
        
        offset: float = self._BORDER_WIDTH / 2.0
        rect: QRectF = QRectF(self.rect()).adjusted(offset, offset, -offset, -offset)
        
        painter.drawRoundedRect(rect, self._BORDER_RADIUS, self._BORDER_RADIUS)
        painter.end()