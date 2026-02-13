from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFileDialog,
    QMessageBox,
    QFormLayout,
    QWidget,
    QSizePolicy
)
from PyQt6.QtCore import Qt, QRectF, QPointF
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QColor, QPen, QBrush, QFont
import pandas as pd
from pathlib import Path

class VennDiagramWidget(QWidget):
    """Custom widget to visualize a venn diagram for merging datasets"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(400, 220)  # Increased height to comfortably fit text
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.join_type = "inner"
        self.left_count = 0
        self.right_count = 0
        self.result_count = 0
        
        # Theme colors
        self.color_active = QColor("#3498DB")  # DataPlotStudio Blue
        self.color_inactive = QColor("#ECF0F1") # Light Grey
        self.color_outline = QColor("#7F8C8D")  # Darker Grey
        self.text_color = QColor("#2C3E50")
        
    def set_data(self, join_type, left_c, right_c, res_c):
        """Update the diagram data and trigger repaint."""
        self.join_type = join_type.lower()
        self.left_count = left_c
        self.right_count = right_c
        self.result_count = res_c
        self.repaint() # Force immediate repaint
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        rect = self.rect()
        width = rect.width()
        height = rect.height()
        
        # Responsive Geometry calculations
        # Leave 50px at top for title, 40px at bottom for labels
        available_height = height - 90 
        radius = min(width / 4, available_height / 2)
        offset = radius * 0.75  # The perfect ratio for a classic Venn overlap
        
        center_y = 50 + (available_height / 2)
        c1 = QPointF(width / 2 - offset, center_y)
        c2 = QPointF(width / 2 + offset, center_y)
        
        # Create base shapes
        path_left = QPainterPath()
        path_left.addEllipse(c1, radius, radius)
        
        path_right = QPainterPath()
        path_right.addEllipse(c2, radius, radius)
        
        # Create distinct Venn diagram segments
        path_intersect = path_left.intersected(path_right)
        path_left_only = path_left.subtracted(path_right)
        path_right_only = path_right.subtracted(path_left)
        
        # Set up transparent colors for a better visual blend
        active_color = QColor(self.color_active)
        active_color.setAlpha(180)  # ~70% opacity
        
        inactive_color = QColor(self.color_inactive)
        inactive_color.setAlpha(100) # ~40% opacity
        
        brush_left = QBrush(inactive_color)
        brush_right = QBrush(inactive_color)
        brush_inner = QBrush(inactive_color)
        
        # Determine segment colors based on join type
        if self.join_type == "inner":
            brush_inner = QBrush(active_color)
        elif self.join_type == "left":
            brush_left = QBrush(active_color)
            brush_inner = QBrush(active_color)
        elif self.join_type == "right":
            brush_right = QBrush(active_color)
            brush_inner = QBrush(active_color)
        elif self.join_type == "outer":
            brush_left = QBrush(active_color)
            brush_right = QBrush(active_color)
            brush_inner = QBrush(active_color)
            
        # Draw the segments
        painter.setPen(Qt.PenStyle.NoPen)
        
        painter.setBrush(brush_left)
        painter.drawPath(path_left_only)
        
        painter.setBrush(brush_right)
        painter.drawPath(path_right_only)
        
        painter.setBrush(brush_inner)
        painter.drawPath(path_intersect)
        
        # Redraw outlines over everything for crispness
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.color_outline, 2))
        painter.drawPath(path_left)
        painter.drawPath(path_right)
        
        # Draw Text info
        painter.setPen(self.text_color)
        
        # Result Header (Top center)
        font = QFont()
        font.setPointSize(11)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(0, 5, width, 25), Qt.AlignmentFlag.AlignCenter, f"Resulting Rows: {self.result_count}")
        
        # Join Type Subtitle
        font.setPointSize(9)
        font.setBold(False)
        painter.setFont(font)
        painter.drawText(QRectF(0, 25, width, 20), Qt.AlignmentFlag.AlignCenter, f"({self.join_type.capitalize()} Join)")
        
        # Dataset Labels (Bottom, centered accurately under each circle)
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        text_y = center_y + radius + 10
        painter.drawText(QRectF(c1.x() - radius, text_y, radius * 2, 20), Qt.AlignmentFlag.AlignCenter, f"Current: {self.left_count}")
        painter.drawText(QRectF(c2.x() - radius, text_y, radius * 2, 20), Qt.AlignmentFlag.AlignCenter, f"New: {self.right_count}")