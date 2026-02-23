import math
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QIcon
from PyQt6.QtCore import QRect, Qt, QPointF, QRectF

from .icon_engine import BaseIconEngine
from .icon_registry import IconBuilder, IconType

def draw_pencil(painter: QPainter, cx: float, cy: float, width: float, height: float, color: QColor, angle: float = 45) -> None:
    painter.save()
    painter.translate(cx, cy)
    painter.rotate(angle)
    
    pw = width * 0.12
    pl = height * 0.35
    tip_l = height * 0.15
    
    pencil_pen = QPen(color)
    pencil_pen.setWidth(max(2, int(width * 0.05)))
    pencil_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(pencil_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    
    painter.drawRect(QRectF(-pw/2, -pl/2, pw, pl))
    painter.drawLine(QPointF(-pw/2, -pl/2 + pw), QPointF(pw/2, -pl/2 + pw))
    painter.drawPolygon(QPolygonF([
        QPointF(-pw/2, pl/2), QPointF(pw/2, pl/2), QPointF(0, pl/2 + tip_l)
    ]))
    painter.setBrush(QBrush(color))
    painter.drawPolygon(QPolygonF([
        QPointF(-pw/4, pl/2 + tip_l/2), QPointF(pw/4, pl/2 + tip_l/2), QPointF(0, pl/2 + tip_l)
    ]))
    painter.restore()

def draw_gear(painter: QPainter, cx: float, cy: float, width: float, color: QColor) -> None:
    gear_r = width * 0.25
    tooth_l = width * 0.08
    
    tooth_pen = QPen(color)
    tooth_pen.setWidth(int(width * 0.08))
    tooth_pen.setCapStyle(Qt.PenCapStyle.FlatCap)
    painter.setPen(tooth_pen)
    
    for i in range(8):
        angle = math.radians(i * 45)
        x1, y1 = cx + math.cos(angle) * gear_r, cy + math.sin(angle) * gear_r
        x2, y2 = cx + math.cos(angle) * (gear_r + tooth_l), cy + math.sin(angle) * (gear_r + tooth_l)
        painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))
        
    painter.setPen(Qt.PenStyle.NoPen)
    painter.setBrush(QBrush(color))
    painter.drawEllipse(QPointF(cx, cy), gear_r, gear_r)
    
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
    painter.drawEllipse(QPointF(cx, cy), width * 0.10, width * 0.10)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
    
@IconBuilder.register(IconType.GENERATE_PLOT)
class GeneratePlotIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        
        draw_pencil(painter, w * 0.40, h * 0.40, w * 1.5, h * 1.5, base_color, angle=45)
        
        plus_cx, plus_cy = w * 0.75, h * 0.75
        plus_size = w * 0.20
        pen_width = max(2, int(w * 0.08)) 
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(plus_cx, plus_cy), plus_size * 1.3, plus_size * 1.3)
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        plus_pen = QPen(base_color)
        plus_pen.setWidth(pen_width)
        plus_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(plus_pen)
        
        painter.drawLine(QPointF(plus_cx - plus_size, plus_cy), QPointF(plus_cx + plus_size, plus_cy))
        painter.drawLine(QPointF(plus_cx, plus_cy - plus_size), QPointF(plus_cx, plus_cy + plus_size))

