# ui/main_window.py
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QFileDialog, QMessageBox, QSplitter, QPushButton)
from PyQt6.QtCore import Qt
from glm import project
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtGui import QIcon

from core import subset_manager
from core.subset_manager import SubsetManager
from ui.data_tab import DataTab
from ui.plot_tab import PlotTab
from core.data_handler import DataHandler
from core.project_manager import ProjectManager
from ui.status_bar import StatusBar


class MainWindow(QWidget):
    """Main application window widget"""
    
    def __init__(self, data_handler: DataHandler, project_manager: ProjectManager, status_bar: StatusBar):
        super().__init__()
        
        self.data_handler = data_handler
        self.project_manager = project_manager
        self.status_bar = status_bar

        self.subset_manager = SubsetManager()
        
        self.init_ui()
        self._connect_subset_managers()
    
    def init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tabs = QTabWidget()
        
        # Data Tab - for viewing and cleaning data
        data_icon = QIcon("icons/data_explorer.png")
        self.data_tab = DataTab(self.data_handler, self.status_bar, self.subset_manager)
        self.tabs.addTab(self.data_tab, data_icon, "Data Explorer")
        
        # Plot Tab - for plotting
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
        file_filter = "Data Files (*.csv *.xlsx *.xls *.txt *.json);;All Files (*)"
        filepath, _ = QFileDialog.getOpenFileName(self, "Import Data File", "", file_filter)
        
        if filepath:
            try:
                self.data_handler.import_file(filepath)
                self.data_tab.refresh_data_view()
                self.plot_tab.update_column_combo()
                self.status_bar.log(f"Imported: {filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import file: {str(e)}")
                self.status_bar.log(f"Import failed: {str(e)}")
    
    def import_google_sheets(self):
        """Import from Google Sheets"""
        # This would open a dialog for sheet_id and sheet_name input
        from ui.dialogs import GoogleSheetsDialog
        dialog = GoogleSheetsDialog(self)
        if dialog.exec():
            sheet_id, sheet_name = dialog.get_inputs()
            try:
                self.data_handler.import_google_sheets(sheet_id, sheet_name)
                self.data_tab.refresh_data_view()
                self.status_bar.log(f"Imported Google Sheet: {sheet_id}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to import Google Sheet: {str(e)}")
    
    def load_project(self, project_data: dict) -> None:
        """Load a project"""
        if 'dataframe' in project_data and project_data['dataframe'] is not None:
            self.data_handler.df = project_data['dataframe']
            self.data_handler.original_df = project_data['dataframe'].copy()
            self.data_tab.refresh_data_view()
        
        if 'plot_config' in project_data:
            self.plot_tab.load_config(project_data['plot_config'])

        if "subsets" in project_data:
            subset_manager = self.subset_manager
            subset_manager.import_subsets(project_data["subsets"])
            self.data_tab.refresh_active_subsets()
            self.plot_tab.refresh_subset_list()
    
    def get_project_data(self) -> dict:
        """Get all project data for saving"""
        subset_manager = self.subset_manager
        return {
            'dataframe': self.data_handler.df,
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