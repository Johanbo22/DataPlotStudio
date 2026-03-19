from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QFont, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations import OverlayAnimationEngine

class SavePlotAnimation(OverlayAnimationEngine):
    def __init__(self, parent: QWidget | None = None, message: str = "Plot Saved") -> None:
        super().__init__(parent)
        self.message = message

    def draw_content(self, painter: QPainter) -> None:
        
        painter.scale(1.2, 1.2)
        
        text_color = QColor(255, 255, 255)
        plot_bg = QColor(250, 250, 250)
        plot_border = QColor(180, 180, 180)
        axes_color = QColor(100, 100, 100)
        line_color = QColor(0, 180, 255)
        drive_bg = QColor(60, 90, 120)
        drive_slot = QColor(30, 45, 60)
        success_color = QColor(40, 200, 80)
        
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(text_color)
        painter.drawText(QRectF(-100, -85, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)
        
        painter.translate(0, 20)
        
        drop_progress: float = 0.0
        if self.progress > 0.2:
            drop_progress = min(1.0, (self.progress - 0.2) / 0.65)
            
        ease_in: float = drop_progress ** 2
        y_offset: float = ease_in * 60.0
        
        painter.save()
        painter.setClipRect(QRectF(-100, -100, 200, 94))
        painter.translate(0, y_offset)
        
        card_rect = QRectF(-35, -65, 70, 50)
        painter.setBrush(QBrush(plot_bg))
        painter.setPen(QPen(plot_border, 2))
        painter.drawRoundedRect(card_rect, 4.0, 4.0)
        
        painter.setPen(QPen(axes_color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.drawLine(-25, -55, -25, -25)
        painter.drawLine(-25, -25, 25, -25)  
        
        path = QPainterPath()
        path.moveTo(-25, -25)
        path.cubicTo(-10, -50, 5, -20, 25, -45)
        
        painter.setPen(QPen(line_color, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
        
        painter.restore()
        
        drive_rect = QRectF(-45, -10, 90, 30)
        painter.setBrush(QBrush(drive_bg))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(drive_rect, 4.0, 4.0)
        
        slot_rect = QRectF(-38, -6, 76, 4)
        painter.setBrush(QBrush(drive_slot))
        painter.drawRoundedRect(slot_rect, 2.0, 2.0)
        
        light_color = drive_slot 
        if self.progress > 0.85:
            light_color = success_color 
        
        painter.setBrush(QBrush(light_color))
        painter.drawEllipse(QPointF(30, 10), 3.0, 3.0)