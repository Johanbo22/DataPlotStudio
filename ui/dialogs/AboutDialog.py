from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QWidget
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from pathlib import Path

from core.resource_loader import get_resource_path
from ui.theme import ThemeColors
from ui.widgets import DataPlotStudioButton
from ui.icons import IconBuilder, IconType

class AboutDialog(QDialog):
    def __init__(self, parent: QWidget, application_version: str) -> None:
        super().__init__(parent)
        self.application_version: str = application_version
        self._init_ui()
        
    def _init_ui(self) -> None:
        self.setObjectName("aboutDialog")
        self.setWindowTitle("About DataPlotStudio")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(32, 32, 32, 24)
        main_layout.setSpacing(16)
        
        # App header
        header_layout = QHBoxLayout()
        header_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        header_layout.setSpacing(12)
        
        logo_label = QLabel()
        logo_pixmap = IconBuilder.build(IconType.AppIcon).pixmap(48, 48)
        if not logo_pixmap.isNull():
            logo_label.setPixmap(logo_pixmap.scaled(72, 72, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        logo_label.setPixmap(logo_pixmap)
        
        header_title = QLabel(f"DataPlotStudio")
        header_title.setObjectName("aboutHeaderLabel")
        
        version_label = QLabel(f"App. Ver. {self.application_version}")
        version_label.setObjectName("aboutVersionLabel")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(header_title)
        header_layout.addWidget(version_label)
        
        subtitle_label = QLabel("A data analysis and visualization tool built with Python and PyQt6.")
        subtitle_label.setObjectName("aboutSubtitleLabel")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setWordWrap(True)
        
        divider = QFrame()
        divider.setObjectName("aboutDivider")
        divider.setFrameShape(QFrame.Shape.HLine)
        divider.setFrameShadow(QFrame.Shadow.Sunken)
        
        features_text: str = (
            "• Import data from CSV, Excel, JSON, Google Sheets and databases\n"
            "• Transform and explore your data\n"
            "• Create 31 types of visualizations\n"
            "• Write custom Python code in the integrated editor\n"
            "• Export data after manipulation\n"
            "• Export code for sharing and customization"
        )
        features_label = QLabel(features_text)
        features_label.setObjectName("aboutFeaturesLabel")
        
        links_layout = QHBoxLayout()
        github_link = QLabel('<a href="https://github.com/Johanbo22/DataPlotStudio">Github Repository</a>')
        github_link.setObjectName("aboutGithubLink")
        github_link.setOpenExternalLinks(True)
        
        website_link = QLabel('<a href="https://www.data-plot-studio.com">Website</a>')
        website_link.setObjectName("aboutWebsiteLink")
        website_link.setOpenExternalLinks(True)
        
        links_layout.addWidget(github_link, alignment=Qt.AlignmentFlag.AlignLeft)
        links_layout.addStretch()
        links_layout.addWidget(website_link, alignment=Qt.AlignmentFlag.AlignRight)
        
        copyright_label = QLabel("Released under the GNU GPL-3 open source license.\n© DataPlotStudio")
        copyright_label.setObjectName("aboutCopyrightLabel")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        button_layout = QHBoxLayout()
        close_button = DataPlotStudioButton("Close", base_color_hex=ThemeColors.MainColor, text_color_hex="white")
        close_button.setObjectName("aboutCloseButton")
        close_button.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        main_layout.addLayout(header_layout)
        main_layout.addWidget(subtitle_label)
        main_layout.addWidget(divider)
        main_layout.addWidget(features_label)
        main_layout.addSpacing(12)
        main_layout.addLayout(links_layout)
        main_layout.addSpacing(12)
        main_layout.addWidget(copyright_label)
        main_layout.addSpacing(8)
        main_layout.addLayout(button_layout)

    @staticmethod
    def show_about_dialog(parent: QWidget, application_version: str) -> None:
        """Shows the about dialog"""
        dialog = AboutDialog(parent, application_version)
        dialog.exec()