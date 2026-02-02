from PyQt6.QtGui import QColor

class ThemeColors:
    """
    Central config for DataPlotStudio theme colors
    """
    
    # Border colors
    BORDER_BASE = QColor("#a0a0a0")
    BORDER_HOVER = QColor("#707070")
    BORDER_FOCUS = QColor("#0078d7")
    
    # Widget overrides
    RADIO_BORDER_BASE = QColor("#777777")
    LIST_BORDER_BASE = QColor("#c2c2c2")
    SLIDER_GROOVE_BORDER = QColor("#c2c2c2")
    
    # Text colors
    TEXT_PRIMARY = QColor("#333333")
    TEXT_DISABLED = QColor("#a0a0a0")
    
    # Background colors
    BG_WHITE = QColor("#ffffff")
    BG_LIGHT_GRAY = QColor("#f0f0f0")
    
    # Indicators
    ACCENT_COLOR = BORDER_FOCUS