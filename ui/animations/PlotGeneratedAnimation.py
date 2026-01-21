from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QPointF
from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class PlotGeneratedAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Plot Generated"):
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter):
        painter.scale(1.3, 1.3)
        axis_color = QColor(200, 200, 200)
        dot_color = QColor(255, 255, 255)
        line_color = QColor(100, 255, 100)

        #text
        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 5)
        
        #animation should be
        """
        first 3 frames: draw axes
        second 3 frames: places points
        last 4 frames: draw line 
        """

        origin_x, origin_y = -30.0, 20.0
        width, height = 60.0, 40.0

        #3 poonts
        p1 = QPointF(origin_x + 10, origin_y - 10)
        p2 = QPointF(origin_x + 30, origin_y - 35)
        p3 = QPointF(origin_x + 50, origin_y - 20)

        points = [p1, p2, p3]

        if self.progress > 0:
            axes_progress = min(self.progress / 0.3, 1.0)

            painter.setPen(QPen(axis_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))

            axes_path = QPainterPath()

            y_len = height * axes_progress
            axes_path.moveTo(origin_x, origin_y)
            axes_path.lineTo(origin_x, origin_y - y_len)

            x_len = width * axes_progress
            axes_path.moveTo(origin_x, origin_y)
            axes_path.lineTo(origin_x + x_len, origin_y)

            painter.drawPath(axes_path)
        
        if self.progress > 0.3:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(dot_color)

            dots_start = 0.3

            for i, point in enumerate(points):
                my_start = dots_start + (i * 0.1)

                if self.progress > my_start:
                    my_progress = min((self.progress - my_start) / 0.15, 1.0)

                    if my_progress < 0.8:
                        scale = my_progress * 1.5
                    else:
                        scale = 1.2 - (my_progress - 0.8)
                    
                    r = 3.0 * scale
                    painter.drawEllipse(point, r, r)
        
        if self.progress > 0.6:
            painter.setPen(QPen(line_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.setBrush(Qt.BrushStyle.NoBrush)

            path = QPainterPath()
            path.moveTo(p1)

            if self.progress > 0.6:
                t1 = min((self.progress - 0.6) / 0.2, 1.0)

                current_x = p1.x() + (p2.x() - p1.x()) * t1
                current_y = p1.y() + (p2.y() - p1.y()) * t1
                path.lineTo(current_x, current_y)
            
            if self.progress > 0.8:
                t2 = min((self.progress - 0.8) / 0.2, 1.0)
                
                current_x = p2.x() + (p3.x() - p2.x()) * t2
                current_y = p2.y() + (p3.y() - p2.y()) * t2
                path.lineTo(current_x, current_y)

            painter.drawPath(path)