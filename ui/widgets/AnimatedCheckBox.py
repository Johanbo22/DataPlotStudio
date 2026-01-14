from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QCheckBox


class DataPlotStudioCheckBox(QCheckBox):
    """A QCheckBox with animated border color on hover/focus."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._base_border_color = QColor("#a0a0a0")
        self._hover_border_color = QColor("#707070")
        self._focus_border_color = QColor("#0078d7") # Blue from css
        self._check_color = self._focus_border_color

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
        icon = "icons/ui_styling/checkmark.svg"
        self.setStyleSheet(f"""
            QCheckBox {{
                spacing: 5px;
                font-size: 11pt;
                color: #333;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1.5px solid {color.name()};
                border-radius: 3px;
                background-color: #fcfcfc;
            }}
            QCheckBox::indicator:checked {{
                border-color: {self._focus_border_color.name()};
                background-color: {self._focus_border_color.name()};
                image: url({icon}); 
            }}
            QCheckBox::indicator:disabled {{
                background-color: #e0e0e0;
                border: 1px solid #b0b0b0;
            }}
            QCheckBox:disabled {{
                color: #a0a0a0;
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