import math
from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class ProjectOpenAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Project Opened"):
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        folder_outer = QColor(240, 190, 60)
        folder_inner = QColor(220, 170, 40)
        paper_color = QColor(250, 250, 255)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 10)

        width, height = 60, 40
        tab_height = 8

        path_back = QPainterPath()
        path_back.moveTo(-width/2, -height/2)
        path_back.lineTo(-width/2 + 20, -height/2)
        path_back.lineTo(-width/2 + 25, -height/2 - tab_height)
        path_back.lineTo(width/2, -height/2 - tab_height)
        path_back.lineTo(width/2, height/2)
        path_back.lineTo(-width/2, height/2)
        path_back.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(folder_inner)

        painter.drawPath(path_back)

        #papers
        paper_slide = 0
        if self.progress > 0.3:
            slide_t = (self.progress - 0.3) / 0.7
            paper_slide = slide_t * 8
        
        painter.save()
        painter.setClipRect(QRectF(-50, -100, 100, 100 + height / 2))

        #draw papers
        for i in range(2, -1, -1):
            offset_y = (i * 3) - paper_slide
            scale_x = 1.0 - (i * 0.05)

            paper_width = (width - 10) * scale_x
            paper_height = height - 5

            rect = QRectF(-paper_width/2, -height/2 + 10 + offset_y, paper_width, paper_height)

            painter.setBrush(paper_color)
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.drawRect(rect)

            if i == 0:
                painter.setPen(QPen(QColor(200, 200, 200), 2))
                painter.drawLine(int(-10), int(rect.center().y() - 5), int(10), int(rect.center().y() - 5))
                painter.drawLine(int(-10), int(rect.center().y() + 5), int(10), int(rect.center().y() + 5))
        
        painter.restore()

        #front of fold
        hinge_y = height / 2

        painter.setPen(Qt.PenStyle.NoPen)

        if self.progress < 0.4:
            open_t = self.progress / 0.4
            current_height = height * (1.0 - open_t)

            rect = QRectF(-width/2, hinge_y - current_height, width, current_height)
            painter.setBrush(folder_outer)
            painter.drawRect(rect)

            if current_height > 10:
                label_rect = QRectF(-15, hinge_y - current_height/2 - 5, 30, 10)
                painter.setBrush(QColor(255, 255, 255, 200))
                painter.drawRect(label_rect)
        
        else:
            open_t = (self.progress - 0.4) / 0.6
            current_height = (height * 0.35) * open_t

            rect = QRectF(-width/2, hinge_y, width, current_height)

            painter.setBrush(folder_inner)
            painter.drawRect(rect)