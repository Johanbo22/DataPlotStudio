import math
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QIcon, QPainterPath
from PyQt6.QtCore import QRect, Qt, QPointF, QRectF

from .icon_engine import BaseIconEngine
from .icon_registry import IconBuilder, IconType

@IconBuilder.register(IconType.PLOT_TAB_ICON)
class PlotTabIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        
        pen_width = max(3, int(w * 0.08))
        
        axis_pen = QPen(base_color)
        axis_pen.setWidth(pen_width)
        axis_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        axis_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(axis_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        ax_left = w * 0.15
        ax_right = w * 0.85
        ax_top = h * 0.15
        ax_bottom = h * 0.85
        
        axes_poly = QPolygonF([
            QPointF(ax_left, ax_top),    
            QPointF(ax_left, ax_bottom),  
            QPointF(ax_right, ax_bottom)   
        ])
        painter.drawPolyline(axes_poly)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(base_color))
        
        arrow_size = pen_width * 1.5
        
        y_arrow = QPolygonF([
            QPointF(ax_left, ax_top - arrow_size),
            QPointF(ax_left - arrow_size, ax_top + arrow_size*0.2),
            QPointF(ax_left + arrow_size, ax_top + arrow_size*0.2)
        ])
        painter.drawPolygon(y_arrow)
        
        x_arrow = QPolygonF([
            QPointF(ax_right + arrow_size, ax_bottom),
            QPointF(ax_right - arrow_size*0.2, ax_bottom - arrow_size),
            QPointF(ax_right - arrow_size*0.2, ax_bottom + arrow_size)
        ])
        painter.drawPolygon(x_arrow)

        trend_pen = QPen(accent_color)
        trend_pen.setWidth(pen_width)
        trend_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        trend_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(trend_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        trend_poly = QPolygonF([
            QPointF(ax_left, ax_bottom),     
            QPointF(w * 0.35, h * 0.55),    
            QPointF(w * 0.50, h * 0.70),   
            QPointF(w * 0.65, h * 0.45),    
            QPointF(w * 0.75, h * 0.55),    
            QPointF(w * 0.92, h * 0.15)     
        ])
        painter.drawPolyline(trend_poly)

@IconBuilder.register(IconType.DATA_EXPLORER_ICON)
class DataExplorerIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        
        grid_color = QColor("#4A90E2")
        glass_rim_color = QColor("#7F94A1")
        glass_handle_color = QColor("#7F94A1")
        glass_lens_color = QColor("#EDF7FF")
        
        if mode == QIcon.Mode.Disabled:
            grid_color = QColor(Qt.GlobalColor.darkGray)
            glass_rim_color = QColor(Qt.GlobalColor.darkGray)
            glass_handle_color = QColor(Qt.GlobalColor.darkGray)
            glass_lens_color = QColor(Qt.GlobalColor.lightGray)

        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.03))

        grid_pen = QPen(grid_color)
        grid_pen.setWidth(pen_width)
        painter.setPen(grid_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)

        grid_x = w * 0.1
        grid_y = h * 0.1
        grid_w = w * 0.8
        grid_h = h * 0.7

        painter.drawRect(QRectF(grid_x, grid_y, grid_w, grid_h))

        for i in range(1, 4):
            y = grid_y + (grid_h / 4) * i
            painter.drawLine(QPointF(grid_x, y), QPointF(grid_x + grid_w, y))

        for i in range(1, 4):
            x = grid_x + (grid_w / 4) * i
            painter.drawLine(QPointF(x, grid_y), QPointF(x, grid_y + grid_h))

        painter.setPen(Qt.PenStyle.NoPen)
        
        lens_cx = w * 0.65
        lens_cy = h * 0.65
        lens_r = w * 0.2
        
        painter.setBrush(QBrush(glass_lens_color))
        painter.drawEllipse(QPointF(lens_cx, lens_cy), lens_r, lens_r)

        rim_pen = QPen(glass_rim_color)
        rim_pen.setWidth(pen_width * 2)
        painter.setPen(rim_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(lens_cx, lens_cy), lens_r, lens_r)

        handle_pen = QPen(glass_handle_color)
        handle_pen.setWidth(pen_width * 3)
        handle_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(handle_pen)
        
        import math
        angle = math.radians(45)
        handle_start_x = lens_cx + math.cos(angle) * lens_r
        handle_start_y = lens_cy + math.sin(angle) * lens_r
        handle_end_x = lens_cx + math.cos(angle) * (lens_r + w * 0.25)
        handle_end_y = lens_cy + math.sin(angle) * (lens_r + w * 0.25)

        painter.drawLine(QPointF(handle_start_x, handle_start_y), QPointF(handle_end_x, handle_end_y))

