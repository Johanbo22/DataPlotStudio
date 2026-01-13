from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty, QTimer
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QPushButton


class DataPlotStudioButton(QPushButton):
    """Custom QPush Button that animates on hover."""

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
                font_weight: str = "bold",
                typewriter_effect: bool = False) -> None:
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

        # Typewriter effect
        self._use_typewriter_effect = typewriter_effect
        self._full_text = text
        self._current_text_index = 0
        self._typewriter_timer = QTimer(self)
        self._typewriter_timer.setInterval(50)
        self._typewriter_timer.timeout.connect(self._update_typewriter_text)

        self.enter_animation = QPropertyAnimation(self, b"animated_color")
        self.enter_animation.setDuration(150)
        self.enter_animation.setEndValue(self._hover_color)
        self.enter_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.leave_animation = QPropertyAnimation(self, b"animated_color")
        self.leave_animation.setDuration(250)
        self.leave_animation.setEndValue(self._base_color)
        self.leave_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_color)

    def setText(self, text: str) -> None:
        self._full_text = text
        if self._typewriter_timer.isActive():
            self._current_text_index = 0
            super().setText("")
        else:
            super().setText(text)
    
    def _update_typewriter_text(self) -> None:
        if self._current_text_index <= len(self._full_text):
            super().setText(self._full_text[:self._current_text_index])
            self._current_text_index += 1
        else:
            self._typewriter_timer.stop()

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

        if self._use_typewriter_effect and self.isEnabled():
            self._current_text_index = 0
            super().setText("")
            self._typewriter_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        """Called when the mouse leaves the button widget."""
        self.enter_animation.stop()
        self.leave_animation.setStartValue(self.animated_color) # Start from current color
        self.leave_animation.start()

        if self._use_typewriter_effect:
            self._typewriter_timer.stop()
            super().setText(self._full_text)
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