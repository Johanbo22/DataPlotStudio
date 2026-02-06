# ui/data_tab.py
import re
import traceback
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QTextEdit,
    QInputDialog,
    QListWidgetItem,
    QApplication,
    QTableView,
    QHeaderView,
    QGraphicsOpacityEffect,
    QMenu,
    QAbstractItemView,
    QDialog,
    QStackedWidget,
)
from PyQt6.QtCore import (
    Qt,
    QTimer,
    pyqtSlot,
    QPropertyAnimation,
    QEasingCurve,
    pyqtSignal,
    QThreadPool
)
from PyQt6.QtGui import QIcon, QFont, QAction, QPalette, QColor, QShortcut, QKeySequence

from core import data_handler
from core.data_handler import DataHandler
from core.aggregation_manager import AggregationManager
from core.resource_loader import get_resource_path
from ui.animations.AggregationAnimation import AggregationAnimation
from ui.animations.DataFilterAnimation import DataFilterAnimation
from ui.animations.DataTypeChangeAnimation import DataTypeChangeAnimation
from ui.animations.DropColumnAnimation import DropColumnAnimation
from ui.animations.MeltDataAnimation import MeltDataAnimation
from ui.animations.OutlierDetectionAnimation import OutlierDetectionAnimation
from ui.animations.RenameColumnAnimation import RenameColumnAnimation
from ui.status_bar import StatusBar
from ui.dialogs import (
    ProgressDialog,
    RenameColumnDialog,
    FilterAdvancedDialog,
    AggregationDialog,
    FillMissingDialog,
    HelpDialog,
    MeltDialog,
    OutlierDetectionDialog,
    TableCustomizationDialog,
    SearchResultsDialog,
    PivotDialog,
    MergeDialog,
    BinningDialog
)
from core.subset_manager import SubsetManager
from pathlib import Path

from core.help_manager import HelpManager
from ui.data_table_model import DataTableModel
from ui.widgets import (
    DataPlotStudioListWidget,
    DataPlotStudioButton,
    DataPlotStudioComboBox,
    DataPlotStudioGroupBox,
    DataPlotStudioLineEdit,
    DataPlotStudioTabWidget,
    HelpIcon
)
from ui.components.data_operations_panel import DataOperationsPanel
from ui.components.statistics_generator import StatisticsGenerator
from ui.LandingPage import LandingPage
from ui.dialogs.ComputedColumnDialog import ComputedColumnDialog

from ui.animations import (
    DropMissingValueAnimation,
    FillMissingValuesAnimation,
    RemoveRowAnimation,
    ResetToOriginalStateAnimation,
    FailedAnimation,
    NewDataFrameAnimation,
    EditModeToggleAnimation,
    FileImportAnimation
)
from ui.workers import GoogleSheetsImportWorker


