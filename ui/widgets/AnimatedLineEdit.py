from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QLineEdit
from ui.widgets.mixins import HoverFocusAnimationMixin


class DataPlotStudioLineEdit(HoverFocusAnimationMixin, QLineEdit):
    """A QLineEdit with animations and effects"""

    def __init__(self, *args, **kwargs):
        QLineEdit.__init__(self, *args, **kwargs)
        HoverFocusAnimationMixin.__init__(self)
        self._update_stylesheet(self._base_border_color)

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