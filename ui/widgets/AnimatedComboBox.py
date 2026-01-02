from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QComboBox


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