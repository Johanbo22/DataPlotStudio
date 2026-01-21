from PyQt6.QtGui import QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class RemoveRowAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Removed Rows"):
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        header_color = QColor(60, 90, 120)
        row_color = QColor(255, 255, 255)
        delete_color = QColor(255, 80, 80)
        grid_color = QColor(200, 200, 220)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 10)

        table_width = 70
        header_height = 12
        std_row_height = 10
        start_x = -table_width / 2
        start_y = -25

        # Deleteing row 1 and sliding other rows up
        target_index = 1

        # Frame 0.0 to 0.2: make row red
        # Frame 0.2 to 0.8: shrink row height

        target_row_height = std_row_height
        target_row_color = row_color

        if self.progress < 0.2:
            ratio = self.progress / 0.2
            red = 255
            green = int(255 * (1 - ratio) + 80 * ratio)
            blue = int(255 * (1 - ratio) + 80 * ratio)
            target_row_color = QColor(red, green, blue)
        else:
            target_row_color = delete_color

            shrink_progress = min((self.progress - 0.2) / 0.6, 1.0)
            target_row_height = std_row_height * (1.0 - shrink_progress)
        
        # dreaw
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(header_color)
        painter.drawRoundedRect(QRectF(start_x, start_y, table_width, header_height), 2, 2)

        current_y = start_y + header_height

        painter.setPen(QPen(grid_color, 1))

        for i in range(4):
            height = std_row_height
            color = row_color

            if i == target_index:
                height = target_row_height
                color = target_row_color
            
            if height > 0.5:
                rect = QRectF(start_x, current_y, table_width, height)

                painter.setBrush(color)
                painter.drawRect(rect)

                painter.setPen(QPen(QColor(200, 200, 200), 2))

                if height > 4:
                    mid_y = current_y + height / 2
                    painter.drawLine(int(start_x + 5), int(mid_y), int(start_x + 20), int(mid_y))
                    painter.drawLine(int(start_x + 30), int(mid_y), int(start_x + 60), int(mid_y))
                
                painter.setPen(QPen(grid_color, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(rect)
            
            current_y += height
        
        if self.progress > 0.1 and target_row_height > 2:
            row1_center_y = start_y + header_height + std_row_height + target_row_height
            icon_x = start_x + table_width + 10

            painter.setPen(QPen(delete_color, 2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(QRectF(icon_x, row1_center_y - 4, 8, 8)) 
            painter.drawLine(int(icon_x - 1), int(row1_center_y - 6), int(icon_x + 9), int(row1_center_y - 6))