class DataTab(QWidget):
    """Tab for viewing and manipulating data"""

    request_open_project = pyqtSignal()
    request_import_file = pyqtSignal()
    request_import_sheets = pyqtSignal()
    request_import_db = pyqtSignal()
    request_quit = pyqtSignal()

    def __init__(
        self,
        data_handler: DataHandler,
        status_bar: StatusBar,
        subset_manager: SubsetManager,
    ):
        super().__init__()

        self.data_handler = data_handler
        self.status_bar = status_bar
        self.subset_manager = subset_manager
        self.aggregation_manager = AggregationManager()
        self.help_manager = HelpManager()
        self.stats_generator = StatisticsGenerator()
        self.plot_tab = None
        self.data_table = None
        self.stats_text = None
        self.data_tabs = None
        self.subset_view_label = None
        self.aggregation_view_label = None
        self.is_editing = False
        
        self.current_precision = 2
        self.current_formatting_rules = []

        self.init_ui()

    def set_plot_tab(self, plot_tab):
        """Sets a reference to the PlotTab"""
        self.plot_tab = plot_tab

    def init_ui(self):
        """Initialize the data tab UI"""
        main_layout = QHBoxLayout(self)

        # Left side: Data table and operations stacked with landing page
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        self.left_stack = QStackedWidget()
        left_layout.addWidget(self.left_stack)

        # Landing page
        self.landing_page = LandingPage()
        self.landing_page.open_project_clicked.connect(self.request_open_project.emit)
        self.landing_page.import_file_clicked.connect(self.request_import_file.emit)
        self.landing_page.import_sheets_clicked.connect(self.request_import_sheets.emit)
        self.landing_page.import_db_clicked.connect(self.request_import_db.emit)
        self.landing_page.new_dataset_clicked.connect(self.create_new_dataset)
        self.landing_page.quit_clicked.connect(self.request_quit.emit)
        self.left_stack.addWidget(self.landing_page)

        # Data view container
        self.data_view_widget = QWidget()
        data_view_layout = QVBoxLayout(self.data_view_widget)
        data_view_layout.setContentsMargins(0, 0, 0, 0)
        self.left_stack.addWidget(self.data_view_widget)

        # data toolbar
        toolbar_layout = QHBoxLayout()
        toolbar_layout.setContentsMargins(0, 0, 0, 0)

        # create dataset
        self.create_new_dataset_button = DataPlotStudioButton(
            "Create a New Dataset",
            parent=self,
            base_color_hex="#3498DB",
            text_color_hex="white",
        )
        self.create_new_dataset_button.setIcon(
            QIcon(get_resource_path("icons/menu_bar/file-plus-corner.svg"))
        )
        self.create_new_dataset_button.setToolTip("Create a new empty DataFrame")
        self.create_new_dataset_button.clicked.connect(self.create_new_dataset)
        toolbar_layout.addWidget(self.create_new_dataset_button)

        self.data_source_refresh_button = DataPlotStudioButton(
            "Refresh Data",
            parent=self,
            base_color_hex="#27ae60",
            hover_color_hex="#229954",
            text_color_hex="white",
            font_weight="bold",
        )
        self.data_source_refresh_button.setIcon(
            QIcon(get_resource_path("icons/menu_bar/google_sheet.png"))
        )
        self.data_source_refresh_button.setToolTip(
            "Re-import data from your Google Sheets document"
        )
        self.data_source_refresh_button.clicked.connect(self.refresh_google_sheets_data)
        self.data_source_refresh_button.setVisible(False)
        toolbar_layout.addWidget(self.data_source_refresh_button)

        toolbar_layout.addStretch()

        # edit current dataset toggle
        self.edit_dataset_toggle_button = DataPlotStudioButton(
            "Edit Mode: OFF",
            parent=self,
            base_color_hex="#95a5a6",
            text_color_hex="white",
        )
        self.edit_dataset_toggle_button.setIcon(QIcon(get_resource_path("icons/pencil-ruler.svg")))
        self.edit_dataset_toggle_button.setCheckable(True)
        self.edit_dataset_toggle_button.setToolTip(
            "Toggle to edit data directly in the table"
        )
        self.edit_dataset_toggle_button.clicked.connect(self.toggle_edit_mode)
        toolbar_layout.addWidget(self.edit_dataset_toggle_button)

        data_view_layout.addLayout(toolbar_layout)

        # Create tabs for data and statistics
        self.data_tabs = DataPlotStudioTabWidget()

        # Data Table Tab
        self.data_table = QTableView()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSortingEnabled(True)
        self.data_table.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.data_table.verticalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        self.data_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        # Data table context menu
        self.data_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.data_table.customContextMenuRequested.connect(self.show_table_context_menu)

        # Search functionality to data table
        self.search_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
        self.search_shortcut.activated.connect(self.open_search_dialog)

        data_table_icon = QIcon(get_resource_path("icons/data_table.png"))
        self.data_tabs.addTab(self.data_table, data_table_icon, "Data Table")

        # Statistics Tab
        self.stats_text = QTextEdit()
        self.stats_text.setReadOnly(True)

        self.stats_opacity_effect = QGraphicsOpacityEffect(self.stats_text)
        self.stats_text.setGraphicsEffect(self.stats_opacity_effect)
        stats_icon = QIcon(get_resource_path("icons/data_stats.png"))
        self.data_tabs.addTab(self.stats_text, stats_icon, "Statistics")

        data_view_layout.addWidget(self.data_tabs, 1)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.operations_panel = DataOperationsPanel(parent=self, controller=self)

        right_layout.addWidget(self.operations_panel)
        
        # Bindings of widgets
        self.filter_column: DataPlotStudioComboBox = self.operations_panel.filter_column
        self.filter_condition: DataPlotStudioComboBox = self.operations_panel.filter_condition
        self.filter_value: DataPlotStudioLineEdit = self.operations_panel.filter_value
        self.apply_filter_help: HelpIcon = self.operations_panel.apply_filter_help
        
        self.column_list: DataPlotStudioListWidget = self.operations_panel.column_list
        self.type_combo: DataPlotStudioComboBox = self.operations_panel.type_combo
        self.text_operation_combo: DataPlotStudioComboBox = self.operations_panel.text_operation_combo
        self.change_datatype_help: HelpIcon = self.operations_panel.change_datatype_help
        
        self.sort_column_combo: DataPlotStudioComboBox = self.operations_panel.sort_column_combo
        self.sort_order_combo: DataPlotStudioComboBox = self.operations_panel.sort_order_combo
        
        self.saved_agg_list: DataPlotStudioListWidget = self.operations_panel.saved_agg_list
        self.view_agg_btn: DataPlotStudioButton = self.operations_panel.view_agg_btn
        self.delete_agg_btn: DataPlotStudioButton = self.operations_panel.delete_agg_btn
        
        self.subset_column_combo: DataPlotStudioComboBox = self.operations_panel.subset_column_combo
        self.active_subsets_list: DataPlotStudioListWidget = self.operations_panel.active_subsets_list
        self.inject_subset_tbn: DataPlotStudioButton = self.operations_panel.inject_subset_tbn
        self.injection_status_label: QLabel = self.operations_panel.injection_status_label
        self.restore_original_btn: DataPlotStudioButton = self.operations_panel.restore_original_btn
        
        self.history_list: DataPlotStudioListWidget = self.operations_panel.history_list

        # Create splitter
        from PyQt6.QtWidgets import QSplitter

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.refresh_data_view()

    def create_new_dataset(self):
        """Creates a new empty dataset"""
        try:
            rows, ok = QInputDialog.getInt(
                self, "New Dataset", "Number of Rows:", 10, 1, 1000000
            )
            if not ok:
                return

            columns, ok = QInputDialog.getInt(
                self, "New Dataset", "Number of Columns:", 3, 1, 1000
            )
            if not ok:
                return

            confirm = QMessageBox.question(
                self,
                "Confirm Create",
                "This will clear the current dataset and create a new empty dataset. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )

            if confirm == QMessageBox.StandardButton.Yes:
                self.data_handler.create_empty_dataframe(rows, columns)
                self.refresh_data_view()
                self.status_bar.log(
                    f"Created new dataset: ({rows}x{columns})", "SUCCESS"
                )

                self.create_new_dataframe_animation = NewDataFrameAnimation(
                    parent=None, message="Created New DataFrame"
                )
                self.create_new_dataframe_animation.start(target_widget=self)

        except Exception as CreateNewDatasetError:
            QMessageBox.critical(
                self, "Error", f"Failed to create dataset: {str(CreateNewDatasetError)}"
            )
            self.failed_animation = FailedAnimation("Failed to Create", parent=None)
            self.failed_animation.start(target_widget=self)

    def toggle_edit_mode(self):
        """Toggles the edit mode in the datble"""
        self.is_editing = self.edit_dataset_toggle_button.isChecked()

        if self.is_editing:
            self.edit_dataset_toggle_button.setText("Edit Mode: ON")
            self.edit_dataset_toggle_button.updateColors(
                base_color_hex="#E74C3C", hover_color_hex="#C0392B"
            )
            self.data_table.setEditTriggers(
                QTableView.EditTrigger.DoubleClicked
                | QTableView.EditTrigger.AnyKeyPressed
            )
            self.status_bar.log(
                "Edit Mode Enabled. You are now able to edit cells in the data table",
                "INFO",
            )

            self.edit_toggle_on_animation = EditModeToggleAnimation(
                parent=self, is_on=True
            )
            self.edit_toggle_on_animation.start(target_widget=self)
        else:
            self.edit_dataset_toggle_button.setText("Edit Mode: OFF")
            self.edit_dataset_toggle_button.updateColors(
                base_color_hex="#95A5A6", hover_color_hex="#7F8C8D"
            )
            self.data_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
            self.status_bar.log("Edit Mode Disabled", "INFO")

            self.edit_toggle_off_animation = EditModeToggleAnimation(
                parent=self, is_on=False
            )
            self.edit_toggle_off_animation.start(target_widget=self)

        # update the flags
        if self.data_table.model() is not None and isinstance(
            self.data_table.model(), DataTableModel
        ):
            self.data_table.model().set_editable(self.is_editing)
        else:
            self.refresh_data_view()

    def open_search_dialog(self):
        """Opens a search dialog to find the values in the data table"""
        if self.data_handler.df is None:
            return

        text, ok = QInputDialog.getText(self, "Find in table", "Search for a value:")
        if ok and text:
            self.perform_search(text)

    def perform_search(self, search_text: str):
        """Executes a search on the dataframe"""
        df = self.data_handler.df
        matches = []

        search_text_lower = str(search_text).lower()

        for row_index in range(df.shape[0]):
            for column_index in range(df.shape[1]):
                value = str(df.iloc[row_index, column_index])
                if search_text_lower in value.lower():
                    matches.append(
                        (row_index, column_index, df.columns[column_index], value)
                    )

        if not matches:
            QMessageBox.information(
                self, "Search", f"No matches found for '{search_text}'"
            )
            return

        if len(matches) == 1:
            self.highlight_cell(matches[0][0], matches[0][1])
            self.status_bar.log(
                f"Found 1 match at Row {matches[0][0]}, Column '{matches[0][1]}'",
                "SUCCESS",
            )
        else:
            dialog = SearchResultsDialog(matches, self)
            if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_match:
                row, col_index, col, value = dialog.selected_match
                self.highlight_cell(row, col_index)
                self.status_bar.log(
                    f"Selected match at Row: {row}, Column: '{col}'", "SUCCESS"
                )

    def highlight_cell(self, row_index: int, column_index: int):
        """Scrolls to and highlights the specified index cell in the data table"""
        if self.data_table.model() is None:
            return

        index = self.data_table.model().index(row_index, column_index)
        if index.isValid():
            self.data_table.setCurrentIndex(index)
            self.data_table.scrollTo(index, QTableView.ScrollHint.EnsureVisible)
            self.data_table.setFocus()

    def inject_subset_to_dataframe(self):
        """Insert the selected subset into the active dataframe view.\n
        This allows the user to view their subset and do further manipulation to it, without having to export the subset first."""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No data", "Please load data first")
            return

        # get the selected subset
        item = self.active_subsets_list.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "None selected",
                "Please select a subset to apply to current data view",
            )
            return

        subset_name = item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Confirm",
            f"Are you sure you want to insert the subset: '{subset_name}' into the active DataFrame\n\n"
            f"This will temporarily replace the current data view.\n"
            f"You can restore the original data view by pressing the 'Revert to Original Data View'",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            # we need to store the original df first.
            if (
                not hasattr(self.data_handler, "pre_insert_df")
                or self.data_handler.pre_insert_df is None
            ):
                self.data_handler.pre_insert_df = self.data_handler.df.copy()
                self.data_handler.inserted_subset_name = None

            subset_manager = self.subset_manager
            subset_df = subset_manager.apply_subset(
                self.data_handler.df, subset_name, use_cache=False
            )

            self.data_handler.df = subset_df.copy()
            self.data_handler.inserted_subset_name = subset_name

            self.refresh_data_view()

            self.injection_status_label.setText(
                f"Status: Working with a subset: '{subset_name}'"
            )
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
                    "operation": "insert_subset_into_active_data_view",
                },
                level="SUCCESS",
            )

            QMessageBox.information(
                self,
                "Insertion Complete",
                f"Subset '{subset_name}' has been inserted into the active DataFrame.\n\n"
                f"Original data: {len(self.data_handler.pre_insert_df):,} rows\n"
                f"Subset data: {len(subset_df):,} rows\n\n"
                f"Click 'Restore Original Data View' to return to the full dataset.",
            )

        except Exception as InsertSubsetIntoDataFrameError:
            self.status_bar.log(
                f"Failed to insert the subset: {str(InsertSubsetIntoDataFrameError)}",
                "ERROR",
            )
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to insert subset:\n{str(InsertSubsetIntoDataFrameError)}",
            )
            self.failed_animation = FailedAnimation(message="Failed to Insert Subset")
            self.failed_animation.start(target_widget=self)
            traceback.print_exc()

    def restore_original_dataframe(self):
        """Restore the original DataFrame into the Active Data View of the Data Table"""
        if (
            not hasattr(self.data_handler, "pre_insert_df")
            or self.data_handler.pre_insert_df is None
        ):
            QMessageBox.warning(
                self, "Nothing to Restore", "No inserted subset to restore from"
            )
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
                    "previous_subset": subset_name,
                    "restored_rows": original_rows,
                    "operation": "restore_original",
                },
                level="SUCCESS",
            )

            QMessageBox.information(
                self,
                "Restore Complete",
                f"Original DataFrame has been restored.\n\n"
                f"Restored: {original_rows:,} rows",
            )

            self.restore_animation = ResetToOriginalStateAnimation(
                "Restored to Original", parent=None
            )
            self.restore_animation.start(target_widget=self)

        except Exception as RestoreOriginalDataFrameError:
            self.status_bar.log(
                f"Failed to restore original data: {str(RestoreOriginalDataFrameError)}",
                "ERROR",
            )
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to restore original data:\n{str(RestoreOriginalDataFrameError)}",
            )
            traceback.print_exc()

    def refresh_data_view(self, reload_model: bool = True):
        """Refresh the data table and statistics"""
        if self.data_handler.df is None:
            if hasattr(self, "left_stack"):
                self.left_stack.setCurrentIndex(0)

            if hasattr(self, "data_table") and self.data_table is not None:
                self.data_table.setModel(None)

            if hasattr(self, "stats_text") and self.stats_text is not None:
                self.stats_text.clear()

            if hasattr(self, "data_source_refresh_button"):
                self.data_source_refresh_button.setVisible(False)

            self.status_bar.set_data_source("")
            self.status_bar.set_view_contex("", "normal")

            return

        if hasattr(self, "left_stack"):
            self.left_stack.setCurrentIndex(1)

        df = self.data_handler.df

        # Update table
        if reload_model:
            self.model = DataTableModel(self.data_handler, editable=self.is_editing, float_precision=self.current_precision, conditional_rules=self.current_formatting_rules)
            self.data_table.setSortingEnabled(False)
            self.data_table.setModel(self.model)

            header = self.data_table.horizontalHeader()
            header.blockSignals(True)

            if self.data_handler.sort_state:
                col_name, ascending = self.data_handler.sort_state
                try:
                    col_index = list(df.columns).index(col_name)
                    order = (
                        Qt.SortOrder.AscendingOrder
                        if ascending
                        else Qt.SortOrder.DescendingOrder
                    )
                    header.setSortIndicator(col_index, order)
                except ValueError:
                    header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
            else:
                header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)

            header.blockSignals(False)
            self.data_table.setSortingEnabled(True)

        if self.is_editing:
            self.data_table.setEditTriggers(
                QTableView.EditTrigger.DoubleClicked
                | QTableView.EditTrigger.AnyKeyPressed
            )
        else:
            self.data_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)

        # Update column selectors
        columns = list(df.columns)
        self.filter_column.clear()
        self.filter_column.addItems(columns)
        self.column_list.clear()
        self.column_list.addItems(columns)

        # Update the sort col combo
        if hasattr(self, "sort_column_combo"):
            current_sort = self.sort_column_combo.currentText()
            self.sort_column_combo.clear()
            self.sort_column_combo.addItems(columns)
            if current_sort and current_sort in columns:
                self.sort_column_combo.setCurrentText(current_sort)
            elif (
                self.data_handler.sort_state
                and self.data_handler.sort_state[0] in columns
            ):
                self.sort_column_combo.setCurrentText(self.data_handler.sort_state[0])

        # Update subset column combo if it exists
        if hasattr(self, "subset_column_combo"):
            try:
                self.subset_column_combo.clear()
                self.subset_column_combo.addItems(columns)
            except Exception as RefreshDataViewError:
                print(
                    f"Warning: Could not update subset column combo: {RefreshDataViewError}"
                )

        if self.plot_tab:
            self.plot_tab.update_column_combo()

        # Update statistics
        self.update_statistics()

        if self.data_handler.has_google_sheets_import():
            self.data_source_refresh_button.setVisible(True)
            display_name = self.data_handler.last_gsheet_name
            if not display_name:
                display_name = f"GID: {self.data_handler.last_gsheet_gid}"
            self.status_bar.set_data_source(f"Google Sheets: {display_name}")
        elif hasattr(self.data_handler, "file_path") and self.data_handler.file_path:
            try:
                file_name = Path(self.data_handler.file_path).name
            except Exception:
                file_name = str(self.data_handler.file_path)

            self.status_bar.set_data_source(f"Local file: {file_name}")
            self.data_source_refresh_button.setVisible(False)
        else:
            self.status_bar.set_data_source("New")
            self.data_source_refresh_button.setVisible(False)

        try:
            if hasattr(self, "subset_manager"):
                self.subset_manager.clear_cache()
            if hasattr(self, "active_subsets_list"):
                self.refresh_active_subsets()
        except Exception as RefreshSubsetInDataViewError:
            print(f"Warning: Could not refresh subsets: {RefreshSubsetInDataViewError}")

        inserted_name = getattr(self.data_handler, "inserted_subset_name", None)
        agg_name = getattr(self.data_handler, "viewing_aggregation_name", None)

        if agg_name:
            self.status_bar.set_view_contex(f"Viewing Aggregation: {agg_name}")
        elif inserted_name:
            self.status_bar.set_view_contex(f"Viewing Subset: {inserted_name}")

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
                initial_item.setIcon(QIcon(get_resource_path("icons/ui_styling/checkmark.png")))

            self.history_list.addItem(initial_item)

            for i, operation in enumerate(history_operations):
                history_index = i + 1
                operation_text = self._format_operation_text(operation)
                item = QListWidgetItem(f"{history_index}. {operation_text}")
                item.setData(Qt.ItemDataRole.UserRole, history_index)

                if history_index == current_index:
                    item.setFont(QFont("Arial", 9, QFont.Weight.Bold))
                    item.setForeground(Qt.GlobalColor.black)
                    item.setIcon(QIcon(get_resource_path("icons/ui_styling/checkmark.png")))
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

        if not hasattr(self, "subset_column_combo"):
            QMessageBox.warning(
                self, "Feature Not Available", "Subset feature not fully initialized"
            )
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                subset_manager = self.subset_manager
                created = subset_manager.create_subset_from_unique_values(
                    self.data_handler.df, column
                )

                # Apply each to get row counts
                for name in created:
                    subset_manager.apply_subset(self.data_handler.df, name)

                self.refresh_active_subsets()

                self.status_bar.log_action(
                    f"Created {len(created)} subsets from column '{column}'",
                    details={
                        "column": column,
                        "subsets_created": len(created),
                        "unique_values": unique_count,
                        "operation": "auto_create_subsets",
                    },
                    level="SUCCESS",
                )

                QMessageBox.information(
                    self,
                    "Success",
                    f"Created {len(created)} subsets from column '{column}'",
                )
            except Exception as QuickCreateSubsetsError:
                self.status_bar.log(
                    f"Failed to create subsets: {str(QuickCreateSubsetsError)}", "ERROR"
                )
                QMessageBox.critical(self, "Error", str(QuickCreateSubsetsError))
                import traceback

                traceback.print_exc()

    def refresh_active_subsets(self):
        """Refresh the list of active subsets"""
        if not hasattr(self, "active_subsets_list"):
            return

        try:
            self.active_subsets_list.clear()

            subset_manager = self.subset_manager

            if self.data_handler.df is not None:
                for name in subset_manager.list_subsets():
                    try:
                        subset_manager.apply_subset(self.data_handler.df, name)
                    except Exception as ApplySubsetError:
                        print(
                            f"Warning: Could not apply subset {name}: {str(ApplySubsetError)}"
                        )

            for name in subset_manager.list_subsets():
                subset = subset_manager.get_subset(name)
                row_text = (
                    f"{subset.row_count} rows" if subset.row_count > 0 else "? rows"
                )
                item = QListWidgetItem(f"{name} ({row_text} rows)")
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.active_subsets_list.addItem(item)
        except Exception as RefreshSubsetListError:
            print(f"Warning: Could not refresh subset list: {RefreshSubsetListError}")

    def view_subset_quick(self):
        """Quick view of selected subset"""
        if not hasattr(self, "active_subsets_list"):
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

            print(
                f"DEBUG open_subset_manager: SubsetManager has {len(subset_manager.list_subsets())} subsets"
            )

            # Create and show dialog
            dialog = SubsetManagerDialog(subset_manager, self.data_handler, self)
            # Request redirection to index 1
            dialog.plot_subset_requested.connect(self.handle_plot_request)

            print("DEBUG open_subset_manager: Dialog created, executing")
            dialog.exec()

            print("DEBUG open_subset_manager: Dialog closed, refreshing active subsets")
            # Refresh the subset list after dialog closes
            self.refresh_active_subsets()

        except Exception as OpenSubsetManagerError:
            print(f"ERROR open_subset_manager: {str(OpenSubsetManagerError)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open subset manager: {str(OpenSubsetManagerError)}",
            )
            import traceback

            traceback.print_exc()

    def handle_plot_request(self, subset_name: str):
        """Handle the signal from SubsetManagerDialog to plot the selected subset"""
        if not self.plot_tab:
            QMessageBox.warning(
                self, "Error", "Plot tab reference not set. Cannot switch tabs"
            )
            self.status_bar.log("Plot tab reference not set", "ERROR")
            return

        try:
            self.plot_tab.activate_subset(subset_name)

            current_widget = self.parentWidget()
            found_tab_widget = False
            while current_widget:
                if isinstance(current_widget, DataPlotStudioTabWidget):
                    current_widget.setCurrentWidget(self.plot_tab)
                    found_tab_widget = True
                    break
                current_widget = current_widget.parentWidget()

            if not found_tab_widget:
                self.status_bar.log(
                    "Could not switch to plot tab automatically: Tab widget not found",
                    "WARNING",
                )

        except Exception as PlotRequestError:
            self.status_bar.log(
                f"Failed to switch to plotting tab: {str(PlotRequestError)}", "ERROR"
            )
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to activate the plot tab: {str(PlotRequestError)}",
            )

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
            self.stats_text.setHtml(
                f"<p style='color: red;'>Error loading data info: {str(UpdateStatisticsError)}</p>"
            )
            return
        
        # Generate HTML
        final_html = self.stats_generator.generate_html(df, info)
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

            self.remove_rows_animation = RemoveRowAnimation(message="Removed Rows")
            self.remove_rows_animation.start(target_widget=self)

            # msg
            self.status_bar.log_action(
                f"Removed {removed:,} duplicate row(s)",
                details={
                    "rows_before": before,
                    "rows_after": after,
                    "rows_removed": removed,
                    "operation": "drop_duplicates",
                },
                level="SUCCESS",
            )
        except Exception as RemoveDuplicatesError:
            self.status_bar.log(
                f"Failed to remove duplicates: {str(RemoveDuplicatesError)}", "ERROR"
            )
            self.failed_animation = FailedAnimation("Failed To Remove Rows")
            self.failed_animation.start(target_widget=self)

    def drop_missing(self):
        """Drop rows with missing values"""
        try:
            before = len(self.data_handler.df)
            self.data_handler.clean_data("drop_missing")
            after = len(self.data_handler.df)
            removed = before - after

            self.refresh_data_view()

            self.status_bar.log_action(
                f"Dropped {removed:,} row(s) with missing values",
                details={
                    "rows_before": before,
                    "rows_after": after,
                    "rows_removed": removed,
                    "operation": "drop_missing",
                },
                level="SUCCESS",
            )
            self.dropmissing_animation = DropMissingValueAnimation(
                parent=None, message="Drop Missing Values"
            )
            self.dropmissing_animation.start(target_widget=self)
        except Exception as DropMissingError:
            self.status_bar.log(
                f"Failed to drop missing values: {str(DropMissingError)}", "ERROR"
            )
            self.failed_animation = FailedAnimation("Failed to Drop Missing values")
            self.failed_animation.start(target_widget=self)

    def fill_missing(self):
        """Fill missing values"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        try:
            columns = list(self.data_handler.df.columns)
            dialog = FillMissingDialog(columns, df=self.data_handler.df, parent=self)

            if dialog.exec():
                config = dialog.get_config()

                df = self.data_handler.df
                missing_before = df.isnull().sum().sum()

                self.data_handler.clean_data(
                    "fill_missing",
                    column=config["column"],
                    method=config["method"],
                    value=config["value"],
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
                        "operation": "fill_missing",
                    },
                    level="SUCCESS",
                )
                self.fill_missing_animation = FillMissingValuesAnimation(
                    message="Fill Missing Values", fill_value=config["value"]
                )
                self.fill_missing_animation.start(target_widget=self)
        except Exception as FillMissingValuesError:
            self.status_bar.log(
                f"Failed to execute 'Fill Missing values': {str(FillMissingValuesError)}",
                "ERROR",
            )
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to execute 'Fill Missing Values':\n{str(FillMissingValuesError)}",
            )

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
                    "operation": "filter",
                },
                level="SUCCESS",
            )

            self.filter_animation = DataFilterAnimation(message="Filter Data")
            self.filter_animation.start(target_widget=self)

        except Exception as ApplyFilterError:
            self.status_bar.log(
                f"Failed to execute 'Filter': {str(ApplyFilterError)}", "ERROR"
            )

    def clear_filters(self):
        """Clear filters by reseting the data to original state"""
        if self.data_handler.df is None:
            return

        self.reset_data()
        self.status_bar.log("Filters cleared and data reset to original state", "INFO")

    def drop_column(self):
        """Drop selected column"""
        if self.data_handler.df is None:
            return

        # Get the selected items
        selected_items = self.column_list.selectedItems()
        if not selected_items:
            self.status_bar.log("No columns selected to drop", "WARNING")
            QMessageBox.warning(
                self, "Selection Error", "Please select at least one column to drop"
            )
            return

        cols_to_drop = [item.text() for item in selected_items]
        msg = f"Are you sure you want to drop {len(cols_to_drop)} column(s)?\n\n"
        msg += ", ".join(cols_to_drop[:5])
        if len(cols_to_drop) > 5:
            msg += "..."

        confirm = QMessageBox.question(
            self,
            "Confirm Drop",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                cols_before = len(self.data_handler.df.columns)
                self.data_handler.clean_data("drop_column", columns=cols_to_drop)

                cols_after = len(self.data_handler.df.columns)
                self.refresh_data_view()

                self.status_bar.log_action(
                    f"Dropped {len(cols_to_drop)} columns",
                    details={
                        "columns": cols_to_drop,
                        "columns_before": cols_before,
                        "columns_after": cols_after,
                        "operation": "drop_column",
                    },
                    level="SUCCESS",
                )

                self.drop_column_animation = DropColumnAnimation(
                    message="Dropped Column"
                )
                self.drop_column_animation.start(target_widget=self)
            except Exception as DropColumnError:
                self.status_bar.log(
                    f"Failed to drop columns: {str(DropColumnError)}", "ERROR"
                )
                QMessageBox.critical(
                    self, "Error", f"Failed to drop columns: {str(DropColumnError)}"
                )

    def rename_column(self):
        """Rename selected column"""
        selected_items = self.column_list.selectedItems()

        if not selected_items:
            self.status_bar.log("No column selected", "WARNING")
            return

        old_name = selected_items[0].text()

        dialog = RenameColumnDialog(old_name, self)
        if dialog.exec():
            new_name = dialog.get_new_name()
            try:
                self.data_handler.clean_data(
                    "rename_column", old_name=old_name, new_name=new_name
                )

                self.refresh_data_view()
                self.status_bar.log_action(
                    f"Renamed '{old_name}' -> '{new_name}'",
                    details={
                        "old_name": old_name,
                        "new_name": new_name,
                        "operation": "rename_column",
                    },
                    level="SUCCESS",
                )

                self.rename_column_animation = RenameColumnAnimation(
                    message="Rename Column"
                )
                self.rename_column_animation.start(self)
            except Exception as RenameColumnError:
                self.status_bar.log(
                    f"Failed to rename column: {str(RenameColumnError)}", "ERROR"
                )

    def change_column_type(self):
        """Change the data type of the selected column"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No data", "Please load data first")
            return

        selected_items = self.column_list.selectedItems()
        if not selected_items:
            self.status_bar.log("No Column Selected", "WARNING")
            return

        if len(selected_items) > 1:
            QMessageBox.warning(
                self,
                "Selection Error",
                "Please select only one column to change datatype",
            )
            return

        column = selected_items[0].text()

        type_str = self.type_combo.currentText()

        # mapping the datatypes to their equiv in pandas
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

            # add some warning to the user if the're trying to ex convert from int to str
            if target_type in ["int", "float", "datetime"]:
                reply = QMessageBox.question(
                    self,
                    "Confirm DataType Conversion",
                    f"Attempting to convert column: '{column}' to {target_type}.\n\n"
                    f"This may fail or result in data loss.\n"
                    f"Invalid values will be converted to 'NaN'.\n\nContinue?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.No:
                    self.status_bar.log("Data Type conversion cancelled", "WARNING")
                    return

                self.data_handler.clean_data(
                    "change_data_type", column=column, new_type=target_type
                )
                self.refresh_data_view()

                new_type = str(self.data_handler.df[column].dtype)

                self.status_bar.log_action(
                    f"Changed datatype of '{column}' from {old_type} to {new_type}",
                    details={
                        "column": column,
                        "old_type": old_type,
                        "new_type": new_type,
                        "operation": "change_data_type",
                    },
                    level="SUCCESS",
                )
                self.changedatatype_animation = DataTypeChangeAnimation(
                    message="Change Data Type", old_type={old_type}, new_type={new_type}
                )
                self.changedatatype_animation.start(self)

        except Exception as ChangeColumnDataTypeError:
            error_msg = f"Failed to convert '{column}' to {target_type}: {str(ChangeColumnDataTypeError)}"
            QMessageBox.critical(self, "Conversion Error", error_msg)
            self.status_bar.log(error_msg, "ERROR")
            traceback.print_exc()
            self.refresh_data_view()

    def apply_text_manipulation(self):
        """Apply the requested text manipulation to the selected column"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No data", "Please load data first")

        selected_items = self.column_list.selectedItems()
        if not selected_items:
            self.status_bar.log("No Column Selected", "WARNING")
            return

        if len(selected_items) > 1:
            QMessageBox.warning(
                self,
                "Selection Error",
                "Please select only one column for text manipulation",
            )
            return

        column = selected_items[0].text()
        selected_operation = self.text_operation_combo.currentText()

        operation_map = {
            "Trim Whitespace": "strip",
            "Trim leading whitespace": "lstrip",
            "Trim trailing whitepsace": "rstrip",
            "Convert to lowercase": "lower",
            "Convert to UPPERCASE": "upper",
            "Convert to Title Case": "title",
            "Capitalize First Letter": "capitalize",
        }

        operation = operation_map.get(selected_operation)

        try:
            self.data_handler.clean_data(
                "text_manipulation", column=column, operation=operation
            )
            self.refresh_data_view()
            self.status_bar.log_action(
                f"Applied text operation: '{selected_operation}' to '{column}'",
                details={
                    "column": column,
                    "operation": operation,
                    "type": "text_manipulation",
                },
                level="SUCCESS",
            )

            self.status_bar.log(
                f"Successfully applied '{selected_operation}' to column '{column}'",
                "SUCCESS",
            )

        except Exception as TextManipulationError:
            QMessageBox.critical(
                self, "Text Manipulation Error", {str(TextManipulationError)}
            )
            self.status_bar.log(
                f"Text manipulation failed: {str(TextManipulationError)}", "ERROR"
            )

    def open_computed_column_dialog(self):
        """Opens the dialog to create a new column from a formula"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        columns = list(self.data_handler.df.columns)
        dialog = ComputedColumnDialog(columns, self)

        if dialog.exec():
            new_column, expression = dialog.get_data()
            try:
                self.data_handler.create_computed_column(new_column, expression)
                self.refresh_data_view()

                self.status_bar.log_action(
                    f"Created column '{new_column}' = {expression}",
                    details={
                        "new_column": new_column,
                        "expression": expression,
                        "operation": "computed_column",
                    },
                    level="SUCCESS",
                )
            except Exception as ComputedColumnError:
                self.status_bar.log(
                    f"Failed to create and calculate new column: {str(ComputedColumnError)}",
                    "ERROR",
                )
                QMessageBox.critical(
                    self,
                    "Computation Error",
                    f"Failed to create and calculate new column:\n{str(ComputedColumnError)}",
                )

    def reset_data(self):
        """Reset data to original state"""

        # confirmation
        reply = QMessageBox.question(
            self,
            "Confirm Reset",
            "Are you sure you want to reset the data to its original state?\n\n"
            "This will discard all changes, "
            "restore the original dataset and delete all history.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.No:
            self.status_bar.log("Data reset cancelled", "INFO")
            return

        try:
            rows_before = (
                len(self.data_handler.df) if self.data_handler.df is not None else 0
            )
            cols_before = (
                len(self.data_handler.df.columns)
                if self.data_handler.df is not None
                else 0
            )

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
                self.injection_status_label.setText(
                    "Status: Working with original data"
                )
                self.injection_status_label.setStyleSheet(
                    "color: #27ae60; font-weight: bold; padding: 5px;"
                    "background-color: #ecf0f1; border-radius: 3px;"
                )
                self.restore_original_btn.setEnabled(False)
                self.inject_subset_tbn.setEnabled(True)

            rows_after = (
                len(self.data_handler.df) if self.data_handler.df is not None else 0
            )
            cols_after = (
                len(self.data_handler.df.columns)
                if self.data_handler.df is not None
                else 0
            )

            self.refresh_data_view()

            self.reset_animation = ResetToOriginalStateAnimation(
                "Reset to Original", parent=None
            )
            self.reset_animation.start(target_widget=self)

            self.status_bar.log_action(
                "Data reset to original state",
                details={
                    "rows_restored": rows_after - rows_before,
                    "cols_restored": cols_after - cols_before,
                    "final_rows": rows_after,
                    "final_cols": cols_after,
                    "operation": "reset_data",
                },
                level="SUCCESS",
            )
        except Exception as ResetDataError:
            self.status_bar.log(f"Failed to reset data: {str(ResetDataError)}", "ERROR")

    def open_advanced_filter(self):
        """Open advanced filter dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "Warning", "No data loaded")
            return
        
        dialog = FilterAdvancedDialog(self.data_handler, self)
        if dialog.exec():
            result = dialog.get_filters()
            filters = result.get("filters", [])
            
            if not filters:
                return
            
            try:
                self.data_handler.filter_data(advanced_filters=filters)
                
                self.refresh_data_view()
                self.status_bar.log(f"Filters applied to data: {filters}")
            except Exception as FilterError:
                QMessageBox.critical(self, "Filter Error", f"Error applying filter:\n{str(FilterError)}")

    def open_aggregation_dialog(self):
        """Open aggregation dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "Warning", "No data loaded")
            return

        dialog = AggregationDialog(self.data_handler, self)
        if dialog.exec():
            config = dialog.get_aggregation_config()
            try:
                self.data_handler.reset_data()

                group_cols = config["group_by"]
                agg_config = config["agg_config"]
                date_grouping = config.get("date_grouping")
                agg_name = config.get("aggregation_name", "")

                self.data_handler.aggregate_data(group_cols, agg_config, date_grouping)
                result_df = self.data_handler.df.copy()

                # ask the user if they want ot save this agg
                if agg_name:
                    try:
                        desc_parts = [
                            f"{func}({col})" for col, func in agg_config.items()
                        ]
                        description = f"Aggregated: {', '.join(desc_parts)} by {', '.join(group_cols)}"

                        self.aggregation_manager.save_aggregation(
                            name=agg_name,
                            description=description,
                            group_by=group_cols,
                            agg_config=agg_config,
                            date_grouping=date_grouping,
                            result_df=result_df,
                        )
                        self.refresh_saved_agg_list()
                        self.status_bar.log(f"Saved aggregation: {agg_name}", "SUCCESS")
                    except ValueError as SaveAggregationDialogError:
                        QMessageBox.warning(
                            self, "Error", str(SaveAggregationDialogError)
                        )

                self.refresh_data_view()

                group_by_str = ", ".join(group_cols)

                self.status_bar.log_action(
                    f"Aggregated data by [{group_by_str}]",
                    details={
                        "group_by_columns": group_cols,
                        "agg_config": agg_config,
                        "date_grouping": date_grouping,
                        "result_rows": len(self.data_handler.df),
                        "operation": "aggregate",
                        "saved": bool(agg_name),
                    },
                    level="SUCCESS",
                )

                self.aggregate_animation = AggregationAnimation(
                    message="Aggregated Data"
                )
                self.aggregate_animation.start(self)
            except Exception as AggregationDialogError:
                QMessageBox.critical(self, "Error", str(AggregationDialogError))
                self.status_bar.log(
                    f"Aggregation failed: {str(AggregationDialogError)}", "ERROR"
                )

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
            print(
                f"Warning: Could not refresh aggregation list: {str(RefreshAggregationListError)}"
            )

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

            # storing state
            if (
                not hasattr(self.data_handler, "pre_agg_view_df")
                or self.data_handler.pre_agg_view_df is None
            ):
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
                    "operation": "view_saved_aggregation",
                },
                level="INFO",
            )
            QMessageBox.information(
                self,
                "Aggregation Loaded",
                f"Now viewing aggregation: {agg_name}\n\n"
                f"Rows: {len(agg_df):,}\n"
                f"Columns: {len(agg_df.columns)}\n\n"
                f"Click 'Reset to Original' to return to your full dataset.",
            )
        except Exception as ViewAggregationError:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to view aggregation:\n{str(ViewAggregationError)}",
            )
            traceback.print_exc()

    def delete_saved_aggregation(self):
        """Delete a saved aggregation"""
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
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.aggregation_manager.delete_aggregation(agg_name):
                self.refresh_saved_agg_list()
                self.view_agg_btn.setEnabled(False)
                self.delete_agg_btn.setEnabled(False)
                self.status_bar.log(f"Deleted aggregation: {agg_name}", "SUCCESS")

    def refresh_google_sheets_data(self):
        """Refresh data from the last imported Google Sheet document"""
        if not self.data_handler.has_google_sheets_import():
            QMessageBox.warning(self, "No Import History", "No Google Sheets import data found")
            return
        
        # Retrieve the stored information
        sheet_id = self.data_handler.last_gsheet_id
        sheet_name = self.data_handler.last_gsheet_name
        delimiter = self.data_handler.last_gsheet_delimiter
        decimal = self.data_handler.last_gsheet_decimal
        thousands = self.data_handler.last_gsheet_thousands
        gid = self.data_handler.last_gsheet_gid
        
        thousands_param = (None if thousands in [None, "None", ""] else thousands)
        
        self.progress_dialog = ProgressDialog(
            title="Refreshing Google Sheets data",
            message=f"Reconnecting to {sheet_id}",
            parent=self
        )
        self.progress_dialog.setModal(True)
        self.progress_dialog.show()
        
        self.rows_before_refresh = (len(self.data_handler.df) if self.data_handler.df is not None else 0)
        
        worker = GoogleSheetsImportWorker(
            self.data_handler,
            sheet_id,
            sheet_name,
            delimiter,
            decimal,
            thousands_param,
            gid
        )
        
        worker.signals.progress.connect(self.progress_dialog.update_progress)
        worker.signals.finished.connect(self.on_refresh_google_sheets_finished)
        worker.signals.error.connect(self.on_refresh_google_sheets_error)
        
        QThreadPool.globalInstance().start(worker)
        
    def on_refresh_google_sheets_finished(self, df):
        """Handle the successful refresh completion from worker"""
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()
        
        rows_after = len(df)
        rows_diff = rows_after - self.rows_before_refresh
        diff_text = f"+{rows_diff}" if rows_diff > 0 else str(rows_diff)
        
        self.refresh_data_view()
        
        sheet_identifier = self.data_handler.last_gsheet_name or f"GID: {self.data_handler.last_gsheet_gid}"
        
        self.status_bar.log_action(
            f"Refreshed Google Sheets data: {self.data_handler.last_gsheet_id}",
            details={
                "sheet_name": sheet_identifier,
                "sheet_id": self.data_handler.last_gsheet_id,
                "rows_before": self.rows_before_refresh,
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
            f"Sheet: {sheet_identifier}\n"
            f"Rows: {rows_after:,} ({diff_text})\n"
            f"Columns: {len(df.columns)}",
        )
    
    def on_refresh_google_sheets_error(self, error: Exception):
        """Handle refresh failure from worker"""
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()
        
        print(f"DEBUG: Refresh failed: {str(error)}")
        if hasattr(self, "status_bar"):
            self.status_bar.log(
                f"Failed to refresh Google Sheets Data: {str(error)}", "ERROR"
            )
        QMessageBox.critical(
        self,
        "Refresh Failed",
        f"Failed to refresh Google Sheets data:\n\n{str(error)}\n\n"
        "Please check:\n"
        "• Internet connection\n"
        "• Sheet is still shared publicly\n"
        "• Sheet name has not changed",
        )

    def open_melt_dialog(self):
        """Opens the melt data dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        dialog = MeltDialog(self.data_handler.df, self)

        if dialog.exec():
            config = dialog.get_config()
            try:
                reply = reply = QMessageBox.question(
                    self,
                    "Confirm Melt",
                    "Melting will restructure your entire dataset.\n\n"
                    "Are you sure you want to proceed?\n"
                    "(You can Undo this operation later)",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply == QMessageBox.StandardButton.Yes:
                    before_shape = self.data_handler.df.shape

                    self.data_handler.melt_data(
                        id_vars=config["id_vars"],
                        value_vars=config["value_vars"],
                        var_name=config["var_name"],
                        value_name=config["value_name"],
                    )

                    after_shape = self.data_handler.df.shape
                    self.refresh_data_view()

                    self.status_bar.log_action(
                        f"Melted data: {before_shape} -> {after_shape}",
                        details={
                            "id_vars": config["id_vars"],
                            "value_vars": config["value_vars"],
                            "shape_before": before_shape,
                            "shape_after": after_shape,
                            "operation": "melt",
                        },
                        level="SUCCESS",
                    )

                    self.melt_animation = MeltDataAnimation()
                    self.melt_animation.start(self)

            except Exception as MeltDataError:
                QMessageBox.critical(
                    self, "Error", f"Failed to melt data:\n{str(MeltDataError)}"
                )
                self.status_bar.log(f"Melt failed: {str(MeltDataError)}", "ERROR")
    
    def open_pivot_dialog(self):
        """Opens the pivot table dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No data", "Please load data first")
            return
        
        dialog = PivotDialog(self.data_handler.df, self)
        
        if dialog.exec():
            config = dialog.get_config()
            try:
                reply = QMessageBox.question(
                    self,
                    "Confirm Pivot",
                    "Pivoting will restructure your entire dataset.\n\n"
                    "Are you sure you want to proceed?\n",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    before_shape = self.data_handler.df.shape
                    
                    self.data_handler.pivot_data(index=config["index"], columns=config["columns"], values=config["values"], aggfunc=config["aggfunc"])
                    after_shape = self.data_handler.df.shape
                    self.refresh_data_view()
                    
                    self.status_bar.log_action(
                        f"Pivoted data: {before_shape} -> {after_shape}",
                        details={
                            "index": config["index"],
                            "columns": config["columns"],
                            "values": config["values"],
                            "aggfunc": config["aggfunc"],
                            "shape_before": before_shape,
                            "shape_after": after_shape,
                            "operation": "pivot",
                        },
                        level="SUCCESS"
                    )
                    self.aggregate_animation = AggregationAnimation(message="Pivoted Data")
                    self.aggregate_animation.start(self)
            except Exception as PivotDataError:
                QMessageBox.critical(self, "Error", f"Failed to pivot data:\n{str(PivotDataError)}")
                self.status_bar.log(f"Pivot Failed: {str(PivotDataError)}", "ERROR")
                print(PivotDataError)
    
    def open_merge_dialog(self):
        """Opens the dialog for merging data"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No data", "Please load data first")
            return
        
        dialog = MergeDialog(self.data_handler, self)
        
        if dialog.exec():
            config = dialog.get_config()
            try:
                rows_before = len(self.data_handler.df)
                
                self.data_handler.merge_data(
                    right_df=config["right_df"],
                    how=config["how"],
                    left_on=config["left_on"],
                    right_on=config["right_on"],
                    suffixes=config["suffixes"]
                )
                
                rows_after = len(self.data_handler.df)
                self.refresh_data_view()
                
                self.status_bar.log_action(
                    f"Merged data ({config["how"]})",
                    details={
                        "how": config["how"],
                        "rows_before": rows_before,
                        "rows_after": rows_after,
                        "operation": "merge"
                    },
                    level="SUCCESS"
                )
                self.merge_animation = FileImportAnimation(message="Data Merged")
                self.merge_animation.start(target_widget=self)
            except Exception as MergeError:
                QMessageBox.critical(self, "Merge Error", str(MergeError))
                self.status_bar.log(f"Merge failed: {str(MergeError)}", "ERROR")

    def open_binning_dialog(self):
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first.")
            return
        
        numeric_cols = self.data_handler.df.select_dtypes(include=["number"]).columns.tolist()
        
        if not numeric_cols:
            QMessageBox.warning(self, "No Numeric Data", "This dataset contains no numeric columns suitable for binning.")
            return
        
        dialog = BinningDialog(numeric_cols, parent=self)
        if dialog.exec():
            config = dialog.get_config()
            if config:
                try:
                    self.data_handler.bin_column(
                            column=config["column"],
                            new_column_name=config["new_column"],
                            method=config["method"],
                            bins=config["bins"],
                            labels=config["labels"]
                        )
                    self.refresh_data_view()
                    
                    method_display = "Quantile" if config["method"] == "qcut" else "Uniform/Custom"
                    bins_display = len(config["bins"]) - 1 if isinstance(config["bins"], list) else config["bins"]
                    
                    self.status_bar.log_action(
                        f"Binned '{config['column']}' -> '{config['new_column']}'",
                        details={
                                "source_column": config["column"],
                                "new_column": config["new_column"],
                                "method": method_display,
                                "bins": bins_display,
                                "operation": "bin_column"
                        },
                        level="SUCCESS")
                except Exception as BinError:
                    QMessageBox.critical(self, "Binning Error", f"Failed to bin column:\n{str(BinError)}")
                    self.status_bar.log(f"Binning failed: {str(BinError)}", "ERROR")
    
    def apply_sort(self):
        """Apply a permanent sorting to data"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No data", "Please load data first")
            return

        column = self.sort_column_combo.currentText()
        if not column:
            return

        ascending = self.sort_order_combo.currentText() == "Ascending"

        try:
            col_index = list(self.data_handler.df.columns).index(column)
            order = (
                Qt.SortOrder.AscendingOrder
                if ascending
                else Qt.SortOrder.DescendingOrder
            )

            self.data_table.sortByColumn(col_index, order)
            self.refresh_data_view(reload_model=False)

            direction = "ascending" if ascending else "descending"
            self.status_bar.log_action(
                f"Sorted data by '{column}' ({direction})",
                details={"column": column, "direction": direction, "operation": "sort"},
                level="SUCCESS",
            )
        except ValueError:
            pass
        except Exception as SortError:
            self.status_bar.log(f"Sort failed: {str(SortError)}", "ERROR")
            QMessageBox.critical(self, "Error", str(SortError))

    def clear(self):
        """Clear the data tab"""
        self.data_table.setModel(None)
        self.stats_text.clear()

        self.data_source_refresh_button.setVisible(False)
        self.status_bar.set_data_source("")
        self.status_bar.set_view_contex("", "normal")

    @pyqtSlot(str)
    def show_help_dialog(self, topic_id: str):
        try:
            title, description, link = self.help_manager.get_help_topic(topic_id)

            if title:
                dialog = HelpDialog(self, topic_id, title, description, link)
                dialog.exec()
            else:
                QMessageBox.warning(
                    self,
                    "Help not found",
                    f"No help topic could be found for '{topic_id}'",
                )
        except Exception as ShowHelpDialogError:
            self.status_bar.log(
                f"Error displaying help dialog: {str(ShowHelpDialogError)}", "ERROR"
            )
            QMessageBox.critical(
                self, "Help Error", "Could not load help content. See log for details"
            )
            traceback.print_exc()

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
            self.status_bar.log(f"Failed to go to state: {str(HistoryError)}", "ERROR")

    def _format_operation_text(self, operation: dict) -> str:
        """Formatter for operation dict back to better text handling"""
        operation_type = operation.get("type", "Unknown")

        match operation_type:
            case "filter":
                return f"Filter: {operation.get('column')} {operation.get('condition')} '{operation.get('value')}'"
            case "drop_column":
                return f"Drop Column: {operation.get('column')}"
            case "rename_column":
                return f"Rename: {operation.get('old_name')} -> {operation.get('new_name')}"
            case "change_data_type":
                return f"Data type change: {operation.get('column')} -> {operation.get('new_type')}"
            case "fill_missing":
                return f"Fill missing Values: {operation.get('column')} ({operation.get('method')})"
            case "drop_missing":
                return "Drop missing Values"
            case "drop_duplicates":
                return "Remove Duplicate Values"
            case "aggregate":
                if "agg_func" in operation:
                    return f"Aggregation: {operation.get('agg_func')} on {len(operation.get('agg_columns', []))} columns"
                else:
                    return f"Aggregation: Grouped by {len(operation.get('group_by', []))} cols"
            case "melt":
                return "Melt/Pivot Data"
            case "sort":
                direction = "Asc" if operation.get("ascending") else "Desc"
                return f"Sort: {operation.get('column')} ({direction})"
            case _:
                return f"{operation_type.replace('_', ' ').title()}"

    def open_outlier_dialog(self, method):
        """Opens the outleier detection dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return

        dialog = OutlierDetectionDialog(self.data_handler, method, self)
        if dialog.exec():
            self.outlier_animation = OutlierDetectionAnimation(method_name=method)
            self.outlier_animation.start(target_widget=self)
            rows_removed = len(dialog.outlier_indices)
            self.refresh_data_view()
            self.status_bar.log_action(
                f"Removed {rows_removed} outliers using {method}",
                details={
                    "method": method,
                    "count": rows_removed,
                    "operation": "remove_outliers",
                },
                level="SUCCESS",
            )

    def show_table_context_menu(self, position):
        """Shows the context menu for the data table"""
        if self.data_handler.df is None:
            return

        menu = QMenu()

        resize_cols_action = menu.addAction("Resize Columns to Contents")
        resize_rows_action = menu.addAction("Resize Rows to Contents")
        menu.addSeparator()

        grid_action = QAction("Show Grid", menu)
        grid_action.setCheckable(True)
        grid_action.setChecked(self.data_table.showGrid())
        grid_action.triggered.connect(
            lambda: self.data_table.setShowGrid(grid_action.isChecked())
        )
        menu.addAction(grid_action)

        alt_rows_action = QAction("Alternating Colors", menu)
        alt_rows_action.setCheckable(True)
        alt_rows_action.setChecked(self.data_table.alternatingRowColors())
        alt_rows_action.triggered.connect(
            lambda: self.data_table.setAlternatingRowColors(alt_rows_action.isChecked())
        )
        menu.addAction(alt_rows_action)

        menu.addSeparator()
        settings_action = menu.addAction("Table Settings...")

        action = menu.exec(self.data_table.viewport().mapToGlobal(position))

        if action == resize_cols_action:
            self.data_table.resizeColumnsToContents()
        elif action == resize_rows_action:
            self.data_table.resizeRowsToContents()
        elif action == settings_action:
            self.open_table_customization()

    def open_table_customization(self):
        """Opens the settings dialog for the table customzation"""
        if self.data_handler.df is None:
            return

        # Get the current settings
        current_font = self.data_table.font()
        current_font_size = current_font.pointSize()
        if current_font_size <= 0:
            current_font_size = 10

        current_alt_color = (
            self.data_table.palette().color(QPalette.ColorRole.AlternateBase).name()
        )

        current_settings = {
            "alternating_rows": self.data_table.alternatingRowColors(),
            "alt_color": current_alt_color,
            "show_grid": self.data_table.showGrid(),
            "show_h_headers": self.data_table.horizontalHeader().isVisible(),
            "show_v_headers": self.data_table.verticalHeader().isVisible(),
            "font_family": current_font.family(),
            "font_size": current_font_size,
            "word_wrap": self.data_table.wordWrap(),
            "selection_behavio": self.data_table.selectionBehavior(),
            "float_precision": self.current_precision,
            "conditional_rules": self.current_formatting_rules
        }

        dialog = TableCustomizationDialog(current_settings, self)
        if dialog.exec():
            settings = dialog.get_settings()
            
            self.current_precision = settings.get("float_precision", 2)
            self.current_formatting_rules = settings.get("conditional_rules", [])

            self.data_table.setAlternatingRowColors(settings["alternating_rows"])
            if settings["alternating_rows"]:
                palette = self.data_table.palette()
                palette.setColor(
                    QPalette.ColorRole.AlternateBase, QColor(settings["alt_color"])
                )
                self.data_table.setPalette(palette)
            self.data_table.setShowGrid(settings["show_grid"])

            self.data_table.horizontalHeader().setVisible(settings["show_h_header"])
            self.data_table.verticalHeader().setVisible(settings["show_v_header"])

            font = QFont(settings["font_family"])
            font.setPointSize(settings["font_size"])
            self.data_table.setFont(font)

            self.data_table.setWordWrap(settings["word_wrap"])
            self.data_table.setSelectionBehavior(settings["selection_behavior"])

            self.data_table.resizeRowsToContents()
            if settings["word_wrap"]:
                self.data_table.resizeColumnsToContents()
            
            if self.data_table.model() and isinstance(self.data_table.model(), DataTableModel):
                self.data_table.model().set_float_precision(self.current_precision)
                self.data_table.model().set_conditional_rules(self.current_formatting_rules)

            self.status_bar.log("Table settings updated", "SUCCESS")

    def get_selection_state(self):
        """Returns the currently selected row indicies and column names"""
        if self.data_table is None or self.data_table.selectionModel() is None:
            return [], []
        
        indexes = self.data_table.selectionModel().selectedIndexes()
        if not indexes:
            return [], []
        
        selected_rows = sorted(list(set(index.row() for index in indexes)))
        if self.data_handler.df is not None:
            col_indices = sorted(list(set(index.column() for index in indexes)))
            selected_columns = []
            for i in col_indices:
                if i < len(self.data_handler.df.columns):
                    selected_columns.append(self.data_handler.df.columns[i])
        else:
            selected_columns = []
        
        return selected_rows, selected_columns