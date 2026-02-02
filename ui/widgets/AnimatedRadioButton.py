from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QRadioButton
from ui.widgets.mixins import HoverFocusAnimationMixin
from ui.theme import ThemeColors


class DataPlotStudioRadioButton(HoverFocusAnimationMixin, QRadioButton):
    """A QRadioButton with animated border color on hover/focus."""
    def __init__(self, *args, **kwargs):
        QRadioButton.__init__(self, *args, **kwargs)
        HoverFocusAnimationMixin.__init__(
            self, 
            base_color=ThemeColors.RADIO_BORDER_BASE,
            hover_color=ThemeColors.BORDER_FOCUS
        )

        self._update_stylesheet(self._base_border_color)

    def _update_stylesheet(self, color: QColor) -> None:

        # Use animated color for unchecked, focus color for checked
        border_color_name = self._focus_border_color.name() if self.isChecked() else color.name()

        dot_color = self._focus_border_color.name()
        bg_color = "#fcfcfc"
        checked_background = (
            f"qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5, "
            f"stop:0 {dot_color}, stop:0.6 {dot_color}, "
            f"stop:0.7 {bg_color}, stop:1 {bg_color})"
        )

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
                border-radius: 7px; 
                background-color: {bg_color};
            }}
            QRadioButton::indicator:checked {{
                background-color: {checked_background};
                border: 1.5px solid {self._focus_border_color.name()};
            }}
            
            QRadioButton::indicator:disabled {{
                background-color: #e0e0e0;
                border: 1px solid #b0b0b0;
            }}
            QRadioButton:disabled {{
                color: #a0a0a0;
            }}
        """)

    def setChecked(self, checked: bool) -> None:
        super().setChecked(checked)
        self._update_stylesheet(self._animated_color)

    def update(self) -> None:
        super().update()
        self._update_stylesheet(self._animated_color)