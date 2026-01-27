from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QSplitter, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QHeaderView
from typing import List

import pandas as pd
from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox


class MeltDialog(QDialog):
    """Dialog for using the melt function"""

    def __init__(self, df: pd.DataFrame, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Melt Data")
        self.setModal(True)
        self.resize(800, 700)
        self.df = df
        self.columns = list(df.columns)
        self.row_count = df.shape[0]
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        #info
        info_label = QLabel("Melt data together")
        info_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(info_label)

        info_description = QLabel(
            "Using melt you unpivot your data fra a wide format to a long format.\n"
            "1. Select ID variables (columns to keep as identifers).\n"
            "2. Select Value Variables (columns to unpivot into rows)."
        )
        info_description.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        info_description.setWordWrap(True)
        layout.addWidget(info_description)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        #id vars
        id_variable_widget = QWidget()
        id_variable_layout = QVBoxLayout(id_variable_widget)
        id_variable_layout.addWidget(QLabel("ID variables (Keep these columns):"))

        self.id_variable_list = QListWidget()
        self.id_variable_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.id_variable_list.addItems(self.columns)
        id_variable_layout.addWidget(self.id_variable_list)

        #buttons
        id_buttons = QHBoxLayout()
        id_select_all = QPushButton("Select All")
        id_select_all.clicked.connect(lambda: self.id_variable_list.selectAll())
        id_buttons.addWidget(id_select_all)
        id_clear_all = QPushButton("Clear All")
        id_clear_all.clicked.connect(lambda: self.id_variable_list.clearSelection())
        id_buttons.addWidget(id_clear_all)
        id_variable_layout.addLayout(id_buttons)

        splitter.addWidget(id_variable_widget)

        #value vars
        value_widget = QWidget()
        value_layout = QVBoxLayout(value_widget)
        value_layout.addWidget(QLabel("Value Variables (Unpivot these):"))
        value_layout.addWidget(QLabel("(Leave empty to unpivot all non-ID columns)", styleSheet="color: gray; font-size: 8pt"))

        self.value_list = QListWidget()
        self.value_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.value_list.addItems(self.columns)
        value_layout.addWidget(self.value_list)

        value_buttons = QHBoxLayout()
        value_select_all = QPushButton("Select All")
        value_select_all.clicked.connect(lambda: self.value_list.selectAll())
        value_buttons.addWidget(value_select_all)
        value_clear_all = QPushButton("Clear All")
        value_clear_all.clicked.connect(lambda: self.value_list.clearSelection())
        value_buttons.addWidget(value_clear_all)
        value_layout.addLayout(value_buttons)

        splitter.addWidget(value_widget)
        layout.addWidget(splitter)

        layout.addSpacing(15)

        #naming
        naming_group = QGroupBox("New Column Names")
        naming_layout = QFormLayout()

        self.variable_name_input = QLineEdit("variable")
        self.variable_name_input.setPlaceholderText("Name for the column containing old headers")
        naming_layout.addRow(QLabel("Variable Column Name:"), self.variable_name_input)

        self.value_name_input = QLineEdit("value")
        self.value_name_input.setPlaceholderText("Name for the column containing values")
        naming_layout.addRow(QLabel("Value Column Name:"), self.value_name_input)

        naming_group.setLayout(naming_layout)
        layout.addWidget(naming_group)

        preview_group = DataPlotStudioGroupBox("Preview")
        preview_layout = QVBoxLayout()

        self.preview_label = QLabel("Click 'Update Preview' to see changes")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        preview_layout.addWidget(self.preview_label)

        self.preview_table = QTableWidget()
        self.preview_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.horizontalHeader().setStretchLastSection(True)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setMinimumHeight(200)
        preview_layout.addWidget(self.preview_table)

        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)

        layout.addStretch()

        #buttons
        button_layout = QHBoxLayout()

        preview_button = DataPlotStudioButton("Update_Preview")
        preview_button.clicked.connect(self.update_preview)
        button_layout.addWidget(preview_button)

        apply_button = DataPlotStudioButton("Melt Data", base_color_hex="#4caf50")
        apply_button.setMinimumWidth(120)
        apply_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(apply_button)

        cancel_button = DataPlotStudioButton("Cancel")
        cancel_button.setMinimumWidth(120)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

    def update_preview(self):
        """Calculate and display the expected shape of the new dataframe"""
        id_vars = [item.text() for item in self.id_variable_list.selectedItems()]
        value_vars = [item.text() for item in self.value_list.selectedItems()]

        overlap = set(id_vars) & set(value_vars)
        if overlap:
            self.preview_label.setText(f"Error: Overlap in ID and Value variables: {', '.join(overlap)}")
            self.preview_label.setStyleSheet("color: red; font-weight: bold;")
            self.preview_table.clear()
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(0)
            return
        
        v_vars = value_vars if value_vars else None

        if not v_vars:
            num_value_vars = len(self.columns) - len(id_vars)
        else:
            num_value_vars = len(v_vars)
        
        new_rows = self.row_count * num_value_vars
        new_cols = len(id_vars) + 2
        try:
            df_slice = self.df.head(15).copy()

            preview_df = pd.melt(
                df_slice,
                id_vars=id_vars,
                value_vars=v_vars,
                var_name=self.variable_name_input.text() or "variable",
                value_name=self.value_name_input.text() or "value"
            )

            self.preview_table.setRowCount(preview_df.shape[0])
            self.preview_table.setColumnCount(preview_df.shape[1])
            self.preview_table.setHorizontalHeaderLabels(list(preview_df.columns))

            for row in range(preview_df.shape[0]):
                for col in range(preview_df.shape[1]):
                    val = str(preview_df.iat[row, col])
                    self.preview_table.setItem(row, col, QTableWidgetItem(val))
            
            text = (
                f"Original Shape: {self.df.shape}  ->  "
                f"Result Shape: ({new_rows}, {new_cols})"
            )
            style = "color: #333; font-weight: bold; padding: 5px; background-color: #e0e0e0; border-radius: 4px;"
            
            if new_rows > 1_000_000 or (self.row_count > 0 and new_rows > self.row_count * 20):
                text += f"\nWarning: Row count will increase by {num_value_vars}x!"
                style = "color: #d32f2f; font-weight: bold; padding: 5px; background-color: #ffebee; border-radius: 4px;"

            self.preview_label.setText(text)
            self.preview_label.setStyleSheet(style)
        
        except Exception as PreviewMeltError:
            self.preview_label.setText(f"Preview Error: {str(PreviewMeltError)}")
            self.preview_label.setStyleSheet("color: red;")
            print(PreviewMeltError)

    def validate_and_accept(self):
        """Validate the inputs in melt"""
        id_vars = [item.text() for item in self.id_variable_list.selectedItems()]
        value_vars = [item.text() for item in self.value_list.selectedItems()]

        overlap = set(id_vars) & set(value_vars)
        if overlap:
            QMessageBox.warning(self, "Validation Error", f"Columns cannot be both ID and value variables:\n{', '.join(overlap)}")
            return

        if not self.variable_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a name for the Variable column")
            return

        if not self.value_name_input.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a name for the Value column")
            return

        self.accept()

    def get_config(self):
        """Return the config for this dialog"""
        return {
            "id_vars": [item.text() for item in self.id_variable_list.selectedItems()],
            "value_vars": [item.text() for item in self.value_list.selectedItems()],
            "var_name": self.variable_name_input.text().strip(),
            "value_name": self.value_name_input.text().strip()
        }