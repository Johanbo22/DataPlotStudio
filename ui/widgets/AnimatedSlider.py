from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QSlider
from ui.widgets.mixins import HoverFocusAnimationMixin
from ui.theme import ThemeColors


class DataPlotStudioSlider(HoverFocusAnimationMixin, QSlider):
    """New qslider"""

    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None):
        if not isinstance(orientation, Qt.Orientation):
            parent = orientation
            orientation = Qt.Orientation.Horizontal

        QSlider.__init__(self, orientation, parent)
        HoverFocusAnimationMixin.__init__(self)
        self._update_stylesheet(self._base_border_color)

    def _update_stylesheet(self, color: QColor) -> None:
        self.setStyleSheet(f"""
            QSlider::groove:horizontal {{
                border: 1px solid {ThemeColors.SLIDER_GROOVE_BORDER.name()};
                height: 4px;
                background: #f0f0f0;
                margin: 0px 0;
                border-radius: 2px;
            }}
            QSlider::handle:horizontal {{
                background: white;
                border: 1.5px solid {color.name()};
                width: 16px;
                height: 16px;
                margin: -7px 0;
                border-radius: 9px;
            }}
            QSlider::groove:vertical {{
                border: 1px solid {ThemeColors.SLIDER_GROOVE_BORDER.name()};
                width: 4px;
                background: #f0f0f0;
                margin: 0 0px;
                border-radius: 2px;
            }}
            QSlider::handle:vertical {{
                background: white;
                border: 1.5px solid {color.name()};
                height: 16px;
                width: 16px;
                margin: 0 -7px;
                border-radius: 9px;
            }}
        """)