import math
from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRect
from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class ResetToOriginalStateAnimation(OverlayAnimationEngine):

    def draw_content(self, painter):
        color = QColor(100, 255, 100)
        pen = QPen(color)
        pen.setWidth(8)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        painter.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(-100, -80, 200, 40), Qt.AlignmentFlag.AlignCenter, "Reset to Original")

        max_angle = 320
        current_angle = self.progress * max_angle

        radius = 40
        start_angle = 90 * 16
        span_angle = int(current_angle * 16)

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(-radius, -radius, -radius*2, radius*2, start_angle, span_angle)

        if self.progress > 0.05:
            painter.save()
            painter.rotate(-current_angle)

            painter.translate(0, -radius)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)

            path = QPainterPath()
            path.moveTo(0, 0)
            path.lineTo(-8, 12)
            path.lineTo(8, 12)
            path.closeSubpath()

            painter.rotate(180)
            painter.drawPath(path)

            painter.restore()