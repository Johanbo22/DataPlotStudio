import math
from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen, QBrush, QFontMetrics
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations import OverlayAnimationEngine

class MeltDataAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Melt Data"):
        super().__init__(parent)
        self.message = str(message)

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)
        
        header_bg = QColor(60, 90, 120)
        header_txt = QColor(255, 255, 255)
        grid_pen = QPen(QColor(200, 200, 220), 1)
        data_bg = QColor(250, 250, 255)
        data_txt = QColor(50, 50, 50)
        highlight_c = QColor(100, 150, 255)

        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(header_txt)
        
        fm = painter.fontMetrics()
        msg_w = fm.horizontalAdvance(self.message)
        painter.drawText(int(-msg_w / 2), -60, self.message)
        
        painter.translate(0, 10)

        cell_w = 40
        cell_h = 20
        
        start_x = -cell_w * 1.5
        start_y = -cell_h

        anim_start = 0.2
        anim_end = 0.8
        t = 0.0
        if self.progress > anim_start:
            t = min((self.progress - anim_start) / (anim_end - anim_start), 1.0)
        
        smooth_t = t * t * (3 - 2 * t)

        wide_opacity = 1.0 - smooth_t
        long_opacity = smooth_t

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(header_bg)
        painter.drawRoundedRect(QRectF(start_x, start_y, cell_w * 3, cell_h), 2, 2)
        
        painter.setBrush(data_bg)
        painter.setPen(grid_pen)
        current_table_h = cell_h * (1 + smooth_t)
        painter.drawRect(QRectF(start_x, start_y + cell_h, cell_w * 3, current_table_h))
        
        painter.drawLine(int(start_x), int(start_y + cell_h * 2), int(start_x + cell_w * 3), int(start_y + cell_h * 2))
        painter.drawLine(int(start_x + cell_w), int(start_y), int(start_x + cell_w), int(start_y + cell_h + current_table_h))
        painter.drawLine(int(start_x + cell_w * 2), int(start_y), int(start_x + cell_w * 2), int(start_y + cell_h + current_table_h))

        painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        painter.setPen(header_txt)
        
        def draw_centered_text(cx, cy, text):
            fm_c = painter.fontMetrics()
            tx = cx - fm_c.horizontalAdvance(text) / 2
            ty = cy + (fm_c.ascent() - fm_c.descent()) / 2
            painter.drawText(int(tx), int(ty), text)

        h_y = start_y + cell_h / 2
        draw_centered_text(start_x + cell_w / 2, h_y, "ID")

        painter.setOpacity(wide_opacity)
        draw_centered_text(start_x + cell_w * 1.5, h_y, "Val_A")
        draw_centered_text(start_x + cell_w * 2.5, h_y, "Val_B")
        
        painter.setOpacity(long_opacity)
        draw_centered_text(start_x + cell_w * 1.5, h_y, "Var")
        draw_centered_text(start_x + cell_w * 2.5, h_y, "Val")
        painter.setOpacity(1.0)

        painter.setFont(QFont("Consolas", 9))
        painter.setPen(data_txt)

        d_y1 = start_y + cell_h + cell_h / 2
        draw_centered_text(start_x + cell_w / 2, d_y1, "1")
        
        painter.setOpacity(long_opacity)
        d_y2 = start_y + cell_h * 2 + cell_h / 2
        draw_centered_text(start_x + cell_w / 2, d_y2, "1")
        
        draw_centered_text(start_x + cell_w * 1.5, d_y1, "A")
        draw_centered_text(start_x + cell_w * 1.5, d_y2, "B")
        painter.setOpacity(1.0)

        v1_start_x = start_x + cell_w * 1.5
        v1_start_y = d_y1
        v1_end_x = start_x + cell_w * 2.5
        v1_end_y = d_y1
        
        v2_start_x = start_x + cell_w * 2.5
        v2_start_y = d_y1
        v2_end_x = start_x + cell_w * 2.5
        v2_end_y = d_y2

        v1_x = v1_start_x + (v1_end_x - v1_start_x) * smooth_t
        v1_y = v1_start_y + (v1_end_y - v1_start_y) * smooth_t
        
        v2_x = v2_start_x + (v2_end_x - v2_start_x) * smooth_t
        v2_y = v2_start_y + (v2_end_y - v2_start_y) * smooth_t
        
        if 0.1 < smooth_t < 0.9:
            painter.setPen(highlight_c)
            painter.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        
        draw_centered_text(v1_x, v1_y, "10")
        draw_centered_text(v2_x, v2_y, "20")