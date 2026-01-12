import math
from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen, QBrush, QLinearGradient
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations.OverlayAnimationEngine import OverlayAnimationEngine

class OutlierDetectionAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Outlier Detection Complete", method_name="z_score"):
        super().__init__(parent)
        self.message = message

        key = method_name.lower()

        display_map = {
            "z_score": "Z-Score",
            "iqr": "IQR",
            "isolation_forest": "Isolation Forest"
        }

        if key in display_map:
            self.method_name = display_map[key]
        else:
            self.method_name = method_name.replace("_", " ").title()
    
    def draw_content(self, painter):
        painter.scale(1.2, 1.2)
        
        header_c = QColor(60, 90, 120)
        grid_c = QColor(200, 200, 220)
        normal_bg = QColor(250, 250, 255)
        normal_data_c = QColor(200, 200, 200)
        
        outlier_bg_final = QColor(255, 220, 220) 
        outlier_data_c = QColor(220, 80, 80)  
        
        scanner_c = QColor(0, 200, 255, 150)
        
        badge_bg = QColor(70, 70, 90)
        badge_border = QColor(255, 215, 0)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-125, -75, 250, 40), Qt.AlignmentFlag.AlignCenter, self.message)
        
        painter.translate(0, 15)

        rows, cols = 5, 4
        cell_w, cell_h = 20, 12
        header_h = 12
        table_w = cols * cell_w
        table_h = header_h + (rows * cell_h)
        start_x = -table_w / 2
        start_y = -table_h / 2 + 5
        
        outlier_coords = [(1, 2), (3, 0), (4, 3)]
        
        scan_duration = 0.6
        badge_start = 0.65
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(header_c)
        painter.drawRoundedRect(QRectF(start_x, start_y, table_w, header_h), 2, 2)
        
        painter.setPen(QPen(grid_c, 1))
        
        current_y = start_y + header_h
        
        for r in range(rows):
            current_x = start_x
            row_progress_threshold = (r + 0.5) / rows 
            
            scanner_passed = self.progress > (row_progress_threshold * scan_duration)

            for c in range(cols):
                rect = QRectF(current_x, current_y, cell_w, cell_h)
                is_outlier = (r, c) in outlier_coords
                
                bg_color = normal_bg
                data_color = normal_data_c
                data_pen_width = 2

                if is_outlier and scanner_passed:
                    bg_color = outlier_bg_final
                    data_color = outlier_data_c
                    data_pen_width = 3
                    
                    if self.progress < badge_start:
                        pulse = math.sin(self.progress * 20) * 0.1 + 0.9
                        painter.save()
                        painter.translate(rect.center())
                        painter.scale(pulse, pulse)
                        painter.translate(-rect.center())
                
                painter.setBrush(bg_color)
                painter.drawRect(rect)
                
                painter.setPen(QPen(data_color, data_pen_width))
                line_y = int(rect.center().y())
                painter.drawLine(int(current_x + 5), line_y, int(current_x + cell_w - 5), line_y)
                
                if is_outlier and scanner_passed:
                    painter.drawLine(int(current_x + 5), line_y+3, int(current_x + cell_w - 8), line_y+3)

                painter.setPen(QPen(grid_c, 1))
                
                if is_outlier and scanner_passed and self.progress < badge_start:
                    painter.restore()

                current_x += cell_w
            current_y += cell_h

        if self.progress < scan_duration:
            scan_y_pos = start_y + (table_h * (self.progress / scan_duration))
            
            scanner_rect = QRectF(start_x - 5, scan_y_pos - 2, table_w + 10, 4)
            
            grad = QLinearGradient(0, scan_y_pos - 2, 0, scan_y_pos + 2)
            grad.setColorAt(0, QColor(0, 0, 0, 0))
            grad.setColorAt(0.5, scanner_c)
            grad.setColorAt(1, QColor(0, 0, 0, 0))
            
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(grad)
            painter.drawRect(scanner_rect)

        if self.progress > badge_start:
            badge_progress = min((self.progress - badge_start) / 0.3, 1.0)
            
            scale = badge_progress
            if badge_progress < 0.8:
                 scale = badge_progress * 1.4
            else:
                 scale = 1.12 - (badge_progress - 0.8) * 0.6
            
            painter.save()
            painter.scale(scale, scale)
            
            badge_w, badge_h = 140, 24
            badge_rect = QRectF(-badge_w/2, -badge_h/2 - 35, badge_w, badge_h)
            
            painter.setPen(QPen(badge_border, 2))
            painter.setBrush(badge_bg)
            painter.drawRoundedRect(badge_rect, 6, 6)
            
            painter.setPen(badge_border)
            painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, f"{self.method_name}")
            
            painter.restore()