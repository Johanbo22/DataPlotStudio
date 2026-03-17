from PyQt6.QtWidgets import QGraphicsView, QGraphicsScene, QGraphicsRectItem, QGraphicsTextItem, QGraphicsPathItem, QWidget, QGraphicsDropShadowEffect, QGraphicsObject
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QColor, QPen, QBrush, QPainterPath, QFont, QPainter, QFontMetrics, QKeyEvent, QWheelEvent, QMouseEvent

from typing import List, Dict, Any, Callable

class FocusHighlightItem(QGraphicsObject):
    def __init__(self, width: float, height: float, parent=None):
        super().__init__(parent)
        self.width = width
        self.height = height
        
        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setColor(QColor(0, 0, 0, 30))
        self.shadow.setBlurRadius(18)
        self.shadow.setOffset(0, 5)
        self.setGraphicsEffect(self.shadow)
        self.setZValue(-1)
    
    def boundingRect(self) -> QRectF:
        return QRectF(0, 0, self.width, self.height)

    def _set_pos(self, pos: QPointF):
        self.setPos(pos)
    
    def _get_pos(self) -> QPointF:
        return self.pos()
    
    animated_pos = pyqtProperty(QPointF, fget=_get_pos, fset=_set_pos)
    
    def paint(self, painter: QPainter, option, widget) -> None:
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 8, 8)
        
        painter.fillPath(path, QBrush(QColor("#EFF6FF")))
        painter.setPen(QPen(QColor("#3b82f6"), 1.5))
        painter.drawPath(path)

