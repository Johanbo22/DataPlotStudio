from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QListWidget


class DataPlotStudioListWidget(QListWidget):
    """New lsitwidget styling"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self._base_border_color = QColor("#c2c2c2")
        self._hover_border_color = QColor("#0078d7")
        self._animated_color = self._base_border_color

        self.enter_animation = QPropertyAnimation(self, b"animated_border_color")
        self.enter_animation.setDuration(150)
        self.enter_animation.setEndValue(self._hover_border_color)
        self.enter_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.leave_animation = QPropertyAnimation(self, b"animated_border_color")
        self.leave_animation.setDuration(150)
        self.leave_animation.setEndValue(self._base_border_color)
        self.leave_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

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
            QListWidget {{
                border: 1.5px solid {color.name()}; 
                border-radius: 4px;
                padding: 4px;
                background-color: #ffffff; 
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 3px;
                margin: 2px 0; 
            }}
            QListWidget::item:hover {{
                background-color: #f0f0f0; 
            }}
            QListWidget::item:selected {{
                background-color: #0078d7; 
                color: #ffffff; 
            }}
            QListWidget::item:selected:hover {{
                background-color: #005fa3; 
            }}
        """)

    def enterEvent(self, event) -> None:
        if self.isEnabled():
            self.leave_animation.stop()
            self.enter_animation.setStartValue(self.animated_border_color)
            self.enter_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self.enter_animation.stop()
        self.leave_animation.setStartValue(self.animated_border_color)
        self.leave_animation.start()
        super().leaveEvent(event)