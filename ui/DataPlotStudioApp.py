# ui/DataPlotStudioApp.py
from core.code_exporter import CodeExporter
from core.data_handler import DataHandler
from core.logger import Logger
from core.project_manager import ProjectManager
from ui.dialogs import SettingsDialog, AboutDialog
from ui.main_window import MainWindow
from ui.menu_bar import MenuBar
from ui.status_bar import StatusBar

from PyQt6.QtGui import QCloseEvent, QFont, QIcon
from PyQt6.QtWidgets import QApplication, QMainWindow, QMessageBox
from pathlib import Path

class DataPlotStudio(QMainWindow):
    """Main Application shell"""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("DataPlotStudio")
        self.setWindowIcon(QIcon(r"icons\DPS_icon.ico"))

        # Initialize the core managers
        self.project_manager = ProjectManager()
        self.data_handler = DataHandler()
        self.code_exporter = CodeExporter()
        self.logger = Logger()

        # Create the status bar
        self.status_bar_widget = StatusBar()
        self.setStatusBar(self.status_bar_widget)
        self.status_bar_widget.set_logger(self.logger)

        self.status_bar_widget.log("DataPlotStudio started", "INFO")

        # Load settings
        self.settings = {
            "dark_mode": False,
            "font_family": "Consolas",
            "font_size": 10
        }
        self.apply_settings(self.settings)

        # Create the menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Create the main widget
        self.main_widget = MainWindow(
            self.data_handler,
            self.project_manager,
            self.code_exporter,
            self.logger,
            self.status_bar_widget
        )
        self.setCentralWidget(self.main_widget)

        self._connect_signals()
        self.show()
    
    def _connect_signals(self) -> None:
        """Routing signals to the main widget"""
        #File menu
        self.menu_bar.file_new.triggered.connect(self.main_widget.new_project)
        self.menu_bar.file_open.triggered.connect(self.main_widget.open_project)
        self.menu_bar.file_save.triggered.connect(self.main_widget.save_project)
        self.menu_bar.file_save_as.triggered.connect(self.main_widget.save_project_as)
        self.menu_bar.import_file.triggered.connect(self.main_widget.import_file)
        self.menu_bar.import_sheets.triggered.connect(self.main_widget.import_google_sheets)
        self.menu_bar.import_database.triggered.connect(self.main_widget.import_from_database)

        # Export menu
        self.menu_bar.export_code.triggered.connect(self.main_widget.export_code)
        self.menu_bar.export_logs.triggered.connect(self.main_widget.export_logs)
        self.menu_bar.export_data_action.triggered.connect(self.main_widget.export_data_dialog)

        # Edit menu
        self.menu_bar.undo_action.triggered.connect(self.main_widget.undo)
        self.menu_bar.redo_action.triggered.connect(self.main_widget.redo)

        # View menu
        self.menu_bar.zoom_in_action.triggered.connect(self.main_widget.zoom_in)
        self.menu_bar.zoom_out_action.triggered.connect(self.main_widget.zoom_out)

        # App level
        self.menu_bar.settings_action.triggered.connect(self.open_settings)
        self.menu_bar.about_action.triggered.connect(self.show_about)
    
    def closeEvent(self, event: QCloseEvent) -> None:
        """Checks for unsaved changes before exiting"""
        if hasattr(self.main_widget, "unsaved_changes") and self.main_widget.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save the current project before exiting?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )
            if reply == QMessageBox.StandardButton.Save:
                if self.main_widget.save_project():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()
    
    def open_settings(self) -> None:
        """Opens the settings dialog"""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.apply_settings(self.settings)
            self.status_bar_widget.log("Settings updated", "INFO")
    
    def show_about(self) -> None:
        """Shows the about dialog box"""
        AboutDialog.show_about_dialog(
            parent=self,
            application_version=self.project_manager.APPLICATION_VERSION
        )
    
    def apply_settings(self, settings) -> None:
        """Apply the settings to main app loop"""
        font = QFont(settings["font_family"], settings["font_size"])
        QApplication.setFont(font)

        if settings["dark_mode"]:
            base_css = self.get_dark_theme()
        else:
            base_css = self.load_stylesheet("styles/style.css")
        
        different_css = base_css + f"""
            QWidget {{
                font-family: "{settings['font_family']}";
                font-size: {settings['font_size']}pt;
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: {settings['font_size'] + 2}pt; 
            }}
        """
        QApplication.instance().setStyleSheet(different_css)
    
    def get_dark_theme(self):
        return self.load_stylesheet("styles/dark_theme.css")
    
    @classmethod
    def load_stylesheet(cls, relative_path: str) -> str:
        path = Path(__file__).parent / relative_path
        return path.read_text(encoding="utf-8")