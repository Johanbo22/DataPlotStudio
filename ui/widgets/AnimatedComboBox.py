from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QComboBox
from ui.widgets.mixins import HoverFocusAnimationMixin


class DataPlotStudioComboBox(HoverFocusAnimationMixin, QComboBox):
    """A Combobox with animated borders and arrow"""
    def __init__(self, parent=None):
        QComboBox.__init__(self, parent)
        HoverFocusAnimationMixin.__init__(self)

        self._update_stylesheet(self._base_border_color)

    def _update_stylesheet(self, color: QColor) -> None:
        arrow_icon_path = "icons/ui_styling/arrow-down-to-line.svg"

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

    # an override for combobox
    def enterEvent(self, event) -> None:
        if not self._is_focussed and not self.view().isVisible():
            self._animate_to(self._hover_border_color)
        QComboBox.enterEvent(self, event)
    
    def leaveEvent(self, event) -> None:
        if not self._is_focussed and not self.view().isVisible():
            self._animate_to(self._base_border_color)
        QComboBox.leaveEvent(self, event)
    
    def focusOutEvent(self, event) -> None:
        self._is_focussed = False
        if not self.view().isVisible():
            if self.underMouse():
                self._animate_to(self._hover_border_color)
            else:
                self._animate_to(self._base_border_color)
        if event is not None:
            QComboBox.focusOutEvent(self, event)

    def showPopup(self):
        self._is_focussed = True
        self._animate_to(self._focus_border_color)
        super().showPopup()

    def hidePopup(self):
        super().hidePopup()
        self._is_focussed = False
        self.focusOutEvent(None)