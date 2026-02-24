from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox
from core.resource_loader import get_resource_path
from ui.widgets.mixins import HoverFocusAnimationMixin


class DataPlotStudioCheckBox(HoverFocusAnimationMixin, QCheckBox):
    """A QCheckBox with animated border color on hover/focus."""
    def __init__(self, *args, **kwargs):
        QCheckBox.__init__(self, *args, **kwargs)

        HoverFocusAnimationMixin.__init__(self)
        
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self._check_color = self._focus_border_color
        self._update_stylesheet(self._base_border_color)
    
    def set_accessibility_metadata(self, name: str, description: str = "") -> None:
        self.setAccessibleName(name)
        if description:
            self.setAccessibleDescription(description)
            self.setToolTip(description)

    def _update_stylesheet(self, color: QColor) -> None:
        icon = get_resource_path("icons/ui_styling/checkmark.svg").replace("\\", "/")
        
        palette: QPalette = self.palette()
        text_color: str = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText).name()
        base_bg: str = palette.color(QPalette.ColorGroup.Active, QPalette.ColorRole.Base).name()
        disabled_text: str = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText).name()
        disabled_bg: str = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base).name()
        disabled_border: str = palette.color(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid).name()
        
        self.setStyleSheet(f"""
            QCheckBox {{
                spacing: 8px;
                font-size: 11pt;
                color: {text_color};
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1.5px solid {color.name()};
                border-radius: 4px;
                background-color: {base_bg};
            }}
            QCheckBox::indicator:checked {{
                border-color: {self._focus_border_color.name()};
                background-color: {self._focus_border_color.name()};
                image: url({icon}); 
            }}
            QCheckBox::indicator:disabled {{
                background-color: {disabled_bg};
                border: 1px solid {disabled_border};
            }}
            QCheckBox:disabled {{
                color: {disabled_text};
            }}
        """)