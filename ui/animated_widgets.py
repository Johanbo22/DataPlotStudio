from PyQt6.QtWidgets import QPushButton, QGroupBox, QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox, QRadioButton
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
    
class AnimatedLineEdit(QLineEdit):
    """A QLineEdit with animations and effects"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._base_border_color = QColor("#a0a0a0")
        self._hover_border_color = QColor("#707070")
        self._focus_border_color = QColor("#0078d7")
        
        self._animated_color = self._base_border_color
        self._is_focussed = False

        self.animation = QPropertyAnimation(self, b"animated_border_color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_border_color)

    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        return self._animated_color
    
    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        self._animated_color = color
        self._update_stylesheet(color)
    
    def _update_stylesheet(self, color: QColor) -> None:
        self.setStyleSheet(f"""
            QLineEdit {{
                border: 1.5px solid {color.name()};
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                background-color: white;
            }}
        """)
    
    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()
    
    def enterEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._hover_border_color)
        super().enterEvent(event)
    
    def leaveEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._base_border_color)
        super().leaveEvent(event)
    
    def focusInEvent(self, event) -> None:
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().focusInEvent(event)
    
    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if self.underMouse():
            self._animate_to(self._hover_border_color)
        else:
            self._animate_to(self._base_border_color)
        super().focusOutEvent(event)

class AnimatedComboBox(QComboBox):
    """A Combobox with animated borders and arrow"""
    def __init__(self, parent=None):
        super().__init__(parent)

        self._base_border_color = QColor("#a0a0a0")
        self._hover_border_color = QColor("#707070")
        self._focus_border_color = QColor("#0078d7")

        self._animated_color = self._base_border_color
        self._is_focussed = False

        self.animation = QPropertyAnimation(self, b"animated_border_color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_border_color)

    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        return self._animated_color

    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        self._animated_color = color
        self._update_stylesheet(color)

    def _update_stylesheet(self, color: QColor) -> None:
        arrow_icon_path = "icons/ui_styling/arrow_down.png" 
        
        self.setStyleSheet(f"""
            QComboBox {{
                border: 1.5px solid {color.name()};
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
                background-color: white;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 15px;
                border-left-width: 1px;
                border-left-color: {color.name()};
                border-left-style: solid; 
                border-top-right-radius: 3px; 
                border-bottom-right-radius: 3px;
                background-color: #f0f0f0;
            }}
            QComboBox::drop-down:hover {{
                background-color: #e0e0e0;
            }}
            QComboBox::down-arrow {{
                image: url({arrow_icon_path});
                width: 9px;
                height: 9px;
            }}
            QComboBox:on {{ 
                border: 1.5px solid {self._focus_border_color.name()};
            }}
        """)
    
    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()

    def enterEvent(self, event) -> None:
        if not self._is_focussed and not self.view().isVisible():
            self._animate_to(self._hover_border_color)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._is_focussed and not self.view().isVisible():
            self._animate_to(self._base_border_color)
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if not self.view().isVisible():
            if self.underMouse():
                self._animate_to(self._hover_border_color)
            else:
                self._animate_to(self._base_border_color)
        super().focusOutEvent(event)

    def showPopup(self):
        self._is_focussed = True 
        self._animate_to(self._focus_border_color)
        super().showPopup()

    def hidePopup(self):
        super().hidePopup()
        self._is_focussed = False
        self.focusOutEvent(None)

class AnimatedSpinBox(QSpinBox):
    """A QSpinBox with animated border color on hover/focus."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self._base_border_color = QColor("#a0a0a0")
        self._hover_border_color = QColor("#707070")
        self._focus_border_color = QColor("#0078d7")

        self._animated_color = self._base_border_color
        self._is_focussed = False

        self.animation = QPropertyAnimation(self, b"animated_border_color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_border_color)

    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        return self._animated_color

    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        self._animated_color = color
        self._update_stylesheet(color)

    def _update_stylesheet(self, color: QColor) -> None:
        self.setStyleSheet(f"""
            QSpinBox {{
                border: 1.5px solid {color.name()};
                border-radius: 3px;
                padding: 1px 4px 1px 3px;
                min-width: 2em;
                background-color: white;
            }}
            QSpinBox::up-button, QSpinBox::down-button {{
                border-width: 0px;
            }}
        """)

    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()

    def enterEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._hover_border_color)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._base_border_color)
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if self.underMouse():
            self._animate_to(self._hover_border_color)
        else:
            self._animate_to(self._base_border_color)
        super().focusOutEvent(event)

