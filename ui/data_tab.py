# ui/data_tab.py
import traceback
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QTextEdit, QListWidgetItem, QApplication, QTableView, QHeaderView, QInputDialog, QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,QTableWidgetItem, QPushButton, QComboBox, QLabel, QLineEdit, QGroupBox, QSpinBox, QMessageBox, QTabWidget, QTextEdit, QScrollArea, QInputDialog, QListWidgetItem, QListWidget, QApplication, QTableView, QHeaderView, QGraphicsOpacityEffect)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QIcon, QFont

from core.data_handler import DataHandler
from core.aggregation_manager import AggregationManager
from ui.status_bar import StatusBar
from ui.dialogs import ProgressDialog, RenameColumnDialog, FilterAdvancedDialog, AggregationDialog, FillMissingDialog, HelpDialog, MeltDialog
from core.subset_manager import SubsetManager
from pathlib import Path
from ui.widgets.AnimatedListWidget import AnimatedListWidget
from core.help_manager import HelpManager
from ui.data_table_model import DataTableModel
from ui.widgets.AnimatedButton import AnimatedButton
from ui.widgets.AnimatedComboBox import AnimatedComboBox
from ui.widgets.AnimatedGroupBox import AnimatedGroupBox
from ui.widgets.AnimatedLineEdit import AnimatedLineEdit
from ui.widgets.AnimatedTabWidget import AnimatedTabWidget
from ui.widgets.HelpIcon import HelpIcon
from ui.animations.ResetToOriginalStateAnimation import ResetToOriginalStateAnimation

