from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QAbstractItemView, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from ui.controllers.data_tab_controller import DataTabController

from core.resource_loader import get_resource_path
from ui.widgets import (
    DataPlotStudioButton, DataPlotStudioTabWidget, DataPlotStudioGroupBox,
    DataPlotStudioComboBox, DataPlotStudioLineEdit, DataPlotStudioListWidget,
    HelpIcon
)
from resources.version import INFO_STYLESHEET
from ui.icons import IconBuilder, IconType

class DataOperationsPanel(QWidget):
    """
    Operations panel for the data tab
    """
    def __init__(self, parent=None, controller: Optional["DataTabController"] = None):
        super().__init__(parent)
        self.controller = controller
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        reset_button = DataPlotStudioButton(
            "Reset to Original",
            parent=self,
            base_color_hex="#ffcccc",
            hover_color_hex="#faafaf",
            typewriter_effect=True,
        )
        reset_button.setIcon(IconBuilder.build(IconType.REDO))
        if self.controller:
            reset_button.clicked.connect(self.controller.reset_data)
        layout.addWidget(reset_button)
        
        self.ops_tabs = DataPlotStudioTabWidget()
        
        self.create_cleaning_tab()
        self.create_filtering_tab()
        self.create_columns_tab()
        self.create_transform_tab()
        self.create_datetime_tab()
        self.create_subsets_tab()
        self.create_history_tab()
        
        layout.addWidget(self.ops_tabs)
    
    def create_cleaning_tab(self):
        cleaning_tab = QWidget()
        cleaning_layout = QVBoxLayout(cleaning_tab)

        clean_info = QLabel("This tab includes operations to clean your dataset.")
        clean_info.setWordWrap(True)
        clean_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        cleaning_layout.addWidget(clean_info)

        # Remove Duplicates
        remove_dups_layout = QHBoxLayout()
        clean_button = DataPlotStudioButton("Remove Duplicate Rows", parent=self)
        clean_button.setToolTip("Use this to remove any instances of duplicate row entries in your dataset")
        clean_button.setIcon(IconBuilder.build(IconType.REMOVE_DUPLICATES))
        if self.controller:
            clean_button.clicked.connect(self.controller.remove_duplicates)
        
        self.remove_duplicates_help = HelpIcon("remove_duplicates")
        if self.controller:
            self.remove_duplicates_help.clicked.connect(self.controller.show_help_dialog)
        
        remove_dups_layout.addWidget(clean_button, 1)
        remove_dups_layout.addWidget(self.remove_duplicates_help)
        cleaning_layout.addLayout(remove_dups_layout)

        # Drop Missing
        drop_missing_layout = QHBoxLayout()
        drop_missing_button = DataPlotStudioButton("Drop Missing Values", parent=self)
        drop_missing_button.setToolTip("Use this to remove rows in your dataset with incomplete entries")
        drop_missing_button.setIcon(IconBuilder.build(IconType.DROP_MISSING_VALUES))
        if self.controller:
            drop_missing_button.clicked.connect(self.controller.drop_missing)
        
        self.drop_missing_help = HelpIcon("drop_missing")
        if self.controller:
            self.drop_missing_help.clicked.connect(self.controller.show_help_dialog)
        
        drop_missing_layout.addWidget(drop_missing_button)
        drop_missing_layout.addWidget(self.drop_missing_help)
        cleaning_layout.addLayout(drop_missing_layout)

        # Fill Missing
        fill_missing_layout = QHBoxLayout()
        fill_missing_button = DataPlotStudioButton("Fill Missing Values", parent=self)
        fill_missing_button.setToolTip("Use this to fill in 'NaN' values in your dataset to something specific")
        fill_missing_button.setIcon(IconBuilder.build(IconType.FILL_MISSING_VALUES))
        if self.controller:
            fill_missing_button.clicked.connect(self.controller.fill_missing)
        
        self.fill_missing_help = HelpIcon("fill_missing")
        if self.controller:
            self.fill_missing_help.clicked.connect(self.controller.show_help_dialog)

        fill_missing_layout.addWidget(fill_missing_button)
        fill_missing_layout.addWidget(self.fill_missing_help)
        cleaning_layout.addLayout(fill_missing_layout)

        # Outlier Detection
        cleaning_layout.addSpacing(10)
        outlier_group = DataPlotStudioGroupBox("Outlier Detection Tools")
        outlier_layout = QVBoxLayout()

        # Z-Score
        zscore_layout = QHBoxLayout()
        zscore_button = DataPlotStudioButton("Z-Score", parent=self)
        zscore_button.setToolTip("Detect outliers using Z-Score (standard Deviations from mean)")
        if self.controller:
            zscore_button.clicked.connect(lambda: self.controller.open_outlier_dialog("z_score"))
        self.zscore_help = HelpIcon("zscore")
        if self.controller:
            self.zscore_help.clicked.connect(self.controller.show_help_dialog)
        zscore_layout.addWidget(zscore_button)
        zscore_layout.addWidget(self.zscore_help)
        outlier_layout.addLayout(zscore_layout)

        # IQR
        iqr_layout = QHBoxLayout()
        iqr_button = DataPlotStudioButton("Interquartile Range (IQR)", parent=self)
        iqr_button.setToolTip("Detect outliers using the Interquartile Range method")
        if self.controller:
            iqr_button.clicked.connect(lambda: self.controller.open_outlier_dialog("iqr"))
        self.iqr_help = HelpIcon("iqr")
        if self.controller:
            self.iqr_help.clicked.connect(self.controller.show_help_dialog)
        iqr_layout.addWidget(iqr_button)
        iqr_layout.addWidget(self.iqr_help)
        outlier_layout.addLayout(iqr_layout)

        # Isolation Forest
        isolation_layout = QHBoxLayout()
        isolation_button = DataPlotStudioButton("Isolation Forest", parent=self)
        isolation_button.setToolTip("Detect outliers using Machine Learning (Isolation Forest)")
        if self.controller:
            isolation_button.clicked.connect(lambda: self.controller.open_outlier_dialog("isolation_forest"))
        self.isolation_help = HelpIcon("isolation_forest")
        if self.controller:
            self.isolation_help.clicked.connect(self.controller.show_help_dialog)
        isolation_layout.addWidget(isolation_button)
        isolation_layout.addWidget(self.isolation_help)
        outlier_layout.addLayout(isolation_layout)

        outlier_group.setLayout(outlier_layout)
        cleaning_layout.addWidget(outlier_group)

        cleaning_layout.addStretch()
        data_clean_icon = IconBuilder.build(IconType.DATA_CLEANING)
        self.ops_tabs.addTab(cleaning_tab, data_clean_icon, "Data Cleaning")

    def create_filtering_tab(self):
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

        self.filter_column = DataPlotStudioComboBox()
        filter_layout.addWidget(self.filter_column)

        filter_layout.addWidget(QLabel("Condition:"))
        filter_condition_info = QLabel("Select which conditional to apply to column. N.B. Uses Python Syntax")
        filter_condition_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        filter_condition_info.setWordWrap(True)
        filter_layout.addWidget(filter_condition_info)

        self.filter_condition = DataPlotStudioComboBox()
        self.filter_condition.addItems(["==", "!=", ">", "<", ">=", "<=", "contains"])
        filter_layout.addWidget(self.filter_condition)

        filter_layout.addWidget(QLabel("Value:"))
        filter_value_info = QLabel("Enter the value you want the column to be evaluate to.\nNote: reference your data. This is case-sensitive")
        filter_value_info.setWordWrap(True)
        filter_value_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        filter_layout.addWidget(filter_value_info)

        self.filter_value = DataPlotStudioLineEdit()
        filter_layout.addWidget(self.filter_value)

        # Apply Filter
        apply_filter_layout = QHBoxLayout()
        apply_filter_button = DataPlotStudioButton("Apply Filter", parent=self)
        apply_filter_button.setIcon(IconBuilder.build(IconType.FILTER))
        if self.controller:
            apply_filter_button.clicked.connect(self.controller.apply_filter)
        
        self.apply_filter_help = HelpIcon("apply_filter")
        if self.controller:
            self.apply_filter_help.clicked.connect(self.controller.show_help_dialog)
        
        apply_filter_layout.addWidget(apply_filter_button)
        apply_filter_layout.addWidget(self.apply_filter_help)
        filter_layout.addLayout(apply_filter_layout)

        # Clear Filter
        clear_filter_layout = QHBoxLayout()
        clear_filter_button = DataPlotStudioButton("Clear Filters", parent=self)
        clear_filter_button.setToolTip("Reset the dataset to its original state and remove the filters")
        clear_filter_button.setIcon(IconBuilder.build(IconType.CLEAR_FILTER))
        if self.controller:
            clear_filter_button.clicked.connect(self.controller.clear_filters)
        
        placeholder_help_icon_clear_filter = QWidget()
        placeholder_help_icon_clear_filter.setFixedSize(self.apply_filter_help.size())
        placeholder_help_icon_clear_filter.setVisible(True)
        clear_filter_layout.addWidget(clear_filter_button)
        clear_filter_layout.addWidget(placeholder_help_icon_clear_filter)
        filter_layout.addLayout(clear_filter_layout)

        filter_layout.addSpacing(10)

        # Advanced Filter
        advanced_filter_layout = QHBoxLayout()
        adv_filter_button = DataPlotStudioButton("Advanced Filter", parent=self)
        adv_filter_button.setIcon(IconBuilder.build(IconType.ADVANCED_FILTER))
        if self.controller:
            adv_filter_button.clicked.connect(self.controller.open_advanced_filter)
        
        # Reusing help icon variable slightly risky if distinct help needed, but following original pattern
        self.adv_filter_help = HelpIcon("apply_filter") 
        if self.controller:
            self.adv_filter_help.clicked.connect(self.controller.show_help_dialog)
        
        advanced_filter_layout.addWidget(adv_filter_button)
        advanced_filter_layout.addWidget(self.adv_filter_help)
        filter_layout.addLayout(advanced_filter_layout)

        filter_layout.addStretch()
        filter_icon = IconBuilder.build(IconType.FILTER)
        self.ops_tabs.addTab(filter_tab, filter_icon, "Filter Data")

    def create_columns_tab(self):
        column_tab = QWidget()
        column_layout = QVBoxLayout(column_tab)

        column_info = QLabel("This tab allows you to change certain elements to the columns of your data")
        column_info.setWordWrap(True)
        column_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        column_layout.addWidget(column_info)

        column_column_info = QLabel("Select the column you wish to work with")
        column_column_info.setWordWrap(True)
        column_column_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        column_layout.addWidget(column_column_info)

        self.column_list = DataPlotStudioListWidget()
        self.column_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.column_list.setMaximumHeight(200)
        column_layout.addWidget(self.column_list)

        # Drop Column
        drop_column_layout = QHBoxLayout()
        drop_column_button = DataPlotStudioButton("Drop Column", parent=self)
        drop_column_button.setToolTip("Use this to remove the selected column from the dataset")
        drop_column_button.setIcon(IconBuilder.build(IconType.DROP_COLUMN))
        if self.controller:
            drop_column_button.clicked.connect(self.controller.drop_column)
        
        self.drop_column_help = HelpIcon("drop_column")
        if self.controller:
            self.drop_column_help.clicked.connect(self.controller.show_help_dialog)
        
        drop_column_layout.addWidget(drop_column_button)
        drop_column_layout.addWidget(self.drop_column_help)
        column_layout.addLayout(drop_column_layout)

        # Rename Column
        rename_layout = QHBoxLayout()
        rename_button = DataPlotStudioButton("Rename Column", parent=self)
        rename_button.setToolTip("Use this to rename the selected column")
        rename_button.setIcon(IconBuilder.build(IconType.RENAME_COLUMN))
        if self.controller:
            rename_button.clicked.connect(self.controller.rename_column)
        
        self.rename_column_help = HelpIcon("rename_column")
        if self.controller:
            self.rename_column_help.clicked.connect(self.controller.show_help_dialog)
        
        rename_layout.addWidget(rename_button)
        rename_layout.addWidget(self.rename_column_help)
        column_layout.addLayout(rename_layout)
        
        # Duplicate Column
        duplicate_layout = QHBoxLayout()
        duplicate_button = DataPlotStudioButton("Duplicate Column", parent=self)
        duplicate_button.setToolTip("Create an exact copy of the selected column")
        duplicate_button.setIcon(IconBuilder.build(IconType.DUPLICATE_COLUMN))
        if self.controller:
            duplicate_button.clicked.connect(self.controller.duplicate_column)
        self.duplicate_column_help = HelpIcon("duplicate_column")
        if self.controller:
            self.duplicate_column_help.clicked.connect(self.controller.show_help_dialog)
            
        duplicate_layout.addWidget(duplicate_button)
        duplicate_layout.addWidget(self.duplicate_column_help)
        column_layout.addLayout(duplicate_layout)

        # Compute Column
        computed_layout = QHBoxLayout()
        computed_button = DataPlotStudioButton("Compute Column", parent=self)
        computed_button.setToolTip("Create a new column based on a formula (e.g., Total = Price * Quantity)")
        computed_button.setIcon(IconBuilder.build(IconType.CALCULATOR))
        if self.controller:
            computed_button.clicked.connect(self.controller.open_computed_column_dialog)
        
        self.compute_column_help = HelpIcon("compute_column")
        if self.controller:
            self.compute_column_help.clicked.connect(self.controller.show_help_dialog)
        
        computed_layout.addWidget(computed_button)
        computed_layout.addWidget(self.compute_column_help)
        column_layout.addLayout(computed_layout)

        column_layout.addSpacing(10)

        # Data Type Conversion
        type_group = DataPlotStudioGroupBox("Change Data Type")
        type_layout = QVBoxLayout()

        data_type_info = QLabel("This operation allows you to change the datatype of your selected column.")
        data_type_info.setWordWrap(True)
        data_type_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        type_layout.addWidget(data_type_info)

        type_layout.addWidget(QLabel("Change selected columns DataType to:"))

        self.type_combo = DataPlotStudioComboBox()
        self.type_combo.addItems([
            "string (object)", "integer (numeric)", "float (numeric)",
            "category (optimzied string)", "datetime (dates/times)",
        ])
        self.type_combo.setToolTip("string: For text data\ninteger: For whole numbers\nfloat: For decimal values\ncategory: For text with few unique values\ndatetime: For dates and time")
        type_layout.addWidget(self.type_combo)

        datatype_layout = QHBoxLayout()
        type_button = DataPlotStudioButton("Apply DataType Change", parent=self)
        type_button.setIcon(IconBuilder.build(IconType.CHANGE_DATATYPE))
        if self.controller:
            type_button.clicked.connect(self.controller.change_column_type)
        
        self.change_datatype_help = HelpIcon("change_datatype")
        if self.controller:
            self.change_datatype_help.clicked.connect(self.controller.show_help_dialog)
        
        datatype_layout.addWidget(type_button)
        datatype_layout.addWidget(self.change_datatype_help)
        type_layout.addLayout(datatype_layout)
        type_group.setLayout(type_layout)
        column_layout.addWidget(type_group)

        column_layout.addSpacing(10)

        # Text Manipulation
        text_group = DataPlotStudioGroupBox("Text Manipulation")
        text_layout = QVBoxLayout()

        text_info = QLabel("Standardize text data in the selected column.\nRemove whitespace, fix casing etc.")
        text_info.setWordWrap(True)
        text_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        text_layout.addWidget(text_info)

        self.text_operation_combo = DataPlotStudioComboBox()
        self.text_operation_combo.addItems([
            "Trim Whitespace", "Trim leading whitespace", "Trim trailing whitepsace",
            "Convert to lowercase", "Convert to UPPERCASE", "Convert to Title Case",
            "Capitalize First Letter",
        ])
        text_layout.addWidget(self.text_operation_combo)

        text_apply_layout = QHBoxLayout()
        text_apply_button = DataPlotStudioButton("Apply Text Operation", parent=self)
        text_apply_button.setIcon(IconBuilder.build(IconType.TEXT_OPERATION))
        if self.controller:
            text_apply_button.clicked.connect(self.controller.apply_text_manipulation)

        self.text_manipulation_help = HelpIcon("text_manipulation")
        if self.controller:
            self.text_manipulation_help.clicked.connect(self.controller.show_help_dialog)

        text_apply_layout.addWidget(text_apply_button)
        text_apply_layout.addWidget(self.text_manipulation_help)
        text_layout.addLayout(text_apply_layout)
        text_group.setLayout(text_layout)
        column_layout.addWidget(text_group)
        
        column_layout.addSpacing(10)
        
        # Binning
        binning_group = DataPlotStudioGroupBox("Binning / Discretization")
        binning_layout = QVBoxLayout()
        
        binning_info = QLabel("Convert continuous numeric variables into categorical buckets (e.g., Age -> Age Groups).")
        binning_info.setWordWrap(True)
        binning_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        binning_layout.addWidget(binning_info)
        
        binning_btn_layout = QHBoxLayout()
        binning_btn = DataPlotStudioButton("Bin / Discretize Column", parent=self)
        binning_btn.setIcon(IconBuilder.build(IconType.DATA_TRANSFORM))
        binning_btn.setToolTip("Open tool to create bins from numeric data")
        if self.controller:
            binning_btn.clicked.connect(self.controller.open_binning_dialog)
        
        self.binning_help = HelpIcon("binning_discretization") 
        if self.controller:
            self.binning_help.clicked.connect(self.controller.show_help_dialog)
        
        binning_btn_layout.addWidget(binning_btn)
        binning_btn_layout.addWidget(self.binning_help)
        binning_layout.addLayout(binning_btn_layout)
        
        binning_group.setLayout(binning_layout)
        column_layout.addWidget(binning_group)
        
        column_layout.addSpacing(10)
        
        norm_group = DataPlotStudioGroupBox("Data Normalization and Scaling")
        norm_layout = QVBoxLayout()
        
        norm_info = QLabel("Scale numeric data to a standard range or distribution")
        norm_info.setWordWrap(True)
        norm_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        norm_layout.addWidget(norm_info)
        
        self.norm_method_combo = DataPlotStudioComboBox()
        self.norm_method_combo.addItems(["Min-Max Scaling", "Standard Scaling", "Median Scaling"])
        norm_layout.addWidget(self.norm_method_combo)
        
        norm_button_layout = QHBoxLayout()
        norm_button = DataPlotStudioButton("Apply Scaling", parent=self)
        norm_button.setIcon(IconBuilder.build(IconType.DATA_TRANSFORM))
        norm_button.setToolTip("Apply the selected scaling technique to selected columns")
        if self.controller:
            norm_button.clicked.connect(self.controller.apply_normalization)
        
        self.norm_help = HelpIcon("data_normalization")
        if self.controller:
            self.norm_help.clicked.connect(self.controller.show_help_dialog)
            
        norm_button_layout.addWidget(norm_button)
        norm_button_layout.addWidget(self.norm_help)
        norm_layout.addLayout(norm_button_layout)
        
        norm_group.setLayout(norm_layout)
        column_layout.addWidget(norm_group)

        column_layout.addStretch()
        column_icon = IconBuilder.build(IconType.EDIT_COLUMNS)
        self.ops_tabs.addTab(column_tab, column_icon, "Columns")

    def create_transform_tab(self):
        transform_tab = QWidget()
        transform_layout = QVBoxLayout(transform_tab)

        transform_info = QLabel("This tab allows you to alter your input data by grouping and aggregation.")
        transform_info.setWordWrap(True)
        transform_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        transform_layout.addWidget(transform_info)

        # Aggregate
        agg_layout = QHBoxLayout()
        agg_button = DataPlotStudioButton("Aggregate Data", parent=self)
        agg_button.setIcon(QIcon(get_resource_path("icons/data_operations/aggregate_data.png")))
        if self.controller:
            agg_button.clicked.connect(self.controller.open_aggregation_dialog)
        self.agg_help = HelpIcon("aggregate_data")
        if self.controller:
            self.agg_help.clicked.connect(self.controller.show_help_dialog)
        agg_layout.addWidget(agg_button)
        agg_layout.addWidget(self.agg_help)
        transform_layout.addLayout(agg_layout)

        # Melt
        melt_layout = QHBoxLayout()
        melt_button = DataPlotStudioButton("Melt/Unpivot Data", parent=self)
        melt_button.setIcon(QIcon(get_resource_path("icons/data_operations/melt_data.svg")))
        if self.controller:
            melt_button.clicked.connect(self.controller.open_melt_dialog)
        self.melt_help = HelpIcon("melt_data")
        if self.controller:
            self.melt_help.clicked.connect(self.controller.show_help_dialog)
        melt_layout.addWidget(melt_button)
        melt_layout.addWidget(self.melt_help)
        transform_layout.addLayout(melt_layout)
        
        # Pivot
        pivot_layout = QHBoxLayout()
        pivot_button = DataPlotStudioButton("Pivot Table", parent=self)
        pivot_button.setIcon(IconBuilder.build(IconType.DATA_TRANSFORM))
        pivot_button.setToolTip("Reshape data using index, columns and values")
        if self.controller:
            pivot_button.clicked.connect(self.controller.open_pivot_dialog)
        self.pivot_help = HelpIcon("pivot_data")
        if self.controller:
            self.pivot_help.clicked.connect(self.controller.show_help_dialog)
        pivot_layout.addWidget(pivot_button)
        pivot_layout.addWidget(self.pivot_help)
        transform_layout.addLayout(pivot_layout)
        
        # Merge
        merge_layout = QHBoxLayout()
        merge_button = DataPlotStudioButton("Merge / Join Datasets", parent=self)
        merge_button.setIcon(IconBuilder.build(IconType.IMPORT_FILE))
        merge_button.setToolTip("Join the current dataset with another file")
        if self.controller:
            merge_button.clicked.connect(self.controller.open_merge_dialog)
        self.merge_help = HelpIcon("merge_data")
        if self.controller:
            self.merge_help.clicked.connect(self.controller.show_help_dialog)
        merge_layout.addWidget(merge_button)
        merge_layout.addWidget(self.merge_help)
        transform_layout.addLayout(merge_layout)        

        # Sorting
        sorting_group = DataPlotStudioGroupBox("Sort Data")
        sorting_layout = QVBoxLayout()

        sorting_info = QLabel("Permanently sort your dataset by a column.")
        sorting_info.setWordWrap(True)
        sorting_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        sorting_layout.addWidget(sorting_info)

        sort_controls = QHBoxLayout()
        self.sort_column_combo = DataPlotStudioComboBox()
        sort_controls.addWidget(self.sort_column_combo, 2)

        self.sort_order_combo = DataPlotStudioComboBox()
        self.sort_order_combo.addItems(["Ascending", "Descending"])
        sort_controls.addWidget(self.sort_order_combo, 1)
        sorting_layout.addLayout(sort_controls)

        sort_button_layout = QHBoxLayout()
        self.sort_button = DataPlotStudioButton("Sort Data", parent=self)
        self.sort_button.setIcon(IconBuilder.build(IconType.SORT))
        if self.controller:
            self.sort_button.clicked.connect(self.controller.apply_sort)

        sort_button_layout.addWidget(self.sort_button)
        sorting_layout.addLayout(sort_button_layout)
        sorting_group.setLayout(sorting_layout)
        transform_layout.addWidget(sorting_group)

        transform_layout.addSpacing(10)

        # Saved Aggregations
        saved_agg_group = DataPlotStudioGroupBox("Saved Aggregations")
        saved_agg_layout = QVBoxLayout()

        saved_agg_info = QLabel("Save aggregations to switch between different views of your dataset")
        saved_agg_info.setWordWrap(True)
        saved_agg_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        saved_agg_layout.addWidget(saved_agg_info)

        self.saved_agg_list = DataPlotStudioListWidget()
        self.saved_agg_list.setMaximumHeight(150)
        if self.controller:
            self.saved_agg_list.itemClicked.connect(self.controller.on_saved_agg_selected)
        saved_agg_layout.addWidget(self.saved_agg_list)

        saved_agg_buttons = QHBoxLayout()
        self.view_agg_btn = DataPlotStudioButton("View Aggregations", parent=self)
        self.view_agg_btn.setToolTip("View the selected aggregated data in the Data Table.")
        self.view_agg_btn.setIcon(IconBuilder.build(IconType.VIEW_ITEM))
        self.view_agg_btn.setEnabled(False)
        if self.controller:
            self.view_agg_btn.clicked.connect(self.controller.view_saved_aggregations)
        saved_agg_buttons.addWidget(self.view_agg_btn)

        self.refresh_agg_list_btn = DataPlotStudioButton("Refresh", parent=self)
        self.refresh_agg_list_btn.setIcon(IconBuilder.build(IconType.REFRESH_ITEM))
        if self.controller:
            self.refresh_agg_list_btn.clicked.connect(self.controller.refresh_saved_agg_list)
        saved_agg_buttons.addWidget(self.refresh_agg_list_btn)
        saved_agg_layout.addLayout(saved_agg_buttons)

        self.delete_agg_btn = DataPlotStudioButton("Delete Selected Aggregtation", parent=self)
        self.delete_agg_btn.setIcon(IconBuilder.build(IconType.DELETE_ITEM))
        self.delete_agg_btn.setEnabled(False)
        if self.controller:
            self.delete_agg_btn.clicked.connect(self.controller.delete_saved_aggregation)
        saved_agg_layout.addWidget(self.delete_agg_btn)

        saved_agg_group.setLayout(saved_agg_layout)
        transform_layout.addWidget(saved_agg_group)

        transform_layout.addStretch()
        transform_icon = IconBuilder.build(IconType.DATA_TRANSFORM)
        self.ops_tabs.addTab(transform_tab, transform_icon, "Transform")

    def create_datetime_tab(self):
        dt_tab = QWidget()
        dt_layout = QVBoxLayout(dt_tab)
        
        dt_info = QLabel("Extract date components from dates or calculate duration between datetime columns")
        dt_info.setWordWrap(True)
        dt_info.setStyleSheet(INFO_STYLESHEET)
        dt_layout.addWidget(dt_info)
        
        extract_group = DataPlotStudioGroupBox("Extract Date Components")
        extract_layout = QVBoxLayout()
        
        extract_layout.addWidget(QLabel("Source Date Columns:"))
        self.dt_source_combo = DataPlotStudioComboBox()
        extract_layout.addWidget(self.dt_source_combo)
        
        extract_layout.addWidget(QLabel("Date Component to Extract:"))
        self.dt_component_combo = DataPlotStudioComboBox()
        self.dt_component_combo.addItems(["Year", "Month", "Month Name", "Day", "Day of Week", "Quarter", "Hour"])
        extract_layout.addWidget(self.dt_component_combo)
        
        extract_button_layout = QHBoxLayout()
        extract_button = DataPlotStudioButton("Extract Component", parent=self)
        extract_button.setToolTip("Create a new column containing the selected time component")
        extract_button.setIcon(IconBuilder.build(IconType.DATA_TRANSFORM))
        if self.controller:
            extract_button.clicked.connect(self.controller.extract_date_component)
        
        self.extract_help = HelpIcon("extract_date")
        if self.controller:
            self.extract_help.clicked.connect(self.controller.show_help_dialog)
        
        extract_button_layout.addWidget(extract_button)
        extract_button_layout.addWidget(self.extract_help)
        extract_layout.addLayout(extract_button_layout)
        
        extract_group.setLayout(extract_layout)
        dt_layout.addWidget(extract_group)
        
        dt_layout.addSpacing(10)
        
        duration_group = DataPlotStudioGroupBox("Calculate Duration Difference")
        duration_layout = QVBoxLayout()
        
        duration_layout.addWidget(QLabel("Start Date Columns:"))
        self.dt_start_combo = DataPlotStudioComboBox()
        duration_layout.addWidget(self.dt_start_combo)
        
        duration_layout.addWidget(QLabel("End Date Column:"))
        self.dt_end_combo = DataPlotStudioComboBox()
        duration_layout.addWidget(self.dt_end_combo)
        
        duration_layout.addWidget(QLabel("Result Unit:"))
        self.dt_unit_combo = DataPlotStudioComboBox()
        self.dt_unit_combo.addItems(["Days", "Weeks", "Hours", "Minutes", "Seconds"])
        duration_layout.addWidget(self.dt_unit_combo)

        duration_button_layout = QHBoxLayout()
        duration_button = DataPlotStudioButton("Calculate Duration", parent=self)
        duration_button.setToolTip("Create a new column with the time difference between two datetime columns")
        duration_button.setIcon(IconBuilder.build(IconType.CALCULATOR))
        if self.controller:
            duration_button.clicked.connect(self.controller.calculate_date_difference)
        self.duration_help = HelpIcon("date_duration")
        if self.controller:
            self.duration_help.clicked.connect(self.controller.show_help_dialog)
        
        duration_button_layout.addWidget(duration_button)
        duration_button_layout.addWidget(self.duration_help)
        duration_layout.addLayout(duration_button_layout)
        
        duration_group.setLayout(duration_layout)
        dt_layout.addWidget(duration_group)
        
        dt_layout.addStretch()
        dt_icon = QIcon(get_resource_path("icons/data_operations/calendar-clock.svg"))
        self.ops_tabs.addTab(dt_tab, dt_icon, "Datetime Tools")
        
    def create_subsets_tab(self):
        subset_tab = QWidget()
        subset_layout = QVBoxLayout(subset_tab)

        subset_info = QLabel("This tab allows you to create and manage data subsets.")
        subset_info.setWordWrap(True)
        subset_info.setStyleSheet(INFO_STYLESHEET)
        subset_layout.addWidget(subset_info)
        subset_layout.addSpacing(10)

        # Manage Subsets
        manage_subsets_layout = QHBoxLayout()
        manage_subsets_btn = DataPlotStudioButton("Manage Subsets", parent=self)
        if self.controller:
            manage_subsets_btn.clicked.connect(self.controller.open_subset_manager)
        
        self.subset_help = HelpIcon("manage_subsets")
        if self.controller:
            self.subset_help.clicked.connect(self.controller.show_help_dialog)
        
        manage_subsets_layout.addWidget(manage_subsets_btn)
        manage_subsets_layout.addWidget(self.subset_help)
        subset_layout.addLayout(manage_subsets_layout)
        subset_layout.addSpacing(10)

        # Quick Subset Creation
        quick_subset_group = DataPlotStudioGroupBox("Quick Subset Creation")
        quick_subset_layout = QVBoxLayout()
        quick_subset_layout.addWidget(QLabel("Split data by column values:"))

        self.subset_column_combo = DataPlotStudioComboBox()
        quick_subset_layout.addWidget(self.subset_column_combo)

        quick_create_subset_layout = QHBoxLayout()
        quick_create_btn = DataPlotStudioButton("Auto-Create Subsets", parent=self)
        if self.controller:
            quick_create_btn.clicked.connect(self.controller.quick_create_subsets)
        
        self.quick_subset_help = HelpIcon("auto_create_subsets")
        if self.controller:
            self.quick_subset_help.clicked.connect(self.controller.show_help_dialog)
        
        quick_create_subset_layout.addWidget(quick_create_btn)
        quick_create_subset_layout.addWidget(self.quick_subset_help)
        quick_subset_layout.addLayout(quick_create_subset_layout)
        quick_subset_group.setLayout(quick_subset_layout)
        subset_layout.addWidget(quick_subset_group)
        subset_layout.addSpacing(10)

        # Active Subsets
        subset_list_group = DataPlotStudioGroupBox("Active Subsets")
        subset_list_layout = QVBoxLayout()

        self.active_subsets_list = DataPlotStudioListWidget()
        self.active_subsets_list.setMaximumHeight(150)
        if self.controller:
            self.active_subsets_list.itemDoubleClicked.connect(self.controller.view_subset_quick)
        subset_list_layout.addWidget(self.active_subsets_list)

        subset_list_btns = QHBoxLayout()
        view_subset_btn = DataPlotStudioButton("View", parent=self)
        view_subset_btn.setIcon(IconBuilder.build(IconType.VIEW_ITEM))
        if self.controller:
            view_subset_btn.clicked.connect(self.controller.view_subset_quick)
        subset_list_btns.addWidget(view_subset_btn)

        refresh_subsets_btn = DataPlotStudioButton("Refresh", parent=self)
        refresh_subsets_btn.setIcon(IconBuilder.build(IconType.REFRESH_ITEM))
        if self.controller:
            refresh_subsets_btn.clicked.connect(self.controller.refresh_active_subsets)
        subset_list_btns.addWidget(refresh_subsets_btn)
        subset_list_layout.addLayout(subset_list_btns)
        subset_list_group.setLayout(subset_list_layout)
        subset_layout.addWidget(subset_list_group)
        subset_layout.addStretch()

        # Subset Injection
        inject_group = DataPlotStudioGroupBox("View Subset as Active DataFrame")
        inject_layout = QVBoxLayout()

        inject_info = QLabel("Insert the selected subset into the active DataFrame to work directly with it.")
        inject_info.setWordWrap(True)
        inject_info.setStyleSheet("color: #ff6b35; font-style: italic; font-size: 9pt;")
        inject_layout.addWidget(inject_info)
        inject_layout.addSpacing(10)

        self.inject_subset_tbn = DataPlotStudioButton(
            "Insert Selected Subset",
            parent=self,
            base_color_hex="#3409db",
            hover_color_hex="#1b0085",
            text_color_hex="white",
            font_weight="bold",
            padding="8px",
        )
        if self.controller:
            self.inject_subset_tbn.clicked.connect(self.controller.inject_subset_to_dataframe)
        inject_layout.addWidget(self.inject_subset_tbn)

        self.injection_status_label = QLabel("Status: Working with original data")
        self.injection_status_label.setStyleSheet(
            "color: #27ae60; font-weight: bold; padding: 5px; background-color: #ecf0f1; border-radius: 3px;"
        )
        inject_layout.addWidget(self.injection_status_label)
        inject_layout.addSpacing(10)

        self.restore_original_btn = DataPlotStudioButton(
            "Revert to Original Data View",
            parent=self,
            base_color_hex="#e74c3c",
            hover_color_hex="#e91801",
            text_color_hex="white",
            padding="8px",
        )
        if self.controller:
            self.restore_original_btn.clicked.connect(self.controller.restore_original_dataframe)
        self.restore_original_btn.setEnabled(False)
        inject_layout.addWidget(self.restore_original_btn)

        inject_group.setLayout(inject_layout)
        subset_layout.addWidget(inject_group)
        subset_layout.addStretch()

        subset_icon = QIcon(get_resource_path("icons/data_operations/subset.png"))
        self.ops_tabs.addTab(subset_tab, subset_icon, "Subsets")

    def create_history_tab(self):
        history_tab = QWidget()
        history_layout = QVBoxLayout(history_tab)

        history_info = QLabel("View and revert to a previous state of data state")
        history_info.setWordWrap(True)
        history_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        history_layout.addWidget(history_info)

        self.history_list = DataPlotStudioListWidget()
        if self.controller:
            self.history_list.itemClicked.connect(self.controller.on_history_clicked)
        history_layout.addWidget(self.history_list)

        history_help = QLabel("Click on a state to go back/forwards to it.\nGray items are undone operations.")
        history_help.setWordWrap(True)
        history_help.setStyleSheet("color: #7f8c8d; font-size: 8pt;")
        history_layout.addWidget(history_help)

        history_icon = QIcon(get_resource_path("icons/data_operations/view.png"))
        self.ops_tabs.addTab(history_tab, history_icon, "History")
    
    ###### Getters for widgets
    def get_filter_parameters(self) -> tuple[str, str, str]:
        """
        Retrieves the current configuration for data filtering.
        Returns:
            tuple: (column_name, condition_operator, filter_value)
        """
        return (
            self.filter_column.currentText(),
            self.filter_condition.currentText(),
            self.filter_value.text()
        )
    
    def get_selected_columns(self) -> list[str]:
        """
        Retrieves a list of names for the currently selected columns in the column list
        """
        return [item.text() for item in self.column_list.selectedItems()]
    
    def get_target_datatype(self) -> str:
        """Retrieves the currently selected data type for conversion"""
        return self.type_combo.currentText()
    
    def get_text_operation(self) -> str:
        """Retrieve the currently selected text manipulation operation"""
        return self.text_operation_combo.currentText()
    
    def get_normalization_method(self) -> str:
        """Get the currently selected normalization method"""
        return self.norm_method_combo.currentText()
    
    def get_sort_parameters(self) -> tuple[str, str]:
        """
        Retrieves the sort configuration
        Returns:
            tuple: (column_name, sort_order_string)
        """
        return (
            self.sort_column_combo.currentText(),
            self.sort_order_combo.currentText()
        )
    
    def get_date_extraction_parameters(self) -> tuple[str, str]:
        """Returns source_column and component_to_extract from box"""
        return (self.dt_source_combo.currentText(), self.dt_component_combo.currentText())
    
    def get_date_diff_parameters(self) -> tuple[str, str, str]:
        """Returns (start_column, end_column, unit)"""
        return (self.dt_start_combo.currentText(), self.dt_end_combo.currentText(), self.dt_unit_combo.currentText())
    
    def get_quick_subset_column(self) -> str:
        """Retrieve the selected column name for auto-creating subsets"""
        return self.subset_column_combo.currentText()
    
    def get_selected_saved_aggregation(self) -> Optional[str]:
        """Retrieve the name of the currently selected saved aggregation"""
        item = self.saved_agg_list.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def get_selected_active_subset(self) -> Optional[str]:
        """Retrieve the name of cthe currently selected active subset"""
        item = self.active_subsets_list.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    def get_selected_history_index(self) -> Optional[int]:
        """Retrieve the selected history state index"""
        item = self.history_list.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
        return None
    
    #####_UI updaters
    
    def update_saved_aggregation_list(self, aggregations: list[tuple[str, int]]) -> None:
        """
        Updates the saved aggregations list widget with new data
        Args:
            aggregations: List of tuples containing (name, row_count)
        """
        self.saved_agg_list.clear()
        if not aggregations:
            placeholder = QListWidgetItem("No saved aggregations")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.saved_agg_list.addItem(placeholder)
            return
        
        for name, row_count in aggregations:
            item_text = f"{name} ({row_count}) rows"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.saved_agg_list.addItem(item)
    
    def set_aggregation_buttons_enabled(self, enabled: bool) -> None:
        self.view_agg_btn.setEnabled(enabled)
        self.delete_agg_btn.setEnabled(enabled)
    
    def update_active_subsets_list(self, subsets: list[tuple[str, str]]) -> None:
        """
        Update the active subsets list widget.
        Args:
            subsets: List of tuples containing (name, display_text_for_rows)
        """
        self.active_subsets_list.clear()
        for name, row_text in subsets:
            item = QListWidgetItem(f"{name} ({row_text})")
            item.setData(Qt.ItemDataRole.UserRole, name)
            self.active_subsets_list.addItem(item)
    
    def set_injection_status_ui(self, is_subset_active: bool, subset_name: str = "") -> None:
        """
        Update the UI elements related to subset injection status.
        Args:
            is_subset_active: True if a subset is currently injected.
            subset_name: Name of the subset (only used if is_subset_active is True).
        """
        if is_subset_active:
            self.injection_status_label.setText(f"Status: Working with a subset: '{subset_name}'")
            self.injection_status_label.setStyleSheet(
                "color: #e74c3c; font-weight: bold; padding: 5px; background-color: #ffe5e5; border-radius: 3px;"
            )
            self.restore_original_btn.setEnabled(True)
            self.inject_subset_tbn.setEnabled(False)
        else:
            self.injection_status_label.setText("Status: Working with original data")
            self.injection_status_label.setStyleSheet(
                "color: #27ae60; font-weight: bold; padding: 5px; background-color: #ecf0f1; border-radius: 3px;"
            )
            self.restore_original_btn.setEnabled(False)
            self.inject_subset_tbn.setEnabled(True)
    
    def select_history_item_by_index(self, target_index: int) -> None:
        """Select the history item corresponding to the given index."""
        for i in range(self.history_list.count()):
            list_item = self.history_list.item(i)
            if list_item.data(Qt.ItemDataRole.UserRole) == target_index:
                self.history_list.setCurrentItem(list_item)
                break