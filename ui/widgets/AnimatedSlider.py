from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QSlider


class AnimatedSlider(QSlider):
    """New qslider"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        if not isinstance(orientation, Qt.Orientation):
            parent = orientation
            orientation = Qt.Orientation.Horizontal

        super().__init__(orientation, parent)

        self._base_border_color = QColor("#a0a0a0")
        self._hover_border_color = QColor("#707070")
        self._focus_border_color = QColor("#0078d7")

        self._animated_color = self._base_border_color
        self._is_focussed = False

        self.animation = QPropertyAnimation(self, b"animated_border_color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_border_color)

    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        return self._animated_color

    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        self._animated_color = color
        self._update_stylesheet(color)

    def _update_stylesheet(self, color: QColor) -> None:
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid #c2c2c2;
                height: 4px;
                background: #f0f0f0;
                margin: 0px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 1.5px solid {color.name()};
                width: 16px;
                height: 16px;
                margin: -7px 0;
                border-radius: 9px;
            }}
            QSlider::groove:vertical {{
                border: 1px solid #c2c2c2;
                width: 4px;
                background: #f0f0f0;
                margin: 0 0px;
                border-radius: 2px;
            }}
            QSlider::handle:vertical {{
                background: white;
                border: 1.5px solid {color.name()};
                height: 16px;
                width: 16px;
                margin: 0 -7px;
                border-radius: 9px;
            }}
        """)

    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()

    def enterEvent(self, event) -> None:
        if not self._is_focussed and self.isEnabled():
            self._animate_to(self._hover_border_color)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._base_border_color)
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if self.underMouse():
            self._animate_to(self._hover_border_color)
        else:
            self._animate_to(self._base_border_color)
        super().focusOutEvent(event)