from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class PlotClearedAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Plot Cleared"):
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter):
        painter.scale(1.3, 1.3)

        axis_color = QColor(200, 200, 200)
        dot_color = QColor(255, 255, 255)
        line_color = QColor(100, 255, 100)

        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 5)

        origin_x, origin_y = -30.0, 20.0
        width, height = 60.0, 40.0
        p1 = QPointF(origin_x + 10, origin_y - 10)
        p2 = QPointF(origin_x + 30, origin_y - 35)
        p3 = QPointF(origin_x + 50, origin_y - 20)

        #wiper
        wiper_start = -40
        wiper_end = 40
        wiper_pos = wiper_start + (wiper_end - wiper_start) * self.progress

        clip_rect = QRectF(wiper_pos, -50, 100, 100)

        painter.save()
        painter.setClipRect(clip_rect)

        #draw axes
        painter.setPen(QPen(axis_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        path = QPainterPath()
        path.moveTo(origin_x, origin_y - height)
        path.lineTo(origin_x, origin_y)
        path.lineTo(origin_x + width, origin_y)
        painter.drawPath(path)

        painter.setPen(QPen(line_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        path = QPainterPath()
        path.moveTo(p1)
        path.lineTo(p2)
        path.lineTo(p3)
        painter.drawPath(path)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(dot_color)
        r = 3.0
        for point in [p1, p2, p3]:
            painter.drawEllipse(point, r, r)

        painter.restore()

        if self.progress < 1.0:
            painter.setPen(Qt.PenStyle.NoPen)

            gradient = QLinearGradient(wiper_pos, 0, wiper_pos - 10, 0)
            gradient.setColorAt(0, QColor(255, 255, 255, 100))
            gradient.setColorAt(1, QColor(255, 255, 255, 0))

            painter.setBrush(gradient)
            painter.drawRect(QRectF(wiper_pos - 10, -30, 10, 60))