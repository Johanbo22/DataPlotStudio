# ui/main_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFileDialog, QMessageBox, QSplitter, QPushButton, QApplication)
from PyQt6.QtCore import Qt, QThreadPool, pyqtSlot, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtGui import QIcon, QCloseEvent
from pathlib import Path

from core import subset_manager
from core.subset_manager import SubsetManager
from ui.workers import FileImportWorker, GoogleSheetsImportWorker
from ui.data_tab import DataTab
from ui.plot_tab import PlotTab
from core.data_handler import DataHandler
from core.project_manager import ProjectManager
from ui.status_bar import StatusBar
from ui.widgets.AnimatedTabWidget import AnimatedTabWidget
from ui.dialogs import ProgressDialog, GoogleSheetsDialog
from ui.animations.SavedProjectAnimation import SavedProjectAnimation

class MainWindow(QWidget):
    """Main application window widget"""
    
    def __init__(self, data_handler: DataHandler, project_manager: ProjectManager, status_bar: StatusBar):
        super().__init__()
        
        self.data_handler = data_handler
        self.project_manager = project_manager
        self.status_bar = status_bar

        self.subset_manager = SubsetManager()

        self.threadpool = QThreadPool()

        self.progress_dialog: ProgressDialog | None = None
        self._temp_import_filepath: str | None = None
        self._temp_import_filesize: float = 0.0

        self.unsaved_changes = False
        
        self.init_ui()
        self._connect_subset_managers()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = AnimatedTabWidget()
        
        # Data Tab: for viewing and cleaning data
        data_icon = QIcon("icons/data_explorer.png")
        self.data_tab = DataTab(self.data_handler, self.status_bar, self.subset_manager)
        self.tabs.addTab(self.data_tab, data_icon, "Data Explorer")
        
        # Plot Tab :for plotting
        plot_icon = QIcon("icons/plot.png")
        self.plot_tab = PlotTab(self.data_handler, self.status_bar)
        self.tabs.addTab(self.plot_tab, plot_icon, "Plot Studio")
        
        layout.addWidget(self.tabs)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.setLayout(layout)
    
    def _connect_subset_managers(self) -> None:
        """Connect the subset manager used in DataTab to PlotTab"""
        #get subset manager name from data tab
        subset_manager = self.data_tab.get_subset_manager()

        #set it in plot tab
        self.plot_tab.set_subset_manager(self.subset_manager)

        self.data_tab.set_plot_tab(self.plot_tab)

        #connect tab to rf subsets in PT
        self.tabs.currentChanged.connect(self._on_tab_changed)
    
    def _on_tab_changed(self, index):
        """Handle tab change events"""
        if index == 1:
            self.plot_tab.refresh_subset_list()

    def import_file(self) -> None:
        """Import a data file"""
        geospatial_filter = "Geospatial Files (*.geojson *.shp *gpkg)"
        data_filter = "Data Files (*.csv *.xlsx *.xls *.txt *.json)"
        all_files_filter = "All Files (*)"

        file_filter = f"{data_filter};;{geospatial_filter};;{all_files_filter}"
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Data File", "", file_filter)
        
        if filepath:
            path = Path(filepath)
            file_size_kb = path.stat().st_size / 1024
            show_progress = file_size_kb > 500

            self._temp_import_filepath = filepath
            self._temp_import_filesize = file_size_kb

            self.progress_dialog = None
            if show_progress:
                self.progress_dialog = ProgressDialog(
                    title="Importing data",
                    message=f"Loading {path.name} ({file_size_kb:.1f} KB)",
                    parent=self
                )
                self.progress_dialog.show()
                self.progress_dialog.update_progress(10, "Reading file")
                QApplication.processEvents()
            else:
                self.status_bar.log(f"Importing: {filepath}...")
            
            worker = FileImportWorker(self.data_handler, filepath)
            worker.signals.finished.connect(self._on_import_finished)
            worker.signals.error.connect(self._on_import_error)
            worker.signals.progress.connect(self._on_import_progress)

            self.threadpool.start(worker)
    
    @pyqtSlot(int, str)
    def _on_import_progress(self, percentage: int, message: str):
        if self.progress_dialog:
            self.progress_dialog.update_progress(percentage, message)
            QApplication.processEvents()
    
    @pyqtSlot(object)
    def _on_import_finished(self, loaded_dataframe):
        if self.progress_dialog:
            self.progress_dialog.update_progress(90, "Updating Interface")
            QApplication.processEvents()
        
        self.data_tab.refresh_data_view()
        self.plot_tab.update_column_combo()

        self.unsaved_changes = True

        if self.progress_dialog:
            self.progress_dialog.update_progress(100, "Complete")
            QTimer.singleShot(300, self.progress_dialog.accept)
            self.progress_dialog = None

        ##log
        try:
            path = Path(self._temp_import_filepath)
            rows, cols = loaded_dataframe.shape

            self.status_bar.log_action(
                f"Imported {path.name}",
                details={
                    "filename": path.name,
                    "filepath": str(path),
                    "rows": rows,
                    "columns": cols,
                    "file_size_kb": round(self._temp_import_filesize),
                    "file_type": path.suffix,
                    "operation": "import_file"
                },
                level="SUCCESS"
            )
        except Exception as LogError:
            self.status_bar.log(f"Failed to log operation to log file: {LogError}", "ERROR")
        
        self._temp_import_filepath = None
        self._temp_import_filesize = 0.0
    
    @pyqtSlot(Exception)
    def _on_import_error(self, error: Exception):
        if self.progress_dialog:
            self.progress_dialog.accept()
            self.progress_dialog = None
            
        QMessageBox.critical(self, "Error", f"Failed to import file: {str(error)}")
        self.status_bar.log(f"Import failed: {str(error)}", "ERROR")
        
        # Clear temp variables
        self._temp_import_filepath = None
        self._temp_import_filesize = 0.0
    
    def import_google_sheets(self):
        """Import from Google Sheets"""
        dialog = GoogleSheetsDialog(self)
        if dialog.exec():
            inputs = dialog.get_inputs()

            if len(inputs) == 5:
                sheet_id, sheet_name, delimiter, decimal, thousands = inputs
            else:
                sheet_id, sheet_name = inputs
                delimiter, decimal, thousands = ",", ".", None
            
            if not sheet_id or not sheet_name:
                QMessageBox.warning(self, "Input Error", "Sheet ID and Sheet Name cannot be empty")
                return
            
            self.progress_dialog = ProgressDialog(
                title="Importing from Google Sheets",
                message=f"Connecting to {sheet_name}...",
                parent=self
            )
            self.progress_dialog.show()
            self.progress_dialog.update_progress(0, "Initializing...")

            worker = GoogleSheetsImportWorker(self.data_handler, sheet_id, sheet_name, delimiter, decimal, thousands)
            worker.signals.progress.connect(self._on_import_progress)
            worker.signals.finished.connect(lambda df: self._on_google_sheet_import_finished(df, sheet_name))
            worker.signals.error.connect(self._on_import_error)

            self.threadpool.start(worker)
    
    @pyqtSlot(object, str)
    def _on_google_sheet_import_finished(self, loaded_dataframe, sheet_name):
        if self.progress_dialog:
            self.progress_dialog.update_progress(90, "Updating Interface")
            QApplication.processEvents()
        
        self.data_tab.refresh_data_view()
        self.plot_tab.update_column_combo()
        self.unsaved_changes = True

        if self.progress_dialog:
            self.progress_dialog.update_progress(100, "Complete")
            QTimer.singleShot(300, self.progress_dialog.accept)
            self.progress_dialog = None
        
        rows, columns = loaded_dataframe.shape
        self.status_bar.log_action(
            f"Imported Google Sheet: {sheet_name}",
            details={
                "sheet_name": sheet_name,
                "rows": rows,
                "columns": columns,
                "operation": "import_google_sheets"
            },
            level="SUCCESS"
        )
    
    def load_project(self, project_data: dict) -> None:
        """Load a project"""
        if 'data' in project_data and project_data['data'] is not None:
            self.data_handler.df = project_data['data']
            self.data_handler.original_df = project_data['data'].copy()
            self.data_tab.refresh_data_view()
        
        if 'plot_config' in project_data:
            self.plot_tab.load_config(project_data['plot_config'])

        if "subsets" in project_data:
            subset_manager = self.subset_manager
            subset_manager.import_subsets(project_data["subsets"])
            self.data_tab.refresh_active_subsets()
            self.plot_tab.refresh_subset_list()
        
        self.unsaved_changes = False

    def save_project(self) -> bool:
        """Saves the current state of the instance"""
        try:
            project_data = self.get_project_data()
            filepath = self.project_manager.get_current_project_path()

            saved_path = self.project_manager.save_project(project_data, filepath)

            self.saved_animation = SavedProjectAnimation(parent=None)
            self.saved_animation.start()

            if saved_path:
                self.unsaved_changes = False
                self.status_bar.log(f"Project saved to {saved_path}")
                return True
            return False
        except Exception as SaveProjectError:
            QMessageBox.critical(self, "Save Error", f"Failed to save project: {str(SaveProjectError)}")
            self.status_bar.log(f"Save failed: {str(SaveProjectError)}", "ERROR")
            return False
    
    
    
    def get_project_data(self) -> dict:
        """Get all project data for saving"""
        subset_manager = self.subset_manager
        return {
            'data': self.data_handler.df,
            'plot_config': self.plot_tab.get_config(),
            "subsets": subset_manager.export_subsets(),
            'metadata': {
                'version': '1.0',
                'name': 'DataPlot Studio Project',
                "subset_count": len(subset_manager.list_subsets())
            }
        }
    
    def clear_all(self):
        """Clear all data"""
        self.data_handler.df = None
        self.data_handler.original_df = None
        self.data_tab.clear()
        self.plot_tab.clear()

        subset_manager = self.subset_manager
        subset_manager.subsets.clear()
        subset_manager.clear_cache()
        self.data_tab.refresh_active_subsets()
        self.plot_tab.refresh_subset_list()