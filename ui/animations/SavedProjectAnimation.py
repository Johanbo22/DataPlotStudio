from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import (
    Qt, QRect
)
from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class SavedProjectAnimation(OverlayAnimationEngine):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.message = message
    def draw_content(self, painter):

        color = QColor(100, 255, 100)
        pen = QPen(color)
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(-100, -90, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        radius = 45
        circle_scale = min(self.progress * 2, 1.0)

        if circle_scale > 0:
            painter.setPen(QPen(color, 4))
            painter.setBrush(Qt.BrushStyle.NoBrush)

            r = radius * circle_scale
            painter.drawEllipse(int(-r), int(-r), int(r*2), int(r*2))

        if self.progress > 0.4:
            check_progress = (self.progress - 0.4) / 0.6

            p1 = (-20, 5)
            p2 = (-5, 20)
            p3 = (25, -15)

            path = QPainterPath()
            path.moveTo(*p1)

            if check_progress < 0.4:
                t = check_progress / 0.4
                x = p1[0] + (p2[0] - p1[0]) * t
                y = p1[1] + (p2[1] - p1[1]) * t
                path.lineTo(x, y)
            else:
                path.lineTo(*p2)

                t = (check_progress - 0.4) / 0.6
                x = p2[0] + (p3[0] - p2[0]) * t
                y = p2[1] + (p3[1] - p2[1]) * t
                path.lineTo(x, y)
            
            pen.setWidth(8)
            painter.setPen(pen)
            painter.drawPath(path)