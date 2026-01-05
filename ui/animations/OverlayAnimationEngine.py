from PyQt6.QtCore import (
    Qt, QTimer, QRect, QEasingCurve, QPropertyAnimation, 
    QVariantAnimation, QAbstractAnimation, QPoint
)
from PyQt6.QtWidgets import QWidget, QApplication
from PyQt6.QtGui import QPainter, QColor, QPen

class OverlayAnimationEngine(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(220, 120)

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

        self.slide_animation = QPropertyAnimation(self, b"pos")
        self.slide_animation.setDuration(500)
        self.slide_animation.setEasingCurve(QEasingCurve.Type.OutCubic)

        self.hold_timer = QTimer(self)
        self.hold_timer.setSingleShot(True)
        self.hold_timer.timeout.connect(self.slide_out)

    def start(self, target_widget=None):
        if target_widget:
            target_screen = target_widget.window().screen()
        elif self.parent():
            target_screen = self.parent().screen()
        else:
            target_screen = QApplication.primaryScreen()
        
        screen_geometry = target_screen.availableGeometry()

        #positions
        final_x = screen_geometry.center().x() - self.width() // 2
        start_y = screen_geometry.top() - self.height()
        final_y = screen_geometry.top()

        self.move(final_x, start_y)
        self.setWindowOpacity(1.0)
        self.progress = 0.0
        self.show()

        self.slide_animation.stop()
        self.slide_animation.setStartValue(QPoint(final_x, start_y))
        self.slide_animation.setEndValue(QPoint(final_x, final_y))
        self.slide_animation.start()

        self.main_animation.start()

        total_time = self.main_animation.duration() + 1500
        self.hold_timer.start(total_time)

    def slide_out(self):
        current_position = self.pos()
        target_y = current_position.y() - self.height() - 100
        
        self.slide_animation.stop()
        self.slide_animation.setStartValue(current_position)
        self.slide_animation.setEndValue(QPoint(current_position.x(), target_y))
        self.slide_animation.finished.connect(self.close)
        self.slide_animation.start()
    
    def _update_progress(self, value):
        self.progress = value
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(QColor(30, 30, 40, 230))
        painter.setPen(Qt.PenStyle.NoPen)

        rect = self.rect().adjusted(5, 5, -5, -5)
        painter.drawRoundedRect(rect, 20, 20)

        painter.translate(self.width() / 2, self.height() / 2)

        painter.scale(0.6, 0.6)

        self.draw_content(painter)
    
    def draw_content(self, painter):
        pass