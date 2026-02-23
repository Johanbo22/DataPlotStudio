from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPolygonF, QIcon
from PyQt6.QtCore import QRect, Qt, QPointF, QRectF

from .icon_engine import BaseIconEngine
from .icon_registry import IconBuilder, IconType

def draw_document_base(painter: QPainter, width: float, height: float, pen_width: int, base_color: QColor) -> None:
    doc_pen = QPen(base_color)
    doc_pen.setWidth(pen_width)
    doc_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    painter.setPen(doc_pen)
    painter.setBrush(Qt.BrushStyle.NoBrush)
    
    doc_poly = QPolygonF([
        QPointF(width * 0.20, height * 0.10),
        QPointF(width * 0.55, height * 0.10),
        QPointF(width * 0.80, height * 0.35),
        QPointF(width * 0.80, height * 0.90),
        QPointF(width * 0.20, height * 0.90)
    ])
    painter.drawPolygon(doc_poly)
    fold_poly = QPolygonF([
        QPointF(width * 0.55, height * 0.10),
        QPointF(width * 0.55, height * 0.35),
        QPointF(width * 0.80, height * 0.35)
    ])
    painter.drawPolygon(fold_poly)

@IconBuilder.register(IconType.OPEN_PROJECT)
class OpenProjectIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        pen = QPen(base_color)
        pen.setWidth(pen_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        back_poly = QPolygonF([
            QPointF(w * 0.15, h * 0.40), 
            QPointF(w * 0.15, h * 0.20), 
            QPointF(w * 0.40, h * 0.20), 
            QPointF(w * 0.48, h * 0.30), 
            QPointF(w * 0.85, h * 0.30), 
            QPointF(w * 0.85, h * 0.85), 
            QPointF(w * 0.15, h * 0.85)  
        ])
        painter.drawPolygon(back_poly)
        
        doc_pen = QPen(accent_color)
        doc_pen.setWidth(pen_width)
        doc_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(doc_pen)
        
        doc_poly = QPolygonF([
            QPointF(w * 0.25, h * 0.45), 
            QPointF(w * 0.25, h * 0.10), 
            QPointF(w * 0.60, h * 0.10), 
            QPointF(w * 0.75, h * 0.25), 
            QPointF(w * 0.75, h * 0.45)
        ])
        painter.drawPolyline(doc_poly)
        
        painter.drawPolyline(QPolygonF([
            QPointF(w * 0.60, h * 0.10), 
            QPointF(w * 0.60, h * 0.25), 
            QPointF(w * 0.75, h * 0.25)
        ]))
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        clear_pen = QPen(Qt.GlobalColor.black)
        clear_pen.setWidth(pen_width + 4)
        clear_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(clear_pen)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        
        front_poly = QPolygonF([
            QPointF(w * 0.05, h * 0.45),
            QPointF(w * 0.95, h * 0.45),
            QPointF(w * 0.85, h * 0.90),
            QPointF(w * 0.15, h * 0.90)
        ])
        painter.drawPolygon(front_poly)
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPolygon(front_poly)

@IconBuilder.register(IconType.NEW_PROJECT)
class NewProjectIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        draw_document_base(painter, w, h, pen_width, base_color)
        plus_cx, plus_cy = w * 0.80, h * 0.75
        plus_size = w * 0.25
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
        painter.setBrush(QBrush(Qt.GlobalColor.black))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(plus_cx, plus_cy), plus_size * 1.5, plus_size * 1.5)
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        plus_pen = QPen(base_color)
        plus_pen.setWidth(pen_width + 4)
        plus_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(plus_pen)
        
        painter.drawLine(QPointF(plus_cx - plus_size, plus_cy), QPointF(plus_cx + plus_size, plus_cy))
        painter.drawLine(QPointF(plus_cx, plus_cy - plus_size), QPointF(plus_cx, plus_cy + plus_size))

@IconBuilder.register(IconType.SAVE_PROJECT)
class SaveProjectIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        pen = QPen(base_color)
        pen.setWidth(pen_width)
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        body_poly = QPolygonF([
            QPointF(w * 0.15, h * 0.15),
            QPointF(w * 0.65, h * 0.15),
            QPointF(w * 0.85, h * 0.35),
            QPointF(w * 0.85, h * 0.85),
            QPointF(w * 0.15, h * 0.85)
        ])
        painter.drawPolygon(body_poly)
        
        painter.drawRect(QRectF(w * 0.30, h * 0.15, w * 0.25, h * 0.25))
        
        painter.drawRect(QRectF(w * 0.25, h * 0.55, w * 0.50, h * 0.30))
        painter.drawLine(QPointF(w * 0.65, h * 0.55), QPointF(w * 0.65, h * 0.75))

