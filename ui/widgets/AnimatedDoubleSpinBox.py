from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QDoubleSpinBox
from ui.widgets.mixins import HoverFocusAnimationMixin


class DataPlotStudioDoubleSpinBox(HoverFocusAnimationMixin, QDoubleSpinBox):
    """A QDoubleSpinBox with animated border color on hover/focus."""
    def __init__(self, parent=None):
        QDoubleSpinBox.__init__(self, parent)
        HoverFocusAnimationMixin.__init__(self)
        self._update_stylesheet(self._base_border_color)

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