@IconBuilder.register(IconType.SAVE_PLOT)
class SavePlotIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        floppy_pen = QPen(base_color)
        floppy_pen.setWidth(pen_width)
        floppy_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(floppy_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        body_poly = QPolygonF([
            QPointF(w * 0.15, h * 0.10),
            QPointF(w * 0.65, h * 0.10),
            QPointF(w * 0.85, h * 0.30),
            QPointF(w * 0.85, h * 0.85),
            QPointF(w * 0.15, h * 0.85)
        ])
        painter.drawPolygon(body_poly)
        
        painter.drawRect(QRectF(w * 0.30, h * 0.10, w * 0.25, h * 0.25))
        
        painter.drawRect(QRectF(w * 0.25, h * 0.55, w * 0.45, h * 0.30))
        painter.drawLine(QPointF(w * 0.60, h * 0.55), QPointF(w * 0.60, h * 0.75))
        
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        clear_pen = QPen(Qt.GlobalColor.black)
        clear_pen.setWidth(pen_width + 6)
        clear_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(clear_pen)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        
        mask_rect = QRectF(w * 0.50, h * 0.50, w * 0.45, h * 0.45)
        painter.drawRect(mask_rect)
        
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        
        axis_pen = QPen(base_color)
        axis_pen.setWidth(max(2, int(w * 0.04)))
        axis_pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        axis_pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(axis_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        axes_poly = QPolygonF([
            QPointF(w * 0.55, h * 0.55),
            QPointF(w * 0.55, h * 0.85),
            QPointF(w * 0.90, h * 0.85)
        ])
        painter.drawPolyline(axes_poly)
        
        trend_pen = QPen(base_color)
        trend_pen.setWidth(max(2, int(w * 0.04)))
        trend_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        trend_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(trend_pen)
        
        trend_poly = QPolygonF([
            QPointF(w * 0.60, h * 0.80),
            QPointF(w * 0.70, h * 0.60),
            QPointF(w * 0.80, h * 0.68),
            QPointF(w * 0.90, h * 0.50)
        ])
        painter.drawPolyline(trend_poly)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(base_color))
        dot_r = w * 0.035
        for point in trend_poly:
            painter.drawEllipse(point, dot_r, dot_r)

@IconBuilder.register(IconType.CLEAR_PLOT)
class ClearPlotIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(220, 50, 50)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        painter.save()
        # Translate to center and rotate so the brush spans corner-to-corner
        painter.translate(w * 0.5, h * 0.5)
        painter.rotate(45) # Handle top-right, bristles bottom-left
        
        pen = QPen(base_color)
        pen.setWidth(pen_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        # Greatly expanded dimensions to fill the canvas
        hw = w * 0.12  # Handle half-width
        fw = w * 0.16  # Ferrule half-width
        
        # 1. Brush Handle (Stretching deep into the top-right)
        painter.drawRect(QRectF(-hw, -h*0.55, hw*2, h*0.45))
        
        # 2. Metal Ferrule (The connector band)
        painter.drawRect(QRectF(-fw, -h*0.10, fw*2, h*0.20))
        
        # 3. Bristles (Accented red to signify the destructive 'clear' action)
        bristle_pen = QPen(base_color)
        bristle_pen.setWidth(pen_width)
        bristle_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(bristle_pen)
        
        bristles = QPolygonF([
            QPointF(-fw, h*0.10),
            QPointF(fw, h*0.10),
            QPointF(fw * 0.7, h*0.50),  # Tapering down into the bottom-left
            QPointF(-fw * 0.7, h*0.50)
        ])
        painter.drawPolygon(bristles)
        
        # Inner bristle details for texture
        painter.drawLine(QPointF(-fw * 0.3, h*0.10), QPointF(-fw * 0.3, h*0.45))
        painter.drawLine(QPointF(fw * 0.3, h*0.10), QPointF(fw * 0.3, h*0.45))
        
        painter.restore()

@IconBuilder.register(IconType.OPEN_PYTHON_EDITOR)
class OpenPythonEditorIcon(BaseIconEngine): 
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        doc_pen = QPen(base_color)
        doc_pen.setWidth(pen_width)
        doc_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(doc_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        doc_left = w * 0.35
        doc_right = w * 0.85
        doc_top = h * 0.10
        doc_bottom = h * 0.90
        fold_size = w * 0.20
        
        painter.drawPolygon(QPolygonF([
            QPointF(doc_left, doc_top), 
            QPointF(doc_right - fold_size, doc_top),
            QPointF(doc_right, doc_top + fold_size), 
            QPointF(doc_right, doc_bottom),
            QPointF(doc_left, doc_bottom)
        ]))
        
        painter.drawPolygon(QPolygonF([
            QPointF(doc_right - fold_size, doc_top), 
            QPointF(doc_right - fold_size, doc_top + fold_size), 
            QPointF(doc_right, doc_top + fold_size)
        ]))
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        
        mask_cx = w * 0.27
        mask_cy = h * 0.75
        mask_r = w * 0.26
        painter.drawEllipse(QPointF(mask_cx, mask_cy), mask_r, mask_r)
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        code_pen = QPen(base_color)
        code_pen.setWidth(pen_width + 2)
        code_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        code_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(code_pen)
        
        painter.drawLine(QPointF(w * 0.22, h * 0.60), QPointF(w * 0.05, h * 0.75))
        painter.drawLine(QPointF(w * 0.05, h * 0.75), QPointF(w * 0.22, h * 0.90))
        
        painter.drawLine(QPointF(w * 0.32, h * 0.60), QPointF(w * 0.49, h * 0.75))
        painter.drawLine(QPointF(w * 0.49, h * 0.75), QPointF(w * 0.32, h * 0.90))

@IconBuilder.register(IconType.PLOT_GENERAL_OPTIONS)
class PlotGeneralOptionsIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        draw_gear(painter, w * 0.6, h * 0.6, w, base_color)

@IconBuilder.register(IconType.PLOT_APPEARANCE)
class PlotAppearanceIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        pen = QPen(base_color)
        pen.setWidth(pen_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawRect(QRectF(w * 0.20, h * 0.40, w * 0.25, h * 0.45))
        painter.drawRect(QRectF(w * 0.25, h * 0.30, w * 0.15, h * 0.10)) 
        painter.drawLine(QPointF(w * 0.325, h * 0.30), QPointF(w * 0.325, h * 0.25)) 
        
        painter.save()
        painter.translate(w * 0.65, h * 0.55)
        painter.rotate(25)
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        clear_pen = QPen(Qt.GlobalColor.black)
        clear_pen.setWidth(pen_width + 6)
        painter.setPen(clear_pen)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.drawRect(QRectF(-w*0.15, -h*0.25, w*0.30, h*0.50))
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        accent_pen = QPen(base_color)
        accent_pen.setWidth(pen_width)
        accent_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(accent_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        painter.drawRect(QRectF(-w*0.125, -h*0.225, w*0.25, h*0.45))
        painter.drawRect(QRectF(-w*0.075, -h*0.325, w*0.15, h*0.10))
        painter.drawLine(QPointF(0, -h*0.325), QPointF(0, -h*0.375))
        painter.restore()

@IconBuilder.register(IconType.PLOT_AXES)
class PlotAxesIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.06))
        
        axis_pen = QPen(base_color)
        axis_pen.setWidth(pen_width)
        axis_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        axis_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(axis_pen)
        
        # Y-Axis
        painter.drawLine(QPointF(w * 0.20, h * 0.85), QPointF(w * 0.20, h * 0.15))
        painter.drawLine(QPointF(w * 0.10, h * 0.25), QPointF(w * 0.20, h * 0.15))
        painter.drawLine(QPointF(w * 0.30, h * 0.25), QPointF(w * 0.20, h * 0.15))
        
        # X-Axis
        painter.drawLine(QPointF(w * 0.15, h * 0.80), QPointF(w * 0.85, h * 0.80))
        painter.drawLine(QPointF(w * 0.75, h * 0.70), QPointF(w * 0.85, h * 0.80))
        painter.drawLine(QPointF(w * 0.75, h * 0.90), QPointF(w * 0.85, h * 0.80))
        
        line_pen = QPen(base_color)
        line_pen.setWidth(pen_width)
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(line_pen)
        painter.drawLine(QPointF(w * 0.20, h * 0.80), QPointF(w * 0.75, h * 0.25))

@IconBuilder.register(IconType.PLOT_LEGEND_GRID)
class PlotLegendGridIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.04))
        
        grid_pen = QPen(base_color)
        grid_pen.setWidth(pen_width)
        painter.setPen(grid_pen)
        
        painter.drawRect(QRectF(w * 0.10, h * 0.10, w * 0.80, h * 0.80))
        painter.drawLine(QPointF(w * 0.36, h * 0.10), QPointF(w * 0.36, h * 0.90))
        painter.drawLine(QPointF(w * 0.63, h * 0.10), QPointF(w * 0.63, h * 0.90))
        painter.drawLine(QPointF(w * 0.10, h * 0.36), QPointF(w * 0.90, h * 0.36))
        painter.drawLine(QPointF(w * 0.10, h * 0.63), QPointF(w * 0.90, h * 0.63))
        
        leg_rect = QRectF(w * 0.60, h * 0.15, w * 0.25, h * 0.30)
        painter.setBrush(QBrush(QColor(Qt.GlobalColor.white) if mode != QIcon.Mode.Disabled else QColor(Qt.GlobalColor.lightGray)))
        
        leg_pen = QPen(base_color)
        leg_pen.setWidth(max(2, int(w * 0.03)))
        painter.setPen(leg_pen)
        painter.drawRect(leg_rect)
        
        item_pen = QPen(base_color)
        item_pen.setWidth(max(2, int(w * 0.04)))
        item_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(item_pen)
        
        painter.drawLine(QPointF(w * 0.65, h * 0.22), QPointF(w * 0.80, h * 0.22))
        painter.drawLine(QPointF(w * 0.65, h * 0.30), QPointF(w * 0.80, h * 0.30))
        painter.drawLine(QPointF(w * 0.65, h * 0.38), QPointF(w * 0.80, h * 0.38))

@IconBuilder.register(IconType.PLOT_CUSTOMIZATION)
class PlotCustomizationIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        draw_gear(painter, w * 0.40, h * 0.40, w, base_color)
        
        painter.save()
        pencil_cx = w * 0.7
        pencil_cy = h * 0.7
        pw = w * 0.12    
        pl = h * 0.35    
        tip_l = h * 0.15 
        
        painter.translate(pencil_cx, pencil_cy)
        painter.rotate(-45) 
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        clear_pen = QPen(Qt.GlobalColor.black)
        clear_pen.setWidth(pen_width + 4) 
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
        painter.restore()
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        draw_pencil(painter, pencil_cx, pencil_cy, w, h, base_color, angle=45)

@IconBuilder.register(IconType.PLOT_ANNOTATIONS)
class PlotAnnotationsIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        note_pen = QPen(base_color)
        note_pen.setWidth(pen_width)
        note_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(note_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        note_poly = QPolygonF([
            QPointF(w * 0.15, h * 0.15), QPointF(w * 0.65, h * 0.15),
            QPointF(w * 0.65, h * 0.70), QPointF(w * 0.35, h * 0.70),
            QPointF(w * 0.15, h * 0.50)
        ])
        painter.drawPolygon(note_poly)
        painter.drawPolygon(QPolygonF([
            QPointF(w * 0.35, h * 0.70), QPointF(w * 0.35, h * 0.50), QPointF(w * 0.15, h * 0.50)
        ]))
        
        painter.drawLine(QPointF(w * 0.25, h * 0.30), QPointF(w * 0.55, h * 0.30))
        painter.drawLine(QPointF(w * 0.25, h * 0.45), QPointF(w * 0.50, h * 0.45))
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        clear_pen = QPen(Qt.GlobalColor.black)
        clear_pen.setWidth(int(w * 0.18))
        clear_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(clear_pen)
        painter.drawLine(QPointF(w * 0.65, h * 0.45), QPointF(w * 0.85, h * 0.85))
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        draw_pencil(painter, w * 0.75, h * 0.65, w, h, base_color, angle=30)

@IconBuilder.register(IconType.PLOT_GEOSPATIAL)
class PlotGeospatialIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        pen = QPen(base_color)
        pen.setWidth(pen_width)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        cx, cy = w * 0.50, h * 0.50
        r = w * 0.40
        
        painter.drawEllipse(QPointF(cx, cy), r, r)
        painter.drawEllipse(QPointF(cx, cy), r, r * 0.30)
        painter.drawEllipse(QPointF(cx, cy), r * 0.40, r)
        painter.drawLine(QPointF(cx, cy - r), QPointF(cx, cy + r))
