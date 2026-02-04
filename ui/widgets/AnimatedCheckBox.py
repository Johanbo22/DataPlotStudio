from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QCheckBox
from core.resource_loader import get_resource_path
from ui.widgets.mixins import HoverFocusAnimationMixin


class DataPlotStudioCheckBox(HoverFocusAnimationMixin, QCheckBox):
    """A QCheckBox with animated border color on hover/focus."""
    def __init__(self, *args, **kwargs):
        QCheckBox.__init__(self, *args, **kwargs)

        HoverFocusAnimationMixin.__init__(self)
        
        self._check_color = self._focus_border_color
        self._update_stylesheet(self._base_border_color)

    def _update_stylesheet(self, color: QColor) -> None:
        icon = get_resource_path("icons/ui_styling/checkmark.svg").replace("\\", "/")
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