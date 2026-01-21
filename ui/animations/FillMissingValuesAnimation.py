from PyQt6.QtGui import QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class FillMissingValuesAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Fill Missing Values", fill_value="0.0"):
        super().__init__(parent)
        self.message = message
        self.fill_value = fill_value

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)

        header_color = QColor(60, 90, 120)
        grid_color = QColor(200, 200, 220)
        normal_bg = QColor(255, 255, 255)

        missing_bg_start = QColor(255, 200, 80)
        missing_txt_start = QColor(180, 100, 0)

        filled_bg_end = QColor(220, 255, 220)
        filled_txt_end = QColor(50, 150, 50)

        painter.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)

        painter.translate(0, 10)

        table_w = 80
        header_h = 14
        row_h = 14
        cols = 3
        rows = 4
        col_w = table_w / cols
        
        start_x = -table_w / 2
        start_y = -25
        
        target_col_idx = 1
        missing_row_indices = [0, 2, 3]

        t_fill = 0.0
        if self.progress > 0.2:
            t_fill = (self.progress - 0.2) / 0.8

        r = missing_bg_start.red() + (filled_bg_end.red() - missing_bg_start.red()) * t_fill
        g = missing_bg_start.green() + (filled_bg_end.green() - missing_bg_start.green()) * t_fill
        b = missing_bg_start.blue() + (filled_bg_end.blue() - missing_bg_start.blue()) * t_fill
        current_fill_bg = QColor(int(r), int(g), int(b))

        nan_opacity = 1.0 - t_fill
        val_opacity = t_fill

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(header_color)
        painter.drawRoundedRect(QRectF(start_x, start_y, table_w, header_h), 2, 2)
        painter.setBrush(QColor(255, 255, 255, 50))
        painter.drawRect(QRectF(start_x + col_w, start_y, col_w, header_h))

        painter.setFont(QFont("Segoe UI", 8))
        
        for r in range(rows):
            y = start_y + header_h + (r * row_h)
            for c in range(cols):
                x = start_x + (c * col_w)
                rect = QRectF(x, y, col_w, row_h)
                
                is_target_cell = (c == target_col_idx and r in missing_row_indices)
                
                if is_target_cell:
                    painter.setBrush(current_fill_bg)
                else:
                    painter.setBrush(normal_bg)

                painter.setPen(QPen(grid_color, 1))
                painter.drawRect(rect)
                
                if is_target_cell:
                    painter.save()
                    if nan_opacity > 0.01:
                        painter.setOpacity(nan_opacity)
                        painter.setPen(missing_txt_start)
                        painter.setFont(QFont("Segoe UI", 8, QFont.Weight.Bold))
                        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, "NaN")
                    
                    if val_opacity > 0.01:
                        painter.setOpacity(val_opacity)
                        painter.setPen(filled_txt_end)
                        painter.setFont(QFont("Segoe UI", 8))
                        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, self.fill_value)
                    painter.restore()
                else:
                    painter.setPen(QPen(QColor(200, 200, 200), 2))
                    painter.drawLine(int(x + 5), int(y + 7), int(x + col_w - 5), int(y + 7))