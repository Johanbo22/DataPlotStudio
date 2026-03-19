import math
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QBrush
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations import OverlayAnimationEngine

class CalculationAnimation(OverlayAnimationEngine):
    
    def __init__(self, parent: QWidget | None = None, message: str = "Calculate ") -> None:
        super().__init__(parent)
        self.message = message
    
    def draw_content(self, painter: QPainter) -> None:
        painter.scale(1.2, 1.2)
        
        text_color = QColor(255, 255, 255)
        input_bg = QColor(60, 90, 120)
        operator_bg = QColor(255, 140, 0)
        output_bg = QColor(0, 180, 255)
        grid_color = QColor(200, 200, 220, 100)
        
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(text_color)
        painter.drawText(QRectF(-100, -80, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)
        
        painter.translate(0, 15)
        
        painter.setPen(QPen(grid_color, 2, Qt.PenStyle.DotLine))
        painter.drawLine(-60, -30, 0, 0)
        painter.drawLine(-60, 30, 0, 0)
        painter.drawLine(0, 0, 60, 0)
        
        node_width: float = 40.0
        node_height: float = 24.0
        
        font_node = QFont("Consolas", 10, QFont.Weight.Bold)
        font_op = QFont("Consolas", 14, QFont.Weight.ExtraBold)
        
        input_opacity = 1.0
        input_offset = 0.0
        
        if self.progress <= 0.4:
            t = self.progress / 0.4
            ease_in = t * t
            input_offset = ease_in * 60.0
        else:
            input_opacity = 0.0
        
        if input_opacity > 0:
            painter.setOpacity(input_opacity)
            painter.setFont(font_node)
            painter.setPen(Qt.PenStyle.NoPen)
            
            rect_top = QRectF(-60 + input_offset - node_width/2, -30 + (input_offset/2) - node_height/2, node_width, node_height)
            painter.setBrush(QBrush(input_bg))
            painter.drawRoundedRect(rect_top, 4.0, 4.0)
            painter.setPen(text_color)
            painter.drawText(rect_top, Qt.AlignmentFlag.AlignCenter, "X")
            
            painter.setPen(Qt.PenStyle.NoPen)
            rect_bottom = QRectF(-60 + input_offset - node_width/2, 30 - (input_offset/2) - node_height/2, node_width, node_height)
            painter.setBrush(QBrush(input_bg))
            painter.drawRoundedRect(rect_bottom, 4.0, 4.0)
            painter.setPen(text_color)
            painter.drawText(rect_bottom, Qt.AlignmentFlag.AlignCenter, "Y")
        
        painter.setOpacity(1.0)
        op_scale = 1.0
        
        if 0.4 < self.progress <= 0.6:
            t = (self.progress - 0.4) / 0.2
            op_scale = 1.0 + (math.sin(t * math.pi) * 0.3)
            
        painter.save()
        painter.scale(op_scale, op_scale)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(operator_bg))
        painter.drawEllipse(QPointF(0, 0), 16.0, 16.0)
        painter.setFont(font_op)
        painter.setPen(text_color)
        painter.drawText(QRectF(-16, -16, 32, 32), Qt.AlignmentFlag.AlignCenter, "ƒ")
        painter.restore()
        
        output_opacity = 0.0
        output_offset = 0.0
        
        if self.progress > 0.6:
            t = (self.progress - 0.6) / 0.4
            ease_out = 1.0 - (1.0 - t) ** 3
            output_offset = ease_out * 60.0
            output_opacity = min(1.0, t * 2.0)
            
        if output_opacity > 0:
            painter.setOpacity(output_opacity)
            painter.setFont(font_node)
            painter.setPen(Qt.PenStyle.NoPen)
            
            rect_out = QRectF(output_offset - node_width/2, -node_height/2, node_width, node_height)
            painter.setBrush(QBrush(output_bg))
            painter.drawRoundedRect(rect_out, 4.0, 4.0)
            painter.setPen(text_color)
            painter.drawText(rect_out, Qt.AlignmentFlag.AlignCenter, "Res")
            
        painter.setOpacity(1.0)