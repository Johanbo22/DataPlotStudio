
class ToolBox:
    PlotToolBoxStylesheet: str = """
    QToolBox::tab {
        background: #E0E0E0;
        border-radius: 2px;
        color: #333;
        font-weight: bold;
        padding-left: 5px;
    }
    QToolBox::tab:selected { 
        background: #D0D0D0;
        color: black;
    }
"""
class Label:
    LandingPageTitleLabel: str = "font-size: 36px; font-weight: bold; color: #2c3e50;"
    LandingPageSubTitleLabel: str = "font-size: 12px; font-weight: bold; color: #95a5a6; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 30px;"
    LandingPageWhatsNewInfoLabel: str = "QFrame#InfoPanel { background-color: white; border-radius: 15px; border: 1px solid #dfe6e9; }"
    LandingPageWhatsNewInfoTitle: str = "font-size: 22px; font-weight: bold; color: #34495e;"
    LandingPageVersionLabel: str = "font-size: 11px; font-weight: bold; color: #2980b9; background-color: #ebf5fb; padding: 4px 10px; border-radius: 10px;"
    LandingPageSectionLabel: str = "color: #95a5a6; font-size: 11px; font-weight: bold; letter-spacing: 1px;"
    LandingPageInfoContentFontFamily: str = "font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 13px; color: #34495e;"
    LandingPageHeaderSeparator: str = "background-color: #dfe6e9; border: none; margin-top: 5px; margin-bottom: 10px;"

class ScrollArea:
    TransparentScrollArea: str = "QScrollArea { background-color: transparent; border: none; }"
    LandingPageScrollArea: str = """
        QScrollArea { 
            background-color: transparent; 
            border: none; 
        }
        QScrollBar:vertical {
            border: none;
            background: transparent;
            width: 8px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #bdc3c7;
            min-height: 30px;
            border-radius: 4px;
        }
        QScrollBar::handle:vertical:hover {
            background: #95a5a6;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
            background: none;
        }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
            background: transparent;
        }
        """

class Dialog:
    ChangelogViewer: str = """
            QDialog { 
                background-color: #f4f6f8; 
            }
            QTextBrowser { 
                background-color: white; 
                border: 1px solid #dfe6e9; 
                border-radius: 8px;
                padding: 15px;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
                font-size: 13px;
                color: #2c3e50;
            }
            QScrollBar:vertical {
                border: none;
                background: transparent;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #bdc3c7;
                min-height: 30px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical:hover {
                background: #95a5a6;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical,
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                height: 0px;
                background: none;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 24px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """