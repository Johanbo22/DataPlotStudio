from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor, QMouseEvent, QPaintEvent, QPainter, QPen, QCursor
from PyQt6.QtWidgets import QSlider, QStyle, QStyleOptionSlider, QToolTip
from ui.widgets.mixins import HoverFocusAnimationMixin
from ui.theme import ThemeColors


class DataPlotStudioSlider(HoverFocusAnimationMixin, QSlider):
    """New qslider"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        if not isinstance(orientation, Qt.Orientation):
            parent = orientation
            orientation = Qt.Orientation.Horizontal

        QSlider.__init__(self, orientation, parent)
        HoverFocusAnimationMixin.__init__(self)
        
        if orientation == Qt.Orientation.Horizontal:
            self.setMinimumHeight(40)
        else:
            self.setMinimumWidth(40)
            
        if self.tickPosition() == QSlider.TickPosition.NoTicks:
            self.setTickPosition(QSlider.TickPosition.TicksBelow)
        self._update_stylesheet(self._base_border_color)

    def _update_stylesheet(self, color: QColor) -> None:
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {ThemeColors.SLIDER_GROOVE_BORDER.name()};
                height: 4px;
                background: #f0f0f0;
                margin: 0px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 1.5px solid {color.name()};
                width: 16px;
                height: 16px;
                margin: -7px 0;
                border-radius: 9px;
            }}
            QSlider::groove:vertical {{
                border: 1px solid {ThemeColors.SLIDER_GROOVE_BORDER.name()};
                width: 4px;
                background: #f0f0f0;
                margin: 0 0px;
                border-radius: 2px;
            }}
            QSlider::handle:vertical {{
                background: white;
                border: 1.5px solid {color.name()};
                height: 16px;
                width: 16px;
                margin: 0 -7px;
                border-radius: 9px;
            }}
            QToolTip {{
                color: #ffffff;
                background-color: #2b2b2b;
                border: 1px solid #555555;
                font-size: 10pt;
                padding: 4px;
            }}
        """)
    
    def mousePressevent(self, event: QMouseEvent) -> None:
        """Enables click to jump behaviour
        Clicking on groove moves the value to that point"""
        if event.button() == Qt.MouseButton.LeftButton:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            style = self.style()
            
            handle_rect = style.subControlRect(
                QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self
            )
            
            # If clicked outside the handle
            # jumpt to the clicked position
            if not handle_rect.contains(event.pos()):
                new_val = style.sliderValueFromPosition(
                    self.minimum(),
                    self.maximum(),
                    event.pos() if self.orientation() == Qt.Orientation.Horizontal else event.pos().y(),
                    self.width() if self.orientation() == Qt.Orientation.Horizontal else self.height(),
                    self.invertedAppearance()
                )
                self.setValue(new_val)
        super().mousePressEvent(event)

        # also show the tooltip for the value
        if self.isEnabled():
            self._show_value_tooltip()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Update tooltip position and value while dragging"""
        super().mouseMoveEvent(event)
        self._show_value_tooltip()
    
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        """Hide tooltip on release"""
        super().mouseReleaseEvent(event)
        QToolTip.hideText()
    
    def _show_value_tooltip(self) -> None:
        """Update the text, position of the tooltip for the value"""
        val_str = str(self.value())
        
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = self.style()
        
        handle_rect = style.subControlRect(
            QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderHandle, self
        )
        
        if handle_rect.isValid():
            global_pos = self.mapToGlobal(handle_rect.center())
            tooltip_pos = global_pos - QPoint(0, 35)
            QToolTip.showText(tooltip_pos, val_str, self)
        else:
            QToolTip.showText(QCursor.pos(), val_str, self)
            
    
    def paintEvent(self, event: QPaintEvent) -> None:
        """
        Custom paint to draw tick marks on groove
        """
        super().paintEvent(event)
        
        tick_pos = self.tickPosition()
        if tick_pos == QSlider.TickPosition.NoTicks:
            return
        
        painter = QPainter(self)
        painter.setPen(QPen(QColor("#a0a0a0"), 1))
        
        # Determine tickinterval
        interval = self.tickInterval()
        if interval == 0:
            interval = self.pageStep()
        
        if interval <= 0:
            return
        
        opt = QStyleOptionSlider()
        self.initStyleOption(opt)
        style = self.style()
        
        groove_rect = style.subControlRect(
            QStyle.ComplexControl.CC_Slider, opt, QStyle.SubControl.SC_SliderGroove, self
        )
        
        val = self.minimum()
        max_val = self.maximum()
        steps = (max_val - val) / interval
        if steps > 1000:
            interval = (max_val - val) // 100
        
        if val > max_val:
            return
        
        while val <= max_val:
            temp_opt = QStyleOptionSlider(opt)
            temp_opt.sliderPosition = val
            temp_opt.sliderValue = val
            
            handle_rect = style.subControlRect(
                QStyle.ComplexControl.CC_Slider, temp_opt, QStyle.SubControl.SC_SliderHandle, self
            )
            
            center = handle_rect.center()
            
            if self.orientation() == Qt.Orientation.Horizontal:
                
                if tick_pos in (QSlider.TickPosition.TicksAbove, QSlider.TickPosition.TicksBothSides):
                    painter.drawLine(center.x(), center.y() - 10, center.x(), center.y() - 15)
                
                if tick_pos in (QSlider.TickPosition.TicksBelow, QSlider.TickPosition.TicksBothSides):
                    painter.drawLine(center.x(), center.y() + 10, center.x(), center.y() + 15)
                    
            else:
                if tick_pos in (QSlider.TickPosition.TicksLeft, QSlider.TickPosition.TicksBothSides):
                    painter.drawLine(center.x() - 10, center.y(), center.x() - 15, center.y())
                
                if tick_pos in (QSlider.TickPosition.TicksRight, QSlider.TickPosition.TicksBothSides):
                    painter.drawLine(center.x() + 10, center.y(), center.x() + 15, center.y())
            
            val += interval