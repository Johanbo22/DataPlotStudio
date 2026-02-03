from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QScrollArea, QTextBrowser, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QAction
from pathlib import Path
import re

from ui.widgets.AnimatedButton import DataPlotStudioButton
from resources.version import APPLICATION_VERSION

class ChangelogViewer(QDialog):
    """
    Dialog to display parsed changelog content
    """
    def __init__(self, title: str, content_html: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(600, 500)
        self.setStyleSheet("""
            QDialog { background-color: white; }
            QTextBrowser { border: none; }
        """)
        
        layout = QVBoxLayout()
        
        self.browser = QTextBrowser()
        self.browser.setHtml(content_html)
        self.browser.setOpenExternalLinks(True)
        layout.addWidget(self.browser)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.close)
        layout.addWidget(button_box)
        self.setLayout(layout)

class LandingPage(QWidget):
    """Welcome page when the application starts"""
    open_project_clicked = pyqtSignal()
    import_file_clicked = pyqtSignal()
    import_sheets_clicked = pyqtSignal()
    import_db_clicked = pyqtSignal()
    new_dataset_clicked = pyqtSignal()
    quit_clicked = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # A left panel where most actions would be stored
        actions_panel = QWidget()
        actions_layout = QVBoxLayout(actions_panel)
        actions_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        actions_layout.setSpacing(20)

        # Logo and title
        title_label = QLabel("DataPlotStudio")
        title_label.setStyleSheet("font-size: 36px; font-weight: bold; color: #2c3e50;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        subtitle_label = QLabel("Data Manipulation and Visualization Tool")
        subtitle_label.setStyleSheet("font-size: 16px; color: #7f8c8d; margin-bottom: 30px;")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        actions_layout.addWidget(title_label)
        actions_layout.addWidget(subtitle_label)

        # Buttons
        button_width = 280

        self.button_open = DataPlotStudioButton("Open Existing Project", base_color_hex="#2980b9", text_color_hex="white", padding="12px", hover_color_hex="#3498db", pressed_color_hex="#1f6390", typewriter_effect=True)
        self.button_open.setIcon(QIcon("icons/menu_bar/folder-open.svg"))
        self.button_open.setFixedWidth(button_width)
        self.button_open.clicked.connect(self.open_project_clicked.emit)

        self.button_import_file = DataPlotStudioButton("Import from file", base_color_hex="#27ae60", text_color_hex="white", padding="12px", hover_color_hex="#2ecc71", pressed_color_hex="#1e8a4c", typewriter_effect=True)
        self.button_import_file.setIcon(QIcon("icons/menu_bar/file-down.svg"))
        self.button_import_file.setFixedWidth(button_width)
        self.button_import_file.clicked.connect(self.import_file_clicked.emit)

        self.button_import_sheet = DataPlotStudioButton("Import from Google Sheets", base_color_hex="#16a085", text_color_hex="white", padding="12px", hover_color_hex="#1abc9c", pressed_color_hex="#107a66", typewriter_effect=True)
        self.button_import_sheet.setIcon(QIcon("icons/menu_bar/google-sheets-logo-icon.svg"))
        self.button_import_sheet.setFixedWidth(button_width)
        self.button_import_sheet.clicked.connect(self.import_sheets_clicked.emit)

        self.button_import_db = DataPlotStudioButton("Import from Database", base_color_hex="#8e44ad", text_color_hex="white", padding="12px", hover_color_hex="#9558b6", pressed_color_hex="#6f3487", typewriter_effect=True)
        self.button_import_db.setIcon(QIcon("icons/menu_bar/database.svg"))
        self.button_import_db.setFixedWidth(button_width)
        self.button_import_db.clicked.connect(self.import_db_clicked.emit)

        self.button_new = DataPlotStudioButton("Create Empty Dataset", base_color_hex="#e67e22", text_color_hex="white", padding="12px", hover_color_hex="#f39c12", pressed_color_hex="#b85f17", typewriter_effect=True)
        self.button_new.setIcon(QIcon("icons/menu_bar/file-plus-corner.svg"))
        self.button_new.setFixedWidth(button_width)
        self.button_new.clicked.connect(self.new_dataset_clicked.emit)

        self.button_quit = DataPlotStudioButton("Quit DataPlotStudio", base_color_hex="#c0392b", text_color_hex="white", padding="12px", hover_color_hex="#e74c3c", pressed_color_hex="#8f231f", typewriter_effect=True)
        self.button_quit.setIcon(QIcon("icons/menu_bar/log-out.svg"))
        self.button_quit.setFixedWidth(button_width)
        self.button_quit.clicked.connect(self.quit_clicked.emit)

        actions_layout.addWidget(self.button_open)
        actions_layout.addWidget(self.button_new)
        actions_layout.addWidget(self.button_import_file)
        actions_layout.addWidget(self.button_import_sheet)
        actions_layout.addWidget(self.button_import_db)
        actions_layout.addSpacing(20)
        actions_layout.addWidget(self.button_quit)

        actions_layout.addStretch()

        # Right side. a whats new panel/updates
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("border: none;")
        info_panel = QFrame()
        info_panel.setFrameShape(QFrame.Shape.StyledPanel)
        info_panel.setStyleSheet("background-color: white; border-radius: 15px; border: 1px solid #dfe6e9;")
        info_layout = QVBoxLayout(info_panel)
        info_layout.setContentsMargins(30, 30, 30, 30)

        info_title = QLabel("What's New")
        info_title.setStyleSheet("font-size: 22px; font-weight: bold; color: #34495e; margin-bottom: 15px;")
        app_version = QLabel(f"App. Ver. {APPLICATION_VERSION}")
        app_version.setStyleSheet("font-size: 12px; font-weight: italic; color: #34495e; margin-bottom: 2px;")

        whats_new_content = "<h3 style='color:red'>Loading failed</h3>"
        try:
            news_path = Path("resources/whats_new.html")

            if not news_path.exists():
                news_path = Path(__file__).parent.parent / "resources" / "whats_new.html"
            
            if news_path.exists():
                whats_new_content = news_path.read_text(encoding="utf-8")
            else:
                whats_new_content += f"<p>File not found at: {news_path.absolute()}</p>"
        except Exception as FailedToLoadWhatsNewError:
            whats_new_content = f"<h3>Error</h3><p>{str(FailedToLoadWhatsNewError)}</p>"

        info_content = QLabel(whats_new_content)
        info_content.setWordWrap(True)
        info_content.setTextFormat(Qt.TextFormat.RichText)
        info_content.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        more_info_label = QLabel(
            '<br>'
            '<a href="current_fixes" style="color: #2980b9; text-decoration: none; font-size: 13px;">View Current Bug Fixes & Changes</a><br>'
            '<a href="past_versions" style="color: #2980b9; text-decoration: none; font-size: 13px;">View Version History</a>'
        )
        more_info_label.setTextFormat(Qt.TextFormat.RichText)
        more_info_label.linkActivated.connect(self.handle_changelog_link)
        more_info_label.setCursor(Qt.CursorShape.PointingHandCursor)

        info_layout.addWidget(info_title)
        info_layout.addWidget(app_version)
        info_layout.addWidget(info_content)
        info_layout.addWidget(more_info_label)
        info_layout.addStretch()
        scroll.setWidget(info_panel)

        layout.addWidget(actions_panel, 1)
        layout.addWidget(scroll, 1)
        
    def handle_changelog_link(self, link: str):
        if link == "current_fixes":
            self.show_changelog_popup("Current Bug Fixes and Changes", mode="fixes")
        elif link == "past_versions":
            self.show_changelog_popup("Version History", mode="history")
        
    def show_changelog_popup(self, title: str, mode: str):
        changelog_path = Path(__file__).parent.parent / "CHANGELOG.md"
        
        if not changelog_path.exists():
            content = "<h3 style='color:red'>CHANGELOG.md not found</h3>"
        else:
            try:
                raw_text = changelog_path.read_text(encoding="utf-8")
                content = self.parse_changelog(raw_text, mode)
            except Exception as Error:
                content = f"<h3 style='color:red'>Error reading changelog</h3><p>{str(Error)}</p>"
        
        dialog = ChangelogViewer(title, content, self)
        dialog.exec()
    
    def parse_changelog(self, text: str, mode: str) -> str:
        """
        Markdown to HTML parser
        mode="fixes": Extracts fixed and changed sections
        mode="history": Extracts all sections
        """
        html_output = "<style>h2 {color: #2c3e50;} h3 {color: #2980b9;} ul {line-height: 1.6;}</style>"
        
        sections = re.split(r'(^|\n)## ', text)
        sections = [section for section in sections if section.strip()]
        
        if not sections:
            return "<p>No changelog data found.</p>"

        valid_versions = []
        for section in sections:
            if section.startswith("#"):
                continue
            valid_versions.append(section)
        
        if not valid_versions:
            return "<p>No version information found.</p>"
        
        latest_section = valid_versions[0]
        past_sections = valid_versions[1:]
        
        if mode == "fixes":
            html_output += f"<h2>Latest Changes & Fixes - {APPLICATION_VERSION}</h2>"
            
            sub_sections = re.split(r'(^|\n)### ', latest_section)
            found_relevant = False
            
            for sub in sub_sections:
                header_match = re.match(r'([A-Za-z ]+)', sub)
                if header_match:
                    header = header_match.group(1).strip()
                    if header in ["Fixed", "Changed"]:
                        found_relevant = True
                        body = sub[len(header):].strip()
                        html_output += f"<h3>{header}</h3>"
                        html_output += self._markdown_list_to_html(body)
            
            if not found_relevant:
                html_output += "<p>No bug fixes or changes listed for the latest version.</p>"
        
        elif mode == "history":
            html_output += "<h2>Version History</h2>"
            if not past_sections:
                html_output += "<p>No past versions found.</p>"
                
            for version_text in past_sections:
                lines = version_text.split('\n')
                version_title = lines[0].strip()
                html_output += f"<hr><h3>{version_title}</h3>"
                
                body = "\n".join(lines[1:])
                body = re.sub(r'### (.*?)\n', r'<h4>\1</h4>\n', body)
                html_output += self._markdown_list_to_html(body)

        return html_output
    
    def _markdown_list_to_html(self, text: str):
        lines = text.split("\n")
        html = "<ul>"
        in_list = False
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- ") or stripped.startswith("* "):
                content = stripped[2:]
                content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
                html += f"<li>{content}</li>"
                in_list = True
            elif in_list and not stripped:
                pass
            else:
                if stripped:
                    html += f"<p>{stripped}</p>"
        
        html += "</ul>"
        return html