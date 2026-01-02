from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QMenu


class AnimatedMenu(QMenu):
    """Custom QMenu"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._animation_duration = 150

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(self._animation_duration)
        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(2)
        shadow.setColor(QColor(0, 0, 0, 40))

        self.setGraphicsEffect(shadow)

    def showEvent(self, event):
        self.setWindowOpacity(0.0)
        super().showEvent(event)

        self.animation.start()

    def hideEvent(self, event):
        super().hideEvent(event)

        self.setWindowOpacity(1.0)