@IconBuilder.register(IconType.SAVE_PROJECT_AS)
class SaveProjectAsIcon(BaseIconEngine): # pencil might need to a tad bigger
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
        
        body_poly = QPolygonF([
            QPointF(w * 0.15, h * 0.15),
            QPointF(w * 0.65, h * 0.15),
            QPointF(w * 0.85, h * 0.35),
            QPointF(w * 0.85, h * 0.85),
            QPointF(w * 0.15, h * 0.85)
        ])
        painter.drawPolygon(body_poly)
        
        painter.drawRect(QRectF(w * 0.30, h * 0.15, w * 0.25, h * 0.25))
        painter.drawRect(QRectF(w * 0.25, h * 0.55, w * 0.50, h * 0.30))
        painter.drawLine(QPointF(w * 0.65, h * 0.55), QPointF(w * 0.65, h * 0.75))
        
        
        painter.save()
        pencil_cx = w * 0.80
        pencil_cy = h * 0.75
        pw = w * 0.12   
        pl = h * 0.30   
        tip_l = h * 0.15 
        
        painter.translate(pencil_cx, pencil_cy)
        painter.rotate(45)
        
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
        
        painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
        pencil_pen = QPen(base_color)
        pencil_pen.setWidth(pen_width)
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

@IconBuilder.register(IconType.IMPORT_FILE)
class ImportFileIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        draw_document_base(painter, w, h, pen_width, base_color)
        
        arrow_pen = QPen(base_color)
        arrow_pen.setWidth(pen_width + 2)
        arrow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(arrow_pen)
        
        cx, cy = w * 0.50, h * 0.55
        aw = w * 0.12
        painter.drawLine(QPointF(cx, cy - aw * 1.5), QPointF(cx, cy + aw)) 
        painter.drawLine(QPointF(cx - aw, cy), QPointF(cx, cy + aw))     
        painter.drawLine(QPointF(cx + aw, cy), QPointF(cx, cy + aw))

@IconBuilder.register(IconType.EXPORT_FILE)
class ExportFileIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(0, 120, 215)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        draw_document_base(painter, w, h, pen_width, base_color)
        
        # Up Arrow
        arrow_pen = QPen(base_color)
        arrow_pen.setWidth(pen_width + 2)
        arrow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(arrow_pen)
        
        cx, cy = w * 0.50, h * 0.50
        aw = w * 0.12
        painter.drawLine(QPointF(cx, cy + aw * 1.5), QPointF(cx, cy - aw)) # Shaft
        painter.drawLine(QPointF(cx - aw, cy), QPointF(cx, cy - aw))       # Head left
        painter.drawLine(QPointF(cx + aw, cy), QPointF(cx, cy - aw))       # Head right

@IconBuilder.register(IconType.IMPORT_DATABASE)
class ImportDatabaseIcon(BaseIconEngine): 
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.05))
        
        pen = QPen(base_color)
        pen.setWidth(pen_width)
        pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        painter.setPen(pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        
        cx, r_w, r_h = w * 0.50, w * 0.35, h * 0.12
        
        painter.drawEllipse(QPointF(cx, h * 0.20), r_w, r_h)
        
        mid_rect = QRectF(cx - r_w, h * 0.50 - r_h, r_w * 2, r_h * 2)
        painter.drawArc(mid_rect, 0, -180 * 16)
        
        bot_rect = QRectF(cx - r_w, h * 0.80 - r_h, r_w * 2, r_h * 2)
        painter.drawArc(bot_rect, 0, -180 * 16)
        
        painter.drawLine(QPointF(cx - r_w, h * 0.20), QPointF(cx - r_w, h * 0.80))
        painter.drawLine(QPointF(cx + r_w, h * 0.20), QPointF(cx + r_w, h * 0.80))

@IconBuilder.register(IconType.QUIT)
class QuitIcon(BaseIconEngine):
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        base_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(Qt.GlobalColor.black)
        accent_color = QColor(Qt.GlobalColor.darkGray) if mode == QIcon.Mode.Disabled else QColor(220, 50, 50) # Red for exit
        w, h = rect.width(), rect.height()
        pen_width = max(2, int(w * 0.06))
        
        # Half bracket (Left side door)
        bracket_pen = QPen(base_color)
        bracket_pen.setWidth(pen_width)
        bracket_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        bracket_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(bracket_pen)
        
        painter.drawPolyline(QPolygonF([
            QPointF(w * 0.45, h * 0.15),
            QPointF(w * 0.20, h * 0.15),
            QPointF(w * 0.20, h * 0.85),
            QPointF(w * 0.45, h * 0.85)
        ]))
        
        # Right facing arrow
        arrow_pen = QPen(base_color)
        arrow_pen.setWidth(pen_width)
        arrow_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        arrow_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(arrow_pen)
        
        cx, cy = w * 0.55, h * 0.50
        aw = w * 0.15
        
        painter.drawLine(QPointF(w * 0.35, cy), QPointF(w * 0.85, cy)) # Shaft escaping right
        painter.drawLine(QPointF(w * 0.85 - aw, cy - aw), QPointF(w * 0.85, cy)) # Top head
        painter.drawLine(QPointF(w * 0.85 - aw, cy + aw), QPointF(w * 0.85, cy))
