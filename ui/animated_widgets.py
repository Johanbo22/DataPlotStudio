from PyQt6.QtWidgets import QPushButton, QGroupBox
from PyQt6.QtCore import QPropertyAnimation, QEasingCurve, pyqtProperty, Qt
from PyQt6.QtGui import QColor

class AnimatedButton(QPushButton):
    """Custom QPush Button that animates on hover. This is currently testing"""

    def __init__(self, 
                text,
                parent=None,
                base_color_hex: str = "#ededed",
                hover_color_hex: str = "#d8d8d8",
                pressed_color_hex: str = "#c6c6c6",
                text_color_hex: str = "#000000",
                border_style: str = "none",
                padding: str = "8px",
                border_radius: str = "4px",
                font_weight: str = "bold") -> None:
        super().__init__(text, parent)

        self._base_color = QColor(base_color_hex)
        self._hover_color = QColor(hover_color_hex)
        self._pressed_color = QColor(pressed_color_hex)
        self._text_color = QColor(text_color_hex)

        self._border_style = border_style
        self._padding = padding
        self._border_radius = border_radius
        self._font_weight = font_weight

        self._animated_color = self._base_color

        self.enter_animation = QPropertyAnimation(self, b"animated_color")
        self.enter_animation.setDuration(150)
        self.enter_animation.setEndValue(self._hover_color)
        self.enter_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.leave_animation = QPropertyAnimation(self, b"animated_color")
        self.leave_animation.setDuration(250)
        self.leave_animation.setEndValue(self._base_color)
        self.leave_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_color)

    @pyqtProperty(QColor)
    def animated_color(self) -> QColor:
        """Get the current animated color."""
        return self._animated_color

    @animated_color.setter
    def animated_color(self, color: QColor) -> None:
        """Set the animated color and update the stylesheet."""
        self._animated_color = color
        self._update_stylesheet(color)
    
    def _update_stylesheet(self, color: QColor) -> None:
        """
        Updates the button's stylesheet based on its role (determined by base color)
        and the current animated color.
        """

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color.name()};
                color: {self._text_color.name()};
                font-weight: {self._font_weight};
                padding: {self._padding};
                border: {self._border_style};
                border-radius: {self._border_radius};
            }}
            QPushButton:pressed {{
                background-color: {self._pressed_color.name()};
            }}
        """)

    def enterEvent(self, event) -> None:
        """Called when the mouse enters the button widget."""
        self.leave_animation.stop()
        self.enter_animation.setStartValue(self.animated_color) # Start from current color
        self.enter_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Called when the mouse leaves the button widget."""
        self.enter_animation.stop()
        self.leave_animation.setStartValue(self.animated_color) # Start from current color
        self.leave_animation.start()
        super().leaveEvent(event)

    def updateColors(self,
                    base_color_hex: str,
                    hover_color_hex: str = None,
                    pressed_color_hex: str = None) -> None:
        """Method to preserve buttons color when using a qcolordialog"""
        self._base_color = QColor(base_color_hex)

        if hover_color_hex:
            self._hover_color = QColor(hover_color_hex)
        else:
            self._hover_color = (self._base_color.darker(110) if self._base_color.lightnessF() > 0.5 else self._base_color.lighter(130))
        
        if pressed_color_hex:
            self._pressed_color = QColor(pressed_color_hex)
        else:
            # 
            self._pressed_color = self._hover_color.darker(115)

        # Update the animation end values
        self.enter_animation.setEndValue(self._hover_color)
        self.leave_animation.setEndValue(self._base_color)

        #
        self.animated_color = self._base_color
        self._update_stylesheet(self._base_color)
        
class AnimatedGroupBox(QGroupBox):
    """GroupBox animation on hover"""

    def __init__(self, title, parent=None):
        super().__init__(title, parent)

        self._base_border_color = QColor("#c2c2c2")
        self._hover_border_color = QColor("#0078d7")
        self._animated_color = self._base_border_color

        # Animation for mouse entering
        self.enter_animation = QPropertyAnimation(self, b"animated_border_color")
        self.enter_animation.setDuration(150)
        self.enter_animation.setEndValue(self._hover_border_color)
        self.enter_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        # Animation for mouse leaving
        self.leave_animation = QPropertyAnimation(self, b"animated_border_color")
        self.leave_animation.setDuration(250)
        self.leave_animation.setEndValue(self._base_border_color)
        self.leave_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_border_color)

    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        """Get the current animated border color."""
        return self._animated_color

    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        """Set the animated color and update the stylesheet."""
        self._animated_color = color
        self._update_stylesheet(color)

    def _update_stylesheet(self, color: QColor) -> None:
        """Updates the groupbox stylesheet with the current animated border color."""
        self.setStyleSheet(f"""
            QGroupBox {{
                font-size: 14pt; 
                font-weight: bold;
                border: 1.5px solid {color.name()} !important; 
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                left: 10px;
                background-color: white; 
                top: -7px
            }}
        """)

    def enterEvent(self, event) -> None:
        """Called when the mouse enters the widget."""
        if self.isEnabled():
            self.leave_animation.stop()
            self.enter_animation.setStartValue(self.animated_border_color)
            self.enter_animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Called when the mouse leaves the widget."""
        self.enter_animation.stop()
        self.leave_animation.setStartValue(self.animated_border_color)
        self.leave_animation.start()
        super().leaveEvent(event)