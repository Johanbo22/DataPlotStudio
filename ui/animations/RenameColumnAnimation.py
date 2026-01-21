import math
from PyQt6.QtGui import QFont, QColor, QPen, QFontMetrics
from PyQt6.QtCore import Qt, QRectF

from ui.animations import OverlayAnimationEngine

class RenameColumnAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Renaming Column", old_name="col_2", new_name="Sales"):
        super().__init__(parent)
        self.message = message
        self.old_name = old_name
        self.new_name = new_name

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)
        
        header_bg_normal = QColor(60, 90, 120)
        header_bg_edit   = QColor(255, 255, 255)
        text_normal      = QColor(255, 255, 255)
        text_edit        = QColor(0, 0, 0)
        highlight_pen    = QPen(QColor(0, 120, 255), 2)
        cursor_color     = QColor(0, 0, 0)
        grid_color       = QColor(200, 200, 220)
        
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)
        
        painter.translate(0, 10)

        table_w = 160
        header_h = 24
        row_h = 16
        cols = 3
        rows = 3
        col_w = table_w / cols
        
        start_x = -table_w / 2
        start_y = -35
        
        target_col = 1 
        
        
        edit_mode_active = 0.1 < self.progress < 0.9
        
        current_text = ""
        if self.progress <= 0.1:
            current_text = self.old_name
        elif self.progress <= 0.4:
            t = (self.progress - 0.1) / 0.3
            chars_to_keep = int(len(self.old_name) * (1.0 - t))
            current_text = self.old_name[:chars_to_keep]
        elif self.progress <= 0.9:
            t = (self.progress - 0.4) / 0.5
            chars_to_show = int(len(self.new_name) * t)
            current_text = self.new_name[:chars_to_show]
        else:
            current_text = self.new_name

        
        edit_font = QFont("Consolas", 9)
        painter.setFont(edit_font)

        for c in range(cols):
            cx = start_x + (c * col_w)
            
            h_rect = QRectF(cx, start_y, col_w, header_h)
            
            if c == target_col:
                if edit_mode_active:
                    painter.setBrush(header_bg_edit)
                    painter.setPen(highlight_pen)
                    painter.drawRect(h_rect)
                    
                    painter.setPen(text_edit)
                    text_rect = h_rect.adjusted(8, 0, -4, 0) 
                    painter.drawText(text_rect, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter, current_text)
                    
                    if math.sin(self.progress * 30) > 0:
                        fm = QFontMetrics(edit_font)
                        text_width = fm.horizontalAdvance(current_text)
                        cursor_x = text_rect.left() + text_width + 1
                        
                        painter.setPen(QPen(cursor_color, 1))
                        painter.drawLine(int(cursor_x), int(h_rect.top()+5), int(cursor_x), int(h_rect.bottom()-5))
                        
                else:
                    painter.setBrush(header_bg_normal)
                    painter.setPen(Qt.PenStyle.NoPen)
                    painter.drawRect(h_rect)
                    painter.setPen(text_normal)
                    painter.drawText(h_rect, Qt.AlignmentFlag.AlignCenter, current_text)
            else:
                painter.setBrush(header_bg_normal)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRect(h_rect)
                painter.setPen(text_normal)
                label = "ID" if c == 0 else "Value"
                painter.drawText(h_rect, Qt.AlignmentFlag.AlignCenter, label)
                
            painter.setPen(QPen(grid_color, 1))
            painter.setBrush(QColor(255, 255, 255))
            for r in range(rows):
                ry = start_y + header_h + (r * row_h)
                r_rect = QRectF(cx, ry, col_w, row_h)
                painter.drawRect(r_rect)
                
                painter.setPen(QPen(QColor(220, 220, 220), 2))
                painter.drawLine(int(cx + 5), int(ry + row_h/2), int(cx + col_w - 10), int(ry + row_h/2))
                painter.setPen(QPen(grid_color, 1))