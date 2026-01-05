import math
from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRect
from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class ResetToOriginalStateAnimation(OverlayAnimationEngine):

    def draw_content(self, painter):
        stroke_width = 8
        color = QColor(100, 255, 100)

        pen = QPen(color)
        pen.setWidth(stroke_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)

        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRect(-100, -90, 200, 40), Qt.AlignmentFlag.AlignCenter, "Reset to Original")

        max_angle = 320
        current_angle = self.progress * max_angle

        radius = 40
        start_angle = 90
        span_angle = self.progress * 300

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawArc(
            int(-radius), int(-radius),
            int(radius*2), int(radius*2),
            int(start_angle * 16),
            int(span_angle * 16)
        )

        if self.progress > 0.05:
            current_tip_angle = start_angle + span_angle
            current_tip_angle_radians = math.radians(current_tip_angle)

            tip_x = radius * math.cos(current_tip_angle_radians)
            tip_y = -radius * math.sin(current_tip_angle_radians)

            painter.save()
            painter.translate(tip_x, tip_y)

            tangent_angle = current_tip_angle + 90
            painter.rotate(-tangent_angle)
            painter.translate(10, 0)

            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(color)

            path = QPainterPath()
            path.moveTo(0, 0)
            path.lineTo(-12, 8)
            path.lineTo(-8, 0)
            path.lineTo(-12, -8)
            path.closeSubpath()

            painter.drawPath(path)
            painter.restore()