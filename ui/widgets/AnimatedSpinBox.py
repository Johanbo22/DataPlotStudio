from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QSpinBox
from ui.widgets.mixins import HoverFocusAnimationMixin


class DataPlotStudioSpinBox(HoverFocusAnimationMixin, QSpinBox):
    """A QSpinBox with animated border color on hover/focus."""
    def __init__(self, parent=None):
        QSpinBox.__init__(self, parent)
        HoverFocusAnimationMixin.__init__(self)

        self._update_stylesheet(self._base_border_color)

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