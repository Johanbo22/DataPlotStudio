from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QRadioButton


class DataPlotStudioRadioButton(QRadioButton):
    """A QRadioButton with animated border color on hover/focus."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._base_border_color = QColor("#777")
        self._hover_border_color = QColor("#0078d7")
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

        # Use animated color for unchecked, focus color for checked
        border_color_name = self._focus_border_color.name() if self.isChecked() else color.name()

        dot_color = self._focus_border_color.name()
        bg_color = "#fcfcfc"
        checked_background = (
            f"qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, "
            f"stop:0 {dot_color}, stop:0.6 {dot_color}, "
            f"stop:0.7 {bg_color}, stop:1 {bg_color})"
        )

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
                border-radius: 7px; 
                background-color: {bg_color};
            }}
            QRadioButton::indicator:checked {{
                background-color: {checked_background};
                border: 1.5px solid {self._focus_border_color.name()};
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