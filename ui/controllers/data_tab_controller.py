import traceback
from typing import TYPE_CHECKING
import weakref

from PyQt6.QtWidgets import (
    QMessageBox,
    QInputDialog,
    QListWidgetItem
)
from PyQt6.QtCore import Qt, QThreadPool
from duckdb import duplicate
from xlrd import colname

from core.data_handler import DataHandler
from core.aggregation_manager import AggregationManager
from core.help_manager import HelpManager
from core.subset_manager import SubsetManager

from ui.animations import (
    AggregationAnimation,
    DataFilterAnimation,
    DataTypeChangeAnimation,
    DropColumnAnimation,
    MeltDataAnimation,
    OutlierDetectionAnimation,
    RenameColumnAnimation,
    DropMissingValueAnimation,
    FillMissingValuesAnimation,
    RemoveRowAnimation,
    ResetToOriginalStateAnimation,
    FailedAnimation,
    NewDataFrameAnimation,
    FileImportAnimation
)
from ui.dialogs import (
    RenameColumnDialog,
    FilterAdvancedDialog,
    AggregationDialog,
    FillMissingDialog,
    HelpDialog,
    MeltDialog,
    OutlierDetectionDialog,
    PivotDialog,
    MergeDialog,
    BinningDialog,
    ComputedColumnDialog,
    SubsetDataViewer,
    SubsetManagerDialog,
    ProgressDialog,
    SplitColumnDialog,
    RegexReplaceDialog
)
from ui.workers import GoogleSheetsImportWorker

if TYPE_CHECKING:
    from ui.data_tab import DataTab
    from ui.status_bar import StatusBar

