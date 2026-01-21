from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations import OverlayAnimationEngine

class DataFilterAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, message="Filtering Data..."):
        super().__init__(parent)
        self.message = message
        
        
        self.particles = [
            (-15, True, 0.0),  (10, False, 0.05), (-5, True, 0.1),
            (18, False, 0.15), (-20, False, 0.2), (8, True, 0.25),
            (-12, True, 0.3),  (15, True, 0.35),  (2, False, 0.4),
            (-8, False, 0.1),  (22, True, 0.2)
        ]

    def draw_content(self, painter):
        painter.scale(1.2, 1.2)
        
        funnel_color = QColor(100, 110, 130)
        keep_color   = QColor(0, 180, 255) 
        filter_color = QColor(255, 80, 80) 
        
        painter.setFont(QFont("Consolas", 12, QFont.Weight.Bold))
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(QRectF(-100, -75, 200, 40), Qt.AlignmentFlag.AlignCenter, self.message)
        
        painter.translate(0, 15)

        funnel_top_y = -30
        funnel_neck_y = 5
        funnel_exit_y = 30
        start_y = -60
        end_y = 50
        
        path_funnel = QPainterPath()
        path_funnel.moveTo(-30, funnel_top_y)
        path_funnel.lineTo(30, funnel_top_y)
        path_funnel.lineTo(10, funnel_neck_y)
        path_funnel.lineTo(10, funnel_exit_y)
        path_funnel.lineTo(-10, funnel_exit_y)
        path_funnel.lineTo(-10, funnel_neck_y)
        path_funnel.closeSubpath()
        
        painter.setPen(QPen(funnel_color.lighter(120), 2))
        painter.setBrush(funnel_color)
        painter.drawPath(path_funnel)
        
        painter.setPen(QPen(QColor(255,255,255, 100), 1, Qt.PenStyle.DotLine))
        painter.drawLine(-10, funnel_neck_y, 10, funnel_neck_y)

        
        painter.setPen(Qt.PenStyle.NoPen)
        dot_radius = 4

        for start_x, is_kept, delay in self.particles:
            p_prog = (self.progress - delay) / 0.6
            if p_prog < 0: continue
            if p_prog > 1: p_prog = 1.0
            
            curr_y = start_y + (end_y - start_y) * p_prog
            
            
            curr_x = start_x
            
            if curr_y < funnel_top_y:
                 pass
            elif curr_y < funnel_neck_y:
                cone_prog = (curr_y - funnel_top_y) / (funnel_neck_y - funnel_top_y)
                curr_x = start_x * (1.0 - cone_prog) + (start_x * 0.1 * cone_prog)
            else:
                curr_x = start_x * 0.1
                if curr_y > funnel_exit_y:
                     spread_prog = (curr_y - funnel_exit_y) / (end_y - funnel_exit_y)
                     curr_x = (start_x * 0.1) + (start_x * 0.3 * spread_prog)

            opacity = 1.0
            
            if not is_kept:
                if curr_y > funnel_top_y:
                    fade_range = funnel_neck_y - funnel_top_y
                    dist_into_funnel = curr_y - funnel_top_y
                    opacity = 1.0 - (dist_into_funnel / fade_range)
                    if opacity < 0: opacity = 0
            
            if opacity > 0.01:
                color = keep_color if is_kept else filter_color
                color.setAlphaF(opacity)
                painter.setBrush(color)
                
                painter.drawEllipse(QPointF(curr_x, curr_y), dot_radius, dot_radius)
        
        painter.setBrush(funnel_color.darker(110))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(-10, funnel_neck_y, 20, funnel_exit_y - funnel_neck_y))