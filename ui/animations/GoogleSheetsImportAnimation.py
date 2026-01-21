from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class GoogleSheetsImportAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Import Google Sheets"):
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        cloud_color = QColor(240, 245, 255)
        sheet_color = QColor(15, 157, 88)
        grid_color = QColor(255, 255, 255, 180)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 10)

        slide_progress = min(self.progress * 0.75, 1.0)

        #Sheets sliding
        sheet_start_y = -15
        sheet_end_y = 35

        current_y = sheet_start_y + (sheet_end_y - sheet_start_y) * slide_progress

        painter.save()
        painter.translate(0, current_y)

        #File
        file_width, file_height = 36, 48
        fold_size = 10

        path_file = QPainterPath()
        path_file.moveTo(-file_width/2, -file_height/2)
        path_file.lineTo(file_width/2 - fold_size, -file_height/2)
        path_file.lineTo(file_width/2, -file_height/2 + fold_size)
        path_file.lineTo(file_width/2, file_height/2)
        path_file.lineTo(-file_width/2, file_height/2)
        path_file.closeSubpath()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(sheet_color)
        painter.drawPath(path_file)

        #Corner
        path_fold = QPainterPath()
        path_fold.moveTo(file_width/2 - fold_size, -file_height/2)
        path_fold.lineTo(file_width/2 - fold_size, -file_height/2 + fold_size)
        path_fold.lineTo(file_width/2, -file_height/2 + fold_size)
        painter.setBrush(QColor(10, 120, 60))
        painter.drawPath(path_fold)

        #Gid
        painter.setPen(QPen(grid_color, 2))
        for i in range(1, 4):
            y = -file_height / 2 + (i * 10) + 5
            painter.drawLine(int(-file_width / 2 + 5), int(y), int(file_width/2 - 5), int(y))
        
        #Vertical lines
        line_start_y = -file_width / 2 + 15
        line_end_y = file_height / 2 -5
        painter.drawLine(int(-5), int(line_start_y), int(-5), int(line_end_y))

        painter.restore()

        #Cloud
        cloud = QPainterPath()
        cloud.setFillRule(Qt.FillRule.WindingFill)
        cloud.addRoundedRect(QRectF(-35, -25, 70, 30), 15, 15)
        cloud.addEllipse(QPointF(-20, -30), 18, 18)
        cloud.addEllipse(QPointF(5, -35), 22, 22)
        cloud.addEllipse(QPointF(25, -28), 16, 16)

        combined_cloud = cloud.simplified()

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(cloud_color)
        painter.drawPath(combined_cloud)