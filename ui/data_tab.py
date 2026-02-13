# ui/data_tab.py
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QMessageBox,
    QTextEdit,
    QInputDialog,
    QListWidgetItem,
    QTableView,
    QHeaderView,
    QGraphicsOpacityEffect,
    QMenu,
    QDialog,
    QStackedWidget,
)
from PyQt6.QtCore import (
    Qt,
    QPropertyAnimation,
    QEasingCurve,
    pyqtSignal
)
from PyQt6.QtGui import QIcon, QFont, QAction, QPalette, QColor, QShortcut, QKeySequence
import numpy as np

from core.data_handler import DataHandler
from core.resource_loader import get_resource_path
from ui.status_bar import StatusBar
from ui.dialogs import (
    TableCustomizationDialog,
    SearchResultsDialog
)
from core.subset_manager import SubsetManager
from pathlib import Path

from ui.data_table_model import DataTableModel
from ui.widgets import (
    DataPlotStudioButton,
    DataPlotStudioTabWidget
)
from ui.components.data_operations_panel import DataOperationsPanel
from ui.components.statistics_generator import StatisticsGenerator
from ui.LandingPage import LandingPage

from ui.animations import (
    EditModeToggleAnimation
)
from ui.controllers.data_tab_controller import DataTabController


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
        self.controller = DataTabController(data_handler=self.data_handler, status_bar=self.status_bar, view=self, subset_manager=self.subset_manager)
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
        self.landing_page.new_dataset_clicked.connect(self.controller.create_new_dataset)
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
        self.create_new_dataset_button.clicked.connect(self.controller.create_new_dataset)
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
        self.data_source_refresh_button.clicked.connect(self.controller.refresh_google_sheets)
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
        
        self.test_results_text = QTextEdit()
        self.test_results_text.setReadOnly(True)
        self.set_test_results_greeting()
        test_result_icon = QIcon(get_resource_path("icons/data_operations/calculator.svg"))
        self.data_tabs.addTab(self.test_results_text, test_result_icon, "Test Results")

        data_view_layout.addWidget(self.data_tabs, 1)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.operations_panel = DataOperationsPanel(parent=self, controller=self.controller)

        right_layout.addWidget(self.operations_panel)

        # Create splitter
        from PyQt6.QtWidgets import QSplitter

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

        self.refresh_data_view()


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

        if not df.empty:
            # Convert all data to strings
            # 
            df_str = df.astype(str)
            mask = df_str.apply(lambda col: col.str.contains(search_text_lower, case=False, regex=False)).to_numpy()
            
            row_indices, col_indices = np.where(mask)
            
            if len(row_indices) > 0:
                matched_cols = df.columns[col_indices]
                matched_values = df_str.to_numpy()[row_indices, col_indices]
                
                matches = list(zip(
                    row_indices.tolist(),
                    col_indices.tolist(),
                    matched_cols.tolist(),
                    matched_values.tolist()
                ))

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

    def refresh_data_view(self, reload_model: bool = True):
        """Refresh the data table and statistics"""
        if self.data_handler.df is None:
            self._handle_empty_data_view()
            return
        
        if hasattr(self, "left_stack"):
            self.left_stack.setCurrentIndex(1)
        
        # UI updaters
        self._update_data_model(reload_model)
        self._update_edit_triggers()
        self._update_column_selectors()
        self.update_statistics()
        self._update_data_source_status()
        self._update_subsets_status()
        self._update_history_list()
        
        self.status_bar.log(f"Data loaded: {self.data_handler.df.shape[0]} rows, {self.data_handler.df.shape[1]} columns")
    
    def _handle_empty_data_view(self) -> None:
        """Clears the UI when no data is loaded"""
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
    
    def _update_data_model(self, reload_model: bool) -> None:
        """Updates the table model and restores sorting states"""
        if not reload_model:
            return
        
        df = self.data_handler.df
        self.model = DataTableModel(self.data_handler, editable=self.is_editing, float_precision=self.current_precision, conditional_rules=self.current_formatting_rules)
        self.data_table.setSortingEnabled(False)
        self.data_table.setModel(self.model)
        
        header = self.data_table.horizontalHeader()
        header.blockSignals(True)
        
        if self.data_handler.sort_state:
            col_name, ascending = self.data_handler.sort_state
            try:
                col_index = list(df.columns).index(col_name)
                order = (Qt.SortOrder.AscendingOrder if ascending else Qt.SortOrder.DescendingOrder)
                header.setSortIndicator(col_index, order)
            except ValueError:
                header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        else:
            header.setSortIndicator(-1, Qt.SortOrder.AscendingOrder)
        
        header.blockSignals(False)
        self.data_table.setSortingEnabled(True)
    
    def _update_edit_triggers(self) -> None:
        """Sets the table edit triggers based on the editing state"""
        if self.is_editing:
            self.data_table.setEditTriggers(QTableView.EditTrigger.DoubleClicked | QTableView.EditTrigger.AnyKeyPressed)
        else:
            self.data_table.setEditTriggers(QTableView.EditTrigger.NoEditTriggers)
            
    def _update_column_selectors(self) -> None:
        """Updates column selection boxes"""
        df = self.data_handler.df
        columns = list(df.columns)
        panel = self.operations_panel
        
        panel.filter_column.clear()
        panel.filter_column.addItems(columns)
        panel.column_list.clear()
        panel.column_list.addItems(columns)
        
        if hasattr(panel, "sort_column_combo"):
            current_sort = panel.sort_column_combo.currentText()
            panel.sort_column_combo.clear()
            panel.sort_column_combo.addItems(columns)
            if current_sort and current_sort in columns:
                panel.sort_column_combo.setCurrentText(current_sort)
            elif (self.data_handler.sort_state and self.data_handler.sort_state[0] in columns):
                panel.sort_column_combo.setCurrentText(self.data_handler.sort_state[0])
        
        if hasattr(panel, "subset_column_combo"):
            try:
                panel.subset_column_combo.clear()
                panel.subset_column_combo.addItems(columns)
            except Exception as Error:
                print(f"Warning: Could not update subset columns: {str(Error)}")
        
        if self.plot_tab:
            self.plot_tab.update_column_combo()
    
    def _update_data_source_status(self) -> None:
        """Updates the status bar and refreshes butotns based on datat source"""
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
            
            self.status_bar.set_data_source(f"Local File: {file_name}")
            self.data_source_refresh_button.setVisible(False)
        else:
            self.status_bar.set_data_source("New")
            self.data_source_refresh_button.setVisible(False)
    
    def _update_subsets_status(self) -> None:
        """Refreshes subset info and updates status bar"""
        try:
            if hasattr(self, "subset_manager"):
                self.subset_manager.clear_cache()
            if hasattr(self, "active_subsets_list"):
                self.controller.refresh_active_subsets()
        except Exception as Error:
            print(f"Warning: Could not refresh subsets: {Error}")
        
        inserted_name = getattr(self.data_handler, "inserted_subset_name", None)
        agg_name = getattr(self.data_handler, "viewing_aggregation_name", None)
        
        if agg_name:
            self.status_bar.set_view_contex(f"Viewing Aggregation: {agg_name}")
        elif inserted_name:
            self.status_bar.set_view_contex(f"Viewing Subset: {inserted_name}")
    
    def _update_history_list(self) -> None:
        """Updates the history list"""
        panel = self.operations_panel
        if not hasattr(panel, "history_list"):
            return
        
        panel.history_list.clear()
        
        history_information = self.data_handler.get_history_info()
        history_operations = history_information["history"]
        current_index = history_information["current_index"]
        
        initial_item = QListWidgetItem("0. Initial Data")
        initial_item.setData(Qt.ItemDataRole.UserRole, 0)
        
        if current_index == 0:
            initial_item.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            initial_item.setForeground(Qt.GlobalColor.black)
            initial_item.setIcon(QIcon(get_resource_path("icons/ui_styling/checkmark.png")))
        
        panel.history_list.addItem(initial_item)
        
        for i, operation in enumerate(history_operations):
            history_index = i + 1
            operation_text = self._format_operation_text(operation)
            item = QListWidgetItem(f"{history_index}. {operation_text}")
            item.setData(Qt.ItemDataRole.UserRole, history_index)
            
            if history_index == current_index:
                item.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
                item.setForeground(Qt.GlobalColor.black)
                item.setIcon(QIcon(get_resource_path("icons/ui_styling/checkmark.png")))
                item.setBackground(Qt.GlobalColor.white)
            elif history_index > current_index:
                item.setForeground(Qt.GlobalColor.gray)
                font = item.font()
                font.setItalic(True)
                item.setFont(font)
            
            panel.history_list.addItem(item)
        
        if panel.history_list.count() > 0:
            panel.history_list.scrollToItem(panel.history_list.item(current_index))

    def get_subset_manager(self):
        """
        DEPRECATED: Use self.subset_manager directly.
        Return the subset manager instance
        """
        # This function is no longer needed as subset_manager is passed in
        return self.subset_manager

    def switch_to_plot_tab(self):
        """Helper to swtich to the plot tab"""
        current_widget = self.parentWidget()
        found_tab_widget = False
        while current_widget:
            if isinstance(current_widget, DataPlotStudioTabWidget):
                current_widget.setCurrentWidget(self.plot_tab)
                found_tab_widget = True
                break
            current_widget = current_widget.parentWidget()
        if not found_tab_widget:
            self.status_bar.log("Could not switch to plot tab: Tab Widget not found", "WARNING")

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

    def clear(self):
        """Clear the data tab"""
        self.data_table.setModel(None)
        self.stats_text.clear()
        if hasattr(self, "test_results_text"):
            self.set_test_results_greeting()

        self.data_source_refresh_button.setVisible(False)
        self.status_bar.set_data_source("")
        self.status_bar.set_view_contex("", "normal")

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
        stats_test_action = menu.addAction("Run Statistical Test...")

        action = menu.exec(self.data_table.viewport().mapToGlobal(position))

        if action == resize_cols_action:
            self.data_table.resizeColumnsToContents()
        elif action == resize_rows_action:
            self.data_table.resizeRowsToContents()
        elif action == settings_action:
            self.open_table_customization()
        elif action == stats_test_action:
            self.controller.run_statistical_test_from_selection()

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
    
    def set_test_results_greeting(self):
        """Sets the initial instructions for the Test Results tab"""
        greeting_html = """
        <div style='padding: 20px; text-align: center; color: #34495e; font-family: sans-serif;'>
            <h2 style='color: #2c3e50; margin-bottom: 10px;'>Statistical Test Suite</h2>
            <p style='font-size: 14px; margin-bottom: 20px;'>Welcome to the DataPlotStudio Statistical Test Results panel</p>
            <div style='background-color: #ecf0f1; border-radius: 8px; padding: 15px; text-align: left; display: inline-block; border-left: 5px solid #3498db;'>
                <h4 style='margin-top: 0; color: #2980b9;'>How to run a statistical test:</h4>
                <ol style='margin-bottom: 0; padding-left: 20px;'>
                    <li style='margin-bottom: 8px;'>Go to the <b>Data Table</b> tab.</li>
                    <li style='margin-bottom: 8px;'><b>Right-click</b> to open the context menu.</li>
                    <li style='margin-bottom: 8px;'>Select the <b>Table Settings...</b> option.</li>
                    <li style='margin-bottom: 8px;'>Select the <b>Behavior</b> option.</li>
                    <li style='margin-bottom: 8px;'>Under <b>Selection Behavior</b> choose the <b>Select columns</b> option.</li>
                    <li style='margin-bottom: 8px;'>Return to the table.</li>
                    <li style='margin-bottom: 8px;'>Select exactly <b>two numeric columns</b>.</li>
                    <li style='margin-bottom: 8px;'><b>Right-click</b> on the table to open the context menu.</li>
                    <li>Select <b>Run Statistical Test...</b> and choose your desired test.</li>
                </ol>
            </div>
            <p style='margin-top: 20px; font-size: 13px; color: #7f8c8d;'>Your test results and interpretations will appear here.</p>
        </div>
        """
        if hasattr(self, 'test_results_text') and self.test_results_text is not None:
            self.test_results_text.setHtml(greeting_html)