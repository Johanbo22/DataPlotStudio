import math
from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class DropMissingValueAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Dropped Missing Values"):
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        header_color = QColor(60, 90, 120)
        grid_color = QColor(200, 200, 200)
        missing_bg = QColor(255, 200, 80)
        missing_text_c = QColor(180, 100, 0)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 10)

        #geometry
        table_width = 80
        header_height = 12
        row_height = 12
        cols = 3
        rows = 3
        col_width = table_width / cols

        start_x = -table_width / 2
        start_y = -20

        #must target middle cell (i1,i1)
        target_row, target_col = 1, 1

        #first 0.2 frames: pause and highligh
        #frame 0.2 ->< 0.8: cell removed and falls down
        drop_progress = 0
        if self.progress > 0.2:
            t = (self.progress - 0.2) / 0.8
            drop_progress = t * t * 60 # moves 60 pixels down
        
        opacity = 1.0
        if self.progress > 0.6:
            opacity = 1.0 - ((self.progress - 0.6) / 0.4)
        
        # drawning
        #table hed
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(header_color)
        painter.drawRoundedRect(QRectF(start_x, start_y, table_width, header_height), 2, 2)

        #cells and gridlines
        painter.setFont(QFont("Consolas", 7))
        for row in range(rows):
            y = start_y + header_height + (row * row_height)
            for column in range(cols):
                x = start_x + (column * col_width)
                rect = QRectF(x, y, col_width, row_height)

                #Borders
                painter.setPen(QPen(grid_color, 1))
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRect(rect)

                #Target missing val
                if row == target_row and column == target_col:
                    continue
                else:
                    painter.setPen(QPen(QColor(200, 200, 200), 2))
                    painter.drawLine(int(x + 5), int(y + 6), int(x + 20), int(y + 6))
        
        #Draw dropped cell
        cell_x = start_x + (target_col * col_width)
        cell_y = start_y + header_height + (target_row * row_height) + drop_progress

        cell_rect = QRectF(cell_x, cell_y, col_width, row_height)

        painter.save()
        
        if drop_progress > 0:
            center = cell_rect.center()
            painter.translate(center)
            painter.rotate(drop_progress * 2)
            painter.translate(-center)
        
        if opacity < 1.0:
            painter.setOpacity(opacity)
        
        #background
        painter.setPen(QPen(missing_text_c, 1))
        painter.setBrush(missing_bg)
        painter.drawRect(cell_rect)

        #Text NANA
        painter.setPen(missing_text_c)
        painter.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        painter.drawText(cell_rect, Qt.AlignmentFlag.AlignCenter, "NaN")

        painter.restore()