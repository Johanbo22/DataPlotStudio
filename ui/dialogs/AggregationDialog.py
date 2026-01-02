from ui.widgets.AnimatedComboBox import AnimatedComboBox


from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QListWidget, QMessageBox, QVBoxLayout

from ui.widgets.AnimatedButton import AnimatedButton
from ui.widgets.AnimatedGroupBox import AnimatedGroupBox
from ui.widgets.AnimatedLineEdit import AnimatedLineEdit


class AggregationDialog(QDialog):
    """Dialog for data aggregation operations"""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggregate Data")
        self.setModal(True)
        self.resize(600, 500)
        self.setMaximumHeight(600)
        self.columns = columns
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        # Group By section
        group_label = QLabel("Group By Columns:")
        group_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(group_label)

        group_info = QLabel("Select one or more columns to group by (hold Ctrl/Cmd) to select multiple")
        group_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        layout.addWidget(group_info)

        #list to select multiple columns
        self.group_by_list = QListWidget()
        self.group_by_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.group_by_list.addItems(self.columns)
        self.group_by_list.setMaximumHeight(180)
        layout.addWidget(self.group_by_list)

        #quick select buttons
        group_buttons = QHBoxLayout()
        select_all_group_btn = AnimatedButton("Select All", parent=self)
        select_all_group_btn.clicked.connect(lambda: self.group_by_list.selectAll())
        group_buttons.addWidget(select_all_group_btn)

        #clear all btn
        clear_group_btn = AnimatedButton("Clear All", parent=self)
        clear_group_btn.clicked.connect(lambda: self.group_by_list.clearSelection())
        group_buttons.addWidget(clear_group_btn)
        layout.addLayout(group_buttons)

        layout.addSpacing(15)

        # AGGREGATION 
        agg_label = QLabel("Aggregate Columns:")
        agg_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(agg_label)

        agg_info = QLabel("Select to columns to aggregate (hold Ctrl/Cmd) to select multiple columns")
        agg_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        layout.addWidget(agg_info)

        #lsit of columns
        self.agg_columns_list = QListWidget()
        self.agg_columns_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        self.agg_columns_list.addItems(self.columns)
        self.agg_columns_list.setMaximumHeight(180)
        layout.addWidget(self.agg_columns_list)

        #quick selection buttons
        #selcet all
        agg_buttons = QHBoxLayout()
        select_all_agg_btn = AnimatedButton("Select All", parent=self)
        select_all_agg_btn.clicked.connect(lambda: self.agg_columns_list.selectAll())
        agg_buttons.addWidget(select_all_agg_btn)

        #clearbtn
        clear_agg_btn = AnimatedButton("Clear All", parent=self)
        clear_agg_btn.clicked.connect(lambda: self.agg_columns_list.clearSelection())
        agg_buttons.addWidget(clear_agg_btn)
        layout.addLayout(agg_buttons)

        layout.addSpacing(10)

        #aggregation function selection
        agg_func_layout = QHBoxLayout()
        agg_func_layout.addWidget(QLabel("Aggregation Function:"))
        self.agg_func_combo = AnimatedComboBox()
        self.agg_func_combo.addItems(["mean", "sum", "median", "min", "max", "count", "std", "var", "first", "last"])
        self.agg_func_combo.setToolTip("This funciton will be applied to all selected columns")
        agg_func_layout.addWidget(self.agg_func_combo)
        layout.addLayout(agg_func_layout)

        layout.addSpacing(10)

        #preview section
        preview_label = QLabel("Preview:")
        preview_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(preview_label)

        self.preview_text = QLabel("Select columns to see preview")
        self.preview_text.setWordWrap(True)
        self.preview_text.setStyleSheet(
            "background-color: #f0f0f0; padding: 10px; "
            "border: 1px solid #ccc; border-radius: 4px;"
        )
        layout.addWidget(self.preview_text)

        #connecting the selection to the prewview
        self.group_by_list.itemSelectionChanged.connect(self.update_preview)
        self.agg_columns_list.itemSelectionChanged.connect(self.update_preview)
        self.agg_func_combo.currentTextChanged.connect(self.update_preview)

        layout.addSpacing(20)

        #save aggregation
        self.save_agg_group = AnimatedGroupBox("Save this aggregation", parent=self)
        self.save_agg_group.setCheckable(True)
        self.save_agg_group.setChecked(False)
        self.save_agg_group.setToolTip("Check this box to save this aggregation")

        save_layout = QFormLayout()
        self.save_name_input = AnimatedLineEdit()
        self.save_name_input.setPlaceholderText("e.g. 'Sales by Region'")
        save_layout.addRow(QLabel("Save as:"), self.save_name_input)

        self.save_agg_group.setLayout(save_layout)
        layout.addWidget(self.save_agg_group)

        layout.addStretch()

        #buttons
        button_layout = QHBoxLayout()

        #apply
        apply_button = AnimatedButton("Apply Aggregation", parent=self, base_color_hex="#4caf50", text_color_hex="white")
        apply_button.setMinimumWidth(120)
        apply_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(apply_button)

        #cancel
        cancel_button = AnimatedButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(120)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.update_preview()

    def update_preview(self):
        """Update the preview text to show what will be aggregated"""
        group_cols = [item.text() for item in self.group_by_list.selectedItems()]
        agg_cols = [item.text() for item in self.agg_columns_list.selectedItems()]
        agg_func = self.agg_func_combo.currentText()

        if not group_cols and not agg_cols:
            self.preview_text.setText("Select Columns to see aggregation preview")
            return

        preview = "<b>Operation:</b><br>"

        if group_cols:
            preview += f"<b>Group by:</b> {', '.join(group_cols)}<br>"
        else:
            preview += "<b>Group by:</b> <span style='color: red;'>None selected</span><br>"

        if agg_cols:
            preview += f"<b>Aggregate:</b> {len(agg_cols)} column(s)<br>"
            preview += f"<b>Function:</b> {agg_func}<br><br>"
            preview += "<b>Columns to aggregate:</b><br>"
            for col in agg_cols:
                preview += f"&nbsp;&nbsp;• {col} = {agg_func}({col})<br>"
        else:
            preview += "<b>Aggregate:</b> <span style='color: red;'>None selected</span>"

        self.preview_text.setText(preview)

    def validate_and_accept(self):
        """Validate selections before accepting"""
        group_cols = [item.text() for item in self.group_by_list.selectedItems()]
        agg_cols = [item.text() for item in self.agg_columns_list.selectedItems()]

        if not group_cols:
            QMessageBox.warning(self, "Validation Error", "Please select at least one column to group by")
            return

        if not agg_cols:
            QMessageBox.warning(self, "Validation Error", "Please select at least one column to aggregate")
            return

        #check for overlap
        overlap = set(group_cols) & set(agg_cols)
        if overlap:
            QMessageBox.warning(self, "Validation Error", f"Columns cannot be both grouped and aggregated:\n{', '.join(overlap)}")
            return

        #check if name is given
        if self.save_agg_group.isChecked():
            if not self.save_name_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter a name for the aggregation you want to save.")
                return

        self.accept()

    def get_aggregation_config(self):
        """Return the aggregation config"""
        group_cols = [item.text() for item in self.group_by_list.selectedItems()]
        agg_cols = [item.text() for item in self.agg_columns_list.selectedItems()]
        agg_func = self.agg_func_combo.currentText()

        config = {
            "group_by": group_cols,
            "agg_columns": agg_cols,
            "agg_func": agg_func
        }

        if self.save_agg_group.isChecked():
            config["aggregation_name"] = self.save_name_input.text().strip()
        else:
            config["aggregation_name"] = ""

        return config