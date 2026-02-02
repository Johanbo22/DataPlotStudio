from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QListWidget
from ui.widgets.mixins import HoverFocusAnimationMixin
from ui.theme import ThemeColors


class DataPlotStudioListWidget(HoverFocusAnimationMixin, QListWidget):
    """New lsitwidget styling"""

    def __init__(self, parent=None):
        QListWidget.__init__(self, parent)
        HoverFocusAnimationMixin.__init__(
            self,
            base_color=ThemeColors.LIST_BORDER_BASE
        )
        self._update_stylesheet(self._base_border_color)

    def _update_stylesheet(self, color: QColor) -> None:
        self.setStyleSheet(f"""
            QListWidget {{
                border: 1.5px solid {color.name()}; 
                border-radius: 4px;
                padding: 4px;
                background-color: #ffffff; 
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 3px;
                margin: 2px 0; 
            }}
            QListWidget::item:hover {{
                background-color: #f0f0f0; 
            }}
            QListWidget::item:selected {{
                background-color: {self._focus_border_color.name()}; 
                color: #ffffff; 
            }}
            QListWidget::item:selected:hover {{
                background-color: #005fa3; 
            }}
        """)