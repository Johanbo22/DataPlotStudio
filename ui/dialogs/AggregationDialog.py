from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox


from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QVBoxLayout,
    QTableWidget,
    QHeaderView,
    QAbstractItemView,
    QTableWidgetItem,
)
from PyQt6.QtCore import Qt

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit
from ui.widgets.AnimatedListWidget import DataPlotStudioListWidget
import pandas as pd


class AggregationDialog(QDialog):
    """Dialog for data aggregation operations"""

    def __init__(self, data_handler, parent=None):
        super().__init__(parent)
        self.data_handler = data_handler
        self.setWindowTitle("Aggregate Data")
        self.setModal(True)
        self.resize(900, 700)
        self.columns = list(data_handler.df.columns)

        self.date_grouping_options = ["None", "Year", "Quarter", "Month", "Week", "Day"]
        self.agg_functions = [
            "mean",
            "sum",
            "median",
            "min",
            "max",
            "count",
            "std",
            "var",
            "first",
            "last",
            "nunique",
        ]
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout()

        # Top sction with configuration options
        config_layout = QHBoxLayout()

        # first: group-by section
        group_box = DataPlotStudioGroupBox("Group By")
        group_layout = QVBoxLayout()

        group_info = QLabel("Select columns to group by:")
        group_info.setStyleSheet("color: #666; font-size: 9pt;")
        group_layout.addWidget(group_info)

        self.group_by_list = DataPlotStudioListWidget()
        self.group_by_list.setSelectionMode(
            DataPlotStudioListWidget.SelectionMode.MultiSelection
        )
        self.group_by_list.addItems(self.columns)
        self.group_by_list.itemSelectionChanged.connect(self.on_group_selection_change)
        group_layout.addWidget(self.group_by_list)

        # Date grouping for datetime cols
        self.date_group_frame = DataPlotStudioGroupBox("Date Grouping")
        self.date_group_frame.setVisible(False)
        date_layout = QFormLayout()
        self.date_freq_combo = DataPlotStudioComboBox()
        self.date_freq_combo.addItems(self.date_grouping_options)
        self.date_freq_combo.currentTextChanged.connect(self.update_preview)
        date_layout.addRow("Frequency:", self.date_freq_combo)
        self.date_group_frame.setLayout(date_layout)
        group_layout.addWidget(self.date_group_frame)

        group_box.setLayout(group_layout)
        config_layout.addWidget(group_box, 1)

        # Aggregation section
        agg_box = DataPlotStudioGroupBox("Aggregation Columns")
        agg_layout = QVBoxLayout()

        selection_layout = QHBoxLayout()

        # _Available cols
        available_layout = QVBoxLayout()
        available_layout.addWidget(QLabel("Available Columns:"))
        self.available_list = DataPlotStudioListWidget()
        self.available_list.addItems(self.columns)
        self.available_list.setSelectionMode(
            DataPlotStudioListWidget.SelectionMode.ExtendedSelection
        )
        available_layout.addWidget(self.available_list)
        selection_layout.addLayout(available_layout)

        # Buttons
        button_layout = QVBoxLayout()
        button_layout.addStretch()
        self.button_add = DataPlotStudioButton("Add >", parent=self)
        self.button_add.clicked.connect(self.add_column_to_agg)
        button_layout.addWidget(self.button_add)
        self.button_remove = DataPlotStudioButton("< Remove", parent=self)
        self.button_remove.clicked.connect(self.remove_column_from_agg)
        button_layout.addWidget(self.button_remove)
        button_layout.addStretch()
        selection_layout.addLayout(button_layout)

        # Selected columns table
        selected_layout = QVBoxLayout()
        selected_layout.addWidget(QLabel("Selected:"))
        self.agg_table = QTableWidget()
        self.agg_table.setColumnCount(2)
        self.agg_table.setHorizontalHeaderLabels(["Column", "Function"])
        self.agg_table.horizontalHeader().setSectionResizeMode(
            0, QHeaderView.ResizeMode.Stretch
        )
        self.agg_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.agg_table.setSelectionBehavior(
            QAbstractItemView.SelectionBehavior.SelectRows
        )
        self.agg_table.verticalHeader().setVisible(False)
        selected_layout.addWidget(self.agg_table)
        selection_layout.addLayout(selected_layout)

        agg_layout.addLayout(selection_layout)
        agg_box.setLayout(agg_layout)
        config_layout.addWidget(agg_box, 2)

        layout.addLayout(config_layout)
        layout.addSpacing(10)

        # Preview table section
        preview_label = QLabel("Preview:")
        preview_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        layout.addWidget(preview_label)

        self.preview_table = QTableWidget()
        self.preview_table.setAlternatingRowColors(True)
        self.preview_table.verticalHeader().setVisible(False)
        self.preview_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.preview_table.setMaximumHeight(200)
        layout.addWidget(self.preview_table)

        layout.addSpacing(10)

        # Save secion
        self.save_agg_group = DataPlotStudioGroupBox(
            "Save this aggregation", parent=self
        )
        self.save_agg_group.setCheckable(True)
        self.save_agg_group.setChecked(False)

        save_layout = QFormLayout()
        self.save_name_input = DataPlotStudioLineEdit()
        self.save_name_input.setPlaceholderText("e.g., 'Sales by Region'")
        save_layout.addRow(QLabel("Save as:"), self.save_name_input)

        self.save_agg_group.setLayout(save_layout)
        layout.addWidget(self.save_agg_group)

        # buttons for accept and reject
        btn_layout = QHBoxLayout()
        apply_button = DataPlotStudioButton(
            "Apply Aggregation",
            parent=self,
            base_color_hex="#4caf50",
            text_color_hex="white",
        )
        apply_button.clicked.connect(self.validate_and_accept)
        btn_layout.addWidget(apply_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self)
        cancel_button.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_button)

        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.update_preview()

    def on_group_selection_change(self):
        """Changes in group by selection t show date options"""
        selected_items = self.group_by_list.selectedItems()
        show_date_options = False

        # check for datetime
        for item in selected_items:
            col_name = item.text()
            if pd.api.types.is_datetime64_any_dtype(self.data_handler.df[col_name]):
                show_date_options = True
                break

        self.date_group_frame.setVisible(show_date_options)
        self.update_preview()

    def add_column_to_agg(self):
        """Add selected columns from the list to the aggregation table"""
        for item in self.available_list.selectedItems():
            col_name = item.text()

            # check if it already is there
            exists = False
            for row in range(self.agg_table.rowCount()):
                if self.agg_table.item(row, 0).text() == col_name:
                    exists = True
                    break

            if not exists:
                row = self.agg_table.rowCount()
                self.agg_table.insertRow(row)

                name_item = QTableWidgetItem(col_name)
                name_item.setFlags(
                    Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable
                )
                self.agg_table.setItem(row, 0, name_item)

                combo = DataPlotStudioComboBox()
                combo.addItems(self.agg_functions)

                # Default based on type
                if pd.api.types.is_numeric_dtype(self.data_handler.df[col_name]):
                    combo.setCurrentText("sum")
                else:
                    combo.setCurrentText("count")

                combo.currentTextChanged.connect(self.update_preview)
                self.agg_table.setCellWidget(row, 1, combo)

        self.update_preview()

    def remove_column_from_agg(self):
        """Remove selected rows from aggregation table"""
        rows = sorted(
            set(index.row() for index in self.agg_table.selectedIndexes()), reverse=True
        )
        for row in rows:
            self.agg_table.removeRow(row)
        self.update_preview()

    def get_current_config(self):
        """Construct the config"""
        group_cols = [item.text() for item in self.group_by_list.selectedItems()]

        agg_config = {}
        for row in range(self.agg_table.rowCount()):
            col = self.agg_table.item(row, 0).text()
            func = self.agg_table.cellWidget(row, 1).currentText()
            agg_config[col] = func

        date_grouping = {}
        if (
            self.date_group_frame.isVisible()
            and self.date_freq_combo.currentText() != "None"
        ):
            freq = self.date_freq_combo.currentText()
            for col in group_cols:
                if pd.api.types.is_datetime64_any_dtype(self.data_handler.df[col]):
                    date_grouping[col] = freq

        return group_cols, agg_config, date_grouping

    def update_preview(self):
        """Generate and display aggragation preview"""
        group_cols, agg_config, date_grouping = self.get_current_config()

        if not group_cols and not agg_config:
            self.preview_table.clear()
            self.preview_table.setRowCount(0)
            self.preview_table.setColumnCount(1)
            self.preview_table.setHorizontalHeaderLabels(["Status"])
            self.preview_table.setItem(
                0, 0, QTableWidgetItem("Select columns to see preview")
            )
            self.preview_table.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.Stretch
            )
            return

        try:
            preview_df = self.data_handler.preview_aggregation(
                group_by=group_cols,
                agg_config=agg_config,
                date_grouping=date_grouping,
                limit=5,
            )

            self.preview_table.clear()
            self.preview_table.setRowCount(len(preview_df))
            self.preview_table.setColumnCount(len(preview_df.columns))
            self.preview_table.setHorizontalHeaderLabels(
                [str(column) for column in preview_df.columns]
            )

            for row in range(len(preview_df)):
                for col in range(len(preview_df.columns)):
                    val = preview_df.iloc[row, col]
                    item = QTableWidgetItem(str(val))
                    self.preview_table.setItem(row, col, item)

            self.preview_table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Interactive
            )

        except Exception as PreviewTableError:
            self.preview_table.clear()
            self.preview_table.setRowCount(1)
            self.preview_table.setColumnCount(1)
            self.preview_table.setHorizontalHeaderLabels(["Error"])
            self.preview_table.setItem(
                0, 0, QTableWidgetItem(f"Cannot preview: {str(PreviewTableError)}")
            )
            self.preview_table.horizontalHeader().setSectionResizeMode(
                0, QHeaderView.ResizeMode.Stretch
            )

    def validate_and_accept(self):
        """Validate selections before accepting"""
        group_cols, agg_config, _ = self.get_current_config()

        if not group_cols:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please select at least one column to group by",
            )
            return

        if not agg_config:
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please select at least one column to aggregate",
            )
            return

        # check for overlap
        overlap = set(group_cols) & set(agg_config.keys())
        if overlap:
            QMessageBox.warning(
                self,
                "Validation Error",
                f"Columns cannot be both grouped and aggregated:\n{', '.join(overlap)}",
            )
            return

        # check if name is given
        if self.save_agg_group.isChecked() and not self.save_name_input.text().strip():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Please enter a name for the aggregation you want to save.",
            )
            return

        self.accept()

    def get_aggregation_config(self):
        """Return the aggregation config"""
        group_cols, agg_config, date_grouping = self.get_current_config()

        config = {
            "group_by": group_cols,
            "agg_config": agg_config,
            "date_grouping": date_grouping,
            "aggregation_name": self.save_name_input.text().strip()
            if self.save_agg_group.isChecked()
            else "",
        }

        return config
