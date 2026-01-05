from PyQt6.QtCore import (
    Qt, QTimer, QRect, QEasingCurve, QPropertyAnimation, 
    QVariantAnimation, QAbstractAnimation
)
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen

class OverlayAnimationEngine(QWidget):
    def __init__(self, parent=None, size=300):
        super().__init__(parent)
        self.setFixedSize(size, size)

        # Setting the Window type and flags, wup
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.Tool |
            Qt.WindowType.WindowStaysOnTopHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)

        self.progress = 0.0

        # Main animation
        self.main_animation = QVariantAnimation()
        self.main_animation.setStartValue(0.0)
        self.main_animation.setEndValue(1.0)
        self.main_animation.setDuration(800)
        self.main_animation.valueChanged.connect(self._update_progress)

        self.pop_animation = QPropertyAnimation(self, b"geometry")
        self.pop_animation.setDuration(400)
        self.pop_animation.setEasingCurve(QEasingCurve.Type.OutElastic)

        self.fade_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_animation.setDuration(300)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.0)
        self.fade_animation.finished.connect(self.close)

        #Timer
        self.hold_timer = QTimer(self)
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.fade_animation.start)
    
    def start(self):
        screen = self.screen().availableGeometry()
        target_rect = QRect(
            screen.center().x() - self.width() // 2,
            screen.center().y() - self.height() // 2,
            self.width(),
            self.height()
        )

        self.setWindowOpacity(1.0)
        self.progress = 0.0
        self.show()

        start_rect = QRect(target_rect)
        start_rect.moveCenter(target_rect.center())
        start_rect.setSize(target_rect.size() * 0.5)

        self.pop_animation.setStartValue(start_rect)
        self.pop_animation.setEndValue(target_rect)
        self.pop_animation.start()

        self.main_animation.start()

        total_time = self.main_animation.duration() + 1000
        self.hold_timer.start(total_time)
    
    def _update_progress(self, value):
        self.progress = value
        self.update()
    
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(30, 30, 40, 220))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(self.rect(), 30 , 30)

        painter.translate(self.width() / 2, self.height() / 2)

        self.draw_content(painter)
    
    def draw_content(self, painter):
        pass