class DataTabController:
    """
    Controller for the DataTab\n
    Handles data operations, dialogs and updating the data view.
    """
    
    def __init__(self, data_handler: DataHandler, status_bar: "StatusBar", view: "DataTab", subset_manager: SubsetManager):
        self.data_handler = data_handler
        self.status_bar = status_bar
        self._view = weakref.ref(view)
        self.subset_manager = subset_manager
        
        # Managers
        self.aggregation_manager = AggregationManager()
        self.help_manager = HelpManager()
        
        self.rows_before_refresh = 0
        
    @property
    def view(self) -> "DataTab":
        return self._view()
    
    def create_new_dataset(self):
        """Creates a new empty dataset"""
        try:
            rows, ok = QInputDialog.getInt(
                self.view, "New Dataset", "Number of Rows:", 10, 1, 1000000
            )
            if not ok:
                return
            
            columns, ok = QInputDialog.getInt(
                self.view, "New Dataset", "Number of Columns:", 3, 1, 1000
            )
            if not ok:
                return
            
            confirm = QMessageBox.question(
                self.view,
                "Confirm Create",
                "This will clear the current dataset and create a new empty dataset. Continue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if confirm == QMessageBox.StandardButton.Yes:
                self.data_handler.create_empty_dataframe(rows, columns)
                self.view.refresh_data_view()
                self.status_bar.log(f"Created new dataset: ({rows}x{columns})", "SUCCESS")
                
                NewDataFrameAnimation(parent=None, message="Created New Dataframe").start(target_widget=self.view)
            
        except Exception as CreateNewDatasetError:
            QMessageBox.critical(
                self.view, "Error", f"Failed to create dataset: {str(CreateNewDatasetError)}"
            )
            FailedAnimation("Failed to Create", parent=None).start(target_widget=self.view)
    
    def refresh_google_sheets(self):
        """Refreshes data from the last imported google sheets document"""
        if not self.data_handler.has_google_sheets_import():
            QMessageBox.warning(self, "No Import History", "No Google Sheets import data found")
            return
        
        sheet_id = self.data_handler.last_gsheet_id
        sheet_name = self.data_handler.last_gsheet_name
        delimiter = self.data_handler.last_gsheet_delimiter
        decimal = self.data_handler.last_gsheet_decimal
        thousands = self.data_handler.last_gsheet_thousands
        gid = self.data_handler.last_gsheet_gid
        
        thousands_param = (None if thousands in [None, "None", ""] else thousands)
        
        self.progress_dialog = ProgressDialog(
            title="Refreshing Google Sheets Data",
            message=f"Reconnecting to {sheet_id}",
            parent=self.view
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
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()
        
        rows_after = len(df)
        rows_diff = rows_after - self.rows_before_refresh
        diff_text = f"+{rows_diff}" if rows_diff > 0 else str(rows_diff)
        
        self.view.refresh_data_view()
        
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
            self.view,
            "Refresh Complete",
            f"Google Sheets data refreshed successfully\n\n"
            f"Sheet: {sheet_identifier}\n"
            f"Rows: {rows_after:,} ({diff_text})\n"
            f"Columns: {len(df.columns)}"
        )
    
    def on_refresh_google_sheets_error(self, error: Exception):
        if hasattr(self, "progress_dialog"):
            self.progress_dialog.close()
        
        if hasattr(self, "status_bar"):
            self.status_bar.log(f"Failed to refresh Google Sheets data: {str(error)}", "ERROR")
        QMessageBox.critical(
            self.view,
            f"Failed to refresh Google Sheets data:\n\n{str(error)}\n\n"
            "Please check:\n"
            "• Internet connection\n"
            "• Sheet is still shared publicly\n"
            "• Sheet name has not changed",
        )
        
    def remove_duplicates(self) -> None:
        """Remove duplicate rows"""
        if self.data_handler.df is None: return
        if getattr(self, "_preview_msg_box", None) is not None:
            self._preview_msg_box.close()
        try:
            df = self.data_handler.df
            
            duplicate_indices = set(i for i, is_dup in enumerate(df.duplicated(keep="first")) if is_dup)
            
            if not duplicate_indices:
                QMessageBox.information(self.view, "No Duplicates", "No duplicate rows found in the dataset.")
                return
            
            if self.view.data_table.model() is not None:
                self.view.data_table.model().set_highlighted_rows(duplicate_indices)
            
            self._preview_msg_box = QMessageBox(self.view)
            self._preview_msg_box.setIcon(QMessageBox.Icon.Question)
            self._preview_msg_box.setWindowTitle("Confirm Removal")
            self._preview_msg_box.setText(f"Found {len(duplicate_indices)} duplicate row(s) (highlighted in red)\nReview the table, then choose whether to remove or keep them.")
            self._preview_msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            self._preview_msg_box.setWindowModality(Qt.WindowModality.NonModal)
            
            def handle_response(button):
                if self.view.data_table.model() is not None:
                    self.view.data_table.model().set_highlighted_rows(set())
                
                if self._preview_msg_box.standardButton(button) == QMessageBox.StandardButton.Yes:
                    self._execute_remove_duplicates()
                else:
                    self.status_bar.log("Remove duplicates operation cancelled.", "INFO")
                
                self._preview_msg_box.deleteLater()
                self._preview_msg_box = None
            
            self._preview_msg_box.buttonClicked.connect(handle_response)
            self._preview_msg_box.show()
            
        except Exception as RemoveDuplicatesError:
            self.status_bar.log(f"Failed to prepare duplicate preview {str(RemoveDuplicatesError)}", "ERROR")
    
    def _execute_remove_duplicates(self) -> None:
        try:
            before = len(self.data_handler.df)
            self.data_handler.clean_data("drop_duplicates")
            after = len(self.data_handler.df)
            removed = before - after

            self.view.refresh_data_view()

            self.remove_rows_animation = RemoveRowAnimation(message="Removed Rows")
            self.remove_rows_animation.start(target_widget=self.view)

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
            self.failed_animation.start(target_widget=self.view)
    
    def drop_missing(self):
        """Drop rows with missing values"""
        if self.data_handler.df is None: return
        if getattr(self, "_preview_msg_box", None) is not None:
            self._preview_msg_box.close()
        try:
            df = self.data_handler.df
            
            missing_indices = set(i for i, has_missing in enumerate(df.isnull().any(axis=1)) if has_missing)
            
            if not missing_indices:
                QMessageBox.information(self.view, "No Missing Values", "No rows with missing values found in the dataset.")
                return
            if self.view.data_table.model() is not None:
                self.view.data_table.model().set_highlighted_rows(missing_indices)
            
            self._preview_msg_box = QMessageBox(self.view)
            self._preview_msg_box.setIcon(QMessageBox.Icon.Question)
            self._preview_msg_box.setWindowTitle("Confirm Removal")
            self._preview_msg_box.setText(f"Found {len(missing_indices)} row(s) with missing values (highlighted in red).\nReview the table, then choose whether to remove them.")
            self._preview_msg_box.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            self._preview_msg_box.setWindowModality(Qt.WindowModality.NonModal)
            
            def handle_response(button):
                if self.view.data_table.model() is not None:
                    self.view.data_table.model().set_highlighted_rows(set())
                    
                if self._preview_msg_box.standardButton(button) == QMessageBox.StandardButton.Yes:
                    self._execute_drop_missing()
                else:
                    self.status_bar.log("Drop missing values operation cancelled.", "INFO")
                
                self._preview_msg_box.deleteLater()
                self._preview_msg_box = None

            self._preview_msg_box.buttonClicked.connect(handle_response)
            self._preview_msg_box.show()
            
        except Exception as DropMissingError:
            self.status_bar.log(f"Failed to prepare missing values preview: {str(DropMissingError)}", "ERROR")
    
    def _execute_drop_missing(self) -> None:
        try:
            before = len(self.data_handler.df)
            self.data_handler.clean_data("drop_missing")
            after = len(self.data_handler.df)
            removed = before - after

            self.view.refresh_data_view()

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
            ).start(target_widget=self.view)
        except Exception as DropMissingError:
            self.status_bar.log(
                f"Failed to drop missing values: {str(DropMissingError)}", "ERROR"
            )
            self.failed_animation = FailedAnimation("Failed to Drop Missing values").start(target_widget=self.view)
            
    def fill_missing(self):
        """Fill missing values"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first")
            return

        try:
            columns = list(self.data_handler.df.columns)
            dialog = FillMissingDialog(columns, df=self.data_handler.df, parent=self.view)

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

                self.view.refresh_data_view()
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
                self.fill_missing_animation.start(target_widget=self.view)
        except Exception as FillMissingValuesError:
            self.status_bar.log(
                f"Failed to execute 'Fill Missing values': {str(FillMissingValuesError)}",
                "ERROR",
            )
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to execute 'Fill Missing Values':\n{str(FillMissingValuesError)}",
            )
    
    def open_outlier_dialog(self, method):
        """Opens the outlier detection dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first")
            return

        dialog = OutlierDetectionDialog(self.data_handler, method, self.view)
        if dialog.exec():
            self.outlier_animation = OutlierDetectionAnimation(method_name=method)
            self.outlier_animation.start(target_widget=self.view)
            rows_removed = len(dialog.outlier_indices)
            self.view.refresh_data_view()
            self.status_bar.log_action(
                f"Removed {rows_removed} outliers using {method}",
                details={
                    "method": method,
                    "count": rows_removed,
                    "operation": "remove_outliers",
                },
                level="SUCCESS",
            )
    
    def apply_normalization(self) -> None:
        """Apply the selected normalization method to the selected colymn"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first.")
            return
        
        selected_columns = self.view.operations_panel.get_selected_columns()
        if not selected_columns:
            self.status_bar.log("No columns selected for normalization", "WARNING")
            QMessageBox.warning(self.view, "Selection Error", "Please Select at least one column from the table to normalize")
            return
        
        method_display = self.view.operations_panel.get_normalization_method()
        if method_display.startswith("Min-Max"):
            method = "min_max"
        elif method_display.startswith("Standard"):
            method = "standard"
        elif method_display.startswith("Median"):
            method = "quantile"
        else:
            method = "min_max"
        try:
            self.data_handler.clean_data("normalize", columns=selected_columns, method=method)
            self.view.refresh_data_view()
            self.status_bar.log_action(
                f"Applied {method_display} to {len(selected_columns)} column(s)",
                details={
                    "columns": selected_columns,
                    "method": method,
                    "operation": "normalize_data"
                },
                level="SUCCESS"
            )
            QMessageBox.information(
                self.view,
                "Success",
                f"Successfully applied {method_display} to:\n{', '.join(selected_columns)}"
            )
        except TypeError as type_err:
            self.status_bar.log(f"Normalization type error: {str(type_err)}", "ERROR")
            QMessageBox.critical(self.view, "Type Error", str(type_err))
        except Exception as NormError:
            self.status_bar.log(f"Normalization failed: {str(NormError)}", "ERROR")
            QMessageBox.critical(self.view, "Normalization Error", f"Failed to normalize data:\n{str(NormError)}")
    def apply_filter(self):
        """Apply filter to data"""
        try:
            # Accessing widgets from the view's operations panel
            column, condition, value = self.view.operations_panel.get_filter_parameters()

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

            self.view.refresh_data_view()

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
            self.filter_animation.start(target_widget=self.view)

        except Exception as ApplyFilterError:
            self.status_bar.log(
                f"Failed to execute 'Filter': {str(ApplyFilterError)}", "ERROR"
            )

    def clear_filters(self):
        """Clear filters by resetting the data to original state"""
        if self.data_handler.df is None:
            return

        self.reset_data()
        self.status_bar.log("Filters cleared and data reset to original state", "INFO")

    def open_advanced_filter(self):
        """Open advanced filter dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "Warning", "No data loaded")
            return
        
        dialog = FilterAdvancedDialog(self.data_handler, self.view)
        if dialog.exec():
            result = dialog.get_filters()
            filters = result.get("filters", [])
            
            if not filters:
                return
            
            try:
                self.data_handler.filter_data(advanced_filters=filters)
                
                self.view.refresh_data_view()
                self.status_bar.log(f"Filters applied to data: {filters}")
            except Exception as FilterError:
                QMessageBox.critical(self.view, "Filter Error", f"Error applying filter:\n{str(FilterError)}")

    def drop_column(self):
        """Drop selected column"""
        if self.data_handler.df is None:
            return

        cols_to_drop = self.view.operations_panel.get_selected_columns()
        if not cols_to_drop:
            self.status_bar.log("No columns selected to drop", "WARNING")
            QMessageBox.warning(
                self.view, "Selection Error", "Please select at least one column to drop"
            )
            return

        msg = f"Are you sure you want to drop {len(cols_to_drop)} column(s)?\n\n"
        msg += ", ".join(cols_to_drop[:5])
        if len(cols_to_drop) > 5:
            msg += "..."

        confirm = QMessageBox.question(
            self.view,
            "Confirm Drop",
            msg,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if confirm == QMessageBox.StandardButton.Yes:
            try:
                cols_before = len(self.data_handler.df.columns)
                self.data_handler.clean_data("drop_column", columns=cols_to_drop)

                cols_after = len(self.data_handler.df.columns)
                self.view.refresh_data_view()

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
                self.drop_column_animation.start(target_widget=self.view)
            except Exception as DropColumnError:
                self.status_bar.log(
                    f"Failed to drop columns: {str(DropColumnError)}", "ERROR"
                )
                QMessageBox.critical(
                    self.view, "Error", f"Failed to drop columns: {str(DropColumnError)}"
                )

    def rename_column(self):
        """Rename selected column"""
        selected_columns = self.view.operations_panel.get_selected_columns()

        if not selected_columns:
            self.status_bar.log("No column selected", "WARNING")
            return

        old_name = selected_columns[0]
        
        existing_columns = self.data_handler.df.columns.tolist() if self.data_handler.df is not None else []
        dialog = RenameColumnDialog(old_name, existing_columns=existing_columns, parent=self.view)
        if dialog.exec():
            new_name = dialog.get_new_name()
            try:
                self.data_handler.clean_data(
                    "rename_column", old_name=old_name, new_name=new_name
                )

                self.view.refresh_data_view()
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
                self.rename_column_animation.start(self.view)
            except Exception as RenameColumnError:
                self.status_bar.log(
                    f"Failed to rename column: {str(RenameColumnError)}", "ERROR"
                )
    
    def duplicate_column(self) -> None:
        """Duplicate the selected column"""
        selected_columns = self.view.operations_panel.get_selected_columns()
        
        if not selected_columns:
            self.status_bar.log("No column selected", "WARNING")
            return
        if len(selected_columns) > 1:
            QMessageBox.warning(self.view, "Selection Error", "Please select only one column to duplicate")
            return
        
        col_name = selected_columns[0]
        new_col_name = f"{col_name}_copy"
        
        counter = 1
        while new_col_name in self.data_handler.df.columns:
            new_col_name = f"{col_name}_copy_{counter}"
            counter += 1
        
        try:
            self.data_handler.clean_data("duplicate_column", column=col_name, new_column=new_col_name)
            self.view.refresh_data_view()
            self.status_bar.log_action(f"Duplicated '{col_name}' to '{new_col_name}'", details={"original_column": col_name, "new_column": new_col_name, "operation": "duplicate_column"}, level="SUCCESS")
        except Exception as DuplicateColumnError:
            self.status_bar.log(f"Failed to duplicate column: {str(DuplicateColumnError)}", "ERROR")
            QMessageBox.critical(self.view, "Error", f"Failed to duplicate column: {str(DuplicateColumnError)}")

    def open_computed_column_dialog(self):
        """Opens the dialog to create a new column from a formula"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first")
            return

        columns = list(self.data_handler.df.columns)
        dialog = ComputedColumnDialog(columns, self.view)

        if dialog.exec():
            new_column, expression = dialog.get_data()
            try:
                self.data_handler.create_computed_column(new_column, expression)
                self.view.refresh_data_view()

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
                    self.view,
                    "Computation Error",
                    f"Failed to create and calculate new column:\n{str(ComputedColumnError)}",
                )

    def change_column_type(self):
        """Change the data type of the selected column"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No data", "Please load data first")
            return

        selected_columns = self.view.operations_panel.get_selected_columns()
        if not selected_columns:
            self.status_bar.log("No Column Selected", "WARNING")
            return

        if len(selected_columns) > 1:
            QMessageBox.warning(
                self.view,
                "Selection Error",
                "Please select only one column to change datatype",
            )
            return

        column = selected_columns[0]

        type_str = self.view.operations_panel.get_target_datatype()

        # mapping the datatypes
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

            # Warning for potential data loss
            if target_type in ["int", "float", "datetime"]:
                reply = QMessageBox.question(
                    self.view,
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
                self.view.refresh_data_view()

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
                self.changedatatype_animation.start(self.view)

        except Exception as ChangeColumnDataTypeError:
            error_msg = f"Failed to convert '{column}' to {target_type}: {str(ChangeColumnDataTypeError)}"
            QMessageBox.critical(self.view, "Conversion Error", error_msg)
            self.status_bar.log(error_msg, "ERROR")
            traceback.print_exc()
            self.view.refresh_data_view()

    def apply_text_manipulation(self):
        """Apply the requested text manipulation to the selected column"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No data", "Please load data first")

        selected_columns = self.view.operations_panel.get_selected_columns()
        if not selected_columns:
            self.status_bar.log("No Column Selected", "WARNING")
            return

        if len(selected_columns) > 1:
            QMessageBox.warning(
                self.view,
                "Selection Error",
                "Please select only one column for text manipulation",
            )
            return

        column = selected_columns[0]
        selected_operation = self.view.operations_panel.get_text_operation()

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
            self.view.refresh_data_view()
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
                self.view, "Text Manipulation Error", {str(TextManipulationError)}
            )
            self.status_bar.log(
                f"Text manipulation failed: {str(TextManipulationError)}", "ERROR"
            )
    
    def open_split_column_dialog(self) -> None:
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first.")
            return
        
        columns = list(self.data_handler.df.columns)
        dialog = SplitColumnDialog(columns, self.view)
        
        if dialog.exec():
            column, delimiter, new_cols = dialog.get_parameters()
            try:
                self.data_handler.clean_data("split_column", column=column, delimiter=delimiter, new_columns=new_cols)
                self.view.refresh_data_view()
            except Exception as error:
                self.view.status_bar.log(f"Failed to split column: {str(error)}", "ERROR")
                QMessageBox.critical(self.main_window, "Error", f"Failed to split column:\n{str(error)}")
    
    def open_regex_replace_dialog(self) -> None:
        """Open the dialog to configure and apply regex text replacement."""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first.")
            return
            
        columns = list(self.data_handler.df.columns)
        dialog = RegexReplaceDialog(columns, self.view)
        
        if dialog.exec():
            column, pattern, replacement = dialog.get_parameters()
            try:
                self.data_handler.clean_data(
                    "regex_replace",
                    column=column,
                    pattern=pattern,
                    replacement=replacement
                )
                self.view.refresh_data_view()
            except Exception as error:
                self.view.status_bar.log(f"Regex operation failed: {str(error)}", "ERROR")
                QMessageBox.critical(self.main_window, "Error", f"Regex operation failed:\n{str(error)}")
                
    def extract_date_component(self):
        """Extracts date components into a new column"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first")
            return
        
        source_col, component = self.view.operations_panel.get_date_extraction_parameters()
        if not source_col or not component:
            QMessageBox.warning(self.view, "Missing Input", "Please select both a column and a date component to extract")
            return
        
        try:
            self.data_handler.clean_data("extract_date_component", column=source_col, component=component)
            self.view.refresh_data_view()
            self.status_bar.log_action(
                f"Extracted '{component}' from '{source_col}'",
                details={
                    "source_column": source_col,
                    "component": component,
                    "operation": "extract_date_component"
                }, level="SUCCESS"
            )
            self.status_bar.log(f"Extracted {component} from {source_col}", "SUCCESS")
        except Exception as ExtractError:
            self.status_bar.log(f"Date extraction failed: {str(ExtractError)}", "ERROR")
            QMessageBox.critical(self.view, "Extraction Error", f"Failed to extract date component:\n{str(ExtractError)}")
    
    def calculate_date_difference(self):
        """Calculates the time difference between two date columns"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first.")
            return
        
        start_col, end_col, unit = self.view.operations_panel.get_date_diff_parameters()
        if not start_col or not end_col:
            QMessageBox.warning(self.view, "Missing Input", "Please select two columns")
            return
        if start_col == end_col:
            QMessageBox.warning(self.view, "Invalid Selection", "The two columns cannot be the same")
            return
        
        try:
            self.data_handler.clean_data("calculate_date_difference", start_column=start_col, end_column=end_col, unit=unit)
            self.view.refresh_data_view()
            
            self.status_bar.log_action(
                f"Calculated duration between '{start_col}' and '{end_col}' in {unit}",
                details={
                    "start_column": start_col,
                    "end_column": end_col,
                    "unit": unit,
                    "operation": "calculate_date_difference"
                }, level="SUCCESS"
            )
            self.status_bar.log(f"Calculated duration in {unit}", "SUCCESS")
        except Exception as CalcError:
            self.status_bar.log(f"Date calculation failed: {str(CalcError)}", "ERROR")
            QMessageBox.critical(self.view, "Calculation Error", f"Failed to calculate duration:\n{str(CalcError)}")

    def open_binning_dialog(self):
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first.")
            return
        
        numeric_cols = self.data_handler.df.select_dtypes(include=["number"]).columns.tolist()
        
        if not numeric_cols:
            QMessageBox.warning(self.view, "No Numeric Data", "This dataset contains no numeric columns suitable for binning.")
            return
        
        dialog = BinningDialog(numeric_cols, parent=self.view)
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
                    self.view.refresh_data_view()
                    
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
                    QMessageBox.critical(self.view, "Binning Error", f"Failed to bin column:\n{str(BinError)}")
                    self.status_bar.log(f"Binning failed: {str(BinError)}", "ERROR")

    def open_aggregation_dialog(self):
        """Open aggregation dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "Warning", "No data loaded")
            return

        dialog = AggregationDialog(self.data_handler, self.view)
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
                            self.view, "Error", str(SaveAggregationDialogError)
                        )

                self.view.refresh_data_view()

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
                self.aggregate_animation.start(self.view)
            except Exception as AggregationDialogError:
                QMessageBox.critical(self.view, "Error", str(AggregationDialogError))
                self.status_bar.log(
                    f"Aggregation failed: {str(AggregationDialogError)}", "ERROR"
                )

    def refresh_saved_agg_list(self):
        """Refreshes the list of saved aggs"""
        try:
            agg_names = self.aggregation_manager.list_aggregations()
            data_list = []
            
            if agg_names:
                for name in agg_names:
                    agg = self.aggregation_manager.get_aggregation(name)
                    if agg:
                        data_list.append((name, agg.row_count))
            
            self.view.operations_panel.update_saved_aggregation_list(data_list)
        except Exception as RefreshAggregationListError:
            print(
                f"Warning: Could not refresh aggregation list: {str(RefreshAggregationListError)}"
            )

    def on_saved_agg_selected(self, item):
        """Handle selection of saved aggs"""
        enabled = (item is not None and item.data(Qt.ItemDataRole.UserRole) is not None)
        self.view.operations_panel.set_aggregation_buttons_enabled(enabled)

    def view_saved_aggregations(self):
        """View the current selected agg in the table"""
        agg_name = self.view.operations_panel.get_selected_saved_aggregation()
        if not agg_name:
            return

        try:
            agg_df = self.aggregation_manager.get_aggregation_df(agg_name)
            if agg_df is None:
                QMessageBox.warning(self.view, "Error", "Aggregation data not found")
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
            self.view.refresh_data_view()

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
                self.view,
                "Aggregation Loaded",
                f"Now viewing aggregation: {agg_name}\n\n"
                f"Rows: {len(agg_df):,}\n"
                f"Columns: {len(agg_df.columns)}\n\n"
                f"Click 'Reset to Original' to return to your full dataset.",
            )
        except Exception as ViewAggregationError:
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to view aggregation:\n{str(ViewAggregationError)}",
            )
            traceback.print_exc()

    def delete_saved_aggregation(self):
        """Delete a saved aggregation"""
        agg_name = self.view.operations_panel.get_selected_saved_aggregation()
        if not agg_name:
            return

        reply = QMessageBox.question(
            self.view,
            "Confirm Delete",
            f"Are you sure you want to delete the saved aggregation '{agg_name}'?\n\n"
            "This will not affect your current data view.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.aggregation_manager.delete_aggregation(agg_name):
                self.refresh_saved_agg_list()
                self.view.operations_panel.set_aggregation_buttons_enabled(False)
                self.status_bar.log(f"Deleted aggregation: {agg_name}", "SUCCESS")

    def open_melt_dialog(self):
        """Opens the melt data dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first")
            return

        dialog = MeltDialog(self.data_handler.df, self.view)

        if dialog.exec():
            config = dialog.get_config()
            try:
                reply = QMessageBox.question(
                    self.view,
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
                    self.view.refresh_data_view()

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
                    self.melt_animation.start(self.view)

            except Exception as MeltDataError:
                QMessageBox.critical(
                    self.view, "Error", f"Failed to melt data:\n{str(MeltDataError)}"
                )
                self.status_bar.log(f"Melt failed: {str(MeltDataError)}", "ERROR")

    def open_pivot_dialog(self):
        """Opens the pivot table dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No data", "Please load data first")
            return
        
        dialog = PivotDialog(self.data_handler.df, self.view)
        
        if dialog.exec():
            config = dialog.get_config()
            try:
                reply = QMessageBox.question(
                    self.view,
                    "Confirm Pivot",
                    "Pivoting will restructure your entire dataset.\n\n"
                    "Are you sure you want to proceed?\n",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    before_shape = self.data_handler.df.shape
                    
                    self.data_handler.pivot_data(index=config["index"], columns=config["columns"], values=config["values"], aggfunc=config["aggfunc"])
                    after_shape = self.data_handler.df.shape
                    self.view.refresh_data_view()
                    
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
                    self.aggregate_animation.start(self.view)
            except Exception as PivotDataError:
                QMessageBox.critical(self.view, "Error", f"Failed to pivot data:\n{str(PivotDataError)}")
                self.status_bar.log(f"Pivot Failed: {str(PivotDataError)}", "ERROR")
                print(PivotDataError)

    def open_merge_dialog(self):
        """Opens the dialog for merging data"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No data", "Please load data first")
            return
        
        dialog = MergeDialog(self.data_handler, self.view)
        
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
                self.view.refresh_data_view()
                
                self.status_bar.log_action(
                    f"Merged data ({config['how']})",
                    details={
                        "how": config["how"],
                        "rows_before": rows_before,
                        "rows_after": rows_after,
                        "operation": "merge"
                    },
                    level="SUCCESS"
                )
                self.merge_animation = FileImportAnimation(message="Data Merged")
                self.merge_animation.start(target_widget=self.view)
            except Exception as MergeError:
                QMessageBox.critical(self.view, "Merge Error", str(MergeError))
                self.status_bar.log(f"Merge failed: {str(MergeError)}", "ERROR")

    def apply_sort(self):
        """Apply a permanent sorting to data"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No data", "Please load data first")
            return

        column, order_text = self.view.operations_panel.get_sort_parameters()
        if not column:
            return

        ascending = (order_text == "Ascending")

        try:
            col_index = list(self.data_handler.df.columns).index(column)
            order = (
                Qt.SortOrder.AscendingOrder
                if ascending
                else Qt.SortOrder.DescendingOrder
            )

            self.view.data_table.sortByColumn(col_index, order)
            self.view.refresh_data_view(reload_model=False)

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
            QMessageBox.critical(self.view, "Error", str(SortError))

    def quick_create_subsets(self):
        """Quick create subsets from column values"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first")
            return
        
        column = self.view.operations_panel.get_quick_subset_column()
        if not column:
            QMessageBox.warning(
                self.view, "Feature Not Available", "Subset feature not fully initialized"
            )
            return

        if not column:
            QMessageBox.warning(self.view, "No Column Selected", "Please select a column")
            return

        unique_count = self.data_handler.df[column].nunique()

        reply = QMessageBox.question(
            self.view,
            "Confirm",
            f"Create {unique_count} subsets (one per unique value in '{column}')?\n\n"
            f"This is useful for analyzing data by groups (e.g., by location, category, etc.)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if reply == QMessageBox.StandardButton.Yes:
            try:
                created = self.subset_manager.create_subset_from_unique_values(
                    self.data_handler.df, column
                )

                # Apply each to get row counts
                for name in created:
                    self.subset_manager.apply_subset(self.data_handler.df, name)

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
                    self.view,
                    "Success",
                    f"Created {len(created)} subsets from column '{column}'",
                )
            except Exception as QuickCreateSubsetsError:
                self.status_bar.log(
                    f"Failed to create subsets: {str(QuickCreateSubsetsError)}", "ERROR"
                )
                QMessageBox.critical(self.view, "Error", str(QuickCreateSubsetsError))
                traceback.print_exc()

    def refresh_active_subsets(self):
        """Refresh the list of active subsets"""
        try:
            subset_data = []

            if self.data_handler.df is not None:
                for name in self.subset_manager.list_subsets():
                    try:
                        self.subset_manager.apply_subset(self.data_handler.df, name)
                    except Exception as ApplySubsetError:
                        print(
                            f"Warning: Could not apply subset {name}: {str(ApplySubsetError)}"
                        )

            for name in self.subset_manager.list_subsets():
                subset = self.subset_manager.get_subset(name)
                row_text = (
                    f"{subset.row_count} rows" if subset.row_count > 0 else "? rows"
                )
                subset_data.append((name, row_text))
            self.view.operations_panel.update_active_subsets_list(subset_data)
        except Exception as RefreshSubsetListError:
            print(f"Warning: Could not refresh subset list: {RefreshSubsetListError}")

    def view_subset_quick(self):
        """Quick view of selected subset"""
        name = self.view.operations_panel.get_selected_active_subset()
        if not name:
            return

        try:
            subset_df = self.subset_manager.apply_subset(self.data_handler.df, name)
            viewer = SubsetDataViewer(subset_df, name, self.view)
            viewer.exec()
        except Exception as ViewSubsetError:
            QMessageBox.critical(self.view, "Error", str(ViewSubsetError))
            traceback.print_exc()

    def open_subset_manager(self):
        """Open the subset manager dialog"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first")
            return

        try:
            # Create and show dialog
            dialog = SubsetManagerDialog(self.subset_manager, self.data_handler, self.view)
            # Request redirection to index 1
            dialog.plot_subset_requested.connect(self.handle_plot_request)

            dialog.exec()

            # Refresh the subset list after dialog closes
            self.refresh_active_subsets()

        except Exception as OpenSubsetManagerError:
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to open subset manager: {str(OpenSubsetManagerError)}",
            )
            traceback.print_exc()

    def handle_plot_request(self, subset_name: str):
        """Handle the signal from SubsetManagerDialog to plot the selected subset"""
        if not self.view.plot_tab:
            QMessageBox.warning(
                self.view, "Error", "Plot tab reference not set. Cannot switch tabs"
            )
            self.status_bar.log("Plot tab reference not set", "ERROR")
            return

        try:
            self.view.plot_tab.activate_subset(subset_name)
            self.view.switch_to_plot_tab()

        except Exception as PlotRequestError:
            self.status_bar.log(
                f"Failed to switch to plotting tab: {str(PlotRequestError)}", "ERROR"
            )
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to activate the plot tab: {str(PlotRequestError)}",
            )

    def inject_subset_to_dataframe(self):
        """Insert the selected subset into the active dataframe view."""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No data", "Please load data first")
            return

        # get the selected subset
        subset_name = self.view.operations_panel.get_selected_active_subset()
        if not subset_name:
            QMessageBox.warning(
                self.view,
                "None selected",
                "Please select a subset to apply to current data view",
            )
            return

        reply = QMessageBox.question(
            self.view,
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

            subset_df = self.subset_manager.apply_subset(
                self.data_handler.df, subset_name, use_cache=False
            )

            self.data_handler.df = subset_df.copy()
            self.data_handler.inserted_subset_name = subset_name

            self.view.refresh_data_view()

            self.view.operations_panel.set_injection_status_ui(is_subset_active=True, subset_name=subset_name)
            self.view.operations_panel.restore_original_btn.setEnabled(True)
            self.view.operations_panel.inject_subset_tbn.setEnabled(False)

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
                self.view,
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
                self.view,
                "Error",
                f"Failed to insert subset:\n{str(InsertSubsetIntoDataFrameError)}",
            )
            self.failed_animation = FailedAnimation(message="Failed to Insert Subset")
            self.failed_animation.start(target_widget=self.view)
            traceback.print_exc()

    def restore_original_dataframe(self):
        """Restore the original DataFrame into the Active Data View of the Data Table"""
        if (
            not hasattr(self.data_handler, "pre_insert_df")
            or self.data_handler.pre_insert_df is None
        ):
            QMessageBox.warning(
                self.view, "Nothing to Restore", "No inserted subset to restore from"
            )
            return

        try:
            subset_name = getattr(self.data_handler, "inserted_subset_name", "Unknown")
            original_rows = len(self.data_handler.pre_insert_df)

            self.data_handler.df = self.data_handler.pre_insert_df.copy()
            self.data_handler.pre_insert_df = None
            self.data_handler.inserted_subset_name = None

            self.view.refresh_data_view()

            self.view.operations_panel.set_injection_status_ui(is_subset_active=False)

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
                self.view,
                "Restore Complete",
                f"Original DataFrame has been restored.\n\n"
                f"Restored: {original_rows:,} rows",
            )

            self.restore_animation = ResetToOriginalStateAnimation(
                "Restored to Original", parent=None
            )
            self.restore_animation.start(target_widget=self.view)

        except Exception as RestoreOriginalDataFrameError:
            self.status_bar.log(
                f"Failed to restore original data: {str(RestoreOriginalDataFrameError)}",
                "ERROR",
            )
            QMessageBox.critical(
                self.view,
                "Error",
                f"Failed to restore original data:\n{str(RestoreOriginalDataFrameError)}",
            )
            traceback.print_exc()
            
    def reset_data(self):
        """Reset data to original state"""

        reply = QMessageBox.question(
            self.view,
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

            if hasattr(self.view, "operations_panel"):
                self.view.operations_panel.set_injection_status_ui(is_subset_active=False)

            rows_after = (
                len(self.data_handler.df) if self.data_handler.df is not None else 0
            )
            cols_after = (
                len(self.data_handler.df.columns)
                if self.data_handler.df is not None
                else 0
            )

            self.view.refresh_data_view()

            self.reset_animation = ResetToOriginalStateAnimation(
                "Reset to Original", parent=None
            )
            self.reset_animation.start(target_widget=self.view)

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

    def show_help_dialog(self, topic_id: str = None):
        """Displays the help dialog for a specific topic"""
        if not isinstance(topic_id, str):
            pass

        try:
            title, description, link = self.help_manager.get_help_topic(topic_id)

            if title:
                dialog = HelpDialog(self.view, topic_id, title, description, link)
                dialog.exec()
            else:
                QMessageBox.warning(
                    self.view,
                    "Help not found",
                    f"No help topic could be found for '{topic_id}'",
                )
        except Exception as ShowHelpDialogError:
            self.status_bar.log(
                f"Error displaying help dialog: {str(ShowHelpDialogError)}", "ERROR"
            )
            QMessageBox.critical(
                self.view, "Help Error", "Could not load help content. See log for details"
            )
            traceback.print_exc()

    def on_history_clicked(self, item):
        """Handles the click of history entry"""
        if not item:
            return

        target_index = item.data(Qt.ItemDataRole.UserRole)
        try:
            self.data_handler.jump_to_history_index(target_index)
            self.view.refresh_data_view()

            self.view.operations_panel.select_history_item_by_index(target_index)

        except Exception as HistoryError:
            self.status_bar.log(f"Failed to go to state: {str(HistoryError)}", "ERROR")
    
    def run_statistical_test_from_selection(self) -> None:
        """Handles the selection of columns and triggers a statistical test"""
        if self.data_handler.df is None:
            QMessageBox.warning(self.view, "No Data", "Please load data first.")
            return
        
        _, selected_columns = self.view.get_selection_state()
        
        if len(selected_columns) != 2:
            QMessageBox.warning(
                self.view, 
                "Selection Error", 
                "Please select exactly two columns in the table to run a statistical comparison."
            )
            return
        
        col1, col2 = selected_columns
        import pandas as pd
        # verify that both columns are numeric
        if not pd.api.types.is_numeric_dtype(self.data_handler.df[col1]) or not pd.api.types.is_numeric_dtype(self.data_handler.df[col2]):
            QMessageBox.warning(
                self.view,
                "Type Error",
                "Both selected columns must be strictly numeric to perform these statistical tests."
            )
            return
        
        test_type, ok = QInputDialog.getItem(
            self.view,
            "Select Statistical Test",
            f"Select test to run between '{col1}' and '{col2}':",
            ["pearson", "t-test", "anova"],
            0,
            False
        )
        
        if ok and test_type:
            try:
                results =self.data_handler.run_statistical_test(test_type, col1, col2)
                
                stat_val = results['statistic']
                p_val = results['p_value']
                test_name = results['test']
                interpretation = results['interpretation']
                html_result = f"""
                <div style='margin-bottom: 15px; padding: 15px; border: 1px solid #bdc3c7; border-radius: 6px; background-color: #f8f9fa;'>
                    <h3 style='margin-top: 0; color: #2c3e50; border-bottom: 1px solid #ecf0f1; padding-bottom: 5px;'>{test_name}</h3>
                    <p><b>Compared Columns:</b> <span style='color: #2980b9;'>{col1}</span> vs <span style='color: #2980b9;'>{col2}</span></p>
                    <table style='width: 100%; margin-bottom: 10px;'>
                        <tr>
                            <td><b>Test Statistic:</b> {stat_val:.4f}</td>
                            <td><b>P-Value:</b> {p_val:.4e}</td>
                        </tr>
                    </table>
                    <div style='background-color: #e8f4f8; padding: 10px; border-left: 4px solid #3498db; border-radius: 3px;'>
                        <b>Interpretation:</b><br>
                        {interpretation}
                    </div>
                </div>
                """
                current_html = self.view.test_results_text.toHtml()
                if "Statistical Test Suite" in current_html and "How to run a statistical test:" in current_html:
                    self.view.test_results_text.clear()
                    
                self.view.test_results_text.append(html_result)
                
                self.view.data_tabs.setCurrentWidget(self.view.test_results_text)
                self.status_bar.log(
                    f"Ran {test_name} on '{col1}' and '{col2}' (p={p_val:.4e})", 
                    "SUCCESS"
                )
            except Exception as StatisticalTestError:
                QMessageBox.critical(self.view, "Error", f"Failed to run statistical test:\n{str(StatisticalTestError)}")
                self.status_bar.log(f"Statistical test failed: {str(StatisticalTestError)}", "ERROR")