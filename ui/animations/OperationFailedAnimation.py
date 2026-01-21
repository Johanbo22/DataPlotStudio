from PyQt6.QtGui import QFont, QColor, QPen
from PyQt6.QtCore import (
    Qt, QRectF
)
from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class FailedAnimation(OverlayAnimationEngine):
    def __init__(self, message, parent=None):
        super().__init__(parent)
        self.message = message
    
    def draw_content(self, painter):
        color = QColor(255, 80, 80)
        pen = QPen(color)
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))

        painter.drawText(QRectF(-100, -90, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 15)

        radius = 45

        circle_scale = min(self.progress * 2.5, 1.0)
        if circle_scale > 0:
            painter.setPen(QPen(color, 4))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            r = radius * circle_scale
            painter.drawEllipse(int(-r), int(-r), int(r*2), int(r*2))

        painter.setPen(pen)
        p1_start, p1_end = (-20, -20), (20, 20)
        p2_start, p2_end = (20, -20), (-20, 20)

        #lines
        if self.progress > 0.4:
            s1 = min((self.progress - 0.4) / 0.3, 1.0)
            x = p1_start[0] + (p1_end[0] - p1_start[0]) * s1
            y = p1_start[1] + (p1_end[1] - p1_start[1]) * s1
            painter.drawLine(int(p1_start[0]), int(p1_start[1]), int(x), int(y))
        
        if self.progress > 0.7:
            s2 = (self.progress - 0.7) / 0.3
            x = p2_start[0] + (p2_end[0] - p2_start[0]) * s2
            y = p2_start[1] + (p2_end[1] - p2_start[1]) * s2
            painter.drawLine(int(p2_start[0]), int(p2_start[1]), int(x), int(y))