class DataTab(QWidget):
    """Tab for viewing and manipulating data"""
    
    def __init__(self, data_handler: DataHandler, status_bar: StatusBar, subset_manager: SubsetManager):
        super().__init__()
        
        self.data_handler = data_handler
        self.status_bar = status_bar
        self.subset_manager = subset_manager
        self.aggregation_manager = AggregationManager()
        self.help_manager = HelpManager()
        self.plot_tab = None
        self.data_table = None
        self.stats_text = None
        self.data_tabs = None
        self.subset_view_label = None
        self.aggregation_view_label = None
        self.is_editing = False
        
        self.init_ui()
    
    def set_plot_tab(self, plot_tab):
        """Sets a reference to the PlotTab"""
        self.plot_tab = plot_tab
    
    def init_ui(self):
        """Initialize the data tab UI"""
        main_layout = QHBoxLayout(self)
        
        # Left side: Data table and operations
        left_layout = QVBoxLayout()

        #data toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        #create dataset
        self.create_new_dataset_button = AnimatedButton("Create a New Dataset", parent=self, base_color_hex="#3498DB", text_color_hex="white")
        self.create_new_dataset_button.setIcon(QIcon("icons/menu_bar/new_project.png"))
        self.create_new_dataset_button.setToolTip("Create a new empty DataFrame")
        self.create_new_dataset_button.clicked.connect(self.create_new_dataset)
        toolbar_layout.addWidget(self.create_new_dataset_button)

        toolbar_layout.addStretch()

        #edit current dataset toggle
        self.edit_dataset_toggle_button = AnimatedButton("Edit Mode: OFF", parent=self, base_color_hex="#95a5a6", text_color_hex="white")
        self.edit_dataset_toggle_button.setIcon(QIcon("icons/code_edit.png"))
        self.edit_dataset_toggle_button.setCheckable(True)
        self.edit_dataset_toggle_button.setToolTip("Toggle to edit data directly in the table")
        self.edit_dataset_toggle_button.clicked.connect(self.toggle_edit_mode)
        toolbar_layout.addWidget(self.edit_dataset_toggle_button)

        left_layout.addLayout(toolbar_layout)

        #data source inor bar
        self.data_source_container = QWidget()
        data_source_layout = QHBoxLayout(self.data_source_container)
        data_source_layout.setContentsMargins(0, 0, 0, 0)

        self.data_source_prefix_label = QLabel("Data Source:")
        self.data_source_prefix_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        data_source_layout.addWidget(self.data_source_prefix_label)

        self.data_source_name_label = QLabel("")
        self.data_source_name_label.setStyleSheet("color: #3498db; font-style: italic;")
        data_source_layout.addWidget(self.data_source_name_label)

        self.subset_view_label = QLabel("")
        self.subset_view_label.setStyleSheet("color: #e67e22; font-weight: bold; margin-left: 10px;")
        self.subset_view_label.setVisible(False)
        data_source_layout.addWidget(self.subset_view_label)

        self.aggregation_view_label = QLabel("")
        self.aggregation_view_label.setStyleSheet("color: #8e44ad; font-weight: bold; margin-left: 10px;")
        self.aggregation_view_label.setVisible(False)
        data_source_layout.addWidget(self.aggregation_view_label)

        data_source_layout.addStretch()
        self.data_source_refresh_button = AnimatedButton("Refresh Data", parent=self, base_color_hex="#27ae60",hover_color_hex="#229954", text_color_hex="white", font_weight="bold", padding="6px 12px")
        
        self.data_source_refresh_button.setIcon(QIcon("icons/menu_bar/google_sheet.png"))
        self.data_source_refresh_button.setToolTip("Re-import data from your Google Sheets document")
        
        self.data_source_refresh_button.clicked.connect(self.refresh_google_sheets_data)
        data_source_layout.addWidget(self.data_source_refresh_button)

        self.data_source_container.setVisible(False)
        left_layout.addWidget(self.data_source_container)
        
        # Create tabs for data and statistics
        self.data_tabs = AnimatedTabWidget()
        
        # Data Table Tab
        self.data_table = QTableView()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSortingEnabled(True)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.data_table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.data_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        data_table_icon = QIcon("icons/data_table.png")
        self.data_tabs.addTab(self.data_table, data_table_icon, "Data Table")
        
        # Statistics Tab
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)

        self.stats_opacity_effect = QGraphicsOpacityEffect(self.stats_text)
        self.stats_text.setGraphicsEffect(self.stats_opacity_effect)
        stats_icon = QIcon("icons/data_stats.png")
        self.data_tabs.addTab(self.stats_text, stats_icon, "Statistics")
        
        left_layout.addWidget(self.data_tabs, 1)
        
        right_layout = QVBoxLayout()
        
        # Reset button at the to
        reset_button = AnimatedButton("Reset to Original", parent=self, base_color_hex="#ffcccc", hover_color_hex="#faafaf")
        reset_button.setIcon(QIcon("icons/data_operations/reset.png"))
        reset_button.clicked.connect(self.reset_data)
        right_layout.addWidget(reset_button)
        
        # Create tabbed operations interface
        ops_tabs = AnimatedTabWidget()
        
        # TAB 1: CLEANING 
        cleaning_tab = QWidget()
        cleaning_layout = QVBoxLayout(cleaning_tab)

        clean_info = QLabel("This tab includes operations to clean your dataset.")
        clean_info.setWordWrap(True)
        clean_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        cleaning_layout.addWidget(clean_info)
        
        remove_dups_layout = QHBoxLayout()
        clean_button = AnimatedButton("Remove Duplicates", parent=self)
        clean_button.setToolTip("Use this to remove any instances of duplicate entries in your dataset")
        clean_button.setIcon(QIcon("icons/data_operations/remove_duplicates.png"))
        clean_button.clicked.connect(self.remove_duplicates)
        self.remove_duplicates_help = HelpIcon('remove_duplicates')
        self.remove_duplicates_help.clicked.connect(self.show_help_dialog)
        remove_dups_layout.addWidget(clean_button, 1)
        remove_dups_layout.addWidget(self.remove_duplicates_help)
        cleaning_layout.addLayout(remove_dups_layout)
        
        drop_missing_layout = QHBoxLayout()
        drop_missing_button = AnimatedButton("Drop Missing Values", parent=self)
        drop_missing_button.setToolTip("Use this to remove rows in your dataset with incomplete entries")
        drop_missing_button.setIcon(QIcon("icons/data_operations/drop_missing_values.png"))
        drop_missing_button.clicked.connect(self.drop_missing)
        self.drop_missing_help = HelpIcon('drop_missing')
        self.drop_missing_help.clicked.connect(self.show_help_dialog)
        drop_missing_layout.addWidget(drop_missing_button)
        drop_missing_layout.addWidget(self.drop_missing_help)
        cleaning_layout.addLayout(drop_missing_layout)
        
        fill_missing_layout = QHBoxLayout()
        fill_missing_button = AnimatedButton("Fill Missing Values", parent=self)
        fill_missing_button.setToolTip("Use this to fill in 'NaN' values in your dataset to something specific")
        fill_missing_button.setIcon(QIcon("icons/data_operations/fill_missing_data.png"))
        fill_missing_button.clicked.connect(self.fill_missing)
        self.fill_missing_help = HelpIcon('fill_missing')
        self.fill_missing_help.clicked.connect(self.show_help_dialog)

        fill_missing_layout.addWidget(fill_missing_button)
        fill_missing_layout.addWidget(self.fill_missing_help)
        cleaning_layout.addLayout(fill_missing_layout)
        
        cleaning_layout.addStretch()
        data_clean_icon = QIcon("icons/data_operations/data_cleaning.png")
        ops_tabs.addTab(cleaning_tab, data_clean_icon, "Cleaning")


        #  TAB 2: FILTERING 
        filter_tab = QWidget()
        filter_layout = QVBoxLayout(filter_tab)

        filter_info = QLabel("This tab has operations which help you filter your dataset based on your own criteria. Use the 'Advanced Filter' dialog to apply more than one filter")
        filter_info.setWordWrap(True)
        filter_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        filter_layout.addWidget(filter_info)

        filter_layout.addWidget(QLabel("Column:"))
        filter_column_info = QLabel("Select the column you wish to apply a filter to")
        filter_column_info.setWordWrap(True)
        filter_column_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        filter_layout.addWidget(filter_column_info)

        self.filter_column = AnimatedComboBox()
        filter_layout.addWidget(self.filter_column)
        
        filter_layout.addWidget(QLabel("Condition:"))
        filter_condition_info = QLabel("Select which conditional to apply to column. N.B. Uses Python Syntax")
        filter_condition_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        filter_condition_info.setWordWrap(True)
        filter_layout.addWidget(filter_condition_info)

        self.filter_condition = AnimatedComboBox()
        self.filter_condition.addItems(['==', '!=', '>', '<', '>=', '<=', 'contains'])
        filter_layout.addWidget(self.filter_condition)
        
        filter_layout.addWidget(QLabel("Value:"))
        filter_value_info = QLabel("Enter the value you want the column to be evaluate to. Note: reference your data. This is case-sensitive")
        filter_value_info.setWordWrap(True)
        filter_value_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        filter_layout.addWidget(filter_value_info)

        self.filter_value = AnimatedLineEdit()
        filter_layout.addWidget(self.filter_value)
        
        apply_filter_layout = QHBoxLayout()
        apply_filter_button = AnimatedButton("Apply Filter", parent=self)
        apply_filter_button.setIcon(QIcon("icons/data_operations/apply_filter.png"))
        apply_filter_button.clicked.connect(self.apply_filter)
        self.apply_filter_help = HelpIcon("apply_filter")
        self.apply_filter_help.clicked.connect(self.show_help_dialog)
        apply_filter_layout.addWidget(apply_filter_button)
        apply_filter_layout.addWidget(self.apply_filter_help)
        filter_layout.addLayout(apply_filter_layout)
        
        filter_layout.addSpacing(10)
        
        advanced_filter_layout = QHBoxLayout()
        adv_filter_button = AnimatedButton("Advanced Filter", parent=self)
        adv_filter_button.setIcon(QIcon("icons/data_operations/advanced_filter.png"))
        adv_filter_button.clicked.connect(self.open_advanced_filter)
        self.apply_filter_help = HelpIcon("apply_filter")
        self.apply_filter_help.clicked.connect(self.show_help_dialog)
        advanced_filter_layout.addWidget(adv_filter_button)
        advanced_filter_layout.addWidget(self.apply_filter_help)
        filter_layout.addLayout(advanced_filter_layout)
        
        filter_layout.addStretch()
        filter_icon = QIcon("icons/data_operations/filter.png")
        ops_tabs.addTab(filter_tab, filter_icon, "Filter Data")
        
        #  TAB 3: COLUMNS 
        column_tab = QWidget()
        column_layout = QVBoxLayout(column_tab)

        column_info = QLabel("This tab allows you to change certain elements to the columns of your data")
        column_info.setWordWrap(True)
        column_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        column_layout.addWidget(column_info)
        
        column_layout.addWidget(QLabel("Select Column:"))
        column_column_info = QLabel("Select the column you wish to work with")
        column_column_info.setWordWrap(True)
        column_column_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        column_layout.addWidget(column_column_info)

        self.column_select = AnimatedComboBox()
        column_layout.addWidget(self.column_select)
        
        drop_column_layout = QHBoxLayout()
        drop_column_button = AnimatedButton("Drop Column", parent=self)
        drop_column_button.setToolTip("Use this to remove the selected column from the dataset")
        drop_column_button.setIcon(QIcon("icons/data_operations/drop_column.png"))
        drop_column_button.clicked.connect(self.drop_column)
        self.drop_column_help = HelpIcon("drop_column")
        self.drop_column_help.clicked.connect(self.show_help_dialog)
        drop_column_layout.addWidget(drop_column_button)
        drop_column_layout.addWidget(self.drop_column_help)
        column_layout.addLayout(drop_column_layout)
        
        rename_layout = QHBoxLayout()
        rename_button = AnimatedButton("Rename Column", parent=self)
        rename_button.setToolTip("Use this to rename the selected column")
        rename_button.setIcon(QIcon("icons/data_operations/rename.png"))
        rename_button.clicked.connect(self.rename_column)
        self.rename_column_help = HelpIcon("rename_column")
        self.rename_column_help.clicked.connect(self.show_help_dialog)
        rename_layout.addWidget(rename_button)
        rename_layout.addWidget(self.rename_column_help)
        column_layout.addLayout(rename_layout)

        column_layout.addSpacing(10)

        #datatype convers
        type_group = AnimatedGroupBox("Change Data Type")
        type_layout = QVBoxLayout()

        data_type_info = QLabel("This operation allows you to change the datatype of your selected column. To see what datatype your data is; reference the statistics tab next to DataTable")
        data_type_info.setWordWrap(True)
        data_type_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        type_layout.addWidget(data_type_info)

        type_layout.addWidget(QLabel("Change selected columns DataType to:"))

        self.type_combo = AnimatedComboBox()
        self.type_combo.addItems([
            "string (object)",
            "integer (numeric)",
            "float (numeric)",
            "category (optimzied string)",
            "datetime (dates/times)"
        ])
        self.type_combo.setToolTip(
            "string: For text data\n"
            "integer: For whole numbers\n"
            "float: For decimal values\n"
            "category: For text with few unique values\n"
            "datetime: For dates and time"
        )
        type_layout.addWidget(self.type_combo)

        datatype_layout = QHBoxLayout()
        type_button = AnimatedButton("Apply DataType Change", parent=self)
        type_button.setIcon(QIcon("icons/data_operations/change_datatype.png"))
        type_button.clicked.connect(self.change_column_type)
        self.change_datatype_help = HelpIcon("change_datatype")
        self.change_datatype_help.clicked.connect(self.show_help_dialog)
        datatype_layout.addWidget(type_button)
        datatype_layout.addWidget(self.change_datatype_help)
        type_layout.addLayout(datatype_layout)

        type_group.setLayout(type_layout)
        column_layout.addWidget(type_group)
        
        column_layout.addStretch()
        column_icon = QIcon("icons/data_operations/edit_cols.png")
        ops_tabs.addTab(column_tab, column_icon, "Columns")
        
        #  TAB 4: TRANSFORM 
        transform_tab = QWidget()
        transform_layout = QVBoxLayout(transform_tab)

        transform_info = QLabel("This tab allows you to alter your input data by grouping and aggregation the data based on statistical parameters. Click the 'Aggregate Data' to learn more")
        transform_info.setWordWrap(True)
        transform_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        transform_layout.addWidget(transform_info)
        
        agg_layout = QHBoxLayout()
        agg_button = AnimatedButton("Aggregate Data", parent=self)
        agg_button.setIcon(QIcon("icons/data_operations/aggregate_data.png"))
        agg_button.clicked.connect(self.open_aggregation_dialog)
        self.agg_help = HelpIcon("aggregate_data")
        self.agg_help.clicked.connect(self.show_help_dialog)
        agg_layout.addWidget(agg_button)
        agg_layout.addWidget(self.agg_help)
        transform_layout.addLayout(agg_layout)

        melt_layout = QHBoxLayout()
        melt_button = AnimatedButton("Melt/Unpivot Data", parent=self)
        # melt_button.setIcon(QIcon(""))
        melt_button.clicked.connect(self.open_melt_dialog)
        self.melt_help = HelpIcon("melt_data")
        self.melt_help.clicked.connect(self.show_help_dialog)
        melt_layout.addWidget(melt_button)
        melt_layout.addWidget(self.melt_help)
        transform_layout.addLayout(melt_layout)


        transform_layout.addSpacing(10)

        ##saved agg section
        saved_agg_group = AnimatedGroupBox("Saved Aggregations")
        saved_agg_layout = QVBoxLayout()

        saved_agg_info = QLabel("Save aggregations to switch between different views of your dataset")
        saved_agg_info.setWordWrap(True)
        saved_agg_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        saved_agg_layout.addWidget(saved_agg_info)

        #list of saved aggs
        self.saved_agg_list = AnimatedListWidget()
        self.saved_agg_list.setMaximumHeight(150)
        self.saved_agg_list.itemClicked.connect(self.on_saved_agg_selected)
        saved_agg_layout.addWidget(self.saved_agg_list)

        #buttons
        saved_agg_buttons = QHBoxLayout()
        self.view_agg_btn = AnimatedButton("View Aggregations", parent=self)
        self.view_agg_btn.setToolTip("View the selected aggregated data in the Data Table. N.B. This replaces your current data view. Reset to the original dataset by clicking 'Reset to Original'")
        self.view_agg_btn.setIcon(QIcon("icons/data_operations/view.png"))
        self.view_agg_btn.setEnabled(False)
        self.view_agg_btn.clicked.connect(self.view_saved_aggregations)
        saved_agg_buttons.addWidget(self.view_agg_btn)

        self.refresh_agg_list_btn = AnimatedButton("Refresh", parent=self)
        self.refresh_agg_list_btn.setToolTip("Refresh the list of saved aggregations of your data. Use this if your aggregations does not show up in the list")
        self.refresh_agg_list_btn.setIcon(QIcon("icons/data_operations/refresh.png"))
        self.refresh_agg_list_btn.clicked.connect(self.refresh_saved_agg_list)
        saved_agg_buttons.addWidget(self.refresh_agg_list_btn)
        saved_agg_layout.addLayout(saved_agg_buttons)

        #delete button
        self.delete_agg_btn = AnimatedButton("Delete Selected Aggregtation", parent=self)
        self.delete_agg_btn.setToolTip("Use this to delete the selected aggregation from the list")
        self.delete_agg_btn.setIcon(QIcon("icons/data_operations/delete.png"))
        self.delete_agg_btn.setEnabled(False)
        self.delete_agg_btn.clicked.connect(self.delete_saved_aggregation)
        saved_agg_layout.addWidget(self.delete_agg_btn)

        saved_agg_group.setLayout(saved_agg_layout)
        transform_layout.addWidget(saved_agg_group)
        
        transform_layout.addStretch()
        transform_icon = QIcon("icons/data_operations/data_transformation.png")
        ops_tabs.addTab(transform_tab, transform_icon, "Transform")

        # TAB 5: SUBSETS
        subset_tab = QWidget()
        subset_layout = QVBoxLayout(subset_tab)

        #info label
        subset_info = QLabel(
            "This tab allows you to create and manage data subsets.\n"
            "Data subsets are smaller, more manageable portions of larger datasets.\n"
            "Subsets do not modify your original dataset.\n"
            "Use the 'Manage Subsets' button to create your own subsets or use the 'Auto-Create Subsets' to automatically create subsets for a column"
        )
        subset_info.setWordWrap(True)
        subset_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        subset_layout.addWidget(subset_info)

        subset_layout.addSpacing(10)

        #manage buttons
        manage_subsets_layout = QHBoxLayout()
        manage_subsets_btn = AnimatedButton("Manage Subsets", parent=self)
        #manage_subsets_btn.setIcon(QIcon("icons/data_operations/subset.png")) # ICON NEEDED!!!!!
        manage_subsets_btn.clicked.connect(self.open_subset_manager)
        self.subset_help = HelpIcon("manage_subsets")
        self.subset_help.clicked.connect(self.show_help_dialog)
        manage_subsets_layout.addWidget(manage_subsets_btn)
        manage_subsets_layout.addWidget(self.subset_help)
        subset_layout.addLayout(manage_subsets_layout)

        subset_layout.addSpacing(10)

        #qucik subset createion
        quick_subset_group = AnimatedGroupBox("Quick Subset Creation")
        quick_subset_layout = QVBoxLayout()
        quick_subset_layout.addWidget(QLabel("Split data by column values:"))

        self.subset_column_combo = AnimatedComboBox()
        quick_subset_layout.addWidget(self.subset_column_combo)

        quick_create_subset_layout = QHBoxLayout()
        quick_create_btn = AnimatedButton("Auto-Create Subsets", parent=self)
        #quick_create_btn.setIcon(QIcon("icons/data_operations/auto_subset.png")) #ICON NEEDDED!!!!!
        quick_create_btn.clicked.connect(self.quick_create_subsets)
        self.quick_subset_help = HelpIcon("auto_create_subsets")
        self.quick_subset_help.clicked.connect(self.show_help_dialog)
        quick_create_subset_layout.addWidget(quick_create_btn)
        quick_create_subset_layout.addWidget(self.quick_subset_help)
        quick_subset_layout.addLayout(quick_create_subset_layout)

        quick_subset_group.setLayout(quick_subset_layout)
        subset_layout.addWidget(quick_subset_group)

        subset_layout.addSpacing(10)

        # Current subsets list
        subset_list_group = AnimatedGroupBox("Active Subsets")
        subset_list_layout = QVBoxLayout()

        self.active_subsets_list = AnimatedListWidget()
        self.active_subsets_list.setMaximumHeight(150)
        self.active_subsets_list.itemDoubleClicked.connect(self.view_subset_quick)
        subset_list_layout.addWidget(self.active_subsets_list)

        subset_list_btns = QHBoxLayout()

        view_subset_btn = AnimatedButton("View", parent=self)
        view_subset_btn.setIcon(QIcon("icons/data_operations/view.png"))
        view_subset_btn.clicked.connect(self.view_subset_quick)
        subset_list_btns.addWidget(view_subset_btn)

        refresh_subsets_btn = AnimatedButton("Refresh", parent=self)
        refresh_subsets_btn.setIcon(QIcon("icons/data_operations/refresh.png"))
        refresh_subsets_btn.clicked.connect(self.refresh_active_subsets)
        subset_list_btns.addWidget(refresh_subsets_btn)

        subset_list_layout.addLayout(subset_list_btns)

        subset_list_group.setLayout(subset_list_layout)
        subset_layout.addWidget(subset_list_group)

        subset_layout.addStretch()

        # subset injection tool.
        #this shulld allow the user to view their subset in the active DF
        inject_group = AnimatedGroupBox("View Subset as Active DataFrame")
        inject_layout = QVBoxLayout()

        inject_info = QLabel(
            "Insert the selected subset into the active DataFrame to work directly with it.\n"
            "Warning: This temporarily replaces your current data view."
        )
        inject_info.setWordWrap(True)
        inject_info.setStyleSheet("color: #ff6b35; font-style: italic; font-size: 9pt;")
        inject_layout.addWidget(inject_info)

        inject_layout.addSpacing(10)

        #thebuttn
        self.inject_subset_tbn = AnimatedButton("Insert Selected Subset", parent=self, base_color_hex="#3409db", hover_color_hex="#1b0085", text_color_hex="white", font_weight="bold", padding="8px")
        #self.inject_subset_tbn.setIcon(QIcon("icons/data_operations/inject.png")) ###mangler ikon
        self.inject_subset_tbn.clicked.connect(self.inject_subset_to_dataframe)
        inject_layout.addWidget(self.inject_subset_tbn)

        #status label
        self.injection_status_label = QLabel("Status: Working with original data")
        self.injection_status_label.setStyleSheet(
            "color: #27ae60; font-weight: bold; padding: 5px; "
            "background-color: #ecf0f1; border-radius: 3px;"
        )
        inject_layout.addWidget(self.injection_status_label)

        inject_layout.addSpacing(10)

        # hmm a restore btn?
        self.restore_original_btn = AnimatedButton("Revert to Original Data View", parent=self, base_color_hex="#e74c3c", hover_color_hex="#e91801", text_color_hex="white", padding="8px")
        #self.restore_original_btn.setIcon(QIcon("icons/data_operations/restore.png")) #Tilføj et ikon senere
        self.restore_original_btn.clicked.connect(self.restore_original_dataframe)
        self.restore_original_btn.setEnabled(False)
        inject_layout.addWidget(self.restore_original_btn)

        inject_group.setLayout(inject_layout)
        subset_layout.addWidget(inject_group)

        subset_layout.addStretch()

        subset_icon = QIcon("icons/data_operations/subset.png")  
        ops_tabs.addTab(subset_tab, subset_icon, "Subsets")

        #Tah6 -history 
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        history_info = QLabel("View and revert to a previous state of data state")
        history_info.setWordWrap(True)
        history_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        history_layout.addWidget(history_info)

        self.history_list = AnimatedListWidget()
        self.history_list.itemClicked.connect(self.on_history_clicked)
        history_layout.addWidget(self.history_list)

        #text for help/understanding
        history_help = QLabel("Click on a state to go back/forwards to it.\nGray items are undone operations.")
        history_help.setWordWrap(True)
        history_help.setStyleSheet("color: #7f8c8d; font-size: 8pt;")
        history_layout.addWidget(history_help)

        history_icon = QIcon("icons/data_operations/view.png")
        ops_tabs.addTab(history_tab, history_icon, "History")
        
        right_layout.addWidget(ops_tabs)
        
        # Create widgets for layout management
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        # Create splitter
        from PyQt6.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def create_new_dataset(self):
        """Creates a new empty dataset"""
        try:
            rows, ok = QInputDialog.getInt(self, "New Dataset", "Number of Rows:", 10, 1, 1000000)
            if not ok: return

            columns, ok = QInputDialog.getInt(self, "New Dataset", "Number of Columns:", 3, 1, 1000)
            if not ok: return

            confirm = QMessageBox.question(
                self, "Confirm Create",
                "This will clear the current dataset and create a new empty dataset. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if confirm == QMessageBox.StandardButton.Yes:
                self.data_handler.create_empty_dataframe(rows, columns)
                self.refresh_data_view()
                self.status_bar.log(f"Created new dataset: ({rows}x{columns})", "SUCCESS")
        
        except Exception as CreateNewDatasetError:
            QMessageBox.critical(self, "Error", f"Failed to create dataset: {str(CreateNewDatasetError)}")
        
    def toggle_edit_mode(self):
        """Toggles the edit mode in the datble"""
        self.is_editing = self.edit_dataset_toggle_button.isChecked()

        if self.is_editing:
            self.edit_dataset_toggle_button.setText("Edit Mode: ON")
            self.edit_dataset_toggle_button.updateColors(base_color_hex="#E74C3C", hover_color_hex="#C0392B")
            self.data_table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed)
            self.status_bar.log(f"Edit Mode Enabled. You are now able to edit cells in the data table", "INFO")
        else:
            self.edit_dataset_toggle_button.setText("Edit Mode: OFF")
            self.edit_dataset_toggle_button.updateColors(base_color_hex="#95A5A6", hover_color_hex="#7F8C8D")
            self.data_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
            self.status_bar.log(f"Edit Mode Disabled", "INFO")
        
        #update the flags
        self.refresh_data_view()


    def inject_subset_to_dataframe(self):
        """Insert the selected subset into the active dataframe view.\n
            This allows the user to view their subset and do further manipulation to it, without having to export the subset first."""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No data", "Please load data first")
            return
        
        # get the selected subset
        item = self.active_subsets_list.currentItem()
        if not item:
            QMessageBox.warning(self, "None selected", "Please select a subset to apply to current data view")
            return
        
        subset_name = item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Are you sure you want to insert the subset: '{subset_name}' into the active DataFrame\n\n"
            f"This will temporarily replace the current data view.\n"
            f"You can restore the original data view by pressing the 'Revert to Original Data View'",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # we need to store the original df first.
            if not hasattr(self.data_handler, "pre_insert_df") or self.data_handler.pre_insert_df is None:
                self.data_handler.pre_insert_df = self.data_handler.df.copy()
                self.data_handler.inserted_subset_name = None

            subset_manager = self.subset_manager
            subset_df = subset_manager.apply_subset(self.data_handler.df, subset_name, use_cache=False)

            self.data_handler.df = subset_df.copy()
            self.data_handler.inserted_subset_name = subset_name

            self.refresh_data_view()

            self.injection_status_label.setText(f"Status: Working with a subset: '{subset_name}'")
            self.injection_status_label.setStyleSheet(
                "color: #e74c3c; font-weight: bold; padding: 5px;"
                "background-color: #ffe5e5; border-radius: 3px;"
            )
            self.restore_original_btn.setEnabled(True)
            self.inject_subset_tbn.setEnabled(False)

            self.status_bar.log_action(
                f"Inserted the subset: '{subset_name}' into the active DataFrame",
                details={
                    "subset_name": subset_name,
                    "subset_rows": len(subset_df),
                    "original_rows": len(self.data_handler.pre_insert_df),
                    "operation": "insert_subset_into_active_data_view"
                },
                level="SUCCESS"
            )

            QMessageBox.information(
                self,
                "Insertion Complete",
                f"Subset '{subset_name}' has been inserted into the active DataFrame.\n\n"
                f"Original data: {len(self.data_handler.pre_insert_df):,} rows\n"
                f"Subset data: {len(subset_df):,} rows\n\n"
                f"Click 'Restore Original Data View' to return to the full dataset."
            )
        
        except Exception as InsertSubsetIntoDataFrameError:
            self.status_bar.log(f"Failed to insert the subset: {str(InsertSubsetIntoDataFrameError)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to insert subset:\n{str(InsertSubsetIntoDataFrameError)}")
            traceback.print_exc()

    def restore_original_dataframe(self):
        """Restore the original DataFrame into the Active Data View of the Data Table"""
        if not hasattr(self.data_handler, "pre_insert_df") or self.data_handler.pre_insert_df is None:
            QMessageBox.warning(self, "Nothing to Restore", "No inserted subset to restore from")
            return
        
        try:
            subset_name = getattr(self.data_handler, "inserted_subset_name", "Unknown")
            original_rows = len(self.data_handler.pre_insert_df)

            self.data_handler.df = self.data_handler.pre_insert_df.copy()
            self.data_handler.pre_insert_df = None
            self.data_handler.inserted_subset_name = None

            self.refresh_data_view()

            self.injection_status_label.setText("Status: Working with original data")
            self.injection_status_label.setStyleSheet(
                "color: #27ae60; font-weight: bold; padding: 5px; "
                "background-color: #ecf0f1; border-radius: 3px;"
            )
            self.restore_original_btn.setEnabled(False)
            self.inject_subset_tbn.setEnabled(True)

            self.status_bar.log_action(
                f"Restored original DataFrame (from subset '{subset_name}')",
                details={
                    'previous_subset': subset_name,
                    'restored_rows': original_rows,
                    'operation': 'restore_original'
                },
                level="SUCCESS"
            )
            
            QMessageBox.information(
                self,
                "Restore Complete",
                f"Original DataFrame has been restored.\n\n"
                f"Restored: {original_rows:,} rows"
            )
        
        except Exception as RestoreOriginalDataFrameError:
            self.status_bar.log(f"Failed to restore original data: {str(RestoreOriginalDataFrameError)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to restore original data:\n{str(RestoreOriginalDataFrameError)}")
            traceback.print_exc()
    
    def refresh_data_view(self):
        """Refresh the data table and statistics"""
        if self.data_handler.df is None:
            self.data_table.setModel(None)
            self.stats_text.clear()
            self.data_source_container.setVisible(False)
            return
        
        df = self.data_handler.df
        
        # Update table
        self.model = DataTableModel(self.data_handler, editable=self.is_editing)
        self.data_table.setModel(self.model)
        self.data_table.setSortingEnabled(True)

        if self.is_editing:
            self.data_table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed)
        else:
            self.data_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
        
        # Update column selectors
        columns = list(df.columns)
        self.filter_column.clear()
        self.filter_column.addItems(columns)
        self.column_select.clear()
        self.column_select.addItems(columns)
        
        # Update subset column combo if it exists
        if hasattr(self, 'subset_column_combo'):
            try:
                self.subset_column_combo.clear()
                self.subset_column_combo.addItems(columns)
            except Exception as RefreshDataViewError:
                print(f"Warning: Could not update subset column combo: {RefreshDataViewError}")
        
        # Update statistics
        self.update_statistics()

        if self.data_handler.has_google_sheets_import():
            self.data_source_container.setVisible(True)
            self.data_source_prefix_label.setText("Google Sheets Data:")
            self.data_source_name_label.setText(self.data_handler.last_gsheet_name)
            self.data_source_refresh_button.setVisible(True)
        elif hasattr(self.data_handler, "file_path") and self.data_handler.file_path:
            try:
                file_name = Path(self.data_handler.file_path).name
            except Exception:
                file_name = str(self.data_handler.file_path)
            
            self.data_source_container.setVisible(True)
            self.data_source_prefix_label.setText("Local file:")
            self.data_source_name_label.setText(file_name)
            self.data_source_refresh_button.setVisible(False)
        else:
            self.data_source_container.setVisible(False)
        
        try:
            if hasattr(self, 'subset_manager'):
                self.subset_manager.clear_cache()
            if hasattr(self, 'active_subsets_list'):
                self.refresh_active_subsets()
        except Exception as RefreshSubsetInDataViewError:
            print(f"Warning: Could not refresh subsets: {RefreshSubsetInDataViewError}")

        inserted_name = getattr(self.data_handler, "inserted_subset_name", None)
        agg_name = getattr(self.data_handler, "viewing_aggregation_name", None)

        if agg_name and self.data_source_container.isVisible():
            if hasattr(self, "aggregation_view_label"):
                self.aggregation_view_label.setText(f"Viewing Aggregation: {agg_name}")
                self.aggregation_view_label.setVisible(True)
            if hasattr(self, "subset_view_label"):
                self.subset_view_label.setVisible(False)
        
        elif inserted_name and self.data_source_container.isVisible():
            if hasattr(self, "subset_view_label"):
                self.subset_view_label.setText(f"Viewing subset: {inserted_name}")
                self.subset_view_label.setVisible(True)
            if hasattr(self, "aggregation_view_label"):
                self.aggregation_view_label.setVisible(False)
        
        else:
            if hasattr(self, "subset_view_label"):
                self.subset_view_label.setText("")
                self.subset_view_label.setVisible(False)
            if hasattr(self, "aggregation_view_label"):
                self.aggregation_view_label.setText("")
                self.aggregation_view_label.setVisible(False)
        
        if hasattr(self, "history_list"):
            self.history_list.clear()

            history_information = self.data_handler.get_history_info()
            history_operations = history_information["history"]
            current_index = history_information["current_index"]

            initial_item = QListWidgetItem("0. Initial Data")
            initial_item.setData(Qt.ItemDataRole.UserRole, 0)

            if current_index == 0:
                initial_item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                initial_item.setForeground(Qt.GlobalColor.black)
                initial_item.setIcon(QIcon("icons/ui_styling/checkmark.png"))
            
            self.history_list.addItem(initial_item)

            for i, operation in enumerate(history_operations):
                history_index = i + 1
                operation_text = self._format_operation_text(operation)
                item = QListWidgetItem(f"{history_index}. {operation_text}")
                item.setData(Qt.ItemDataRole.UserRole, history_index)

                if history_index == current_index:
                    item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                    item.setForeground(Qt.GlobalColor.black)
                    item.setIcon(QIcon("icons/ui_styling/checkmark.png"))
                    item.setBackground(Qt.GlobalColor.white)
                elif history_index > current_index:
                    item.setForeground(Qt.GlobalColor.gray)
                    font = item.font()
                    font.setItalic(True)
                    item.setFont(font)
                
                self.history_list.addItem(item)

            if self.history_list.count() > 0:
                self.history_list.scrollToItem(self.history_list.item(current_index))

        self.status_bar.log(f"Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    def quick_create_subsets(self):
        """Quick create subsets from column values"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return
        
        if not hasattr(self, 'subset_column_combo'):
            QMessageBox.warning(self, "Feature Not Available", "Subset feature not fully initialized")
            return
        
        column = self.subset_column_combo.currentText()
        if not column:
            QMessageBox.warning(self, "No Column Selected", "Please select a column")
            return
        
        unique_count = self.data_handler.df[column].nunique()
        
        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Create {unique_count} subsets (one per unique value in '{column}')?\n\n"
            f"This is useful for analyzing data by groups (e.g., by location, category, etc.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                subset_manager = self.subset_manager
                created = subset_manager.create_subset_from_unique_values(
                    self.data_handler.df,
                    column
                )
                
                # Apply each to get row counts
                for name in created:
                    subset_manager.apply_subset(self.data_handler.df, name)
                
                self.refresh_active_subsets()
                
                self.status_bar.log_action(
                    f"Created {len(created)} subsets from column '{column}'",
                    details={
                        'column': column,
                        'subsets_created': len(created),
                        'unique_values': unique_count,
                        'operation': 'auto_create_subsets'
                    },
                    level="SUCCESS"
                )
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Created {len(created)} subsets from column '{column}'"
                )
            except Exception as QuickCreateSubsetsError:
                self.status_bar.log(f"Failed to create subsets: {str(QuickCreateSubsetsError)}", "ERROR")
                QMessageBox.critical(self, "Error", str(QuickCreateSubsetsError))
                import traceback
                traceback.print_exc()
    
    def refresh_active_subsets(self):
        """Refresh the list of active subsets"""
        if not hasattr(self, 'active_subsets_list'):
            return
        
        try:
            self.active_subsets_list.clear()
            
            subset_manager = self.subset_manager

            if self.data_handler.df is not None:
                for name in subset_manager.list_subsets():
                    try:
                        subset_manager.apply_subset(self.data_handler.df, name)
                    except Exception as ApplySubsetError:
                        print(f"Warning: Could not apply subset {name}: {str(ApplySubsetError)}")

            for name in subset_manager.list_subsets():
                subset = subset_manager.get_subset(name)
                row_text = f"{subset.row_count} rows" if subset.row_count > 0 else "? rows"
                item = QListWidgetItem(f"{name} ({row_text} rows)")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.active_subsets_list.addItem(item)
        except Exception as RefreshSubsetListError:
            print(f"Warning: Could not refresh subset list: {RefreshSubsetListError}")
    
    def view_subset_quick(self):
        """Quick view of selected subset"""
        if not hasattr(self, 'active_subsets_list'):
            return
        
        item = self.active_subsets_list.currentItem()
        if not item:
            return
        
        name = item.data(Qt.ItemDataRole.UserRole)
        
        try:
            from ui.dialogs import SubsetDataViewer
            subset_manager = self.subset_manager
            subset_df = subset_manager.apply_subset(self.data_handler.df, name)
            viewer = SubsetDataViewer(subset_df, name, self)
            viewer.exec()
        except Exception as ViewSubsetError:
            QMessageBox.critical(self, "Error", str(ViewSubsetError))
            import traceback
            traceback.print_exc()
    
    def open_subset_manager(self):
        """Open the subset manager dialog"""
        print("DEBUG open_subset_manager: Opening dialog")
    
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return
        
        try:
            from ui.dialogs import SubsetManagerDialog
            subset_manager = self.subset_manager
            
            print(f"DEBUG open_subset_manager: SubsetManager has {len(subset_manager.list_subsets())} subsets")
            
            # Create and show dialog
            dialog = SubsetManagerDialog(subset_manager, self.data_handler, self)
            
            print(f"DEBUG open_subset_manager: Dialog created, executing")
            dialog.exec()
            
            print("DEBUG open_subset_manager: Dialog closed, refreshing active subsets")
            # Refresh the subset list after dialog closes
            self.refresh_active_subsets()
            
        except Exception as OpenSubsetManagerError:
            print(f"ERROR open_subset_manager: {str(OpenSubsetManagerError)}")
            QMessageBox.critical(self, "Error", f"Failed to open subset manager: {str(OpenSubsetManagerError)}")
            import traceback
            traceback.print_exc()
    
    def handle_plot_request(self, subset_name: str):
        """Handle the signal from SubsetManagerDialog to plot the selected subset"""
        if not self.plot_tab:
            QMessageBox.warning(self, "Error", "Plot tab reference not set. Cannot switch tabs")
            self.status_bar.log("Plot tab reference not set", "ERROR")
            return
        
        try:
            self.plot_tab.activate_subset(subset_name)

            parent_tab_widget = self.parentWidget()
            if isinstance(parent_tab_widget, AnimatedTabWidget):
                parent_tab_widget.setCurrentWidget(self.plot_tab)
            else:
                self.status_bar.log("Could not switch to plot tab automatically", "WARNING")
            
        except Exception as PlotRequestError:
            self.status_bar.log(f"Failed to switch to plotting tab: {str(PlotRequestError)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to activate the plot tab: {str(PlotRequestError)}")

    def get_subset_manager(self):
        """
        DEPRECATED: Use self.subset_manager directly.
        Return the subset manager instance
        """
        # This function is no longer needed as subset_manager is passed in
        return self.subset_manager
    
    def update_statistics(self) -> None:
        """Update statistics display"""
        if self.data_handler.df is None:
            return
        
        try:
            info = self.data_handler.get_data_info()
            df = self.data_handler.df
        except Exception as UpdateStatisticsError:
            self.stats_text.setHtml(f"<p style='color: red;'>Error loading data info: {str(UpdateStatisticsError)}</p>")
            return
        
        try:
            css_file_path = Path("resources/statistics_style.css")
            html_path = Path("resources/template.html")

            if not css_file_path:
                raise FileNotFoundError(f"Missing CSS resource file: {css_file_path.resolve()}")
            css_content = css_file_path.read_text(encoding="UTF-8")

            if not html_path:
                raise FileNotFoundError(f"Missing HTML resource file: {html_path.resolve()}")
            html_template = html_path.read_text(encoding="UTF-8")

        except Exception as LoadHTMLError:
            error_msg = f"Failed to load CSS/HTML templates: {str(LoadHTMLError)}"
            self.stats_text.setHtml(f"<p style='color: red;'>{error_msg}</p>")
            self.status_bar.log(error_msg, "ERROR")
            traceback.print_exc()
            return
        
        body_html = ""

        body_html += "<h2>Dataset Overview</h2>"
        body_html += "<div class='info-box'>"
        body_html += f"<div class='info-item'><span class='info-label'>Total Rows:</span> <span class='info-value'>{info.get('shape', [0])[0]:,}</span></div>"
        body_html += f"<div class='info-item'><span class='info-label'>Total Columns:</span> <span class='info-value'>{len(info.get('columns', []))}</span></div>"

        #memory
        try:
            total_memory_bytes = df.memory_usage(deep=True).sum()
            total_memory = total_memory_bytes / 1024

            if total_memory > 1024:
                memory_str = f"{total_memory/1024:.2f} MB"
            else:
                memory_str = f"{total_memory:.2f} KB"
        except Exception:
            memory_str = "N/A"
        
        body_html += f"<div class='info-item'><span class='info-label'>Memory Usage:</span> <span class='info-value'>{memory_str}</span></div>"

        try:
            total_missing = sum(info.get("missing_values", {}).values())
        except:
            total_missing = 0
        body_html += f"<div class='info-item'><span class='info-label'>Total Missing Values:</span> <span class='info-value'>{total_missing:,}</span></div>"
        body_html += "</div>"
        
        #colinfo
        body_html += "<h2>Column Information</h2>"
        body_html += "<table>"
        body_html += "<tr><th>Column Name</th><th>Data Type</th><th>Non-Null Count</th><th>Missing Values</th><th>Missing %</th></tr>"

        total_rows = info.get("shape", [0])[0]
        for col in info.get("columns", []):
            try:
                dtype = str(info.get("dtypes", {}).get(col, "Unknown"))
                missing = info.get("missing_values", {}).get(col, 0)
                non_null = total_rows - missing
                missing_pct = (missing / total_rows * 100) if total_rows > 0 else 0

                row_class = ""
                if missing_pct > 50:
                    row_class = "style='background-color: #ffebee;'"
                elif missing_pct > 20:
                    row_class = "style='background-color: #fff9c4;'"
                
                body_html += f"<tr {row_class}>"
                body_html += f"<td><strong>{col}</strong></td>"
                body_html += f"<td>{dtype}</td>"
                body_html += f"<td class='numeric-col'>{non_null:,}</td>"
                body_html += f"<td class='numeric-col'>{missing:,}</td>"
                body_html += f"<td class='numeric-col'>{missing_pct:.1f}%</td>"
                body_html += "</tr>"
            except Exception:
                continue
        
        body_html += "</table>"
        
        #wwarning fr misisng values
        if total_missing > 0:
            high_missing_cols = [col for col, missing in info.get("missing_values", {}).items() if missing > 0]
            
            if high_missing_cols:
                body_html += "<div class='warning'>"
                body_html += f"<strong>Warning:</strong> {len(high_missing_cols)} column(s) contain missing values. "
                body_html += "Consider using data cleaning operations."
                body_html += "</div>"
        
        try:
            numeric_df = df.select_dtypes(include=["int64", "int32", "float64", "float32"])

            if len(numeric_df.columns) > 0:
                body_html += "<h2>Descriptive Statistics (Numeric Columns)</h2>"

                df_describe = numeric_df.describe()

                body_html += "<table>"
                body_html += "<tr><th>Statistics</th>"
                for col in df_describe.columns:
                    body_html += f"<th>{col}</th>"
                body_html += "</tr>"

                stats_labels = {
                    "count": "Count",
                    "mean": "Mean",
                    "std": "Standard Deviation",
                    "min": "Minimum",
                    "25%": "25th Percentile",
                    "50%": "Median",
                    "75%": "75th Percentile",
                    "max": "Maximum"
                }

                for stat in df_describe.index:
                    body_html += f"<tr><td><strong>{stats_labels.get(stat, stat)}</strong></td>"
                    for col in df_describe.columns:
                        value = df_describe.loc[stat, col]
                        if stat == "count":
                            body_html += f"<td class='numeric-col'>{int(value):,}</td>"
                        else:
                            body_html += f"<td class='numeric-col'>{value:.4f}</td>"
                    body_html += "</tr>"

                body_html += "</table>"
        except Exception as UpdateNumericalStatisticsError:
            body_html += f"<div class='warning'>Unable to calculate numeric statistics: {str(UpdateNumericalStatisticsError)}</div>"
        
        #correlation matrix
        try:
            numeric_df = df.select_dtypes(include=["int64", "int32", "float64", "float32"])
            
            if len(numeric_df.columns) > 1:
                body_html += "<h2>Correlation Matrix</h2>"
                corr = numeric_df.corr()

                body_html += "<table>"
                body_html += "<tr><th></th>"
                for col in corr.columns:
                    body_html += f"<th>{col}</th>"
                body_html += "</tr>"

                for idx in corr.index:
                    body_html += f"<tr><td><strong>{idx}</strong></td>"
                    for col in corr.columns:
                        value = corr.loc[idx, col]

                        # color coding
                        if abs(value) >= 0.8 and idx != col:
                            cell_style = "background-color: #c8e6c9; font-weight: bold;"
                        elif abs(value) >= 0.5 and idx != col:
                            cell_style = "background-color: #fff9c4;"
                        elif idx == col:
                            cell_style = "background-color: #e3f2fd;"
                        else:
                            cell_style = ""
                        
                        body_html += f"<td class='numeric-col' style='{cell_style}'>{value:.3f}</td>"
                    body_html += "</tr>"
                
                body_html += "</table>"

                body_html += "<div class='info-box'>"
                body_html += "<strong>Legend:</strong> "
                body_html += "<span style='background-color: #c8e6c9; padding: 2px 6px; border-radius: 3px;'>Strong correlation (≥0.8)</span> "
                body_html += "<span style='background-color: #fff9c4; padding: 2px 6px; border-radius: 3px;'>Moderate correlation (≥0.5)</span>"
                body_html += "</div>"
        except Exception as UpdateCorrelationMatrixError:
            body_html += f"<div class='warning'>Unable to calculate correlation matrix: {str(UpdateCorrelationMatrixError)}</div>"
        
        # categorical stats
        try:
            categorical_df = df.select_dtypes(include=["object", "category"])

            if len(categorical_df.columns) > 0:
                body_html += "<h2>Categorical Column Statistics</h2>"
                body_html += "<table>"
                body_html += "<tr><th>Column</th><th>Unique Values</th><th>Most Common</th><th>Frequency</th></tr>"

                for col in categorical_df.columns:
                    try:
                        unique_count = df[col].nunique()
                        value_counts = df[col].value_counts()

                        if len(value_counts) > 0:
                            most_common = str(value_counts.index[0])
                            most_common_freq = value_counts.iloc[0]

                            body_html += "<tr>"
                            body_html += f"<td><strong>{col}</strong></td>"
                            body_html += f"<td class='numeric-col'>{unique_count}</td>"
                            body_html += f"<td>{most_common}</td>"
                            body_html += f"<td class='numeric-col'>{most_common_freq:,}</td>"
                            body_html += "</tr>"
                    except:
                        #
                        continue
                
                body_html += "</table>"
        except Exception as UpdateCategoricalStatisticsError:
            body_html += f"<div class='warning'>Unable to calculate categorical statistics: {str(UpdateCategoricalStatisticsError)}</div>"
        
        final_html = html_template.format(
            css_content=css_content,
            body_content=body_html
        )
        self.stats_text.setHtml(final_html)

        self.stats_animation = QPropertyAnimation(self.stats_opacity_effect, b"opacity")
        self.stats_animation.setDuration(500)
        self.stats_animation.setStartValue(0.0)
        self.stats_animation.setEndValue(1.0)
        self.stats_animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.stats_animation.start()

    def remove_duplicates(self) -> None:
        """Remove duplicate rows"""
        try:
            before = len(self.data_handler.df)
            self.data_handler.clean_data("drop_duplicates")
            after = len(self.data_handler.df)
            removed = before - after

            self.refresh_data_view()

            #msg
            self.status_bar.log_action(
                f"Removed {removed:,} duplicate row(s)",
                details={
                    "rows_before": before,
                    "rows_after": after,
                    "rows_removed": removed,
                    "operation": "drop_duplicates"
                },
                level="SUCCESS"
            )
        except Exception as RemoveDuplicatesError:
            self.status_bar.log(f"Failed to remove duplicates: {str(RemoveDuplicatesError)}", "ERROR")
    
    def drop_missing(self):
        """Drop rows with missing values"""
        try:
            before = len(self.data_handler.df)
            self.data_handler.clean_data('drop_missing')
            after = len(self.data_handler.df)
            removed = before - after

            self.refresh_data_view()

            self.status_bar.log_action(
                f"Dropped {removed:,} row(s) with missing values",
                details={
                    "rows_before": before,
                    "rows_after": after,
                    "rows_removed": removed,
                    "operation": "drop_missing"
                },
                level="SUCCESS"
            )
        except Exception as DropMissingError:
            self.status_bar.log(f"Failed to drop missing values: {str(DropMissingError)}", "ERROR")
    
    def fill_missing(self):
        """Fill missing values"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return
        
        try:
            columns = list(self.data_handler.df.columns)
            dialog = FillMissingDialog(columns, self)

            if dialog.exec():
                config = dialog.get_config()

                df = self.data_handler.df
                missing_before = df.isnull().sum().sum()

                self.data_handler.clean_data(
                    "fill_missing",
                    column=config["column"],
                    method=config["method"],
                    value=config["value"]
                )

                missing_after = self.data_handler.df.isnull().sum().sum()
                filled = missing_before - missing_after

                self.refresh_data_view()
                col_msg = config["column"]
                method_msg = config["method"]
                if method_msg == "static_value":
                    method_msg = f"value '{config['value']}'"
                
                self.status_bar.log_action(
                    f"Filled {filled:,} missing values in {col_msg} using {method_msg}",
                    details={
                        "missing_before": missing_before,
                        "missing_after": missing_after,
                        "filled_count": filled,
                        "method": config["method"],
                        "column": config["column"],
                        "operation": "fill_missing"
                    },
                    level="SUCCESS"
                )
        except Exception as FillMissingValuesError:
            self.status_bar.log(f"Failed to execute 'Fill Missing values': {str(FillMissingValuesError)}", "ERROR")
            QMessageBox.critical(self, "Error", f"Failed to execute 'Fill Missing Values':\n{str(FillMissingValuesError)}")
    
    def apply_filter(self):
        """Apply filter to data"""
        try:
            column = self.filter_column.currentText()
            condition = self.filter_condition.currentText()
            value = self.filter_value.text()

            try:
                if "." in value:
                    value = float(value)
                else:
                    value = int(value)
            except ValueError:
                pass

            #we reset to original before apply a new filter. this is so the user doesnt have to click the button themselves
            if self.data_handler.original_df is not None:
                self.data_handler.reset_data()

                if hasattr(self.data_handler, "pre_insert_df"):
                    self.data_handler.pre_insert_df = None
                if hasattr(self.data_handler, "inserted_subset_name"):
                    self.data_handler.inserted_subset_name = None
                if hasattr(self.data_handler, "viewing_aggregation_name"):
                    self.data_handler.viewing_aggregation_name = None
                if hasattr(self.data_handler, "pre_agg_view_df"):
                    self.data_handler.pre_agg_view_df = None
                
                if hasattr(self, "injection_status_label"):
                    self.injection_status_label.setText("Status: Working with original data")
                    self.injection_status_label.setStyleSheet(
                        "color: #27ae60; font-weight: bold; padding: 5px;"
                        "background-color: #ecf0f1; border-radius: 3px;"
                    )
                    self.restore_original_btn.setEnabled(False)
                    self.inject_subset_tbn.setEnabled(True)
            
            before = len(self.data_handler.df)
            self.data_handler.filter_data(column, condition, value)
            after = len(self.data_handler.df)
            removed = before - after

            self.refresh_data_view()

            self.status_bar.log_action(
                f"Filter: {column} {condition} '{value}' -> {removed:,} rows removed",
                details={
                    "column": column,
                    "condition": condition,
                    "value": value,
                    "rows_before": before,
                    "rows_after": after,
                    "rows_removed": removed,
                    "operation": "filter"
                },
                level="SUCCESS"
            )
        
        except Exception as ApplyFilterError:
            self.status_bar.log(f"Failed to execute 'Filter': {str(ApplyFilterError)}", "ERROR")

    
    def drop_column(self):
        """Drop selected column"""
        try:
            column = self.column_select.currentText()
            cols_before = len(self.data_handler.df.columns)
            
            self.data_handler.clean_data('drop_column', column=column)
            
            cols_after = len(self.data_handler.df.columns)
            
            self.refresh_data_view()
            
            self.status_bar.log_action(
                f"Dropped column '{column}'",
                details={
                    'column': column,
                    'columns_before': cols_before,
                    'columns_after': cols_after,
                    'operation': 'drop_column'
                },
                level="SUCCESS"
            )
        except Exception as DropColumnFromDataFrameError:
            self.status_bar.log(f"Failed to drop column: {str(DropColumnFromDataFrameError)}", "ERROR")
    
    def rename_column(self):
        """Rename selected column"""
        old_name = self.column_select.currentText()
        if not old_name:
            self.status_bar.log("No column selected", "WARNING")
            return
        
        dialog = RenameColumnDialog(old_name, self)
        if dialog.exec():
            new_name = dialog.get_new_name()
            try:
                self.data_handler.clean_data(
                    'rename_column', 
                    old_name=old_name, 
                    new_name=new_name
                )

                self.refresh_data_view()
                self.status_bar.log_action(
                    f"Renamed '{old_name}' → '{new_name}'",
                    details={
                        'old_name': old_name,
                        'new_name': new_name,
                        'operation': 'rename_column'
                    },
                    level="SUCCESS"
                )
            except Exception as RenameColumnError:
                self.status_bar.log(f"Failed to rename column: {str(RenameColumnError)}", "ERROR")

    def change_column_type(self):
        """Change the data type of the selected column"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No data", "Please load data first")
            return

        column = self.column_select.currentText()
        if not column:
            self.status_bar.log("No Column Selected", "WARNING")
            return
        
        type_str = self.type_combo.currentText()

        #mapping the datatypes to their equiv in pandas
        if type_str.startswith("string"):
            target_type = "string"
        elif type_str.startswith("integer"):
            target_type = "int"
        elif type_str.startswith("float"):
            target_type = "float"
        elif type_str.startswith("category"):
            target_type = "category"
        elif type_str.startswith("datetime"):
            target_type = "datetime"
        else:
            self.status_bar.log(f"Unknown DataType: {type_str}", "ERROR")
            return
        
        try:
            old_type = str(self.data_handler.df[column].dtype)

            #add some warning to the user if the're trying to ex convert from int to str
            if target_type in ["int", "float", "datetime"]:
                reply = QMessageBox.question(
                    self,
                    "Confirm DataType Conversion",
                    f"Attempting to convert column: '{column}' to {target_type}.\n\n"
                    f"This may fail or result in data loss.\n"
                    f"Invalid values will be converted to 'NaN'.\n\nContinue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    self.status_bar.log(f"Data Type conversion cancelled", "WARNING")
                    return
                
                self.data_handler.clean_data(
                    "change_data_type",
                    column=column,
                    new_type=target_type
                )
                self.refresh_data_view()

                new_type = str(self.data_handler.df[column].dtype)

                self.status_bar.log_action(
                    f"Changed datatype of '{column}' from {old_type} to {new_type}",
                    details={
                        "column": column,
                        "old_type": old_type,
                        "new_type": new_type,
                        "operation": "change_data_type"
                    },
                    level="SUCCESS"
                )
        except Exception as ChangeColumnDataTypeError:
            error_msg = f"Failed to convert '{column}' to {target_type}: {str(ChangeColumnDataTypeError)}"
            QMessageBox.critical(self, "Conversion Error", error_msg)
            self.status_bar.log(error_msg, "ERROR")
            self.refresh_data_view()

    def reset_data(self):
        """Reset data to original state"""

        #confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset the data to its original state?\n\n"
            "This will discard all changes "
            "and restore the original dataset.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.No:
            self.status_bar.log("Data reset cancelled", "INFO")
            return

        try:
            rows_before = len(self.data_handler.df) if self.data_handler.df is not None else 0
            cols_before = len(self.data_handler.df.columns) if self.data_handler.df is not None else 0

            self.data_handler.reset_data()

            if hasattr(self.data_handler, "pre_insert_df"):
                self.data_handler.pre_insert_df = None
            if hasattr(self.data_handler, "inserted_subset_name"):
                self.data_handler.inserted_subset_name = None

            if hasattr(self.data_handler, "viewing_aggregation_name"):
                self.data_handler.viewing_aggregation_name = None
            if hasattr(self.data_handler, "pre_agg_view_df"):
                self.data_handler.pre_agg_view_df = None

            if hasattr(self, "injection_status_label"):
                self.injection_status_label.setText("Status: Working with original data")
                self.injection_status_label.setStyleSheet(
                    "color: #27ae60; font-weight: bold; padding: 5px;"
                    "background-color: #ecf0f1; border-radius: 3px;"
                )
                self.restore_original_btn.setEnabled(False)
                self.inject_subset_tbn.setEnabled(True)

            rows_after = len(self.data_handler.df) if self.data_handler.df is not None else 0
            cols_after = len(self.data_handler.df.columns) if self.data_handler.df is not None else 0

            self.refresh_data_view()

            self.reset_animation = ResetToOriginalStateAnimation("Reset to Original", parent=None)
            self.reset_animation.start(target_widget=self)

            self.status_bar.log_action(
                "Data reset to original state",
                details={
                    'rows_restored': rows_after - rows_before,
                    'cols_restored': cols_after - cols_before,
                    'final_rows': rows_after,
                    'final_cols': cols_after,
                    'operation': 'reset_data'
                },
                level="SUCCESS"
            )
        except Exception as ResetDataError:
            self.status_bar.log(f"Failed to reset data: {str(ResetDataError)}", "ERROR")
    
    def open_advanced_filter(self):
        """Open advanced filter dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "Warning", "No data loaded")
            return
        
        columns = list(self.data_handler.df.columns)
        dialog = FilterAdvancedDialog(columns, self)
        if dialog.exec():
            filter_config = dialog.get_filters()
            filters = filter_config['filters']
            logic = filter_config['logic']
            
            try:
                before = len(self.data_handler.df)
                
                # Reset to original first
                self.data_handler.reset_data()
                df = self.data_handler.df
                
                if logic == 'AND':
                    # Apply filters sequentially (AND logic)
                    for f in filters:
                        # Convert value if needed
                        value = f['value']
                        try:
                            if '.' in str(value):
                                value = float(value)
                            else:
                                value = int(value)
                        except (ValueError, TypeError):
                            pass
                        
                        self.data_handler.filter_data(f['column'], f['condition'], value)
                else:
                    # Apply OR logic - combine all conditions
                    import pandas as pd
                    mask = pd.Series([False] * len(df))
                    
                    for f in filters:
                        column = f['column']
                        condition = f['condition']
                        value = f['value']
                        
                        # Try to convert value to appropriate type
                        try:
                            if column in df.columns:
                                col_dtype = df[column].dtype
                                if col_dtype in ['int64', 'int32', 'int16', 'int8']:
                                    value = int(value)
                                elif col_dtype in ['float64', 'float32', 'float16']:
                                    value = float(value)
                        except (ValueError, TypeError):
                            pass
                        
                        # Create condition mask
                        try:
                            if condition == '>':
                                mask = mask | (df[column] > value)
                            elif condition == '<':
                                mask = mask | (df[column] < value)
                            elif condition == '==':
                                mask = mask | (df[column] == value)
                            elif condition == '!=':
                                mask = mask | (df[column] != value)
                            elif condition == '>=':
                                mask = mask | (df[column] >= value)
                            elif condition == '<=':
                                mask = mask | (df[column] <= value)
                            elif condition == 'contains':
                                mask = mask | df[column].astype(str).str.contains(str(value), na=False)
                            elif condition == 'in':
                                mask = mask | df[column].isin([value])
                        except Exception as FilterError:
                            QMessageBox.warning(self, "Warning", f"Error with filter {column} {condition} {value}: {str(FilterError)}")
                            continue
                    
                    # Apply the OR mask
                    self.data_handler.df = df[mask]
                
                after = len(self.data_handler.df)
                removed = before - after
                
                self.refresh_data_view()
                filter_desc = f" {logic} ".join([f"{f['column']} {f['condition']} '{f['value']}'" for f in filters])
                self.status_bar.log(
                    f"Advanced filters ({logic}): {filter_desc} | Rows: {before:,} → {after:,} (-{removed:,})",
                    "SUCCESS"
                )
            except Exception as FilterError:
                QMessageBox.critical(self, "Error", str( FilterError))
                self.status_bar.log(f"Filter failed: {str( FilterError)}", "ERROR")
    
    def open_aggregation_dialog(self):
        """Open aggregation dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "Warning", "No data loaded")
            return
        
        columns = list(self.data_handler.df.columns)
        dialog = AggregationDialog(columns, self)
        if dialog.exec():
            config = dialog.get_aggregation_config()
            try:
                self.data_handler.reset_data()

                group_cols = config["group_by"]
                agg_cols = config["agg_columns"]
                agg_func = config["agg_func"]
                agg_name = config.get("aggregation_name", "")

                self.data_handler.aggregate_data(group_cols, agg_cols, agg_func)
                result_df = self.data_handler.df.copy()

                #ask the user if they want ot save this agg
                if agg_name:
                    try:
                        description = f"{agg_func}({', '.join(agg_cols)}) grouped by {', '.join(group_cols)}"
                        self.aggregation_manager.save_aggregation(
                            name=agg_name,
                            description=description,
                            group_by=group_cols,
                            agg_columns=agg_cols,
                            agg_func=agg_func,
                            result_df=result_df
                        )
                        self.refresh_saved_agg_list()
                        self.status_bar.log(f"Saved aggregation: {agg_name}", "SUCCESS")
                    except ValueError as OpenAggregationDialogError:
                        QMessageBox.warning(self, "Error", str(OpenAggregationDialogError))
                
                self.refresh_data_view()

                group_by_str = ", ".join(group_cols)
                agg_cols_str = ", ".join(agg_cols)

                self.status_bar.log_action(
                    f"Aggregated data by [{group_by_str}]: {agg_func}([{agg_cols_str}])",
                    details={
                        "group_by_columns": group_cols,
                        "agg_columns": agg_cols,
                        "agg_function": agg_func,
                        "result_rows": len(self.data_handler.df),
                        "operation": "aggregate",
                        "saved": bool(agg_name)
                    },
                    level="SUCCESS"
                )
            except Exception as AggregationDialogError:
                QMessageBox.critical(self, "Error", str(AggregationDialogError))
                self.status_bar.log(f"Aggregation failed: {str(AggregationDialogError)}", "ERROR")
    
    def refresh_saved_agg_list(self):
        """Refreshes the list of saved aggs"""
        if not hasattr(self, "saved_agg_list"):
            return
        
        try:
            self.saved_agg_list.clear()

            agg_names = self.aggregation_manager.list_aggregations()
            if not agg_names:
                placeholder = QListWidgetItem("(No saved aggregations)")
                placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
                self.saved_agg_list.addItem(placeholder)
                return
            
            for name in agg_names:
                agg = self.aggregation_manager.get_aggregation(name)
                if agg:
                    item_text = f"{name} ({agg.row_count} rows)"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, name)
                    self.saved_agg_list.addItem(item)
        except Exception as RefreshAggregationListError:
            print(f"Warning: Could not refresh aggregation list: {str(RefreshAggregationListError)}")
    
    def on_saved_agg_selected(self, item):
        """Handle selection o fs saved aggs"""
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            self.view_agg_btn.setEnabled(False)
            self.delete_agg_btn.setEnabled(False)
            return
        
        self.view_agg_btn.setEnabled(True)
        self.delete_agg_btn.setEnabled(True)
    
    def view_saved_aggregations(self):
        """View the current selected agg in the table"""
        if not hasattr(self, "saved_agg_list"):
            return
        
        item = self.saved_agg_list.currentItem()
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            return
        
        agg_name = item.data(Qt.ItemDataRole.UserRole)

        try:
            agg_df = self.aggregation_manager.get_aggregation_df(agg_name)
            if agg_df is None:
                QMessageBox.warning(self, "Error", "Aggregation data not found")
                return
            
            #storing state
            if not hasattr(self.data_handler, "pre_agg_view_df") or self.data_handler.pre_agg_view_df is None:
                self.data_handler.pre_agg_view_df = self.data_handler.df.copy()
            
            self.data_handler.df = agg_df.copy()
            self.data_handler.viewing_aggregation_name = agg_name
            self.data_handler.inserted_subset_name = None
            self.refresh_data_view()

            agg = self.aggregation_manager.get_aggregation(agg_name)
            self.status_bar.log_action(
                f"Viewing saved aggregation: {agg_name}",
                details={
                    "aggregation_name": agg_name,
                    "rows": len(agg_df),
                    "columns": len(agg_df.columns),
                    "operation": "view_saved_aggregation"
                },
                level="INFO"
            )
            QMessageBox.information(
                self,
                "Aggregation Loaded",
                f"Now viewing aggregation: {agg_name}\n\n"
                f"Rows: {len(agg_df):,}\n"
                f"Columns: {len(agg_df.columns)}\n\n"
                f"Click 'Reset to Original' to return to your full dataset."
            )
        except Exception as ViewAggregationError:
            QMessageBox.critical(self, "Error", f"Failed to view aggregation:\n{str(ViewAggregationError)}")
            traceback.print_exc() 
    
    def delete_saved_aggregation(self):
        """Delete a saved aggregation """
        if not hasattr(self, "saved_agg_list"):
            return
        
        item = self.saved_agg_list.currentItem()
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            return
        
        agg_name = item.data(Qt.ItemDataRole.UserRole)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete the saved aggregation '{agg_name}'?\n\n"
            "This will not affect your current data view.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.aggregation_manager.delete_aggregation(agg_name):
                self.refresh_saved_agg_list()
                self.view_agg_btn.setEnabled(False)
                self.delete_agg_btn.setEnabled(False)
                self.status_bar.log(f"Deleted aggregation: {agg_name}", "SUCCESS")

    
    def refresh_google_sheets_data(self):
        """Refresh data from the last imported Google Sheet document"""
        try:
            print(f"DEBUG: Attempting to refresh Google Sheets")
            print(f"DEBUG: Sheet ID: {self.data_handler.last_gsheet_id}")
            print(f"DEBUG: Sheet Name: {self.data_handler.last_gsheet_name}")
            print(f"DEBUG: Delimiter: '{self.data_handler.last_gsheet_delimiter}'")
            print(f"DEBUG: Decimal: '{self.data_handler.last_gsheet_decimal}'")
            print(f"DEBUG: Thousands: '{self.data_handler.last_gsheet_thousands}'")
            print(f"DEBUG: Has import: {self.data_handler.has_google_sheets_import()}")

            if not self.data_handler.has_google_sheets_import():
                QMessageBox.warning(self, "No Import History", "No Google Sheets import data found")
                return
        
            progress_dialog = ProgressDialog(
                title="Refreshing Google Sheets data",
                message=f"Reconnecting to {self.data_handler.last_gsheet_id}"
            )
            progress_dialog.show()
            progress_dialog.update_progress(10, "Establishing connection")
            QApplication.processEvents()

            rows_before = len(self.data_handler.df) if self.data_handler.df is not None else 0
            print(f"DEBUG: Rows before refresh: {rows_before}")

            progress_dialog.update_progress(30, f"Downloading data from: '{self.data_handler.last_gsheet_id}'")
            QApplication.processEvents()

            print(f"DEBUG: Calling refresh_google_sheets()...")
            self.data_handler.refresh_google_sheets()
            print(f"DEBUG: refresh_google_sheets() completed successfully")

            progress_dialog.update_progress(70, "Processing data")
            QApplication.processEvents()

            print(f"DEBUG: Refreshing data view...")
            self.refresh_data_view()
            print(f"DEBUG: Data view refreshed")

            progress_dialog.update_progress(100, "Complete")
            QTimer.singleShot(300, progress_dialog.accept)

            rows_after = len(self.data_handler.df)
            rows_diff = rows_after - rows_before
            diff_text = f"+{rows_diff}" if rows_diff > 0  else str(rows_diff)

            print(f"DEBUG: Rows after refresh: {rows_after}")
            print(f"DEBUG: Row difference: {diff_text}")

            #loogg
            self.status_bar.log_action(
                f"Refreshed Google sheets data: {self.data_handler.last_gsheet_id}",
                details={
                    "sheet_name": self.data_handler.last_gsheet_name,
                    "sheed_id": self.data_handler.last_gsheet_id,
                    "rows_before": rows_before,
                    "rows_after": rows_after,
                    "rows_changed": rows_diff,
                    "operation": "refresh_google_sheets"
                },
                level="SUCCESS"
            )
            QMessageBox.information(
                    self,
                    "Refresh Complete",
                    f"Google Sheets data refreshed successfully\n\n"
                    f"Sheet: {self.data_handler.last_gsheet_name}\n"
                    f"Rows: {rows_after:,} ({diff_text})\n"
                    f"Columns: {len(self.data_handler.df.columns)}"
            )
        except Exception as RefreshGoogleSheetsDataError:
            print(f"DEBUG: Exception occurred during refresh: {type(RefreshGoogleSheetsDataError).__name__}")
            print(f"DEBUG: Exception message: {str(RefreshGoogleSheetsDataError)}")
            print(f"DEBUG: Traceback:\n{traceback.format_exc()}")
            if "progress_dialog" in locals() and progress_dialog:
                progress_dialog.accept()
            self.status_bar.log(f"Failed to refresh Google Sheet Data: {str(RefreshGoogleSheetsDataError)}", "ERROR")
            QMessageBox.critical(
                self,
                "Refresh Failed",
                f"Failed to refresh Google Sheets data:\n\n{str(RefreshGoogleSheetsDataError)}\n\n"
                "Please check:\n"
                "• Internet connection\n"
                "• Sheet is still shared publicly\n"
                "• Sheet name has not changed"
            )
    
    def open_melt_dialog(self):
        """Opens the melt data dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return
        
        columns = list(self.data_handler.df.columns)
        dialog = MeltDialog(columns, self)

        if dialog.exec():
            config = dialog.get_config()
            try:
                reply = reply = QMessageBox.question(
                    self,
                    "Confirm Melt",
                    "Melting will restructure your entire dataset.\n\n"
                    "Are you sure you want to proceed?\n"
                    "(You can Undo this operation later)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    before_shape = self.data_handler.df.shape

                    self.data_handler.melt_data(
                        id_vars=config['id_vars'],
                        value_vars=config['value_vars'],
                        var_name=config['var_name'],
                        value_name=config['value_name']
                    )

                    after_shape = self.data_handler.df.shape
                    self.refresh_data_view()

                    self.status_bar.log_action(
                        f"Melted data: {before_shape} -> {after_shape}",
                        details={
                            "id_vars": config['id_vars'],
                            "value_vars": config['value_vars'],
                            "shape_before": before_shape,
                            "shape_after": after_shape,
                            "operation": "melt"
                        },
                        level="SUCCESS"
                    )
            
            except Exception as MeltDataError:
                QMessageBox.critical(self, "Error", f"Failed to melt data:\n{str(MeltDataError)}")
                self.status_bar.log(f"Melt failed: {str(MeltDataError)}", "ERROR")

    def clear(self):
        """Clear the data tab"""
        self.data_table.setModel(None)
        self.stats_text.clear()

        if hasattr(self, "data_source_container"):
            self.data_source_container.setVisible(False)

    @pyqtSlot(str)
    def show_help_dialog(self, topic_id: str):
        try:
            title, description, full_image_path, link  = self.help_manager.get_help_topic(topic_id)

            if title:
                dialog = HelpDialog(title, description, full_image_path, link, self)
                dialog.exec()
            else:
                QMessageBox.warning(self, "Help not found", f"No help topic could be found for '{topic_id}'")
        except Exception as ShowHelpDialogError:
            self.status_bar.log(f"Error displaying help dialog: {str(ShowHelpDialogError)}", "ERROR")
            QMessageBox.critical(self, "Help Error", "Could not load help content. See log for details")

    def on_history_clicked(self, item):
        """Handles the click of history entry"""
        if not item:
            return
        
        target_index = item.data(Qt.ItemDataRole.UserRole)
        try:
            self.data_handler.jump_to_history_index(target_index)
            self.refresh_data_view()

            for i in range(self.history_list.count()):
                list_item = self.history_list.item(i)
                if list_item.data(Qt.ItemDataRole.UserRole) == target_index:
                    self.history_list.setCurrentItem(list_item)
                    break
        
        except Exception as HistoryError:
            self.status_bar.log(F"Failed to go to state: {str(HistoryError)}", "ERROR")
    
    def _format_operation_text(self, operation: dict) -> str:
        """Formatter for operation dict back to better text handling"""
        operation_type = operation.get("type", "Unknown")

        match operation_type:
            case "filter":
                return f"Filter: {operation.get('column')} {operation.get('condition')} '{operation.get('value')}'"
            case "drop_column":
                return f"Drop Column: {operation.get("column")}"
            case "rename_column":
                return f"Rename: {operation.get("old_name")} -> {operation.get("new_name")}"
            case "change_data_type":
                return f"Data type change: {operation.get("column")} -> {operation.get("new_type")}"
            case "fill_missing":
                return f"Fill missing Values: {operation.get("column")} ({operation.get("method")})"
            case "drop_missing":
                return f"Drop missing Values"
            case "drop_duplicates":
                return f"Remove Duplicate Values"
            case "aggregate":
                return f"Aggregation: {operation.get("agg_func")} on {len(operation.get("agg_columns", []))} columns"
            case "melt":
                return f"Melt/Pivot Data"
            case _:
                return f"{operation_type.replace("_", " ").title()}"