import math
from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen, QPolygonF
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class ExportFileAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Export Completed", extension="CSV"):
        super().__init__(parent)
        self.message = message
        self.extension = extension[:4].upper()

    def draw_content(self, painter):
        color = QColor(100, 200, 255)
        pen = QPen(color)
        pen.setWidth(4)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)

        painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -90, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 15)

        file_width, file_height = 50, 60
        fold_size = 12

        file_path = QPainterPath()
        
        # top left
        file_path.moveTo(-file_width / 2, -file_height / 2)
        # Create a line to top-right
        file_path.lineTo(file_width / 2 - fold_size, -file_height / 2)
        # Create a fold?
        file_path.lineTo(file_width / 2, -file_height / 2 + fold_size)
        # Create a line to bototm-right
        file_path.lineTo(file_width / 2, file_height / 2)
        #Line to bottom left
        file_path.lineTo(-file_width / 2, file_height / 2)
        file_path.closeSubpath()

        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(file_path)

        fold_path = QPainterPath()
        fold_path.moveTo(file_width / 2 - fold_size, -file_height / 2)
        fold_path.lineTo(file_width/2 - fold_size, -file_height/2 + fold_size)
        fold_path.lineTo(file_width/2, -file_height/2 + fold_size)
        painter.drawPath(fold_path)

        #Draw the extension on the file
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        painter.setPen(color)
        painter.drawText(QRectF(-file_width/2, 5, file_width, 20), Qt.AlignmentFlag.AlignCenter, self.extension)

        #Arrow
        arrow_progress = min(self.progress * 1.5, 1.0)

        start_y = -45
        end_y = -5
        current_y = start_y + (end_y - start_y) * arrow_progress

        arrow_color = QColor(color)
        alpha = int(min(arrow_progress * 2, 1.0) * 255)
        arrow_color.setAlpha(alpha)

        painter.setPen(QPen(arrow_color, 4, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap, Qt.PenJoinStyle.RoundJoin))
        painter.setBrush(arrow_color)

        painter.save()
        painter.translate(0, current_y)

        arrow_path = QPainterPath()
        arrow_path.moveTo(0, 10)
        arrow_path.lineTo(-6, 2)
        arrow_path.lineTo(-2, 2)
        arrow_path.lineTo(-2, -10)
        arrow_path.lineTo(2, -10)
        arrow_path.lineTo(2, 2)
        arrow_path.lineTo(6, 2)
        arrow_path.closeSubpath()

        painter.drawPath(arrow_path)
        painter.restore()
