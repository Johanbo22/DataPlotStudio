from PyQt6.QtGui import QIcon, QPainter, QColor, QPen, QBrush, QPolygonF
from PyQt6.QtCore import QRect, Qt, QPointF, QRectF

from .icon_engine import BaseIconEngine
from .icon_registry import IconBuilder, IconType

@IconBuilder.register(IconType.FILTER)
class FilterIconEngine(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.gray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        
        pen_width = max(2, int(rect.width() * 0.05))
        
        pen = QPen(base_color)
        pen.setWidth(pen_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(QBrush(base_color, Qt.BrushStyle.NoBrush))
        
        pad = int(rect.width() * 0.1)
        cx = rect.center().x()
        cy = rect.center().y()
        funnel = QPolygonF([
            QPointF(rect.left() + pad, rect.top() + pad),
            QPointF(rect.right() - pad, rect.top() + pad),
            QPointF(cx + pen_width, cy + pen_width),
            QPointF(cx + pen_width, rect.bottom() - pad),
            QPointF(cx - pen_width, rect.bottom() - pad - pen_width),
            QPointF(cx - pen_width, cy + pen_width),
        ])
        painter.drawPolygon(funnel)

@IconBuilder.register(IconType.ADVANCED_FILTER)
class AdvancedFilterIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        
        pen_width = max(2, int(rect.width() * 0.05))
        width = rect.width()
        height = rect.height()
        
        funnel_pen = QPen(base_color)
        funnel_pen.setWidth(pen_width)
        funnel_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        funnel_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(funnel_pen)
        painter.setBrush(QBrush(base_color, Qt.BrushStyle.NoBrush))
        
        funnel_left = width * 0.10
        funnel_right = width * 0.75
        funnel_top = height * 0.175
        funnel_bottom = height * 0.825
        cx = (funnel_left + funnel_right) / 2
        cy = height / 2
        
        funnel = QPolygonF([
            QPointF(funnel_left, funnel_top * 0.2),
            QPointF(funnel_right, funnel_top * 0.2),
            QPointF(cx + pen_width, cy + pen_width),
            QPointF(cx + pen_width, funnel_bottom * 0.85),
            QPointF(cx - pen_width, funnel_bottom * 0.85 - pen_width * 2),
            QPointF(cx - pen_width, cy + pen_width)
        ])
        painter.drawPolygon(funnel)
        
        plus_pen = QPen(accent_color)
        plus_pen.setWidth(int(pen_width * 1.2))
        plus_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(plus_pen)
        
        plus_cx = width * 0.80
        plus_cy = height * 0.30
        plus_size = width * 0.12
        
        painter.drawLine(
            QPointF(plus_cx - plus_size, plus_cy),
            QPointF(plus_cx + plus_size, plus_cy)
        )
        painter.drawLine(
            QPointF(plus_cx, plus_cy - plus_size),
            QPointF(plus_cx, plus_cy + plus_size)
            
        )

@IconBuilder.register(IconType.CLEAR_FILTER)
class ClearFilterIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(220, 50, 50)
        
        pen_width = max(2, int(rect.width() * 0.05))
        width = rect.width()
        height = rect.height()
        
        funnel_pen = QPen(base_color)
        funnel_pen.setWidth(pen_width)
        funnel_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        funnel_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(funnel_pen)
        painter.setBrush(QBrush(base_color, Qt.BrushStyle.NoBrush))
        
        funnel_left = width * 0.10
        funnel_right = width * 0.75
        funnel_top = height * 0.175
        funnel_bottom = height * 0.825
        cx = (funnel_left + funnel_right) / 2
        cy = height / 2
        
        funnel = QPolygonF([
            QPointF(funnel_left, funnel_top),
            QPointF(funnel_right, funnel_top),
            QPointF(cx + pen_width, cy + pen_width),
            QPointF(cx + pen_width, funnel_bottom),
            QPointF(cx - pen_width, funnel_bottom - pen_width * 2),
            QPointF(cx - pen_width, cy + pen_width),
        ])
        painter.drawPolygon(funnel)
        
        x_pen = QPen(accent_color)
        x_pen.setWidth(int(pen_width * 1.2))
        x_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(x_pen)
        
        x_cx = width * 0.80
        x_cy = height * 0.30
        x_size = width * 0.10
        
        painter.drawLine(
            QPointF(x_cx - x_size, x_cy - x_size),
            QPointF(x_cx + x_size, x_cy + x_size)
        )
        painter.drawLine(
            QPointF(x_cx + x_size, x_cy - x_size),
            QPointF(x_cx - x_size, x_cy + x_size)
        )

@IconBuilder.register(IconType.REMOVE_DUPLICATES)
class RemoveDuplicatesIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(220, 50, 50)
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.08))
        
        row_pen = QPen(base_color)
        row_pen.setWidth(pen_width)
        row_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(row_pen)
        
        row_left = width * 0.15
        row_right = width * 0.85
        
        painter.drawLine(QPointF(row_left, height * 0.25), QPointF(row_right, height * 0.25))
        painter.drawLine(QPointF(row_left, height * 0.75), QPointF(row_right, height * 0.75))
        
        short_row_right = width * 0.55
        painter.drawLine(QPointF(row_left, height * 0.50), QPointF(short_row_right, height * 0.50))
        
        x_pen = QPen(accent_color)
        x_pen.setWidth(int(pen_width * 1.2))
        x_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(x_pen)
        
        x_cx = width * 0.75
        x_cy = height * 0.50
        x_size = width * 0.10 
        
        painter.drawLine(QPointF(x_cx - x_size, x_cy - x_size), QPointF(x_cx + x_size, x_cy + x_size))
        painter.drawLine(QPointF(x_cx + x_size, x_cy - x_size), QPointF(x_cx - x_size, x_cy + x_size))