class GraphNode(QGraphicsObject):
    clicked = pyqtSignal(int)

    def __init__(self, index: int, label: str, operation: dict, is_active: bool, is_undone: bool, parent=None):
        super().__init__(parent)
        self.index = index
        self.label = label
        self.operation = operation
        self.is_active = is_active
        self.is_undone = is_undone
        self.is_hovered = False

        self.width = 260.0
        self.height = 48.0
        
        self.setAcceptHoverEvents(True)
        self.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        if self.operation:
            details = "".join(f"<li><b>{k}</b>: {v}</li>" for k, v in self.operation.items() if k != "type")
            self.setToolTip(
                f"<div style='padding: 4px; color: #F8FAFC;'>"
                f"<b>Operation Details:</b><br>"
                f"<ul style='margin-top: 4px; margin-bottom: 0px;'>{details}</ul>"
                f"</div>"
            )
        else:
            self.setToolTip("<div style='color: #F8FAFC;'>Original imported data state</div>")

        self.shadow = QGraphicsDropShadowEffect()
        self.shadow.setColor(QColor(0, 0, 0, 25))
        self.setGraphicsEffect(self.shadow)
        
        self._update_styling()

    def boundingRect(self) -> QRectF:
        """Required for QGraphicsObject rendering and collision."""
        return QRectF(0, 0, self.width, self.height)

    def shape(self) -> QPainterPath:
        """Provides precise bounds for hover and click detection."""
        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 8, 8)
        return path

    def _update_styling(self):
        """Updates colors and shadow elevation based on state and hover."""
        if self.is_active:
            self.bg_color = QColor(219, 234, 254, 150) if self.is_hovered else QColor(Qt.GlobalColor.transparent)
            self.border_color = QColor(Qt.GlobalColor.transparent)
            self.text_color = QColor("#1E3A8A")
            self.dot_color = QColor("#3B82F6")
            self.shadow.setEnabled(False) 
        elif self.is_undone:
            self.bg_color = QColor("#F8FAFC") if not self.is_hovered else QColor("#F1F5F9")
            self.border_color = QColor("#CBD5E1")
            self.text_color = QColor("#94A3B8")
            self.dot_color = self.border_color
            self.shadow.setEnabled(self.is_hovered)
        else:
            self.bg_color = QColor("#FFFFFF") if not self.is_hovered else QColor("#F8FAFC")
            self.border_color = QColor("#94A3B8")
            self.text_color = QColor("#334155")
            self.dot_color = self.border_color
            self.shadow.setEnabled(True)
        
        if not self.is_active:
            if self.is_hovered:
                self.shadow.setBlurRadius(18)
                self.shadow.setOffset(0, 5)
            else:
                self.shadow.setBlurRadius(10)
                self.shadow.setOffset(0, 3)

    def hoverEnterEvent(self, event):
        self.is_hovered = True
        self._update_styling()
        self.update()
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event):
        self.is_hovered = False
        self._update_styling()
        self.update()
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.index)
            event.accept()
        else:
            super().mousePressEvent(event)

    def paint(self, painter: QPainter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(self.boundingRect(), 8, 8)
        
        painter.fillPath(path, QBrush(self.bg_color))
        
        pen = QPen(self.border_color, 1.5)
        if self.is_undone and not self.is_active:
            pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(pen)
        painter.drawPath(path)
        
        dot_radius = 4.5
        dot_x = 18.0
        dot_y = self.height / 2
        
        painter.setBrush(QBrush(self.dot_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(dot_x, dot_y), dot_radius, dot_radius)
        
        font = QFont("Inter", 9)
        if self.is_active:
            font.setWeight(QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(self.text_color)
        
        metrics = QFontMetrics(font)
        text_width_limit = int(self.width - 45)
        elided_text = metrics.elidedText(self.label, Qt.TextElideMode.ElideRight, text_width_limit)
        
        text_rect = metrics.boundingRect(elided_text)
        x = 34.0
        y = (self.height + text_rect.height()) / 2 - metrics.descent()
        
        painter.drawText(QPointF(x, y), elided_text)


class PipelineGraphView(QGraphicsView):
    """A visual node-based representation of the data transformation history."""
    node_selected = pyqtSignal(int)

    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        
        self.graph_scene = QGraphicsScene(self)
        self.setScene(self.graph_scene)
        
        self.setMouseTracking(True)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setObjectName("PipelineGraphView")
        self.setProperty("styleClass", "transparent_scroll_area")
        
        self.nodes: List[GraphNode] = []
        self.edges: List[QGraphicsPathItem] = []
        self.focus_selector = None
        self.current_index = 0
        self.max_index = 0
        self._scroll_animation = None
        self._pill_animation = None
    
    def _set_view_center(self, center: QPointF):
        self.centerOn(center)
    
    def _get_view_center(self) -> QPointF:
        return self.mapToScene(self.viewport().rect().center())
    
    viewCenter = pyqtProperty(QPointF, fget=_get_view_center, fset=_set_view_center)
    
    def center_on_animated(self, item: QGraphicsObject):
        if self._scroll_animation:
            self._scroll_animation.stop()
        
        self._scroll_animation = QPropertyAnimation(self, b"viewCenter")
        self._scroll_animation.setDuration(600)
        self._scroll_animation.setStartValue(self.viewCenter)
        self._scroll_animation.setEndValue(item.sceneBoundingRect().center())
        self._scroll_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._scroll_animation.start()
    
    def drawBackground(self, painter: QPainter, rect: QRectF):
        painter.fillRect(rect, QColor("#F8FAFC"))
        
        grid_size = 20
        dot_color = QColor("#CBD5E1")
        dot_radius = 1.0
        
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(dot_color)
        
        for x in range(left, int(rect.right()), grid_size):
            for y in range(top, int(rect.bottom()), grid_size):
                painter.drawEllipse(QPointF(x, y), dot_radius, dot_radius)
    
    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier:
            zoom_in_factor = 1.15
            zoom_out_factor = 1.0 / zoom_in_factor
            
            old_scene_pos = self.mapToScene(event.position().toPoint())
            
            if event.angleDelta().y() > 0:
                self.scale(zoom_in_factor, zoom_in_factor)
            else:
                self.scale(zoom_out_factor, zoom_out_factor)
            
            new_scene_pos = self.mapToScene(event.position().toPoint())
            delta = new_scene_pos - old_scene_pos
            self.translate(delta.x(), delta.y())
            
            event.accept()
        else:
            super().wheelEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.MiddleButton:
            self.resetTransform()
            if self.nodes and 0 <= self.current_index < len(self.nodes):
                self.center_on_animated(self.nodes[self.current_index])
            event.accept()
        else:
            super().mousePressEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Up:
            if self.current_index > 0:
                self._handle_node_clicked(self.current_index - 1)
                event.accept()
        elif event.key() == Qt.Key.Key_Down:
            if self.current_index < self.max_index:
                self._handle_node_clicked(self.current_index + 1)
                event.accept()
        elif event.key() == Qt.Key.Key_F:
            scene_rect = self.graph_scene.itemsBoundingRect()
            scene_rect.adjust(-20, -20, 20, 20)
            self.fitInView(scene_rect, Qt.AspectRatioMode.KeepAspectRatio)
            event.accept()
        else:
            super().keyPressEvent(event)

    def build_graph(self, history_operations: List[Dict[str, Any]], current_index: int, format_func: Callable):
        """Constructs nodes and paths for the entire operation pipeline."""
        needs_full_rebuild = len(self.nodes) != len(history_operations) + 1
        if not needs_full_rebuild:
            for i, op in enumerate(history_operations):
                if self.nodes[i+1].operation != op:
                    needs_full_rebuild = True
                    break

        if not needs_full_rebuild:
            self._update_selection_in_place(current_index)
            return

        # 2. Full Rebuild
        self.graph_scene.clear()
        self.nodes.clear()
        self.edges.clear()
        self.focus_selector = None
        self.current_index = current_index
        self.max_index = len(history_operations)

        y_offset = 20.0
        x_pos = 20.0
        vertical_spacing = 25.0
        active_node_item = None

        # Create initial state node
        initial_node = GraphNode(0, "0. Initial Data", {}, current_index == 0, current_index < 0)
        initial_node.setPos(x_pos, y_offset)
        initial_node.clicked.connect(self._handle_node_clicked)
        self.graph_scene.addItem(initial_node)
        self.nodes.append(initial_node)
        
        if current_index == 0:
            active_node_item = initial_node

        y_offset += initial_node.height + vertical_spacing
        prev_node = initial_node

        for i, operation in enumerate(history_operations):
            hist_idx = i + 1
            op_text = format_func(operation)
            label = f"{hist_idx}. {op_text}"
            
            is_active = (hist_idx == current_index)
            is_undone = (hist_idx > current_index)

            node = GraphNode(hist_idx, label, operation, is_active, is_undone)
            node.setPos(x_pos, y_offset)
            node.clicked.connect(self._handle_node_clicked)
            self.graph_scene.addItem(node)
            self.nodes.append(node)

            if is_active:
                active_node_item = node

            # Draw directional edge connecting the nodes
            edge = QGraphicsPathItem()
            path = QPainterPath()
            start_pt = QPointF(x_pos + node.width / 2, prev_node.y() + prev_node.height)
            end_pt = QPointF(x_pos + node.width / 2, node.y())
            
            path.moveTo(start_pt)
            path.lineTo(end_pt)
            edge.setPath(path)
            
            # Color the edge blue if it leads to a done/active state, otherwise gray/dashed
            if is_undone:
                edge_pen = QPen(QColor("#CBD5E1"), 2, Qt.PenStyle.DashLine)
            else:
                edge_pen = QPen(QColor("#3B82F6"), 2.5, Qt.PenStyle.SolidLine)
            
            edge.setPen(edge_pen)
            
            # Ensure edges render behind the shadow effects and the sliding focus selector
            edge.setZValue(-2)
            self.graph_scene.addItem(edge)
            self.edges.append(edge)

            prev_node = node
            y_offset += node.height + vertical_spacing

        # Expand scene to encompass nodes and styling paddings
        self.setSceneRect(0, 0, x_pos + 260 + 20, y_offset + 20)

        if active_node_item:
            new_y = active_node_item.y()
            self.focus_selector = FocusHighlightItem(260.0, 48.0)
            self.focus_selector.setPos(x_pos, new_y)
            self.graph_scene.addItem(self.focus_selector)

        # Smoothly focus the viewport on the active state
        if active_node_item:
            self.center_on_animated(active_node_item)
    
    def _handle_node_clicked(self, index: int):
        if self.current_index != index:
            self._update_selection_in_place(index)
            self.node_selected.emit(index)
    
    def _update_selection_in_place(self, new_index: int):
        if not self.nodes or not self.focus_selector:
            return
        
        old_y = self.focus_selector.y()
        new_y = None
        self.current_index = new_index
        
        for node in self.nodes:
            node.is_active = (node.index == new_index)
            node.is_undone = (node.index > new_index)
            node._update_styling()
            node.update()
            
            if node.is_active:
                new_y = node.y()
        
        for i, edge in enumerate(self.edges):
            target_idx = i + 1
            is_undone = target_idx > new_index
            if is_undone:
                edge.setPen(QPen(QColor("#CBD5E1"), 2, Qt.PenStyle.DashLine))
            else:
                edge.setPen(QPen(QColor("#3B82F6"), 2.5, Qt.PenStyle.SolidLine))
            
        if old_y is not None and new_y is not None and old_y != new_y:
            if self._pill_animation:
                self._pill_animation.stop()
            
            self._pill_animation = QPropertyAnimation(self.focus_selector, b"animated_pos")
            self._pill_animation.setDuration(400)
            self._pill_animation.setStartValue(QPointF(self.focus_selector.x(), old_y))
            self._pill_animation.setEndValue(QPointF(self.focus_selector.x(), new_y))
            self._pill_animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
            self._pill_animation.start()
        
        if 0 <= new_index < len(self.nodes):
            self.center_on_animated(self.nodes[new_index])