class AnimatedDoubleSpinBox(QDoubleSpinBox):
    """A QDoubleSpinBox with animated border color on hover/focus."""
    def __init__(self, parent=None):
        super().__init__(parent)

        self._base_border_color = QColor("#a0a0a0")
        self._hover_border_color = QColor("#707070")
        self._focus_border_color = QColor("#0078d7")

        self._animated_color = self._base_border_color
        self._is_focussed = False

        self.animation = QPropertyAnimation(self, b"animated_border_color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_border_color)

    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        return self._animated_color

    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        self._animated_color = color
        self._update_stylesheet(color)

    def _update_stylesheet(self, color: QColor) -> None:
        self.setStyleSheet(f"""
            QDoubleSpinBox {{
                border: 1.5px solid {color.name()};
                border-radius: 3px;
                padding: 1px 4px 1px 3px;
                min-width: 2em;
                background-color: white;
            }}
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
                border-width: 0px;
            }}
        """)

    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()

    def enterEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._hover_border_color)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._base_border_color)
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if self.underMouse():
            self._animate_to(self._hover_border_color)
        else:
            self._animate_to(self._base_border_color)
        super().focusOutEvent(event)

class AnimatedCheckBox(QCheckBox):
    """A QCheckBox with animated border color on hover/focus."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._base_border_color = QColor("#a0a0a0")
        self._hover_border_color = QColor("#707070")
        self._focus_border_color = QColor("#0078d7") # Blue from css
        self._check_color = self._focus_border_color

        self._animated_color = self._base_border_color
        self._is_focussed = False

        self.animation = QPropertyAnimation(self, b"animated_border_color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_border_color)

    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        return self._animated_color

    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        self._animated_color = color
        self._update_stylesheet(color)

    def _update_stylesheet(self, color: QColor) -> None:
        # We define a complete style here, similar to your QRadioButton
        icon = "icons/ui_styling/checkmark.png"
        self.setStyleSheet(f"""
            QCheckBox {{
                spacing: 5px;
                font-size: 11pt;
                color: #333;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                border: 1.5px solid {color.name()};
                border-radius: 3px;
                background-color: #fcfcfc;
            }}
            QCheckBox::indicator:checked {{
                border-color: {self._focus_border_color.name()};
                background-color: {self._focus_border_color.name()};
                image: url({icon}); 
            }}
            QCheckBox::indicator:disabled {{
                background-color: #e0e0e0;
                border: 1px solid #b0b0b0;
            }}
            QCheckBox:disabled {{
                color: #a0a0a0;
            }}
        """)
        
    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()

    def enterEvent(self, event) -> None:
        if not self._is_focussed and self.isEnabled():
            self._animate_to(self._hover_border_color)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._base_border_color)
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if self.underMouse():
            self._animate_to(self._hover_border_color)
        else:
            self._animate_to(self._base_border_color)
        super().focusOutEvent(event)

class AnimatedRadioButton(QRadioButton):
    """A QRadioButton with animated border color on hover/focus."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._base_border_color = QColor("#777")
        self._hover_border_color = QColor("#0078d7") # Blue from css
        self._focus_border_color = QColor("#0078d7")
        
        self._animated_color = self._base_border_color
        self._is_focussed = False

        self.animation = QPropertyAnimation(self, b"animated_border_color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self._update_stylesheet(self._base_border_color)

    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        return self._animated_color

    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        self._animated_color = color
        self._update_stylesheet(color)

    def _update_stylesheet(self, color: QColor) -> None:
        # This style is based on your style.css
        
        # Use animated color for unchecked, focus color for checked
        border_color_name = self._focus_border_color.name() if self.isChecked() else color.name()
        
        self.setStyleSheet(f"""
            QRadioButton {{
                spacing: 5px;
                font-size: 11pt;
                color: #333;
            }}
            QRadioButton::indicator {{
                width: 13px;
                height: 13px;
                border: 1.5px solid {border_color_name};
                border-radius: 7px; /* Makes it a circle */
                background-color: #fcfcfc;
            }}
            QRadioButton::indicator:checked {{
                background-color: #fcfcfc;
                border: 1.5px solid {self._focus_border_color.name()};
            }}
            QRadioButton::indicator:checked::after {{
                content: '';
                display: block;
                width: 9px;
                height: 9px;
                border-radius: 4.5px;
                background-color: {self._focus_border_color.name()};
                margin: 2px; /* Centers the dot */
            }}
            QRadioButton::indicator:disabled {{
                background-color: #e0e0e0;
                border: 1px solid #b0b0b0;
            }}
            QRadioButton:disabled {{
                color: #a0a0a0;
            }}
        """)

    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()

    def enterEvent(self, event) -> None:
        if not self._is_focussed and self.isEnabled():
            self._animate_to(self._hover_border_color)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._base_border_color)
        super().leaveEvent(event)

    def focusInEvent(self, event) -> None:
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().focusInEvent(event)

    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if self.underMouse():
            self._animate_to(self._hover_border_color)
        else:
            self._animate_to(self._base_border_color)
        super().focusOutEvent(event)

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self._update_stylesheet(self._animated_color)

    def update(self) -> None:
        super().update()
        self._update_stylesheet(self._animated_color)