@IconBuilder.register(IconType.EXPLORE_STATISTICS_ICON)
class ExploreStatsPanelIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        outline_color = QColor(Qt.GlobalColor.black) if mode != QIcon.Mode.Disabled else QColor(Qt.GlobalColor.darkGray)
        c_pink = QColor("#FF8080")
        c_yellow = QColor("#FFFFAA")
        c_green = QColor("#55FFBB")
        c_blue = QColor("#66BBFF")
        c_bubble = QColor("#33FFCC")
        c_white = QColor(Qt.GlobalColor.white)

        if mode == QIcon.Mode.Disabled:
            c_pink = c_yellow = c_green = c_blue = c_bubble = QColor(Qt.GlobalColor.lightGray)
            c_white = QColor(Qt.GlobalColor.gray)

        w, h = rect.width(), rect.height()
        pen_width = max(3, int(w * 0.06))

        main_pen = QPen(outline_color)
        main_pen.setWidth(pen_width)
        main_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        main_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(main_pen)
        
        painter.setBrush(Qt.BrushStyle.NoBrush)
        axes_path = QPainterPath()
        axes_path.moveTo(w * 0.05, h * 0.05) 
        axes_path.lineTo(w * 0.05, h * 0.95) 
        axes_path.lineTo(w * 0.95, h * 0.95) 
        painter.drawPath(axes_path)

        bar_w = w * 0.15
        base_y = h * 0.95
        bars = [
            (w * 0.15, h * 0.65, bar_w, h * 0.30, c_pink),
            (w * 0.35, h * 0.50, bar_w, h * 0.45, c_yellow),
            (w * 0.55, h * 0.60, bar_w, h * 0.35, c_green),
            (w * 0.75, h * 0.45, bar_w, h * 0.50, c_blue),
        ]

        for bx, by, bw, bh, color in bars:
            painter.setBrush(QBrush(color))
            painter.drawRect(QRectF(bx, by - pen_width/2, bw, bh))

        points = [
            QPointF(w * 0.225, h * 0.50),
            QPointF(w * 0.425, h * 0.35), 
            QPointF(w * 0.625, h * 0.45), 
            QPointF(w * 0.825, h * 0.25), 
        ]
        point_colors = [c_pink, c_yellow, c_green, c_green] 

        painter.setBrush(Qt.BrushStyle.NoBrush)
        line_path = QPainterPath()
        line_path.moveTo(points[0])
        for p in points[1:]:
            line_path.lineTo(p)
        painter.drawPath(line_path)

        dot_r = w * 0.06
        for i, p in enumerate(points):
            painter.setBrush(QBrush(point_colors[i]))
            painter.drawEllipse(p, dot_r, dot_r)

        bubble_cx, bubble_cy = w * 0.75, h * 0.25
        bubble_r = w * 0.22
        bubble_path = QPainterPath()
        bubble_path.addEllipse(QPointF(bubble_cx, bubble_cy), bubble_r, bubble_r)
        
        tail_poly = QPolygonF([
            QPointF(bubble_cx - bubble_r * 0.2, bubble_cy + bubble_r * 0.9),
            QPointF(w * 0.75, h * 0.55), 
            QPointF(bubble_cx + bubble_r * 0.5, bubble_cy + bubble_r * 0.8) 
        ])
        bubble_path.addPolygon(tail_poly)
        bubble_path = bubble_path.simplified()

        painter.setBrush(QBrush(c_bubble))
        painter.drawPath(bubble_path)

        painter.setBrush(QBrush(c_white))
        dot_size = w * 0.05
        painter.drawEllipse(QPointF(bubble_cx, bubble_cy - bubble_r * 0.4), dot_size, dot_size)
        
        i_body_w = w * 0.06
        i_body_h = h * 0.15
        i_body_rect = QRectF(bubble_cx - i_body_w/2, bubble_cy - bubble_r * 0.1, i_body_w, i_body_h)
        painter.drawRoundedRect(i_body_rect, i_body_w/2, i_body_w/2)

@IconBuilder.register(IconType.UNDO)
class UndoIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.08))
        
        pen = QPen(color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        path = QPainterPath()
        path.moveTo(w * 0.5, h * 0.2)
        path.cubicTo(w * 0.1, h * 0.2, w * 0.1, h * 0.8, w * 0.5, h * 0.8)
        path.lineTo(w * 0.8, h * 0.8)
        painter.drawPath(path)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        arrow_head = QPolygonF([
            QPointF(w * 0.5, h * 0.2 + pen_width),
            QPointF(w * 0.35, h * 0.05),
            QPointF(w * 0.65, h * 0.05)
        ])
        painter.drawPolygon(arrow_head)

@IconBuilder.register(IconType.REDO)
class RedoIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        painter.translate(rect.width(), 0)
        painter.scale(-1, 1)
        UndoIcon().draw_icon(painter, rect, mode)

@IconBuilder.register(IconType.SETTINGS)
class SettingsIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        cx, cy = w * 0.5, h * 0.5
        
        outer_r = w * 0.45
        inner_r = w * 0.30
        hole_r = w * 0.12
        num_teeth = 8
        tooth_depth = w * 0.08
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        
        path = QPainterPath()
        path.moveTo(cx + outer_r, cy)
        for i in range(num_teeth * 2):
            angle = math.radians(i * (360 / (num_teeth * 2)))
            r = outer_r if i % 2 == 0 else outer_r - tooth_depth
            x = cx + math.cos(angle) * r
            y = cy + math.sin(angle) * r
            path.lineTo(x, y)
        path.closeSubpath()
        
        hole_path = QPainterPath()
        hole_path.addEllipse(QPointF(cx, cy), hole_r, hole_r)
        path = path.subtracted(hole_path)
        
        painter.drawPath(path)
        
        pen = QPen(color)
        pen.setWidth(max(2, int(w * 0.04)))
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), inner_r, inner_r)

class BaseZoomIcon(BaseIconEngine):
    def draw_magnifier(self, painter: QPainter, rect: QRect, color: QColor, pen_width: int) -> tuple[float, float, float]:
        w, h = rect.width(), rect.height()
        
        lens_r = w * 0.3
        lens_cx, lens_cy = w * 0.4, h * 0.4
        painter.drawEllipse(QPointF(lens_cx, lens_cy), lens_r, lens_r)
        
        handle_start = QPointF(lens_cx + lens_r * math.cos(math.pi/4), 
                               lens_cy + lens_r * math.sin(math.pi/4))
        handle_end = QPointF(w * 0.85, h * 0.85)
        painter.drawLine(handle_start, handle_end)
        
        return lens_cx, lens_cy, lens_r

@IconBuilder.register(IconType.ZOOM_IN)
class ZoomInIcon(BaseZoomIcon):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w = rect.width()
        pen_width = max(2, int(w * 0.06))
        
        pen = QPen(color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        cx, cy, r = self.draw_magnifier(painter, rect, color, pen_width)
        
        plus_size = r * 0.5
        painter.drawLine(QPointF(cx - plus_size, cy), QPointF(cx + plus_size, cy))
        painter.drawLine(QPointF(cx, cy - plus_size), QPointF(cx, cy + plus_size))

@IconBuilder.register(IconType.ZOOM_OUT)
class ZoomOutIcon(BaseZoomIcon):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w = rect.width()
        pen_width = max(2, int(w * 0.06))
        
        pen = QPen(color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        cx, cy, r = self.draw_magnifier(painter, rect, color, pen_width)
        
        minus_size = r * 0.5
        painter.drawLine(QPointF(cx - minus_size, cy), QPointF(cx + minus_size, cy))

@IconBuilder.register(IconType.INFORMATION)
class InformationIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.06))
        cx, cy = w * 0.5, h * 0.5
        
        pen = QPen(color)
        pen.setWidth(pen_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawEllipse(QPointF(cx, cy), w * 0.45, h * 0.45)
        
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.drawLine(QPointF(cx, h * 0.45), QPointF(cx, h * 0.75))
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(color))
        dot_size = w * 0.06
        painter.drawEllipse(QPointF(cx, h * 0.25), dot_size, dot_size)

@IconBuilder.register(IconType.REFRESH_ITEM)
class RefreshItemIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(3, int(w * 0.08)) 
        
        pen = QPen(color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.translate(w * 0.5, h * 0.5)
        
        r = w * 0.30
        arc_rect = QRectF(-r, -r, r*2, r*2)
        
        def draw_arrow_head(angle_deg: float):
            """Calculates the tangent at the given angle and draws a wide, distinct arrowhead."""
            painter.save()
            rad = math.radians(angle_deg)
            px = r * math.cos(rad)
            py = -r * math.sin(rad)
            
            painter.translate(px, py)
            
            qt_angle = math.degrees(math.atan2(py, px))
            painter.rotate(qt_angle + 90)
            
            wing_len = r * 0.60
            back_len = wing_len * 0.5 

            painter.drawLine(QPointF(0, 0), QPointF(-back_len, -wing_len))
            painter.drawLine(QPointF(0, 0), QPointF(-back_len, wing_len))
            painter.restore()

        painter.drawArc(arc_rect, 150 * 16, -120 * 16)
        draw_arrow_head(30)
        
        painter.drawArc(arc_rect, 330 * 16, -120 * 16)
        draw_arrow_head(210)
        
@IconBuilder.register(IconType.VIEW_ITEM)
class ViewItemIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(3, int(w * 0.08))
        
        pen = QPen(color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        
        painter.translate(w * 0.5, h * 0.5)
        r_eye = w * 0.40 
        
        painter.setBrush(Qt.BrushStyle.NoBrush)
        path = QPainterPath()
        path.moveTo(-r_eye, 0)
        path.quadTo(0, -r_eye * 0.8, r_eye, 0) # Top lid
        path.quadTo(0, r_eye * 0.8, -r_eye, 0)
        painter.drawPath(path)
        
        pupil_r = w * 0.15
        painter.setBrush(QBrush(color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(0, 0), pupil_r, pupil_r)
    
@IconBuilder.register(IconType.DELETE_ITEM)
class DeleteItemIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(3, int(w * 0.10))
        
        pen = QPen(color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        
        painter.translate(w * 0.5, h * 0.5)
        r_x = w * 0.35 
        
        painter.drawLine(QPointF(-r_x, -r_x), QPointF(r_x, r_x))
        painter.drawLine(QPointF(r_x, -r_x), QPointF(-r_x, r_x))