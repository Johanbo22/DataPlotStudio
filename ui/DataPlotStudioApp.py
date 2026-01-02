from core.code_exporter import CodeExporter
from core.data_handler import DataHandler
from core.logger import Logger
from core.project_manager import ProjectManager
from ui.dialogs import DatabaseConnectionDialog, ExportDialog, ProgressDialog, SettingsDialog
from ui.main_window import MainWindow
from ui.menu_bar import MenuBar
from ui.status_bar import StatusBar


from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QCloseEvent, QFont, QIcon
from PyQt6.QtWidgets import QApplication, QFileDialog, QMainWindow, QMessageBox


import traceback
from pathlib import Path
import os
import logging


class DataPlotStudio(QMainWindow):
    """Main application window"""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataPlot Studio")
        self.setWindowIcon(QIcon(r"icons\DPS_icon.ico"))

        # Initialize core managers
        self.project_manager = ProjectManager()
        self.data_handler = DataHandler()
        self.code_exporter = CodeExporter()
        self.logger = Logger()

        # Create status bar for terminal output
        self.status_bar_widget = StatusBar()
        self.setStatusBar(self.status_bar_widget)

        # Link logger to status bar
        self.status_bar_widget.set_logger(self.logger)

        # Log startup
        self.status_bar_widget.log("DataPlot Studio started", "INFO")

        #load default settings
        self.settings = {
            "dark_mode": False,
            "font_family": "Consolas",
            "font_size": 10
        }
        self.apply_settings(self.settings)

        # Create menu bar
        self.menu_bar = MenuBar(self)
        self.setMenuBar(self.menu_bar)

        # Create main window widget
        self.main_widget = MainWindow(self.data_handler, self.project_manager, self.status_bar_widget)
        self.setCentralWidget(self.main_widget)

        self._connect_signals()

        self.show()

    def _connect_signals(self):
        """Connect signals between components"""
        # Menu signals
        self.menu_bar.file_new.triggered.connect(self.new_project)
        self.menu_bar.file_open.triggered.connect(self.open_project)
        self.menu_bar.file_save.triggered.connect(self.save_project)
        self.menu_bar.import_file.triggered.connect(self.main_widget.import_file)
        self.menu_bar.import_sheets.triggered.connect(self.import_google_sheets)
        self.menu_bar.import_database.triggered.connect(self.import_from_database)
        self.menu_bar.export_code.triggered.connect(self.export_code)
        self.menu_bar.export_logs.triggered.connect(self.export_logs)

        # Edit menu
        self.menu_bar.undo_action.triggered.connect(self.undo_action)
        self.menu_bar.redo_action.triggered.connect(self.redo_action)
        self.menu_bar.settings_action.triggered.connect(self.open_settings)

        #edport menu
        self.menu_bar.export_data_action.triggered.connect(self.export_data_dialog)

        # View menu
        self.menu_bar.zoom_in_action.triggered.connect(self.zoom_in)
        self.menu_bar.zoom_out_action.triggered.connect(self.zoom_out)
        self.menu_bar.about_action.triggered.connect(self.show_about)

    def new_project(self):
        """Create a new project"""
        self.project_manager.new_project()
        self.main_widget.clear_all()
        self.status_bar_widget.log("New project created")

    def open_project(self):
        """Open an existing project"""
        filepath = self.project_manager.open_project_dialog()
        if filepath:
            try:
                project = self.project_manager.load_project(filepath)
                self.main_widget.load_project(project)
                self.status_bar_widget.log(f"Project loaded: {filepath}")
            except Exception as LoadProjectError:
                QMessageBox.critical(self, "Error", f"Failed to load project: {str(LoadProjectError)}")

    def save_project(self):
        """Save current project"""
        try:
            project_data = self.main_widget.get_project_data()
            filepath = self.project_manager.save_project(project_data)
            self.main_widget.unsaved_changes = False
            from pathlib import Path
            path = Path(filepath)

            self.status_bar_widget.log_action(
                f"Project saved: {path.name}",
                details={
                    'filename': path.name,
                    'filepath': str(path),
                    'data_rows': len(self.data_handler.df) if self.data_handler.df is not None else 0,
                    'data_cols': len(self.data_handler.df.columns) if self.data_handler.df is not None else 0,
                    'operation': 'save_project'
                },
                level="SUCCESS"
            )
        except Exception as SaveProjectError:
            self.status_bar_widget.log(f"Save failed: {str(SaveProjectError)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to save project: {str(SaveProjectError)}")

    def import_google_sheets(self):
        """Import from Google Sheets"""
        from ui.dialogs import GoogleSheetsDialog, ProgressDialog
        try:
            dialog = GoogleSheetsDialog(self)
            if dialog.exec():
                sheet_id, sheet_name, delimiter, decimal, thousands = dialog.get_inputs()

                if not sheet_id or not sheet_name:
                    QMessageBox.warning(self, "Input Error", "Please enter both Sheet ID and Sheet Name")
                    return

                #create progress dialog
                progress_dialog = ProgressDialog(title="Importing from Google Sheets", message=f"Connecting to {sheet_name}", parent=self)
                progress_dialog.show()
                progress_dialog.update_progress(10, "Establising connection")
                QApplication.processEvents()

                #show delimiter info
                delimiter_name = {
                    ",": "comma",
                    ";": "semicolon",
                    "\t": "tab",
                    "|": "pipe",
                    " ": "space"
                }.get(delimiter, f"'{delimiter}'")

                progress_dialog.update_progress(30, f"Downloading data Sheet_ID: {sheet_id}, Sheet_Name: {sheet_name}")
                QApplication.processEvents()


                # Show loading message
                self.status_bar_widget.log(f"Connecting to Google Sheets (delimiter: {delimiter_name})...")

                #acutal import
                self.data_handler.import_google_sheets(sheet_id, sheet_name, delimiter=delimiter, decimal=decimal, thousands=thousands)

                progress_dialog.update_progress(70, "Processing data")
                QApplication.processEvents()

                self.main_widget.data_tab.refresh_data_view()

                progress_dialog.update_progress(90, "Updating interface")
                QApplication.processEvents()

                self.main_widget.plot_tab.update_column_combo()

                progress_dialog.update_progress(100, "Complete")
                QTimer.singleShot(300, progress_dialog.accept)

                #log
                rows, cols = self.data_handler.df.shape
                self.status_bar_widget.log_action(
                    f"✓ Successfully imported {sheet_name} from Google Sheet",
                    details={
                        "sheet_name": sheet_name,
                        "rows": rows,
                        "columns": cols,
                        "delimiter": delimiter_name,
                        "decimal": decimal,
                        "thousands": thousands or "none",
                        "operation": "import_google_sheets"
                }, level="SUCCESS")

                QMessageBox.information(self, "Success",
                    f"Google Sheet import complete\n\n"
                    f"Sheet Name: {sheet_name}\n"
                    f"Rows: {rows:,}\n"
                    f"Columns: {cols}\n"
                    f"Delimiter: {delimiter_name}\n"
                    f"Decimal: {decimal}")

        except Exception as ImportGoogleSheetsError:
            if "progress_dialog" in locals() and progress_dialog:
                progress_dialog.accept()
            error_msg = str(ImportGoogleSheetsError)
            self.status_bar_widget.log(f"✗ Import failed: {error_msg}")
            QMessageBox.critical(self, "Import Error",
                            f"Failed to import Google Sheet:\n\n{error_msg}\n\n"
                            "Please verify:\n"
                            "• Sheet ID is correct\n"
                            "• Sheet name exists\n"
                            "• Sheet is shared publicly\n"
                            "• You have internet connection")

    def import_from_database(self):
        """Import data from a database connection"""
        try:
            dialog = DatabaseConnectionDialog(self)
            if dialog.exec():
                db_type, connection_string, query = dialog.get_details()

                if not connection_string or not query:
                    QMessageBox.warning(self, "Input Error", "Invalid connection details or query")
                    return

                progress_dialog = ProgressDialog(title=f"Importing from {db_type}", message=f"Connecting to {db_type}...", parent=self)
                progress_dialog.show()
                progress_dialog.update_progress(10, "Establishing connection")
                QApplication.processEvents()

                self.status_bar_widget.log(f"Connecting to {db_type} database...")

                progress_dialog.update_progress(30, "Executing query...")
                QApplication.processEvents()

                # Actual import
                self.data_handler.import_from_database(connection_string, query)

                progress_dialog.update_progress(70, "Processing data")
                QApplication.processEvents()

                self.main_widget.data_tab.refresh_data_view()

                progress_dialog.update_progress(90, "Updating interface")
                QApplication.processEvents()

                self.main_widget.plot_tab.update_column_combo()

                progress_dialog.update_progress(100, "Complete")
                QTimer.singleShot(300, progress_dialog.accept)

                # Log
                rows, cols = self.data_handler.df.shape
                self.status_bar_widget.log_action(
                    f"✓ Successfully imported {rows:,} rows from {db_type} database",
                    details={
                        "db_type": db_type,
                        "rows": rows,
                        "columns": cols,
                        "query": query,
                        "operation": "import_database"
                }, level="SUCCESS")

                QMessageBox.information(self, "Success",
                    f"Database import complete\n\n"
                    f"Type: {db_type}\n"
                    f"Rows: {rows:,}\n"
                    f"Columns: {cols}")

        except Exception as ImportDatabaseError:
            if "progress_dialog" in locals() and progress_dialog:
                progress_dialog.accept()
            error_msg = str(ImportDatabaseError)
            self.status_bar_widget.log(f"✗ Database import failed: {error_msg}")
            QMessageBox.critical(self, "Import Error",
                            f"Failed to import from database:\n\n{error_msg}\n\n"
                            "Please verify:\n"
                            "• Connection details (host, port, user, pass)\n"
                            "• Database name is correct\n"
                            "• SQL query is valid\n"
                            "• Necessary drivers (e.g., psycopg2) are installed")

    def undo_action(self):
        """Undo last action"""
        try:
            if self.data_handler.undo():
                self.main_widget.data_tab.refresh_data_view()
                self.status_bar_widget.log("Undo: Previous state restored")
            else:
                QMessageBox.information(self, "Info", "Nothing to undo")
                self.status_bar_widget.log("Nothing to undo")
        except Exception as UndoError:
            QMessageBox.warning(self, "Error", f"Cannot undo: {str(UndoError)}")

    def redo_action(self):
        """Redo last undone action"""
        try:
            if self.data_handler.redo():
                self.main_widget.data_tab.refresh_data_view()
                self.status_bar_widget.log("Redo: Action restored")
            else:
                QMessageBox.information(self, "Info", "Nothing to redo")
                self.status_bar_widget.log("Nothing to redo")
        except Exception as RedoError:
            QMessageBox.warning(self, "Error", f"Cannot redo: {str(RedoError)}")

    def zoom_in(self):
        """Zoom in on plot"""
        try:
            current_tab = self.main_widget.tabs.currentIndex()
            PLOT_STUDIO_TAB = 1
            if current_tab == PLOT_STUDIO_TAB:
                # Get current figure size
                fig = self.main_widget.plot_tab.plot_engine.current_figure
                width, height = fig.get_size_inches()

                new_width = min(width * 1.1, 20)
                new_height = min(height * 1.1, 16)
                fig.set_size_inches(new_width, new_height)
                self.main_widget.plot_tab.canvas.draw()
                self.status_bar_widget.log(f"Zoomed in: {new_width:.1f}x{new_height:.1f} inches")
            else:
                QMessageBox.information(self, "Info", "Zoom only works in Plot Studio tab")
        except Exception as ZoomInError:
            self.status_bar_widget.log(f"Zoom in failed: {str(ZoomInError)}")

    def zoom_out(self):
        """Zoom out on plot"""
        try:
            current_tab = self.main_widget.tabs.currentIndex()
            if current_tab == 1:
                fig = self.main_widget.plot_tab.plot_engine.current_figure
                width, height = fig.get_size_inches()
                new_width = max(width * 0.9, 4)
                new_height = max(height * 0.9, 3)
                fig.set_size_inches(new_width, new_height)
                self.main_widget.plot_tab.canvas.draw()
                self.status_bar_widget.log(f"Zoomed out: {new_width:.1f}x{new_height:.1f} inches")
            else:
                QMessageBox.information(self, "Info", "Zoom only works in Plot Studio tab")
        except Exception as ZoomOutError:
            self.status_bar_widget.log(f"Zoom out failed: {str(ZoomOutError)}")

    def show_about(self):
        """Show about dialog"""
        link_to_github_repository = "https://github.com/Johanbo22/DataPlotStudio"
        message = QMessageBox(self)
        message.setWindowTitle("About DataPlot Studio")
        message.setTextFormat(Qt.TextFormat.RichText)
        message.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        message.setText(
            f"""
            <b>DataPlot Studio v{self.project_manager.APPLICATION_VERSION}</b><br><br>
            A data analysis and visualization tool built with Python and the PyQt6 Framework. <br><br>
            <u>Features:</u><br>
            • Timport data from CSV, Excel, JSON, Google Sheets and database connections<br>
            • Tranform and explore your data<br>
            • Create 31 types of visualizations<br>
            • Export code for sharing and further customization<br><br>
            <a href="{link_to_github_repository}">Link to Github Repository</a>
        """)
        message.exec()

    def export_code(self):
        """Export data manipulation and plotting code"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "Warning", "No data loaded. Please load data first.")
            return

        # Get all required info
        source_info = self.data_handler.get_data_source_info()
        data_filepath = source_info.get("file_path")
        is_temp = source_info.get("is_temp_file", False)

        source_info = {
            "is_temp_file": is_temp,
            "last_gsheet_id": self.data_handler.last_gsheet_id,
            "last_gsheet_name": self.data_handler.last_gsheet_name,
            "last_gsheet_delimiter": self.data_handler.last_gsheet_delimiter,
            "last_gsheet_decimal": self.data_handler.last_gsheet_decimal,
            "last_gsheet_thousands": self.data_handler.last_gsheet_thousands,
            "last_db_connection_string": self.data_handler.last_db_connection_string,
            "last_db_query": self.data_handler.last_db_query
        }

        data_operations = self.data_handler.operation_log


        plot_config = {}
        dataframe = self.data_handler.df
        # 

        #check if source is valid
        if not data_filepath:
            QMessageBox.warning(self, "Warning", "No data source filepath found")
            return

        #inform the user about the temp file from google sheets
        if is_temp:
            mgs_box = QMessageBox()
            mgs_box.setWindowTitle("Google Sheets Data Source")
            mgs_box.setWindowIcon(QIcon("icons/menu_bar/google_sheet.png"))
            mgs_box.setIcon(QMessageBox.Icon.Information)
            mgs_box.setText("This data has been imported from Google Sheets")
            mgs_box.setInformativeText(
                "The exported script will try to re-download this data directly from Google Sheets.\n\n"
                "Please ensure the sheet remains public and accessible."
            )
            mgs_box.setStandardButtons(QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
            mgs_box.button(QMessageBox.StandardButton.Ok).setText("Continue Export")
            mgs_box.button(QMessageBox.StandardButton.Cancel).setText("Cancel")

            if mgs_box.exec() == QMessageBox.StandardButton.Cancel:
                return


        # Ask user what to export
        dialog = QMessageBox()
        dialog.setWindowTitle("Export Code")
        dialog.setText("What would you like to export?")
        dialog.setInformativeText("You can export the data processing steps, or both data processing and the current plot.")

        btn_data_only = dialog.addButton("Data Processing Only", QMessageBox.ButtonRole.YesRole)
        btn_data_plot = dialog.addButton("Data + Plot", QMessageBox.ButtonRole.NoRole)
        dialog.addButton("Cancel", QMessageBox.ButtonRole.RejectRole)


        dialog.exec()

        #
        export_type = ""
        if dialog.clickedButton() == btn_data_only:
            export_type = "Data Only"
        elif dialog.clickedButton() == btn_data_plot:
            export_type = "Data + Plot"
            plot_config = self.main_widget.plot_tab.get_config()
        else:
            return
        # 

        # Get save location
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export as Python Script",
            "dataplot_script.py",
            "Python Files (*.py)"
        )

        if not filepath:
            return

        try:
            script = self.code_exporter.generate_full_script(
                df=dataframe,
                data_filepath=str(data_filepath),
                source_info=source_info,
                data_operations=data_operations,
                plot_config=plot_config,
                export_type=export_type #
            )


            # Write script to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(script)

            log_details = {
                "filename": Path(filepath).name,
                "filepath": str(filepath),
                "data_rows": len(self.data_handler.df) if self.data_handler.df is not None else 0,
                "data_cols": len(self.data_handler.df.columns) if self.data_handler.df is not None else 0,
                "operation": "export_code to .py file",
                "export_type": export_type,
                "source_is_temp": is_temp,
                "source_path": str(data_filepath),
                "data_ops_count": len(data_operations),
                "plot_type": plot_config.get("plot_type") if plot_config else "N/A"
            }

            self.status_bar_widget.log_action(
                f"Python script exported: {Path(filepath).name} ({export_type})",
                details=log_details,
                level="SUCCESS"
            )

            success_mgs = f"Python script exported successfully!\n\nFile: {filepath}\n\n"
            success_mgs += f"You can now run this script independently to:\n"
            success_mgs += f"• Reproduce your data analysis\n"
            success_mgs += f"• Extend with custom code\n"
            success_mgs += f"• Share with collaborators"

            if is_temp:
                success_mgs += (
                    "\n\nNote:\n"
                    "The script is set to re-download from Google Sheets.\n"
                    "Ensure the sheet remains public for the script to work."
                )

            QMessageBox.information(self, "Success", success_mgs)

        except Exception as ExportCodeError:
            self.status_bar_widget.log(f"Failed to export code: {str(ExportCodeError)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to export code: {str(ExportCodeError)}\n\n{traceback.format_exc()}")

    def export_logs(self):
        """Export session logs to file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Session Logs",
            "dataplot_session.log",
            "Log Files (*.log);;Text Files (*.txt)"
        )

        if not filepath:
            return

        try:
            # Ask for detail level
            dialog = QMessageBox()
            dialog.setWindowTitle("Export Logs")
            dialog.setText("Include detailed timestamps?")
            dialog.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            dialog.button(QMessageBox.StandardButton.Yes).setText("Detailed (Full Timestamps)")
            dialog.button(QMessageBox.StandardButton.No).setText("Standard (Time Only)")

            detailed = dialog.exec() == QMessageBox.StandardButton.Yes

            # Export logs using logger directly
            self.logger.export_logs(filepath, detailed)

            stats = self.logger.get_stats()

            self.status_bar_widget.log(
                f"✓ Session logs exported: {filepath} ({stats['total_entries']} entries, "
                f"duration {stats['session_duration']})"
            )

            QMessageBox.information(self, "Success",
                f"Session logs exported successfully!\n\n"
                f"File: {filepath}\n"
                f"Total Entries: {stats['total_entries']}\n"
                f"Session Duration: {stats['session_duration']}\n\n"
                f"Entries by type:\n"
                f"• SUCCESS: {stats['by_level'].get('SUCCESS', 0)}\n"
                f"• INFO: {stats['by_level'].get('INFO', 0)}\n"
                f"• WARNING: {stats['by_level'].get('WARNING', 0)}\n"
                f"• ERROR: {stats['by_level'].get('ERROR', 0)}")

        except Exception as ExportLogError:
            self.status_bar_widget.log(f"✗ Failed to export logs: {str(ExportLogError)}")
            # do not add secondary args to .log(), causes bug
            QMessageBox.critical(self, "Error", f"Failed to export logs: {str(ExportLogError)}")

    def export_data_dialog(self):
        """Open export dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "Warning", "No data to export")
            return

        dialog = ExportDialog(self)
        if dialog.exec():
            config = dialog.get_export_config()
            if config["filepath"]:
                try:
                    format_extension = config["format"]
                    include_index = config.get("include_index", False)
                    self.data_handler.export_data(config["filepath"], format=format_extension, include_index=include_index)
                    self.status_bar_widget.log(f"Exported data to {config["filepath"]}")
                    QMessageBox.information(self, "Success", f"Data exported successfully to {config["filepath"]}")
                except Exception as ExportDataError:
                    QMessageBox.critical(self, "Error", f"Failed to export: {str(ExportDataError)}")

    def closeEvent(self, event: QCloseEvent) -> None:
        """Check for changes in the app state and prompt if changes are not saved"""
        if hasattr(self.main_widget, "unsaved_changes") and self.main_widget.unsaved_changes:
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save the current project before exiting?",
                QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
                QMessageBox.StandardButton.Save
            )

            if reply == QMessageBox.StandardButton.Save:
                if self.save_project():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.StandardButton.Discard:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()

    def open_settings(self):
        """open the settings """
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            new_settings = dialog.get_settings()
            self.settings.update(new_settings)
            self.apply_settings(self.settings)
            self.status_bar_widget.log("Settings updated", "INFO")

    def apply_settings(self, settings) -> None:
        """apply settings to the main app"""
        font = QFont(settings["font_family"], settings["font_size"])
        QApplication.setFont(font)

        if settings["dark_mode"]:
            base_qss = self.get_dark_theme()
        else:
            base_qss = self.load_stylesheet("styles/style.css")

        different_qss = base_qss + f"""
            QWidget {{
                font-family: "{settings['font_family']}";
                font-size: {settings['font_size']}pt;
            }}
            QGroupBox {{
                font-weight: bold;
                font-size: {settings['font_size'] + 2}pt; 
            }}
        """

        QApplication.instance().setStyleSheet(different_qss)

    def get_dark_theme(self):
        return self.load_stylesheet("styles/dark_theme.css")
    
    @classmethod
    def load_stylesheet(cls, relative_path: str) -> str:
        """Load the qss style into main"""
        path = Path(__file__).parent / relative_path
        return path.read_text(encoding="utf-8")