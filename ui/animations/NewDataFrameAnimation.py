from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class NewDataFrameAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Created New DataFrame"):
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        header_color = QColor(60, 90, 120)
        body_color = QColor(245, 245, 255)
        grid_color = QColor(200, 200, 220)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 10)

        table_width = 60
        header_height = 12
        row_height = 10
        total_rows = 4
        total_height = header_height + (row_height * total_rows)

        start_x = -table_width / 2
        start_y = -total_height / 2 + 5

        header_progress = min(self.progress / 0.3, 1.0)

        current_width = table_width * header_progress
        header_rect = QRectF(start_x + (table_width - current_width)/2, start_y, current_width, header_height)

        if header_progress > 0:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(header_color)
            painter.drawRoundedRect(header_rect, 2, 2)
        
        if self.progress > 0.3:
            body_progress = min((self.progress - 0.3) / 0.3, 1.0)

            current_height = (total_height - header_height) * body_progress

            body_rect = QRectF(start_x, start_y + header_height, table_width, current_height)

            painter.setBrush(body_color)
            path_body = QPainterPath()
            path_body.addRect(body_rect)
            painter.drawPath(path_body)
        
        if self.progress > 0.6:
            grid_progress = (self.progress - 0.6) / 0.4

            painter.setPen(QPen(grid_color, 1))

            number_of_columns = 3
            column_width = table_width / number_of_columns

            for column in range(1, number_of_columns):
                x = start_x + (column * column_width)
                line_len = (total_height - header_height) * grid_progress

                p1 = QPointF(x, start_y + header_height)
                p2 = QPointF(x, start_y + header_height + line_len)
                painter.drawLine(p1, p2)
            
            for row in range(1, total_rows):
                y = start_y + header_height + (row * row_height)
                max_body_y = start_y + header_height + (total_height - header_height)

                if y <= max_body_y:
                    line_width = table_width * grid_progress

                    p1 = QPointF(start_x, y)
                    p2 = QPointF(start_x + line_width, y)
                    painter.drawLine(p1, p2)
            
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(grid_color, 2))

            visible_height = header_height + (total_height - header_height) * min((self.progress - 0.3) / 0.3, 1.0)
            if visible_height > header_height:
                painter.drawRect(QRectF(start_x, start_y, table_width, visible_height))