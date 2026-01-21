from PyQt6.QtGui import QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class DropColumnAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Dropping Column"):
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)
        
        header_color = QColor(60, 90, 120)
        grid_color   = QColor(200, 200, 220)
        normal_bg    = QColor(255, 255, 255)
        delete_bg    = QColor(255, 200, 200)
        delete_text  = QColor(200, 50, 50)
        
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)
        
        painter.translate(0, 10)

        table_w = 90
        header_h = 14
        row_h = 12
        cols = 3
        rows = 4
        col_w = table_w / cols
        
        start_x = -table_w / 2
        start_y = -25
        
        target_col = 1 
        
        
        drop_offset = 0.0
        opacity = 1.0
        slide_offset = 0.0
        
        if self.progress > 0.2:
            t = (self.progress - 0.2) / 0.8
            
            # Gravity Drop (t^2)
            drop_offset = t * t * 80 
            opacity = 1.0 - t
            
            slide_offset = t * col_w

        painter.setFont(QFont("Consolas", 8))
        
        for c in range(cols):
            current_x = start_x + (c * col_w)
            current_y_mod = 0.0
            
            if c == target_col:
                current_y_mod = drop_offset
                
            elif c > target_col:
                current_x -= slide_offset

            painter.save()
            if c == target_col and opacity < 1.0:
                painter.setOpacity(opacity)

            h_rect = QRectF(current_x, start_y + current_y_mod, col_w, header_h)
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(header_color if c != target_col else delete_text)
            painter.drawRect(h_rect)
            
            for r in range(rows):
                y = start_y + header_h + (r * row_h) + current_y_mod
                rect = QRectF(current_x, y, col_w, row_h)
                
                bg = normal_bg
                if c == target_col:
                    bg = delete_bg
                
                painter.setBrush(bg)
                painter.setPen(QPen(grid_color, 1))
                painter.drawRect(rect)
                
                painter.setPen(QPen(QColor(200, 200, 200), 2))
                if c == target_col:
                    painter.setPen(QPen(delete_text, 2))
                    
                painter.drawLine(int(current_x + 5), int(y + 6), int(current_x + col_w - 5), int(y + 6))

            painter.restore()
