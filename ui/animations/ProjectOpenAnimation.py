import math
from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen, QBrush, QPolygonF
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
        hinge_y = height / 2

        path_back = QPainterPath()
        path_back.moveTo(-width/2, -height/2)
        path_back.lineTo(-width/2 + 20, -height/2)
        path_back.lineTo(-width/2 + 25, -height/2 - tab_height)
        path_back.lineTo(width/2, -height/2 - tab_height)
        path_back.lineTo(width/2, height/2)
        path_back.lineTo(-width/2, height/2)
        path_back.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(folder_outer)

        painter.drawPath(path_back)

        #papers
        slide_amount = 0
        if self.progress > 0.1:
            t = (self.progress - 0.1) / 0.9
            slide_amount = t * 12

        painter.save()
        painter.setClipRect(QRectF(-width, -height*2, width*2, height*2 + hinge_y - 2))

        painter.translate(0, -slide_amount)

        for i in range(2, -1, -1):
            offset = i * 2
            sheet_width = width - 10 -(i * 4)
            sheet_height = height - 5

            rect = QRectF(-sheet_width/2, -sheet_height/2 + 8 + offset, sheet_width, sheet_height)

            painter.setBrush(paper_color)
            painter.setPen(QPen(QColor(200, 200, 200), 1))
            painter.drawRect(rect)

            if i == 0:
                painter.setPen(QPen(QColor(210, 210, 210), 2))
                painter.drawLine(int(-10), int(rect.top() + 15), int(10), int(rect.top() + 15))
                painter.drawLine(int(-10), int(rect.top() + 25), int(10), int(rect.top() + 25))
        
        painter.restore()

        # adding tilt to folder 
        tilt_offset = self.progress * 15

        front_top_y = -height / 2 + tilt_offset

        #trapetz
        poly = QPolygonF([
            QPointF(-width/2, front_top_y),
            QPointF(width/2, front_top_y),
            QPointF(width/2, hinge_y),
            QPointF(-width/2, hinge_y)
        ])

        painter.setPen(QPen(QColor(210, 160, 40), 1))
        painter.setBrush(folder_inner)
        painter.drawPolygon(poly)

        if self.progress > 0.2:
            shadow_height = self.progress * 4
            shadow_rect = QRectF(-width/2, front_top_y, width, shadow_height)

            grad = QColor(0, 0, 0, 20)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRect(shadow_rect)