from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class FileImportAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Imported File"):
        super().__init__(parent)
        self.message = message
    
    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        folder_color = QColor(240, 190, 60)
        folder_dark = QColor(210, 160, 40)
        paper_color = QColor(245, 245, 255)

        pen = QPen(folder_dark)
        pen.setWidth(3)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 15)

        folder_width = 50
        folder_height = 35
        folder_bottom_y = folder_height / 2

        path_back = QPainterPath()
        path_back.moveTo(-folder_width/2, -folder_height/2)
        path_back.lineTo(-folder_width/2 + 20, -folder_height/2)
        path_back.lineTo(-folder_width/2 + 25, -folder_height/2 - 8)
        path_back.lineTo(folder_width/2, -folder_height/2 - 8)
        path_back.lineTo(folder_width/2, folder_height/2)
        path_back.lineTo(-folder_width/2, folder_height/2)
        path_back.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(folder_dark)
        painter.drawPath(path_back)

        painter.save()
        clip_height = 100 + folder_bottom_y
        painter.setClipRect(QRectF(-50, -100, 100, clip_height))

        #Animation for a file sliding up from the folder icon
        slide_progress = min(self.progress * 0.75, 1.0)

        paper_start_y = 10
        paper_end_y = -25
        paper_current_y = paper_start_y + (paper_end_y - paper_start_y) * slide_progress
        
        painter.translate(0, paper_current_y)

        paper_width, paper_height = 36, 46
        painter.setBrush(paper_color)
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.drawRect(QRectF(-paper_width/2, -paper_height/2, paper_width, paper_height))

        painter.setPen(QPen(QColor(200, 200, 200), 2))
        for i in range(3):
            y_line = -10 + (i * 8)
            painter.drawLine(int(-10), int(y_line), int(10), int(y_line))
        
        #Green arrow
        if slide_progress < 1.0:
            arrow_color = QColor(100, 220, 100)
            painter.setPen(QPen(arrow_color, 3, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            path_arrow = QPainterPath()
            path_arrow.moveTo(0, 5)
            path_arrow.lineTo(0, -5)
            path_arrow.lineTo(-4, -1)
            path_arrow.moveTo(0, -5)
            path_arrow.lineTo(4, -1)
            painter.drawPath(path_arrow)

        painter.restore()

        # Folder pocket
        path_front = QPainterPath()
        path_front.moveTo(-folder_width/2, -folder_height/2 + 10)
        path_front.lineTo(folder_width/2, -folder_height/2 + 10)
        path_front.lineTo(folder_width/2 - 5, folder_height/2)
        path_front.lineTo(-folder_width/2 + 5, folder_height/2)
        path_front.closeSubpath()

        painter.setPen(QPen(folder_dark, 2))
        painter.setBrush(folder_color)
        painter.drawPath(path_front)