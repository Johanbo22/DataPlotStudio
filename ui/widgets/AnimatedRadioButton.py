from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QRadioButton


class AnimatedRadioButton(QRadioButton):
    """A QRadioButton with animated border color on hover/focus."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._base_border_color = QColor("#777")
        self._hover_border_color = QColor("#0078d7") # Blue from css
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
        # This style is based on your style.css

        # Use animated color for unchecked, focus color for checked
        border_color_name = self._focus_border_color.name() if self.isChecked() else color.name()

        self.setStyleSheet(f"""
            QRadioButton {{
                spacing: 5px;
                font-size: 11pt;
                color: #333;
            }}
            QRadioButton::indicator {{
                width: 13px;
                height: 13px;
                border: 1.5px solid {border_color_name};
                border-radius: 7px; /* Makes it a circle */
                background-color: #fcfcfc;
            }}
            QRadioButton::indicator:checked {{
                background-color: #fcfcfc;
                border: 1.5px solid {self._focus_border_color.name()};
            }}
            QRadioButton::indicator:checked::after {{
                content: '';
                display: block;
                width: 9px;
                height: 9px;
                border-radius: 4.5px;
                background-color: {self._focus_border_color.name()};
                margin: 2px; /* Centers the dot */
            }}
            QRadioButton::indicator:disabled {{
                background-color: #e0e0e0;
                border: 1px solid #b0b0b0;
            }}
            QRadioButton:disabled {{
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

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self._update_stylesheet(self._animated_color)

    def update(self) -> None:
        super().update()
        self._update_stylesheet(self._animated_color)