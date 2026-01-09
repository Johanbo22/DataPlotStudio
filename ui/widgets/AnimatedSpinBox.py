from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QSpinBox


class DataPlotStudioSpinBox(QSpinBox):
    """A QSpinBox with animated border color on hover/focus."""
    def __init__(self, parent=None):
        super().__init__(parent)

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
            QSpinBox {{
                border: 1.5px solid {color.name()};
                border-radius: 3px;
                padding: 1px 4px 1px 3px;
                min-width: 2em;
                background-color: white;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                border-width: 0px;
            }}
        """)

    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()

    def enterEvent(self, event) -> None:
        if not self._is_focussed:
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