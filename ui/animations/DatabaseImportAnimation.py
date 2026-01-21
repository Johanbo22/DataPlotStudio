from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class DatabaseImportAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Import from Database", db_type="SQL"):
        super().__init__(parent)

        self.message = message
        self.db_type = db_type[:8].upper()

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        db_base_color = QColor(70, 100, 140)
        db_top_color = QColor(90, 120, 160)
        highlight_color = QColor(255, 255, 255, 40)
        data_color = QColor(245, 245, 255)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 10)

        slide_progress = min(self.progress * 0.75, 1.0)

        data_start_y = -10
        data_end_y = 40

        current_data_y = data_start_y + (data_end_y - data_start_y) * slide_progress

        painter.save()
        painter.translate(0, current_data_y)

        sheet_width, sheet_height = 32, 40
        painter.setPen(QPen(QColor(200, 200, 200), 1))
        painter.setBrush(data_color)
        painter.drawRect(QRectF(-sheet_width/2, -sheet_height/2, sheet_width, sheet_height))

        painter.setPen(QPen(QColor(200, 200, 200), 2))
        for i in range(3):
            y = -10 + (i * 10)
            painter.drawLine(int(-10), int(y), int(10), int(y))
        
        painter.drawLine(0, -15, 0, 15)

        painter.restore()

        db_width = 50
        db_height = 45
        disk_height = 12

        painter.setPen(Qt.PenStyle.NoPen)

        # Main database cylinder
        body_rect = QRectF(-db_width/2, -db_height/2 + disk_height/2, db_width, db_height - disk_height)
        painter.setBrush(db_base_color)
        painter.drawRect(body_rect)

        #layers
        painter.setBrush(db_base_color)
        painter.drawEllipse(QRectF(-db_width/2, db_height/2 - disk_height, db_width, disk_height))
        
        layer_spacing = (db_height - disk_height) / 2

        painter.setBrush(QColor(50, 80, 120))
        painter.drawEllipse(QRectF(-db_width/2, -5, db_width, disk_height))

        painter.drawEllipse(QRectF(-db_width/2, -5 - layer_spacing, db_width, disk_height))

        painter.setBrush(db_base_color)
        painter.drawRect(QRectF(-db_width/2, -5, db_width, 5))
        painter.drawRect(QRectF(-db_width/2, -5 - layer_spacing, db_width, 5))

        painter.setBrush(db_top_color)
        painter.drawEllipse(QRectF(-db_width/2, -db_height/2, db_width, disk_height))

        #text
        painter.setPen(QColor(255, 255, 255))
        font_size = 9 if len(self.db_type) > 4 else 11
        painter.setFont(QFont("Consolas", font_size, QFont.Weight.Bold))

        painter.drawText(QRectF(-db_width/2, -5, db_width, 20), Qt.AlignmentFlag.AlignCenter, self.db_type)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(highlight_color)
        shine_path = QPainterPath()
        shine_path.addEllipse(QRectF(-db_width/2 + 5, -db_height/2 + 2, 20, 6))
        painter.drawPath(shine_path)