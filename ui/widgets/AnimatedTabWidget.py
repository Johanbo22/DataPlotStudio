from PyQt6.QtWidgets import QTabWidget


class DataPlotStudioTabWidget(QTabWidget):
    """A QTabWidget subclass with a new stylesheet"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._set_stylesheet()

    def _set_stylesheet(self):
        self.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #c2c2c2;
                margin-top: -1px;
                border-radius: 0 0 4px 4px;
                padding: 10px;
                background-color: white;
            }
            
            QTabWidget::tab-bar {
                alignment: left;
                left: 10px;
            }
            
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #c2c2c2;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 12px;
                margin-right: 2px;
                color: #333333;
                font-weight: bold;
            }
            
            QTabBar::tab:hover {
                background: #e0e0e0;
            }

            QTabBar::tab:selected {
                background: white;
                border: 1px solid #c2c2c2;
                border-bottom: 1px solid white;
                color: #0078d7;
            }
            
            QTabBar::tab:!selected {
                margin-top: 3px;
            }
        """)