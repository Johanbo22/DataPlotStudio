from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtWidgets import (
    QDialog,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QRadioButton,
    QButtonGroup,
    QListWidget,
    QAbstractItemView,
    QListWidgetItem,
    QMessageBox,
    QApplication,
    QWidget
)
import pandas as pd
import traceback
from typing import Optional, List, Any, Dict

from ui.widgets import DataPlotStudioButton, DataPlotStudioComboBox, DataPlotStudioGroupBox, DataPlotStudioListWidget, DataPlotStudioRadioButton, DataPlotStudioCheckBox


class ExportDialog(QDialog):
    """Dialog for exporting data"""

    def __init__(self, parent: Optional[QWidget] = None, data_handler=None, selected_rows=None, selected_columns=None):
        super().__init__(parent)
        self.setWindowTitle("Export Data")
        self.setModal(True)
        self.resize(700, 600)

        self.data_handler = data_handler
        self.selected_rows: List[int] = selected_rows if selected_rows is not None else []
        self.pre_selected_columns: List[str] = selected_columns if selected_columns is not None else []

        self.has_row_selection: bool = len(self.selected_rows) > 0
        self.has_col_selection: bool = len(self.pre_selected_columns) > 0
        
        self.to_clipboard: bool = False
        self.filepath: Optional[str] = None

        self.available_columns = []
        if self.data_handler and self.data_handler.df is not None:
            self.available_columns = list(self.data_handler.df.columns)

        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        # Export format selection
        format_label = QLabel("Export Format:")
        format_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(format_label)

        self.format_combo = DataPlotStudioComboBox()
        self.format_combo.addItems(['CSV', 'XLSX', 'JSON'])
        layout.addWidget(self.format_combo)

        layout.addSpacing(10)

        # Data selection options
        selection_group = DataPlotStudioGroupBox("Data Selection", parent=self)
        selection_layout = QVBoxLayout()

        selection_layout.addWidget(QLabel("Rows:"))
        self.rows_group = QButtonGroup(self)

        self.rows_radio_all = DataPlotStudioRadioButton("All Rows")
        self.rows_radio_all.setChecked(True)
        self.rows_group.addButton(self.rows_radio_all)
        selection_layout.addWidget(self.rows_radio_all)

        self.rows_radio_selected = DataPlotStudioRadioButton(f"Selected Rows Only: {len(self.selected_rows)}")
        self.rows_group.addButton(self.rows_radio_selected)
        selection_layout.addWidget(self.rows_radio_selected)

        if self.has_row_selection:
            self.rows_radio_selected.setChecked(True)
        else:
            self.rows_radio_all.setChecked(True)
            self.rows_radio_selected.setEnabled(False)
            self.rows_radio_selected.setToolTip("No rows selected in the table")
        
        selection_layout.addSpacing(10)

        # Column seleciont
        selection_layout.addWidget(QLabel("Columns"))
        self.cols_group = QButtonGroup(self)

        self.cols_radio_all = DataPlotStudioRadioButton("All Columns")
        self.cols_radio_all.setChecked(True)
        self.cols_group.addButton(self.cols_radio_all)
        selection_layout.addWidget(self.cols_radio_all)

        self.cols_radio_specific = DataPlotStudioRadioButton("Specific Columns")
        self.cols_group.addButton(self.cols_radio_specific)
        selection_layout.addWidget(self.cols_radio_specific)

        self.column_list = DataPlotStudioListWidget()
        self.column_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
        self.column_list.setMaximumHeight(300)

        if self.available_columns:
            for col in self.available_columns:
                item = QListWidgetItem(col)
                self.column_list.addItem(item)
                if self.has_col_selection and col in self.pre_selected_columns:
                    item.setSelected(True)
                elif not self.has_col_selection:
                    item.setSelected(True)
                else:
                    item.setSelected(False)
        else:
            self.column_list.addItem("No Columns available")
            self.column_list.setEnabled(False)
            self.cols_radio_specific.setEnabled(False)
        
        if self.has_col_selection and len(self.pre_selected_columns) < len(self.available_columns):
            self.cols_radio_specific.setChecked(True)
            self.column_list.setEnabled(True)
        else:
            self.cols_radio_all.setChecked(True)
            self.column_list.setEnabled(False)
        
        selection_layout.addWidget(self.column_list)

        self.cols_radio_all.toggled.connect(self.toggle_column_list)
        self.cols_radio_specific.toggled.connect(self.toggle_column_list)

        selection_group.setLayout(selection_layout)
        layout.addWidget(selection_group)

        layout.addSpacing(10)

        # Options
        options_group = DataPlotStudioGroupBox("Options", parent=self)
        options_layout = QVBoxLayout()

        self.include_index_check = DataPlotStudioCheckBox("Include Index")
        self.include_index_check.setChecked(False)
        options_layout.addWidget(self.include_index_check)

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #888888; font-style: italic; font-size: 11px;")
        options_layout.addWidget(self.description_label)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        self.format_combo.currentTextChanged.connect(self.update_format_info)
        self.include_index_check.stateChanged.connect(self.update_format_info)

        self.update_format_info()

        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()

        # Copy to clipboard
        self.clipboard_button = DataPlotStudioButton("Copy to clipboard", parent=self)
        self.clipboard_button.setToolTip("Copy the data to system clipboard")
        self.clipboard_button.clicked.connect(self.on_clipboard_clicked)
        button_layout.addWidget(self.clipboard_button)

        button_layout.addStretch()

        export_button = DataPlotStudioButton("Export", parent=self)
        export_button.setMinimumWidth(100)
        export_button.clicked.connect(self.on_export_clicked)
        button_layout.addWidget(export_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
    
    def toggle_column_list(self):
        """toggle the column list"""
        is_specific = self.cols_radio_specific.isChecked()
        self.column_list.setEnabled(is_specific)
        if is_specific and self.available_columns:
            self.column_list.setStyleSheet("background-color: white; border: 1px solid #ccc;")
        else:
            self.column_list.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd; color: #888;")

    def update_format_info(self) -> None:
        """Update a description label based on selected format and current optins"""
        format = self.format_combo.currentText()
        include_index = self.include_index_check.isChecked()

        if format == "JSON":
            if include_index:
                self.description_label.setText("Export as a 'columns' oriented JSON.")
            else:
                self.description_label.setText("Export as a 'records' oriented JSON.")
        elif format == "CSV":
            self.description_label.setText("Standard Comma Separated Values file.")
        elif format == "XLSX":
            self.description_label.setText("Microsoft Excel Spreadsheet format.")
        else:
            self.description_label.setText("")
    
    def _get_export_data(self) -> Optional[pd.DataFrame]:
        """Get the dataframe current selection"""
        if not self.data_handler or self.data_handler.df is None:
            return None
        
        df = self.data_handler.df

        if self.rows_radio_selected.isChecked() and self.selected_rows:
            try:
                df = df.iloc[self.selected_rows]
            except IndexError as error:
                QMessageBox.warning(self, "Selection Error", f"Error slicing selected rows. They may be out of bounds.\n{str(error)}")
                return None
            except Exception as error:
                QMessageBox.critical(self, "Slicing Error", f"An unexpected error occurred while filtering rows:\n{str(error)}")
                return None
        
        if self.cols_radio_specific.isChecked():
            selected_cols = [item.text() for item in self.column_list.selectedItems()]
            if not selected_cols:
                QMessageBox.warning(self, "No Columns Selected", "You have selected 'Specific Columns' but no columns are highlighted. Please select at least one column.")
                return None
            df = df[selected_cols]
        return df

    def on_clipboard_clicked(self):
        """Copy to clipboard"""
        self.to_clipboard = True
        if self.data_handler:
            try:
                df_to_export = self._get_export_data()
                if df_to_export is not None:
                    include_index = self.include_index_check.isChecked()

                    df_to_export.to_clipboard(excel=True, index=include_index)
                    rows, cols = df_to_export.shape

                    QMessageBox.information(
                        self,
                        "Copied",
                        f"Copied {rows} rows and {cols} columns to clipboard\n You can paste this into Excel or Google Sheets"
                    )
                    self.accept()
                    return
            except Exception as ClipboardError:
                QMessageBox.critical(self, "Error", f"Failed to copy to clipboard: {str(ClipboardError)}")
                return
        
        self.accept()

    def on_export_clicked(self):
        """Handle export button click"""
        export_format = self.format_combo.currentText()

        # Determine file filter and extension
        if export_format == 'CSV':
            file_filter = "CSV Files (*.csv)"
            default_ext = ".csv"
        elif export_format == 'XLSX':
            file_filter = "Excel Files (*.xlsx)"
            default_ext = ".xlsx"
        else:  # JSON
            file_filter = "JSON Files (*.json)"
            default_ext = ".json"

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Data",
            f"export{default_ext}",
            file_filter
        )
        if not filepath:
            return
        self.filepath = filepath
        if self.data_handler:
            try:
                df_to_export = self._get_export_data()
                if df_to_export is not None:
                    include_index = self.include_index_check.isChecked()

                    if export_format == "CSV":
                        df_to_export.to_csv(filepath, index=include_index)
                    elif export_format == "XLSX":
                        df_to_export.to_excel(filepath, index=include_index)
                    elif export_format == "JSON":
                        orient = "columns" if include_index else "records"
                        df_to_export.to_json(filepath, orient=orient, indent=4)
                        
                    QMessageBox.information(self, "Success", f"Data exported to {filepath}")
            except Exception as Error:
                QMessageBox.critical(self, "Export Error", f"Failed to export data: {str(Error)}")
                return

    def get_export_config(self):
        """Return export configuration"""
        config = {
            'format': self.format_combo.currentText().lower(),
            'filepath': self.filepath,
            'include_index': self.include_index_check.isChecked(),
            'to_clipboard': self.to_clipboard,
            'selected_rows_only': self.rows_radio_selected.isChecked(),
            'specific_columns': self.cols_radio_specific.isChecked(),
            'selected_columns': [item.text() for item in self.column_list.selectedItems()]
        }
        return config