@IconBuilder.register(IconType.DROP_MISSING_VALUES)
class DropMissingValuesIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(220, 50, 50)
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.08))
        row_pen = QPen(base_color)
        row_pen.setWidth(pen_width)
        row_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(row_pen)
        
        row_left = width * 0.15
        row_right = width * 0.85
        
        painter.drawLine(QPointF(row_left, height * 0.25), QPointF(row_right, height * 0.25))
        
        painter.drawLine(QPointF(row_left, height * 0.75), QPointF(row_right, height * 0.75))
        
        painter.drawLine(QPointF(row_left, height * 0.50), QPointF(width * 0.35, height * 0.50))
        painter.drawLine(QPointF(width * 0.50, height * 0.50), QPointF(width * 0.60, height * 0.50))
        
        x_pen = QPen(accent_color)
        x_pen.setWidth(int(pen_width * 1.2))
        x_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(x_pen)
        
        x_cx = width * 0.78
        x_cy = height * 0.50
        x_size = width * 0.10 
        
        painter.drawLine(QPointF(x_cx - x_size, x_cy - x_size), QPointF(x_cx + x_size, x_cy + x_size))
        painter.drawLine(QPointF(x_cx + x_size, x_cy - x_size), QPointF(x_cx - x_size, x_cy + x_size))

@IconBuilder.register(IconType.FILL_MISSING_VALUES)
class FillMissingValuesIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.08))
        
        row_pen = QPen(base_color)
        row_pen.setWidth(pen_width)
        row_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(row_pen)
        
        row_left = width * 0.15
        row_right = width * 0.85
        
        painter.drawLine(QPointF(row_left, height * 0.25), QPointF(row_right, height * 0.25))
        
        painter.drawLine(QPointF(row_left, height * 0.75), QPointF(row_right, height * 0.75))
        
        painter.drawLine(QPointF(row_left, height * 0.50), QPointF(width * 0.35, height * 0.50))
        painter.drawLine(QPointF(width * 0.50, height * 0.50), QPointF(width * 0.60, height * 0.50))
        
        fill_pen = QPen(accent_color)
        fill_pen.setWidth(pen_width)
        fill_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(fill_pen)
        
        painter.drawLine(QPointF(width * 0.35, height * 0.50), QPointF(width * 0.50, height * 0.50))
        
        plus_pen = QPen(accent_color)
        plus_pen.setWidth(int(pen_width * 1.2))
        plus_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(plus_pen)
        
        plus_cx = width * 0.78
        plus_cy = height * 0.50
        plus_size = width * 0.10 
        
        painter.drawLine(QPointF(plus_cx - plus_size, plus_cy), QPointF(plus_cx + plus_size, plus_cy))
        painter.drawLine(QPointF(plus_cx, plus_cy - plus_size), QPointF(plus_cx, plus_cy + plus_size))

