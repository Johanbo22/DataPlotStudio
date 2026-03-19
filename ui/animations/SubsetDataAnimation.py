from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF

from ui.animations import OverlayAnimationEngine

class SubsetDataAnimation(OverlayAnimationEngine):
    def __init__(self, parent: QWidget | None = None, message: str = "Subset Created") -> None:
        super().__init__(parent)
        self.message = message
    
    def draw_content(self, painter: QPainter) -> None:
        painter.scale(1.2, 1.2)
        
        grid_color = QColor(200, 200, 220)
        header_bg = QColor(60, 90, 120)
        table_bg = QColor(240, 240, 240)
        subset_highlight_bg = QColor(0, 180, 255, 60)
        subset_border = QColor(0, 180, 255)
        text_color = QColor(255, 255, 255)
        
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(text_color)
        painter.drawText(QRectF(-100, -90, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)
        
        painter.translate(-60, -30)
        
        col_w: float = 30.0
        row_h: float = 16.0
        total_cols: int = 4
        total_rows: int = 5
        
        sub_r_start: int = 1
        sub_r_count: int = 3
        sub_c_start: int = 1
        sub_c_count: int = 2
        
        main_opacity: float = 1.0
        if self.progress > 0.7:
            main_opacity = max(0.4, 1.0 - ((self.progress - 0.7) / 0.3))
        
        painter.setOpacity(main_opacity)
        
        for r in range(total_rows):
            for c in range(total_cols):
                rect = QRectF(c * col_w, r * row_h, col_w, row_h)
                
                if r == 0:
                    painter.setBrush(header_bg)
                else:
                    painter.setBrush(table_bg)
                
                painter.setPen(QPen(grid_color, 1))
                painter.drawRect(rect)
                
                if r > 0:
                    painter.setPen(QPen(QColor(210, 210, 210), 2))
                    painter.drawLine(
                        int(c * col_w +6), int(r * row_h + row_h / 2), int((c + 1) * col_w - 6), int(r * row_h + row_h / 2)
                    )
        painter.setOpacity(1.0)
        
        extract_progress: float = 0.0
        if self.progress > 0.2:
            extract_progress = min(1.0, (self.progress - 0.2) / 0.6)
        
        ease_out = 1.0 - (1.0 - extract_progress) ** 3
        
        offset_x: float = ease_out * 70.0
        offset_y: float = ease_out * 40.0
        
        painter.translate(offset_x, offset_y)
        
        for r in range(sub_r_count):
            for c in range(sub_c_count):
                orig_r = sub_r_start + r
                orig_c = sub_c_start + c
                
                rect = QRectF(orig_c * col_w, orig_r * row_h, col_w, row_h)
                
                if extract_progress == 0.0:
                    painter.setBrush(subset_highlight_bg)
                    painter.setPen(QPen(subset_border, 2))
                    painter.drawRect(rect)
                else:
                    if r == 0:
                        painter.setBrush(header_bg.lighter(130))
                    else:
                        painter.setBrush(QColor(255, 255, 255))
                    
                    painter.setPen(QPen(subset_border, 1))
                    painter.drawRect(rect)
                    
                    painter.setPen(QPen(grid_color, 1))
                    painter.drawLine(
                        int(orig_c * col_w + 6), int(orig_r * row_h + row_h / 2), 
                        int((orig_c + 1) * col_w - 6), int(orig_r * row_h + row_h / 2)
                    )