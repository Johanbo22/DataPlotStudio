from PyQt6.QtGui import QPainterPath, QFont, QColor, QPen
from PyQt6.QtCore import Qt, QRectF, QPointF

from ui.animations import OverlayAnimationEngine
from ui.help_animation_engine import HelpAnimationEngine

class EditModeToggleAnimation(OverlayAnimationEngine):
    def __init__(self, parent=None, is_on=True):
        """
        is_on: True for transitioning TO Edit Mode, 
            False for transitioning TO View Mode.
        """
        super().__init__(parent)
        self.is_on = is_on
        self.message = "Switching to Edit Mode" if is_on else "Switching to View Mode"

    def draw_content(self, painter):
        painter.scale(1.4, 1.4)
        painter.translate(0, 10)
        
        track_off_c = QColor(180, 180, 190)
        icon_off_c  = QColor(150, 150, 160)
        text_off_c  = QColor(200, 200, 210)
        
        track_on_c  = QColor(40, 160, 255) 
        icon_on_c   = QColor(60, 180, 255)
        text_on_c   = QColor(255, 255, 255)
        
        knob_c = QColor(255, 255, 255)
        
        raw_t = self.progress if self.is_on else (1.0 - self.progress)
        
        t = raw_t * raw_t * (3 - 2 * raw_t)

        current_track_c = HelpAnimationEngine.lerp_color(self, track_off_c, track_on_c, t)
        current_icon_c = HelpAnimationEngine.lerp_color(self, icon_off_c, icon_on_c, t)
        
        
        switch_w = 60
        switch_h = 30
        knob_pad = 4
        knob_size = switch_h - (knob_pad * 2)
        
        switch_rect = QRectF(-switch_w/2, -switch_h/2, switch_w, switch_h)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(current_track_c)
        painter.drawRoundedRect(switch_rect, switch_h/2, switch_h/2)
        
        knob_start_x = switch_rect.left() + knob_pad + knob_size/2
        knob_end_x   = switch_rect.right() - knob_pad - knob_size/2
        current_knob_x = knob_start_x + (knob_end_x - knob_start_x) * t
        
        painter.setBrush(knob_c)
        painter.setPen(QPen(QColor(0,0,0,30), 1)) 
        painter.drawEllipse(QPointF(current_knob_x, 0), knob_size/2, knob_size/2)

        icon_y = -35
        
        painter.save()
        painter.translate(0, icon_y)
        
        start_angle = -45
        end_angle = -10
        current_angle = start_angle + (end_angle - start_angle) * t
        
        start_off_x, start_off_y = -5, 0
        end_off_x, end_off_y = 5, 5
        curr_off_x = start_off_x + (end_off_x - start_off_x) * t
        curr_off_y = start_off_y + (end_off_y - start_off_y) * t
        
        painter.translate(curr_off_x, curr_off_y)
        painter.rotate(current_angle)

        pencil_w = 8
        pencil_h = 24
        tip_h = 8
        
        path_pencil = QPainterPath()
        path_pencil.addRect(QRectF(-pencil_w/2, -pencil_h/2, pencil_w, pencil_h))
        
        path_tip = QPainterPath()
        path_tip.moveTo(-pencil_w/2, pencil_h/2)
        path_tip.lineTo(pencil_w/2, pencil_h/2)
        path_tip.lineTo(0, pencil_h/2 + tip_h)
        path_tip.closeSubpath()
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(current_icon_c)
        painter.drawPath(path_pencil)
        
        painter.setBrush(current_icon_c.darker(120))
        painter.drawPath(path_tip)
        
        painter.restore()
    
        if t > 0.1:
            line_opacity = (t - 0.1) / 0.9 
            
            painter.save()
            painter.translate(0, icon_y + 15) 
            
            line_c = current_icon_c
            line_c.setAlphaF(line_opacity)
            line_width = 20 * t 
            
            painter.setPen(QPen(line_c, 2, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap))
            painter.drawLine(QPointF(-line_width/2, 0), QPointF(line_width/2, 0))
            painter.restore()

        
        text_y = 35
        painter.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        
        def draw_fading_text(text, color, opacity, y_pos):
            if opacity <= 0.01: return
            painter.save()
            c = QColor(color)
            c.setAlphaF(opacity)
            painter.setPen(c)
            fm = painter.fontMetrics()
            tw = fm.horizontalAdvance(text)
            painter.drawText(int(-tw/2), int(y_pos), text)
            painter.restore()

        draw_fading_text("View Mode", text_off_c, 1.0 - t, text_y)
        draw_fading_text("Edit Mode", text_on_c, t, text_y)