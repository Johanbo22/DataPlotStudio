from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class ScriptLogExportAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Exported", operation_type="python"):
        super().__init__(parent)
        self.message = message
        self.operation_type = operation_type.lower()

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        color = QColor(100, 200, 255)
        pen = QPen(color)
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        # Draw the text
        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 10)

        file_w, file_h = 40, 50
        fold_size = 12

        file_path = QPainterPath()
        file_path.moveTo(-file_w/2, -file_h/2) 
        file_path.lineTo(file_w/2 - fold_size, -file_h/2)
        file_path.lineTo(file_w/2, -file_h/2 + fold_size)
        file_path.lineTo(file_w/2, file_h/2)
        file_path.lineTo(-file_w/2, file_h/2)
        file_path.closeSubpath()

        painter.setPen(pen)
        painter.setBrush(QColor(255, 255, 255, 20))
        painter.drawPath(file_path)

        fold_path = QPainterPath()
        fold_path.moveTo(file_w/2 - fold_size, -file_h/2)
        fold_path.lineTo(file_w/2 - fold_size, -file_h/2 + fold_size)
        fold_path.lineTo(file_w/2, -file_h/2 + fold_size)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(fold_path)
        
        # arrow
        arrow_progress = min(self.progress * 1.5, 1.0)

        start_y = -50
        end_y = -35
        current_y = start_y + (end_y - start_y) * arrow_progress

        alpha = int(min(arrow_progress * 3, 1.0) * 255)
        arrow_color = QColor(100, 255, 100)
        arrow_color.setAlpha(alpha)

        painter.setPen(QPen(arrow_color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(arrow_color)

        painter.save()
        painter.translate(0, current_y)

        arrow_path = QPainterPath()
        arrow_path.moveTo(0, 10)
        arrow_path.lineTo(-6, 0)
        arrow_path.lineTo(-2, 0)
        arrow_path.lineTo(-2, -12)
        arrow_path.lineTo(2, -12)
        arrow_path.lineTo(2, 0)
        arrow_path.lineTo(6, 0)
        arrow_path.closeSubpath()

        painter.drawPath(arrow_path)
        painter.restore()

        #draw based on operand type
        if "python" in self.operation_type:
            self.draw_python_logo(painter)
        elif "log" in self.operation_type:
            self.draw_log_content(painter)
    
    def draw_python_logo(self, painter):
        blue = QColor(55, 115, 165)
        yellow = QColor(255, 215, 65)

        painter.setPen(Qt.PenStyle.NoPen)

        painter.setBrush(blue)
        blue_snek = QPainterPath()
        blue_snek.moveTo(-5, -12)
        blue_snek.lineTo(5, -12)
        blue_snek.quadTo(12, -12, 12, -5)
        blue_snek.lineTo(12, 0)
        blue_snek.lineTo(4, 0)
        blue_snek.lineTo(4, -4) #the nek of snek
        blue_snek.lineTo(-4, -4)
        blue_snek.lineTo(-4, 5)
        blue_snek.quadTo(-4, 9, -9, 9)
        blue_snek.lineTo(-12, 9)
        blue_snek.quadTo(-12, 0, -5, -12)
        painter.drawPath(blue_snek)

        painter.setBrush(yellow)
        yellow_snek = QPainterPath()
        yellow_snek.moveTo(5, 12)
        yellow_snek.lineTo(-5, 12)
        yellow_snek.quadTo(-12, 12, -12, 5)
        yellow_snek.lineTo(-12, 0)
        yellow_snek.lineTo(-4, 0)
        yellow_snek.lineTo(-4, 4)
        yellow_snek.lineTo(4, 4)
        yellow_snek.lineTo(4, -5)
        yellow_snek.quadTo(4, -9, 9, -9)
        yellow_snek.lineTo(12, -9)
        yellow_snek.quadTo(12, 0, 5, 12)
        painter.drawPath(yellow_snek)

        #eyesss
        painter.setBrush(QColor(255, 255, 255))
        painter.drawEllipse(QPointF(-2, -8), 1.5, 1.5)
        painter.drawEllipse(QPointF(2, 8), 1.5, 1.5)
    
    def draw_log_content(self, painter):

        painter.setPen(QColor(200, 200, 200))
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawText(QRectF(-20, -20, 40, 20), Qt.AlignmentFlag.AlignCenter, "LOG")

        painter.setPen(QPen(QColor(150, 150, 150), 2))
        for y in [0, 8, 16]:
            path = QPainterPath()
            start_x = -12
            path.moveTo(start_x, y)
            path.cubicTo(start_x + 5, y - 3, start_x + 10, y + 3, start_x + 15, y)
            path.cubicTo(start_x+20, y-3, start_x+25, y+3, start_x+24, y)
            painter.drawPath(path)