@IconBuilder.register(IconType.DROP_COLUMN)
class DropColumnIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(220, 50, 50) 
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.08))
        
        col_pen = QPen(base_color)
        col_pen.setWidth(pen_width)
        col_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(col_pen)
        
        col_top = height * 0.15
        col_bottom = height * 0.85
        
        painter.drawLine(QPointF(width * 0.25, col_top), QPointF(width * 0.25, col_bottom))
        
        painter.drawLine(QPointF(width * 0.75, col_top), QPointF(width * 0.75, col_bottom))
        
        short_col_bottom = height * 0.55
        painter.drawLine(QPointF(width * 0.50, col_top), QPointF(width * 0.50, short_col_bottom))
        
        x_pen = QPen(accent_color)
        x_pen.setWidth(int(pen_width * 1.2))
        x_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(x_pen)
        
        x_cx = width * 0.50
        x_cy = height * 0.75
        x_size = width * 0.10 
        
        painter.drawLine(QPointF(x_cx - x_size, x_cy - x_size), QPointF(x_cx + x_size, x_cy + x_size))
        painter.drawLine(QPointF(x_cx + x_size, x_cy - x_size), QPointF(x_cx - x_size, x_cy + x_size))

@IconBuilder.register(IconType.RENAME_COLUMN)
class RenameColumnIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.08))
        
        col_pen = QPen(base_color)
        col_pen.setWidth(pen_width)
        col_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(col_pen)
        
        col_top = height * 0.15
        col_bottom = height * 0.85
        
        painter.drawLine(QPointF(width * 0.25, col_top), QPointF(width * 0.25, col_bottom))
        
        painter.drawLine(QPointF(width * 0.75, col_top), QPointF(width * 0.75, col_bottom))
        
        short_col_top = height * 0.45
        painter.drawLine(QPointF(width * 0.50, short_col_top), QPointF(width * 0.50, col_bottom))
        
        cursor_pen = QPen(accent_color)
        cursor_pen.setWidth(max(2, int(pen_width * 0.8))) 
        cursor_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(cursor_pen)
        
        cursor_top = height * 0.15
        cursor_bottom = height * 0.35
        cursor_x = width * 0.50
        serif_width = width * 0.08 
        
        painter.drawLine(QPointF(cursor_x, cursor_top), QPointF(cursor_x, cursor_bottom))
        painter.drawLine(QPointF(cursor_x - serif_width, cursor_top), QPointF(cursor_x + serif_width, cursor_top))
        painter.drawLine(QPointF(cursor_x - serif_width, cursor_bottom), QPointF(cursor_x + serif_width, cursor_bottom))

