# ui/menu_bar.py
from stat import filemode
from PyQt6.QtWidgets import QMenuBar, QMenu
from PyQt6.QtGui import QAction, QIcon
from ui.animated_widgets import AnimatedMenu


class MenuBar(QMenuBar):
    """Custom menu bar for the application"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # File Menu
        file_menu = AnimatedMenu(self.tr("&File"), self)
        self.addMenu(file_menu)
        
        self.file_new = QAction(QIcon("icons/menu_bar/new_project.png"),self.tr("&New Project"), parent)
        self.file_new.setShortcut("Ctrl+N")
        self.file_new.setToolTip(self.tr("Create a new project from scratch"))
        file_menu.addAction(self.file_new)
        
        self.file_open = QAction(QIcon("icons/menu_bar/open_project.png"), self.tr("&Open Project"), parent)
        self.file_open.setShortcut("Ctrl+O")
        self.file_open.setToolTip(self.tr("Open an exisiting project"))
        file_menu.addAction(self.file_open)
        
        self.file_save = QAction(QIcon("icons/menu_bar/save_project.png"), self.tr("&Save Project"), parent)
        self.file_save.setShortcut("Ctrl+S")
        self.file_save.setToolTip(self.tr("Save the current project"))
        file_menu.addAction(self.file_save)
        
        file_menu.addSeparator()
        
        self.import_file = QAction(QIcon("icons/menu_bar/import_data.png"), self.tr("&Import Data"), parent)
        self.import_file.setShortcut("Ctrl+I")
        self.import_file.setToolTip(self.tr("Import data from a file on your computer"))
        file_menu.addAction(self.import_file)
        
        self.import_sheets = QAction(QIcon("icons/menu_bar/google_sheet.png"), self.tr("&Import from Google Sheets"), parent)
        self.import_sheets.setToolTip(self.tr("Import data from Google Sheet"))
        file_menu.addAction(self.import_sheets)

        self.import_database = QAction(QIcon("icons/menu_bar/database.png"), self.tr("Import from &Database"), parent)
        self.import_database.setToolTip(self.tr("Import data from a database (SQLite, PostgreSQL, MySQL)"))
        file_menu.addAction(self.import_database)
        
        file_menu.addSeparator()
        
        self.export_code = QAction(QIcon("icons/menu_bar/export_python.png"), self.tr("&Export to Python (.py) file"), parent)
        self.export_code.setShortcut("Ctrl+E")
        self.export_code.setToolTip(self.tr("Export the data manipulation and plotting code to an external Python (.py) file"))
        file_menu.addAction(self.export_code)
        
        self.export_logs = QAction(QIcon("icons/menu_bar/export_log.png"), self.tr("&Export Log file"), parent)
        self.export_logs.setToolTip(self.tr("Export the .log file to view the logging of your session"))
        file_menu.addAction(self.export_logs)
        
        file_menu.addSeparator()
        
        exit_action = QAction(QIcon("icons/menu_bar/exit.png"), self.tr("E&xit"), parent)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.setToolTip(self.tr("Exit the program"))
        exit_action.triggered.connect(parent.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = AnimatedMenu(self.tr("&Edit"), self)
        self.addMenu(edit_menu)
        
        self.undo_action = QAction(QIcon("icons/menu_bar/undo.png"), self.tr("&Undo"), parent)
        self.undo_action.setShortcut("Ctrl+Z")
        self.undo_action.setToolTip(self.tr("Undo the last action"))
        edit_menu.addAction(self.undo_action)
        
        self.redo_action = QAction(QIcon("icons/menu_bar/redo.png"), self.tr("&Redo"), parent)
        self.redo_action.setShortcut("Ctrl+Y")
        self.redo_action.setToolTip(self.tr("Redo the previous action"))
        edit_menu.addAction(self.redo_action)

        edit_menu.addSeparator()
        self.settings_action = QAction(QIcon("icons/plot_tab/customization_tabs/general.png"), self.tr("&Settings"), parent)
        self.settings_action.setShortcut("Ctrl+,")
        self.settings_action.setToolTip(self.tr("Configre application preferences"))
        edit_menu.addAction(self.settings_action)
        
        # View Menu
        view_menu = AnimatedMenu("&View", self)
        self.addMenu(view_menu)
        
        self.zoom_in_action = QAction(QIcon("icons/menu_bar/zoom_in.png"), self.tr("Zoom &In"), parent)
        self.zoom_in_action.setShortcut("Ctrl++")
        self.zoom_in_action.setToolTip(self.tr("Zoom into the plot"))
        view_menu.addAction(self.zoom_in_action)
        
        self.zoom_out_action = QAction(QIcon("icons/menu_bar/zoom_out.png"), self.tr("Zoom &Out"), parent)
        self.zoom_out_action.setShortcut("Ctrl+-")
        self.zoom_out_action.setToolTip(self.tr("Zoom out from the plot"))
        view_menu.addAction(self.zoom_out_action)

        # Export menu
        export_menu = AnimatedMenu(self.tr("&Export Data"), self)
        self.addMenu(export_menu)

        self.export_data_action = QAction(QIcon("icons/menu_bar/export.png"), self.tr("&Export Data"), parent)
        self.export_data_action.setToolTip(self.tr("Export the current data view into a new file"))
        export_menu.addAction(self.export_data_action)

        
        # Help Menu
        help_menu = AnimatedMenu(self.tr("&Help"), self)
        self.addMenu(help_menu)
        
        self.about_action = QAction(QIcon("icons/menu_bar/about.png"), self.tr("&About"), parent)
        help_menu.addAction(self.about_action)