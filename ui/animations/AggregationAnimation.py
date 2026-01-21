from PyQt6.QtGui import QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF

from ui.animations import OverlayAnimationEngine

class AggregationAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Grouping by Region"):
        super().__init__(parent)
        self.message = str(message)

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)
        
        header_color = QColor(60, 90, 120)
        row_bg_a     = QColor(240, 245, 255)
        row_bg_b     = QColor(255, 245, 240) 
        border_pen   = QPen(QColor(200, 200, 220), 1)
        text_color   = QColor(50, 50, 50)
        
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        
        fm = painter.fontMetrics()
        msg_w = fm.horizontalAdvance(self.message)
        painter.drawText(int(-msg_w / 2), -60, self.message)
        
        painter.translate(0, 10)

        table_w = 160  
        row_h = 24     
        col_w = table_w / 2
        
        start_x = -table_w / 2
        start_y = -30 
        
        
        rows_data = [
            {"label": "East", "val_start": 10, "val_end": 30, "color": row_bg_a, "start_idx": 0, "end_idx": 0, "is_merging": False},
            {"label": "East", "val_start": 20, "val_end": None, "color": row_bg_a, "start_idx": 1, "end_idx": 0, "is_merging": True},
            {"label": "West", "val_start": 5,  "val_end": 5,  "color": row_bg_b, "start_idx": 2, "end_idx": 1, "is_merging": False}
        ]
        
        slide_t = 0.0
        if self.progress > 0.2:
            slide_t = min((self.progress - 0.2) / 0.5, 1.0)
            
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(header_color)
        painter.drawRoundedRect(QRectF(start_x, start_y - row_h, table_w, row_h), 2, 2)
        
        painter.setPen(QColor(255, 255, 255))
        
        painter.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        
        fm_h = painter.fontMetrics()
        h1 = "Region"
        h2 = "Sales"
        painter.drawText(int(start_x + col_w/2 - fm_h.horizontalAdvance(h1)/2), int(start_y - 7), h1)
        painter.drawText(int(start_x + col_w*1.5 - fm_h.horizontalAdvance(h2)/2), int(start_y - 7), h2)

        painter.setFont(QFont("Segoe UI", 10))
        
        for i, row in enumerate(rows_data):
            y_start = start_y + (row["start_idx"] * row_h)
            y_end = start_y + (row["end_idx"] * row_h)
            
            smooth_t = slide_t * slide_t * (3 - 2 * slide_t)
            current_y = y_start + (y_end - y_start) * smooth_t
            
            rect = QRectF(start_x, current_y, table_w, row_h)
            
            opacity = 1.0
            if row["is_merging"]:
                if slide_t > 0.8:
                    opacity = 1.0 - (slide_t - 0.8) / 0.2
            
            painter.setOpacity(opacity)
            
            painter.setPen(border_pen)
            painter.setBrush(row["color"])
            painter.drawRect(rect)
            
            display_val = row["val_start"]
            is_result_container = (i == 0)
            if is_result_container and slide_t >= 0.95:
                display_val = row["val_end"]
                painter.setBrush(row["color"].lighter(110))
                painter.drawRect(rect)
            
            text_label = str(row["label"])
            text_val   = str(display_val)
            
            painter.drawLine(int(start_x + col_w), int(current_y), int(start_x + col_w), int(current_y + row_h))
            
            painter.setPen(text_color)
            fm_row = painter.fontMetrics()
            
            cy = current_y + 16 
            
            cx1 = start_x + col_w/2 - fm_row.horizontalAdvance(text_label)/2
            painter.drawText(int(cx1), int(cy), text_label)
            
            cx2 = start_x + col_w*1.5 - fm_row.horizontalAdvance(text_val)/2
            painter.drawText(int(cx2), int(cy), text_val)

        painter.setOpacity(1.0)
        
        if 0.3 < slide_t < 0.9:
            alpha = 1.0 - abs(slide_t - 0.6) / 0.3
            plus_c = QColor(100, 150, 255)
            plus_c.setAlphaF(alpha)
            
            painter.setPen(QPen(plus_c, 2))
            plus_y = start_y + (0.5 * row_h)
            painter.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
            painter.drawText(int(start_x + table_w + 10), int(plus_y + 8), "+")