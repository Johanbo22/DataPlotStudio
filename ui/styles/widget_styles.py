
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
    LandingPageSubTitleLabel: str = "font-size: 16px; color: #7f8c8d; margin-bottom: 30px;"
    LandingPageWhatsNewInfoLabel: str = "background-color: white; border-radius: 15px; border: 1px solid #dfe6e9;"
    LandingPageWhatsNewInfoTitle: str = "font-size: 22px; font-weight: bold; color: #34495e; margin-bottom: 15px;"
    LandingPageVersionLabel: str = "font-size: 12px; font-weight: italic; color: #34495e; margin-bottom: 2px;"