@IconBuilder.register(IconType.DUPLICATE_COLUMN)
class DuplicateColumnIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.06))
        
        col_w = width * 0.35
        col_h = height * 0.60
        header_offset = height * 0.15
        
        back_x = width * 0.20
        back_y = height * 0.10
        
        back_pen = QPen(base_color)
        back_pen.setWidth(pen_width)
        back_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(back_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawRect(QRectF(back_x, back_y, col_w, col_h))
        painter.drawLine(QPointF(back_x, back_y + header_offset), QPointF(back_x + col_w, back_y + header_offset))
        
        
        front_x = width * 0.45
        front_y = height * 0.30
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        
        clear_pen = QPen(Qt.GlobalColor.black)
        clear_pen.setWidth(pen_width + 6)
        clear_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(clear_pen)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        
        painter.drawRect(QRectF(front_x, front_y, col_w, col_h))
        
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        front_pen = QPen(accent_color)
        front_pen.setWidth(pen_width)
        front_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(front_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawRect(QRectF(front_x, front_y, col_w, col_h))
        painter.drawLine(QPointF(front_x, front_y + header_offset), QPointF(front_x + col_w, front_y + header_offset))

@IconBuilder.register(IconType.CALCULATOR)
class CalculatorIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215) # UI Blue
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.05))
        
        body_pen = QPen(base_color)
        body_pen.setWidth(pen_width)
        body_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(body_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        body_x = width * 0.20
        body_y = height * 0.10
        body_w = width * 0.60
        body_h = height * 0.80
        corner_radius = width * 0.05
        
        painter.drawRoundedRect(QRectF(body_x, body_y, body_w, body_h), corner_radius, corner_radius)
        
        screen_x = width * 0.30
        screen_y = height * 0.20
        screen_w = width * 0.40
        screen_h = height * 0.15
        
        painter.drawRect(QRectF(screen_x, screen_y, screen_w, screen_h))
        
        btn_w = width * 0.09
        btn_h = height * 0.07
        
        cols = [width * 0.30, width * 0.455, width * 0.61]
        rows = [height * 0.45, height * 0.58, height * 0.71]
        
        for r_idx, row_y in enumerate(rows):
            for c_idx, col_x in enumerate(cols):
                if r_idx == 2 and c_idx == 2:
                    continue
                
                painter.drawRect(QRectF(col_x, row_y, btn_w, btn_h))
                
        accent_pen = QPen(accent_color)
        accent_pen.setWidth(pen_width)
        accent_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(accent_pen)
        
        painter.setBrush(QBrush(accent_color))
        painter.drawRect(QRectF(cols[2], rows[2], btn_w, btn_h))

@IconBuilder.register(IconType.CHANGE_DATATYPE)
class ChangeDataTypeIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        
        width = rect.width()
        height = rect.height()
        
        text_pen = QPen(base_color)
        text_pen.setWidth(max(2, int(width * 0.04))) 
        text_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        text_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(text_pen)
        
        painter.drawLine(QPointF(width * 0.05, height * 0.80), QPointF(width * 0.20, height * 0.20))
        painter.drawLine(QPointF(width * 0.20, height * 0.20), QPointF(width * 0.35, height * 0.80))
        painter.drawLine(QPointF(width * 0.12, height * 0.60), QPointF(width * 0.28, height * 0.60)) 
        
        painter.drawLine(QPointF(width * 0.80, height * 0.20), QPointF(width * 0.80, height * 0.80)) 
        painter.drawLine(QPointF(width * 0.68, height * 0.35), QPointF(width * 0.80, height * 0.20)) 
        painter.drawLine(QPointF(width * 0.65, height * 0.80), QPointF(width * 0.95, height * 0.80))
        
        arrow_pen = QPen(accent_color)
        arrow_pen.setWidth(max(2, int(width * 0.05))) 
        arrow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(arrow_pen)
        
        painter.drawLine(QPointF(width * 0.42, height * 0.50), QPointF(width * 0.58, height * 0.50)) 
        painter.drawLine(QPointF(width * 0.50, height * 0.40), QPointF(width * 0.58, height * 0.50)) 
        painter.drawLine(QPointF(width * 0.50, height * 0.60), QPointF(width * 0.58, height * 0.50)) 

@IconBuilder.register(IconType.TEXT_OPERATION)
class TextOperationIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.05))
        
        base_pen = QPen(base_color)
        base_pen.setWidth(pen_width)
        base_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        base_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(base_pen)
        
        painter.drawLine(QPointF(width * 0.15, height * 0.75), QPointF(width * 0.325, height * 0.25)) 
        painter.drawLine(QPointF(width * 0.325, height * 0.25), QPointF(width * 0.50, height * 0.75)) 
        painter.drawLine(QPointF(width * 0.22, height * 0.55), QPointF(width * 0.43, height * 0.55))  
        
        accent_pen = QPen(accent_color)
        accent_pen.setWidth(pen_width)
        accent_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        accent_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(accent_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        bowl_rect = QRectF(width * 0.58, height * 0.50, width * 0.25, height * 0.25)
        painter.drawEllipse(bowl_rect)
        
        painter.drawLine(QPointF(width * 0.83, height * 0.45), QPointF(width * 0.83, height * 0.75))

@IconBuilder.register(IconType.DATA_TRANSFORM)
class DataTransformIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        import math
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215) 
        
        width = rect.width()
        height = rect.height()
        
        pen_width = max(2, int(width * 0.06))
        
        cx = width * 0.50
        cy = height * 0.50
        gear_r = width * 0.12
        tooth_l = width * 0.05
        
        tooth_pen = QPen(base_color)
        tooth_pen.setWidth(int(width * 0.06))
        tooth_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
        painter.setPen(tooth_pen)
        
        for i in range(8):
            angle = math.radians(i * 45)
            x1 = cx + math.cos(angle) * gear_r
            y1 = cy + math.sin(angle) * gear_r
            x2 = cx + math.cos(angle) * (gear_r + tooth_l)
            y2 = cy + math.sin(angle) * (gear_r + tooth_l)
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
            
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(base_color))
        painter.drawEllipse(QPointF(cx, cy), gear_r, gear_r)
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.drawEllipse(QPointF(cx, cy), width * 0.05, width * 0.05)
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        shape_pen = QPen(base_color)
        shape_pen.setWidth(pen_width)
        shape_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(shape_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        sq_size = width * 0.16
        sq_x = width * 0.20 - (sq_size / 2)
        sq_y = height * 0.80 - (sq_size / 2)
        painter.drawRect(QRectF(sq_x, sq_y, sq_size, sq_size))
        
        c_r = width * 0.09
        painter.drawEllipse(QPointF(width * 0.80, height * 0.20), c_r, c_r)
        
        arrow_pen = QPen(accent_color)
        arrow_pen.setWidth(pen_width)
        arrow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(arrow_pen)
        
        arc_rect = QRectF(width * 0.15, height * 0.15, width * 0.70, height * 0.70)
        
        painter.drawArc(arc_rect, 270 * 16, 90 * 16)
        
        ah1_x = width * 0.85
        ah1_y = height * 0.50
        ah_size = width * 0.06
        painter.drawLine(QPointF(ah1_x, ah1_y), QPointF(ah1_x - ah_size, ah1_y + ah_size))
        painter.drawLine(QPointF(ah1_x, ah1_y), QPointF(ah1_x + ah_size, ah1_y + ah_size))
        
        painter.drawArc(arc_rect, 90 * 16, 90 * 16)
        
        ah2_x = width * 0.15
        ah2_y = height * 0.50
        painter.drawLine(QPointF(ah2_x, ah2_y), QPointF(ah2_x - ah_size, ah2_y - ah_size))
        painter.drawLine(QPointF(ah2_x, ah2_y), QPointF(ah2_x + ah_size, ah2_y - ah_size))

@IconBuilder.register(IconType.EDIT_COLUMNS)
class EditColumnsIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215) 
        
        width = rect.width()
        height = rect.height()
        
        bg_pen_width = max(2, int(width * 0.04))
        fg_pen_width = max(2, int(width * 0.06))
        
        table_pen = QPen(base_color)
        table_pen.setWidth(bg_pen_width)
        table_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        table_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(table_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        tbl_x = width * 0.10
        tbl_y = height * 0.10
        tbl_w = width * 0.50
        tbl_h = height * 0.60
        
        painter.drawRect(QRectF(tbl_x, tbl_y, tbl_w, tbl_h))
        
        header_y = tbl_y + tbl_h * 0.25
        painter.drawLine(QPointF(tbl_x, header_y), QPointF(tbl_x + tbl_w, header_y))
        
        row_y = tbl_y + tbl_h * 0.65
        painter.drawLine(QPointF(tbl_x, row_y), QPointF(tbl_x + tbl_w, row_y))
        
        col_x = tbl_x + tbl_w * 0.50
        painter.drawLine(QPointF(col_x, header_y), QPointF(col_x, tbl_y + tbl_h))
        
        painter.save()
        
        pencil_cx = width * 0.60
        pencil_cy = height * 0.60
        pw = width * 0.22   
        pl = height * 0.55 
        tip_l = height * 0.25 
        
        painter.translate(pencil_cx, pencil_cy)
        painter.rotate(40) 
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        clear_pen = QPen(Qt.GlobalColor.black)
        clear_pen.setWidth(fg_pen_width + 6) 
        clear_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(clear_pen)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        
        mask_poly = QPolygonF([
            QPointF(-pw/2, -pl/2), 
            QPointF(pw/2, -pl/2), 
            QPointF(pw/2, pl/2), 
            QPointF(0, pl/2 + tip_l), 
            QPointF(-pw/2, pl/2)
        ])
        painter.drawPolygon(mask_poly)
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        pencil_pen = QPen(base_color)
        pencil_pen.setWidth(fg_pen_width)
        pencil_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pencil_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawRect(QRectF(-pw/2, -pl/2, pw, pl))
        
        painter.drawLine(QPointF(-pw/2, -pl/2 + pw), QPointF(pw/2, -pl/2 + pw))
        
        painter.drawPolygon(QPolygonF([
            QPointF(-pw/2, pl/2),
            QPointF(pw/2, pl/2),
            QPointF(0, pl/2 + tip_l)
        ]))
        
        painter.setBrush(QBrush(base_color))
        painter.drawPolygon(QPolygonF([
            QPointF(-pw/4, pl/2 + tip_l/2),
            QPointF(pw/4, pl/2 + tip_l/2),
            QPointF(0, pl/2 + tip_l)
        ]))
        
        painter.restore()

@IconBuilder.register(IconType.DATA_CLEANING)
class DataCleaningIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215) 
        
        w = rect.width()
        h = rect.height()
        pen_width = max(2, int(w * 0.05))
        
        db_pen = QPen(base_color)
        db_pen.setWidth(pen_width)
        db_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        db_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(db_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        cx, r_w, r_h = w * 0.40, w * 0.30, h * 0.10
        top_y = h * 0.20
        mid_y = h * 0.45
        bot_y = h * 0.70
        painter.drawEllipse(QPointF(cx, top_y), r_w, r_h)
        painter.drawArc(QRectF(cx - r_w, mid_y - r_h, r_w * 2, r_h * 2), 0, -180 * 16)
        painter.drawArc(QRectF(cx - r_w, bot_y - r_h, r_w * 2, r_h * 2), 0, -180 * 16)
        painter.drawLine(QPointF(cx - r_w, top_y), QPointF(cx - r_w, bot_y))
        painter.drawLine(QPointF(cx + r_w, top_y), QPointF(cx + r_w, bot_y))
        
        sponge_x = w * 0.60
        sponge_y = h * 0.60
        sponge_w = w * 0.35
        sponge_h = h * 0.25
        sponge_rect = QRectF(sponge_x, sponge_y, sponge_w, sponge_h)
        sponge_radius = w * 0.08

        painter.save()
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        clear_pen = QPen(Qt.GlobalColor.black)
        clear_pen.setWidth(pen_width + 6)
        painter.setPen(clear_pen)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawRoundedRect(sponge_rect, sponge_radius, sponge_radius)
        painter.restore()
        
        sponge_pen = QPen(base_color)
        sponge_pen.setWidth(pen_width)
        sponge_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(sponge_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawRoundedRect(sponge_rect, sponge_radius, sponge_radius)
        
        pore_pen = QPen(base_color)
        pore_pen.setWidth(max(2, int(pen_width * 0.8)))
        pore_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pore_pen)
        
        pores = [
            QPointF(sponge_x + sponge_w*0.3, sponge_y + sponge_h*0.3),
            QPointF(sponge_x + sponge_w*0.7, sponge_y + sponge_h*0.4),
            QPointF(sponge_x + sponge_w*0.4, sponge_y + sponge_h*0.7),
            QPointF(sponge_x + sponge_w*0.8, sponge_y + sponge_h*0.65),
        ]
        painter.drawPoints(pores)
        
        sparkle_pen = QPen(base_color)
        sparkle_pen.setWidth(max(2, int(pen_width * 0.8)))
        sparkle_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(sparkle_pen)
        
        def draw_sparkle(px, py, size):
            painter.drawLine(QPointF(px - size, py), QPointF(px + size, py))
            painter.drawLine(QPointF(px, py - size), QPointF(px, py + size))

        draw_sparkle(w * 0.75, h * 0.20, w * 0.08)
        draw_sparkle(w * 0.90, h * 0.35, w * 0.05)

@IconBuilder.register(IconType.SORT)
class SortIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.06))
        
        pen = QPen(base_color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Dimensions
        arrow_h_margin = h * 0.15 # Vertical padding from edges
        arrow_head_sz = w * 0.15  # Size of the arrow head wings
        
        # Left Arrow (Upward)
        cx1 = w * 0.35
        # Shaft
        painter.drawLine(QPointF(cx1, h - arrow_h_margin), QPointF(cx1, arrow_h_margin))
        # Head
        painter.drawPolyline(QPolygonF([
            QPointF(cx1 - arrow_head_sz, arrow_h_margin + arrow_head_sz),
            QPointF(cx1, arrow_h_margin),
            QPointF(cx1 + arrow_head_sz, arrow_h_margin + arrow_head_sz)
        ]))
        
        # Right Arrow (Downward)
        cx2 = w * 0.65
        # Shaft
        painter.drawLine(QPointF(cx2, arrow_h_margin), QPointF(cx2, h - arrow_h_margin))
        # Head
        painter.drawPolyline(QPolygonF([
            QPointF(cx2 - arrow_head_sz, h - arrow_h_margin - arrow_head_sz),
            QPointF(cx2, h - arrow_h_margin),
            QPointF(cx2 + arrow_head_sz, h - arrow_h_margin - arrow_head_sz)
        ]))
