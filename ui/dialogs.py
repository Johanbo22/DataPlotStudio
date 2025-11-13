# ui/dialogs.py
from logging import warning
from re import I, T
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,QPushButton, QMessageBox, QInputDialog, QComboBox,QSpinBox, QDoubleSpinBox, QCheckBox, QGroupBox, QFormLayout, QFileDialog, QProgressBar, QApplication, QListWidget, QSplitter, QWidget, QTextEdit, QListWidgetItem, QTableWidget, QTableWidgetItem, QDialogButtonBox)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon
from pathlib import Path
import sys
from ui.animated_widgets import AnimatedButton, AnimatedGroupBox, AnimatedLineEdit, AnimatedComboBox, AnimatedSpinBox, AnimatedDoubleSpinBox, AnimatedCheckBox, AnimatedRadioButton

class GoogleSheetsDialog(QDialog):
    """Dialog for importing data from Google Sheets"""
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Import Google Sheets")
        self.setModal(True)
        self.setGeometry(100, 100, 500, 350)
        
        self.init_ui()
    
    def init_ui(self) -> None:
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        # Information label
        info_label = QLabel("Enter your Google Sheets details below:")
        info_label.setFont(QFont("Arial", 10))
        layout.addWidget(info_label)
        
        # Form layout for inputs
        form_layout = QFormLayout()
        
        # Sheet ID input
        sheet_id_label = QLabel("Sheet ID:")
        self.sheet_id = AnimatedLineEdit()
        self.sheet_id.setToolTip("This is the unique sheet ID for your sheet.")
        self.sheet_id.setPlaceholderText("e.g., 1BxiMVs0XRA5nFMoon9FFBiMKo6YcK7...")
        self.sheet_id.setMinimumWidth(350)
        form_layout.addRow(sheet_id_label, self.sheet_id)
        
        # Sheet Name input
        sheet_name_label = QLabel("Sheet Name:")
        self.sheet_name = AnimatedLineEdit()
        self.sheet_name.setToolTip("This is the name of the sheet you want to import data from.")
        self.sheet_name.setPlaceholderText("e.g., Sheet1")
        form_layout.addRow(sheet_name_label, self.sheet_name)
        
        layout.addLayout(form_layout)

        layout.addSpacing(10)

        #delimter
        delimiter_group = AnimatedGroupBox("CSV Delimtter Settings", parent=self)
        delimiter_layout = QVBoxLayout()

        delimiter_info = QLabel("Google Sheets exports data as a CSV. Choose the delimitter used in your sheet")
        delimiter_info.setWordWrap(True)
        delimiter_info.setStyleSheet("font-weight: normal; color: #555;")
        delimiter_layout.addWidget(delimiter_info)

        #delimter box
        delimiter_select_layout = QHBoxLayout()
        delimiter_select_layout.addWidget(QLabel("Delimiter:"))

        self.delimiter_combo = AnimatedComboBox()
        self.delimiter_combo.addItems([
            "Comma (,) - Standard",
            "Semicolon (;) - European",
            "Tab (\\t) - Tab-separated",
            "Pipe (|) - Pipe-separated",
            "Space ( ) - Space-separated",
            "Custom"
        ])
        self.delimiter_combo.setCurrentIndex(0)
        self.delimiter_combo.currentTextChanged.connect(self.on_delimiter_changed)
        delimiter_select_layout.addWidget(self.delimiter_combo, 1)
        delimiter_layout.addLayout(delimiter_select_layout)

        #custom
        custom_delimiter_layout = QHBoxLayout()
        custom_delimiter_layout.addWidget(QLabel("Custom Delimiter:"))
        self.custom_delimiter_input = AnimatedLineEdit()
        self.custom_delimiter_input.setPlaceholderText("Enter single delimiter character")
        self.custom_delimiter_input.setMaxLength(1)
        self.custom_delimiter_input.setEnabled(False)
        self.custom_delimiter_input.setMaximumWidth(100)
        custom_delimiter_layout.addWidget(self.custom_delimiter_input)
        custom_delimiter_layout.addStretch()
        delimiter_layout.addLayout(custom_delimiter_layout)

        #decimal sep
        decimal_layout = QHBoxLayout()
        decimal_layout.addWidget(QLabel("Decimal Separator:"))
        self.decimal_combo = AnimatedComboBox()
        self.decimal_combo.addItems([
            "Dot (.) - UK/US",
            "Comma (,) - European",
        ])
        self.decimal_combo.setCurrentIndex(0)
        decimal_layout.addWidget(self.decimal_combo, 1)
        delimiter_layout.addLayout(decimal_layout)

        #1000sep
        thousands_layout = QHBoxLayout()
        thousands_layout.addWidget(QLabel("Thousands Separator"))
        self.thousands_combo = AnimatedComboBox()
        self.thousands_combo.addItems([
            "None",
            "Comma (,) - US Style",
            "Dot (.) - European",
            "Space ( ) - International"
        ])
        self.thousands_combo.setCurrentIndex(0)
        thousands_layout.addWidget(self.thousands_combo, 1)
        delimiter_layout.addLayout(thousands_layout)

        delimiter_group.setLayout(delimiter_layout)
        layout.addWidget(delimiter_group)

        # Help text
        help_text = QLabel(
            "How to use:\n"
            "1. Open your Google Sheet in a browser\n"
            "2. Copy the ID from the URL:\n"
            "   docs.google.com/spreadsheets/d/[SHEET_ID]/edit\n"
            "3. Check the sheet tab name (bottom left corner)\n"
            "4. IMPORTANT: Share the sheet publicly\n"
            "   (File → Share → \"Anyone with the link\")\n"
            "5. Select appropriate delimiter and decimal for your region\n"
            "6. Paste the ID and sheet name below"
        )
        help_text.setFont(QFont("Arial", 9))
        help_text.setStyleSheet("color: #333333; background-color: #e8f4f8; padding: 12px; border-radius: 4px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        import_button = AnimatedButton("Import", parent=self)
        import_button.setMinimumWidth(100)
        import_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(import_button)
        
        cancel_button = AnimatedButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        layout.addStretch()
        
        self.setLayout(layout)
    
    def on_delimiter_changed(self, text) -> None:
        """Handle delimiter selection change"""
        self.custom_delimiter_input.setEnabled(text == "Custom")
    
    def validate_and_accept(self) -> None:
        """Validate inputs before accepting"""
        if not self.sheet_id.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a Sheet ID")
            return
        
        if not self.sheet_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a Sheet Name")
            return
        
        #validate custom delimiter
        if self.delimiter_combo.currentText() == "Custom":
            if not self.custom_delimiter_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter delimiter")
                return
        
        self.accept()
    
    def get_inputs(self) -> tuple:
        """Return the sheet ID and name and delimiter settings"""
        sheet_id = self.sheet_id.text().strip()
        sheet_name = self.sheet_name.text().strip()

        #delimiter
        delimiter_text = self.delimiter_combo.currentText()
        if delimiter_text.startswith("Comma"):
            delimiter = ","
        elif delimiter_text.startswith("Semicolon"):
            delimiter = ";"
        elif delimiter_text.startswith("Tab"):
            delimiter = "\t"
        elif delimiter_text.startswith("Pipe"):
            delimiter = "|"
        elif delimiter_text.startswith("Space"):
            delimiter = " "
        elif delimiter_text == "Custom":
            delimiter = self.custom_delimiter_input.text().strip()
        else:
            delimiter = ","
        
        #get decimal separator
        decimal_text = self.decimal_combo.currentText()
        decimal = "," if decimal_text.startswith("Comma") else "."

        # get thousands sep
        thousands_text = self.thousands_combo.currentText()
        if thousands_text.startswith("None"):
            thousands = None
        elif thousands_text.startswith("Comma"):
            thousands = ","
        elif thousands_text.startswith("Dot"):
            thousands = "."
        elif thousands_text.startswith("Space"):
            thousands = " "
        else:
            thousands = None
        
        return sheet_id, sheet_name, delimiter, decimal, thousands


class RenameColumnDialog(QDialog):
    """Dialog for renaming a column"""
    
    def __init__(self, column_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename Column")
        self.setModal(True)
        self.setGeometry(100, 100, 400, 150)
        
        self.column_name = column_name
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        # Old name display
        old_name_layout = QHBoxLayout()
        old_name_layout.addWidget(QLabel("Current Name:"))
        old_name_display = AnimatedLineEdit()
        old_name_display.setText(self.column_name)
        old_name_display.setReadOnly(True)
        old_name_layout.addWidget(old_name_display)
        layout.addLayout(old_name_layout)
        
        # New name input
        new_name_layout = QHBoxLayout()
        new_name_layout.addWidget(QLabel("New Name:"))
        self.new_name_input = AnimatedLineEdit()
        self.new_name_input.setPlaceholderText(f"Enter new name for '{self.column_name}'")
        self.new_name_input.setMinimumWidth(200)
        new_name_layout.addWidget(self.new_name_input)
        layout.addLayout(new_name_layout)
        
        layout.addSpacing(20)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        ok_button = AnimatedButton("Rename", parent=self)
        ok_button.setMinimumWidth(100)
        ok_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(ok_button)
        
        cancel_button = AnimatedButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def validate_and_accept(self):
        """Validate new name before accepting"""
        new_name = self.new_name_input.text().strip()
        
        if not new_name:
            QMessageBox.warning(self, "Validation Error", "Please enter a new column name")
            return
        
        if new_name == self.column_name:
            QMessageBox.warning(self, "Validation Error", "New name must be different from current name")
            return
        
        self.accept()
    
    def get_new_name(self):
        """Return the new column name"""
        return self.new_name_input.text().strip()


class AggregationDialog(QDialog):
    """Dialog for data aggregation operations"""
    
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Aggregate Data")
        self.setModal(True)
        self.setGeometry(100, 100, 600, 500)
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

class ExportDialog(QDialog):
    """Dialog for exporting data"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Data")
        self.setModal(True)
        self.setGeometry(100, 100, 500, 250)
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        # Export format selection
        format_label = QLabel("Export Format:")
        format_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(format_label)
        
        self.format_combo = AnimatedComboBox()
        self.format_combo.addItems(['CSV', 'XLSX', 'JSON'])
        layout.addWidget(self.format_combo)
        
        layout.addSpacing(10)
        
        # Options
        options_group = AnimatedGroupBox("Options", parent=self)
        options_layout = QVBoxLayout()
        
        self.include_index_check = AnimatedCheckBox("Include Index")
        self.include_index_check.setChecked(False)
        options_layout.addWidget(self.include_index_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        
        export_button = AnimatedButton("Export", parent=self)
        export_button.setMinimumWidth(100)
        export_button.clicked.connect(self.on_export_clicked)
        button_layout.addWidget(export_button)
        
        cancel_button = AnimatedButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
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
            "Export_Data",
            f"export{default_ext}",
            file_filter
        )
        
        if filepath:
            self.filepath = filepath
            self.accept()
    
    def get_export_config(self):
        """Return export configuration"""
        return {
            'format': self.format_combo.currentText().lower(),
            'filepath': getattr(self, 'filepath', None),
            'include_index': self.include_index_check.isChecked()
        }


class FilterAdvancedDialog(QDialog):
    """Dialog for advanced filtering with multiple conditions"""
    
    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Filter")
        self.setModal(True)
        self.setGeometry(100, 100, 650, 450)
        
        self.columns = columns
        self.filters = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)
        
        instruction_label = QLabel("Add filter conditions:")
        instruction_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(instruction_label)
        
        # Logical operator selection
        logic_layout = QHBoxLayout()
        logic_layout.addWidget(QLabel("Combine filters using:"))
        self.logic_combo = AnimatedComboBox()
        self.logic_combo.addItems(["AND", "OR"])
        self.logic_combo.setToolTip("AND = All conditions must be True\nOR = Any condition can be True")
        logic_layout.addWidget(self.logic_combo)
        logic_layout.addStretch()
        layout.addLayout(logic_layout)

        layout.addSpacing(19)


        self.filter_rows = []
        for i in range(5):
            #create group bxo ofr each filter element
            filter_group = AnimatedGroupBox(f"Filter {i+1}", parent=self)
            filter_layout = QHBoxLayout()
            
            #checkbox
            enable_check = AnimatedCheckBox("Active")
            enable_check.setChecked(i == 0)
            filter_layout.addWidget(enable_check)

            # Column selector
            column_combo = AnimatedComboBox()
            column_combo.addItems(self.columns)
            filter_layout.addWidget(QLabel("Column:"))
            filter_layout.addWidget(column_combo, 1)
            
            # Condition selector
            condition_combo = AnimatedComboBox()
            condition_combo.addItems(['==', '!=', '>', '<', '>=', '<=', 'contains', 'in'])
            filter_layout.addWidget(QLabel("Condition:"))
            filter_layout.addWidget(condition_combo, 1)
            
            # Value input
            value_input = AnimatedLineEdit()
            value_input.setPlaceholderText("Enter value...")
            filter_layout.addWidget(QLabel("Value:"))
            filter_layout.addWidget(value_input, 2)
            
            filter_group.setLayout(filter_layout)
            layout.addWidget(filter_group)
            
            self.filter_rows.append({
                'column': column_combo,
                'condition': condition_combo,
                'value': value_input,
                'active': enable_check,
                'group': filter_group
            })
        
        layout.addSpacing(15)

        # preview text
        self.preview_label = QLabel("Preview: No filters active")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border: 1px solid #ccc;")
        layout.addWidget(self.preview_label)

        #update on change
        for row in self.filter_rows:
            row['active'].stateChanged.connect(self.update_preview)
            row['column'].currentTextChanged.connect(self.update_preview)
            row['condition'].currentTextChanged.connect(self.update_preview)
            row['value'].textChanged.connect(self.update_preview)
        self.logic_combo.currentTextChanged.connect(self.update_preview)

        layout.addStretch()
        
        # Button layout
        button_layout = QHBoxLayout()
        
        apply_button = AnimatedButton("Apply Filters", parent=self, base_color_hex="#e8f5fa")
        apply_button.setMinimumWidth(120)
        apply_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(apply_button)
        
        cancel_button = AnimatedButton("Cancel", parent=self, base_color_hex="#e8f5fa")
        cancel_button.setMinimumWidth(120)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        self.update_preview()
    
    def update_preview(self):
        """update the filter preview"""
        active_filters = []
        for i, row in enumerate(self.filter_rows):
            if row['active'].isChecked() and row['value'].text().strip():
                active_filters.append(
                    f"{row['column'].currentText()} {row['condition'].currentText()} '{row['value'].text()}'"
                )
        
        if active_filters:
            logic = f" {self.logic_combo.currentText()} "
            preview = f"Preview: {logic.join(active_filters)}"
            self.preview_label.setText(preview)
        else:
            self.preview_label.setText(f"Preview: No filters active")
    
    def validate_and_accept(self):
        """Validate filters before accepting"""
        active_count = sum(1 for row in self.filter_rows if row['active'].isChecked())
        
        if active_count == 0:
            QMessageBox.warning(self, "Validation Error", "Please activate at least one filter")
            return
        
        # Check that active filters have values
        for row in self.filter_rows:
            if row['active'].isChecked() and not row['value'].text().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter values for all active filters")
                return
        
        self.accept()
    
    def get_filters(self):
        """Return active filters with logical operator"""
        filters = []
        for row in self.filter_rows:
            if row['active'].isChecked():
                filters.append({
                    'column': row['column'].currentText(),
                    'condition': row['condition'].currentText(),
                    'value': row['value'].text().strip()
                })
        return {
            'logic': self.logic_combo.currentText(),
            'filters': filters
        }

class ProgressDialog(QDialog):
    """A dualog showing progress for long operations and datasets"""

    def __init__(self, title="Processing", message="Please wait...", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)

        self.init_ui(message)

    def init_ui(self, message) -> None:
        """Initialize the ui"""
        layout = QVBoxLayout()

        #msg lbl
        self.message_label = QLabel(message)
        self.message_label.setFont(QFont("Arial", 10))
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)

        layout.addSpacing(10)

        #prgs bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("QProgressBar { border: 2px solid #3498db; border-radius: 5px; text-align: center; font-weight: bold; background-color: #ecf0f1;} QProgressBar::chunk { background-color: #3498db; border-radius: 3px;}")
        layout.addWidget(self.progress_bar)

        layout.addSpacing(10)

        #status lbl
        self.status_label = QLabel("Initializing")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #7f8c8d")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addSpacing(10)

        #canel btn
        self.cancel_button = AnimatedButton("Cancel", parent=self)
        self.cancel_button.setMaximumWidth(100)
        self.cancel_button.clicked.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.was_cancelled = False

    def update_progress(self, value, status="") -> None:
        """ipdate the progress bar value and msg"""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
        QApplication.processEvents()
    
    def set_message(self, message) -> None:
        """update main msg"""
        self.message_label.setText(message)
        QApplication.processEvents()

    def set_status(self, status) -> None:
        """update the status"""
        self.status_label.setText(status)
        QApplication.processEvents()
    
    def is_cancelled(self) -> bool:
        """Check if operation is cancelled"""
        return self.was_cancelled
    
    def reject(self) -> None:
        """Handle cnacel button"""
        self.was_cancelled = True
        super().reject()

class SubsetManagerDialog(QDialog):
    """Dialog for handling data susbets"""
    plot_subset_requested = pyqtSignal(str)

    def __init__(self, subset_manager, data_handler, parent=None):
        super().__init__(parent)
        self.subset_manager = subset_manager
        self.data_handler = data_handler
        self.setWindowTitle("Data Subsets Tool")
        self.setModal(True)
        self.setGeometry(100, 100, 900, 600)

        self.init_ui()
        print(f"DEBUG: SubsetManager has {len(self.subset_manager.list_subsets())} subsets")
        if self.data_handler.df is not None:
            print(f"DEBUG: Applying subsets to calculate row counts")
            self.apply_all_subsets()
        else:
            print(f"DEBUG: No data to apply subsets")

        print(f"DEBUG: Refreshing the subset list")
        self.refresh_subset_list()

        print(f"DEBUG: QListWidget has {self.subset_list.count()} items")

    def apply_all_subsets(self):
        """Apply all subsets to calculate row counts"""
        print("DEBUG apply_all_subsets: Starting")
    
        if self.data_handler.df is None:
            print("WARNING apply_all_subsets: No data available")
            return
        
        if not hasattr(self, 'subset_manager'):
            print("ERROR apply_all_subsets: No subset_manager")
            return
        
        try:
            subset_names = self.subset_manager.list_subsets()
            print(f"DEBUG apply_all_subsets: Processing {len(subset_names)} subsets")
            
            for name in subset_names:
                try:
                    print(f"DEBUG apply_all_subsets: Applying subset '{name}'")
                    result_df = self.subset_manager.apply_subset(self.data_handler.df, name)
                    print(f"DEBUG apply_all_subsets: Subset '{name}' has {len(result_df)} rows")
                except Exception as e:
                    print(f"WARNING apply_all_subsets: Could not apply subset {name}: {str(e)}")
                    continue
                    
        except Exception as e:
            print(f"ERROR apply_all_subsets: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def init_ui(self):
        """Init ui for the dialog"""
        layout = QVBoxLayout()

        #title
        title = QLabel("Data Subset Creation Tool")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)

        #info
        info = QLabel(
            "Create named subsets (filtered views) of your data to create unique ways to analysing and visualize your data.\n"
            "Subsets do not modify your original data"
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #666; font-style: italic; margin-bottom: 10px;")
        layout.addWidget(info)

        #main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)

        #left subset list
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)

        left_layout.addWidget(QLabel("Existing Subsets"))
        
        self.subset_list = QListWidget()
        self.subset_list.itemClicked.connect(self.on_subset_selected)
        left_layout.addWidget(self.subset_list)

        print("DEBUG init_ui: Created subset_list QListWidget")

        # buttons for the list
        list_buttons = QHBoxLayout()

        self.new_btn = AnimatedButton("New Subset", parent=self)
        self.new_btn.clicked.connect(self.create_new_subset)
        list_buttons.addWidget(self.new_btn)

        self.auto_create_btn = AnimatedButton("Auto create subsets by column", parent=self)
        self.auto_create_btn.clicked.connect(self.auto_create_subsets)
        list_buttons.addWidget(self.auto_create_btn)

        left_layout.addLayout(list_buttons)

        splitter.addWidget(left_widget)

        #right subset detials
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)

        self.details_group = AnimatedGroupBox("Subset Details", parent=self)
        details_layout = QVBoxLayout()

        #name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_label = QLabel("(Select a Subset)")
        self.name_label.setStyleSheet("font-weight: bold;")
        name_layout.addWidget(self.name_label)
        name_layout.addStretch()
        details_layout.addLayout(name_layout)

        #description
        details_layout.addWidget(QLabel("Description:"))
        self.description_label = QLabel("")
        self.description_label.setWordWrap(True)
        details_layout.addWidget(self.description_label)

        #stats
        stats_layout = QHBoxLayout()
        stats_layout.addWidget(QLabel("Rows:"))
        self.rows_label = QLabel("-")
        stats_layout.addWidget(self.rows_label)
        stats_layout.addSpacing(20)
        stats_layout.addWidget(QLabel("Created:"))
        self.created_label = QLabel("-")
        stats_layout.addWidget(self.created_label)
        stats_layout.addStretch()
        details_layout.addLayout(stats_layout)

        #filters
        details_layout.addWidget(QLabel("Filters:"))
        self.filters_text = QTextEdit()
        self.filters_text.setReadOnly(True)
        self.filters_text.setMaximumHeight(150)
        details_layout.addWidget(self.filters_text)

        # Action buttons
        action_buttons = QHBoxLayout()
        
        self.view_btn = AnimatedButton("View Data", parent=self)
        self.view_btn.clicked.connect(self.view_subset_data)
        self.view_btn.setEnabled(False)
        action_buttons.addWidget(self.view_btn)
        
        self.plot_btn = AnimatedButton("Plot Subset", parent=self)
        self.plot_btn.clicked.connect(self.plot_subset)
        self.plot_btn.setEnabled(False)
        action_buttons.addWidget(self.plot_btn)
        
        self.edit_btn = AnimatedButton("Edit", parent=self)
        self.edit_btn.clicked.connect(self.edit_subset)
        self.edit_btn.setEnabled(False)
        action_buttons.addWidget(self.edit_btn)
        
        self.delete_btn = AnimatedButton("Delete", parent=self)
        self.delete_btn.clicked.connect(self.delete_subset)
        self.delete_btn.setEnabled(False)
        action_buttons.addWidget(self.delete_btn)
        
        details_layout.addLayout(action_buttons)
        
        self.details_group.setLayout(details_layout)
        right_layout.addWidget(self.details_group)
        
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        splitter.setSizes([300, 600])
        
        layout.addWidget(splitter)

        # bottom buttons [lmao 
        bottom_buttons = QHBoxLayout()
        bottom_buttons.addStretch()
        
        close_btn = AnimatedButton("Close", parent=self)
        close_btn.clicked.connect(self.accept)
        bottom_buttons.addWidget(close_btn)
        
        layout.addLayout(bottom_buttons)
        self.setLayout(layout)

        print("DEBUG init_ui: UI initialization complete")
    
    def refresh_subset_list(self):
        """Refreshes the list of subsets"""
        print(f"DEBUG: resfresh_subset_list: Starting")
        print(f"DEBUG: refresh_subset_list: subset_list widget exists: {hasattr(self, "subset_list")}")

        if not hasattr(self, "subset_list"):
            print("ERROR: subset_list_widget not found")
            return
        
        self.subset_list.clear()
        print(f"DEBUG: refresh_subset_list: Cleared the list widget")

        subset_names = self.subset_manager.list_subsets()
        print(f"DEBUG refresh_subset_list: Found {len(subset_names)} subsets: {subset_names}")

        if not subset_names:
            placeholder = QListWidgetItem("(No subsets created yet)")
            placeholder.setFlags(Qt.ItemFlag.NoItemFlags)
            self.subset_list.addItem(placeholder)
            print(f"DEBUG: refresh_subset_list: Added placeholder for empty list")
            return
        
        for name in subset_names:
            try:
                subset = self.subset_manager.get_subset(name)
                if not subset:
                    print(f"WARNING: Subset '{name}' returned None from get_subset()")
                    continue

                row_text = f"{subset.row_count} rows" if subset.row_count > 0 else "? rows"
                item_text = f"{name} ({row_text})"
                print(f"DEBUG: refresh_subset_list: Adding item: {item_text}")

                item = QListWidgetItem(item_text)
                item.setData(Qt.ItemDataRole.UserRole, name)
                self.subset_list.addItem(item)
                print(f"DEBUG refresh_subset_list: Addded: {name}")
            
            except Exception as e:
                print(f"ERROR adding subset {name} to list: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        final_count = self.subset_list.count()
        print(f"DEBUG refresh_subset_list: Final item count: {final_count}")
    
    def on_subset_selected(self, item):
        """Subset selection"""
        # Check if item is the placeholder
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            return
        
        name = item.data(Qt.ItemDataRole.UserRole)
        subset = self.subset_manager.get_subset(name)

        if not subset:
            QMessageBox.warning(self, "Error", f"Subset '{name}' not found")
            return

        # Update UI with subset information
        self.name_label.setText(name)
        self.description_label.setText(subset.description or "No Description")
        self.rows_label.setText(str(subset.row_count) if subset.row_count > 0 else "?")
        self.created_label.setText(subset.created_at.strftime("%Y-%m-%d %H:%M"))

        # Format filters
        filters_text = f"Logic: {subset.logic}\n\nFilters:\n"
        for i, f in enumerate(subset.filters, 1):
            filters_text += f"{i}. {f['column']} {f['condition']} '{f['value']}'\n"
        
        self.filters_text.setText(filters_text)

        # Enable buttons
        self.view_btn.setEnabled(True)
        self.plot_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        
    def create_new_subset(self):
        """Create a new subset"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return
        
        dialog = CreateSubsetDialog(
            self.data_handler.df.columns.tolist(),
            self
        )

        if dialog.exec():
            config = dialog.get_config()
            try:
                self.subset_manager.create_subset(
                    name=config["name"],
                    description=config["description"],
                    filters=config["filters"],
                    logic=config["logic"]
                )

                #apply 
                self.subset_manager.apply_subset(self.data_handler.df, config["name"])

                self.refresh_subset_list()
                QMessageBox.information(self, "Success", f"Subset '{config['name']}' created")
            except ValueError as e:
                QMessageBox.warning(self, "Error", {str(e)})
    
    def auto_create_subsets(self):
        """Auto create subsets based on unique values in a column"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first")
            return
        
        column, ok = QInputDialog.getItem(
            self, 
            "Auto-Create Subsets",
            "Select column to split by:",
            self.data_handler.df.columns.tolist(),
            0,
            False
        )

        if ok and column:
            unique_count = self.data_handler.df[column].nunique()

            reply = QMessageBox.question(
                self,
                "Confirm",
                f"This will create {unique_count} subsets (one for each unique value in '{column}').\n\nContinue?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )

            if reply == QMessageBox.StandardButton.Yes:
                try:
                    created = self.subset_manager.create_subset_from_unique_values(
                        self.data_handler.df,
                        column
                    )

                    #apply 
                    for name in created:
                        self.subset_manager.apply_subset(self.data_handler.df, name)
                    
                    self.refresh_subset_list()
                    QMessageBox.information(
                        self,
                        "Success",
                        f"Created {len(created)} subsets from column '{column}'"
                    )
                except Exception as e:
                    QMessageBox.critical(self, "Error", str(e))
    
    def view_subset_data(self):
        """View the filtered data for a selected subset"""
        item = self.subset_list.currentItem()
        if not item:
            return
        
        name = item.data(Qt.ItemDataRole.UserRole)
        try:
            subset_df = self.subset_manager.apply_subset(self.data_handler.df, name)

            #show in new dialog
            viewer = SubsetDataViewer(subset_df, name, self)
            viewer.exec()
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
    
    def plot_subset(self):
        """Switch to plot tab with subset data active"""
        item = self.subset_list.currentItem()
        if not item:
            QMessageBox.warning(self, "No Selection", "Please select a subset you wish to visualize")
            return
        
        name = item.data(Qt.ItemDataRole.UserRole)
        if not name:
            return
        
        self.plot_subset_requested.emit(name)
        self.accept()

    def edit_subset(self):
        """Edit the selected subset"""
        item = self.subset_list.currentItem()
        if not item:
            return
        
        name = item.data(Qt.ItemDataRole.UserRole)
        subset = self.subset_manager.get_subset(name)

        dialog = CreateSubsetDialog(
            self.data_handler.df.columns.tolist(),
            self,
            existing_subset=subset
        )

        if dialog.exec():
            config = dialog.get_config()
            try:
                self.subset_manager.update_subset(
                    name=name,
                    description=config["description"],
                    filters=config["filters"],
                    logic=config["logic"]
                )

                # apply agian
                self.subset_manager.apply_subset(self.data_handler.df, name, use_cache=False)

                self.refresh_subset_list()
                self.on_subset_selected(item)
                QMessageBox.information(self, "Success", f"Subset '{name}' updated")
            except Exception as e:
                QMessageBox.warning(self, "Error", str(e))

    def delete_subset(self):
        """Delete the selected subset"""
        item = self.subset_list.currentItem()
        if not item:
            return
        
        name = item.data(Qt.ItemDataRole.UserRole)

        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete subset '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.subset_manager.delete_subset(name)
            self.refresh_subset_list()
            
            # Clear details
            self.name_label.setText("(Select a subset)")
            self.description_label.setText("")
            self.rows_label.setText("-")
            self.created_label.setText("-")
            self.filters_text.clear()
            
            # Disable buttons
            self.view_btn.setEnabled(False)
            self.plot_btn.setEnabled(False)
            self.edit_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
    
class CreateSubsetDialog(QDialog):
    """Dialog for creating andediting subsets"""

    def __init__(self, columns, parent=None, existing_subset=None):
        super().__init__(parent)
        self.columns = columns
        self.existing_subset = existing_subset
        self.filter_rows = []

        self.setWindowTitle("Create Subset" if not existing_subset else "Edit Subset")
        self.setModal(True)
        self.setGeometry(100, 100, 650, 500)

        self.init_ui()

        if existing_subset:
            self.load_existing_subset()
    
    def init_ui(self):
        """Init the UI"""
        layout = QVBoxLayout()

        #name for the new subsets
        if not self.existing_subset:
            name_layout = QHBoxLayout()
            name_layout.addWidget(QLabel("Subset Name:"))
            self.name_input = AnimatedLineEdit()
            self.name_input.setPlaceholderText("e.g. high_values, location_A, etc")
            name_layout.addWidget(self.name_input)
            layout.addLayout(name_layout)

        #description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_input = AnimatedLineEdit()
        self.desc_input.setPlaceholderText("Optional description")
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)
        
        layout.addSpacing(10)

        # Logic selection
        logic_layout = QHBoxLayout()
        logic_layout.addWidget(QLabel("Combine filters using:"))
        self.logic_combo = AnimatedComboBox()
        self.logic_combo.addItems(["AND", "OR"])
        self.logic_combo.setToolTip("AND = All conditions must be true\nOR = Any condition can be true")
        logic_layout.addWidget(self.logic_combo)
        logic_layout.addStretch()
        layout.addLayout(logic_layout)
        
        layout.addSpacing(10)

        # Filters
        layout.addWidget(QLabel("Filters:"))
        
        # Add up to 5 filter rows
        for i in range(5):
            filter_group = AnimatedGroupBox(f"Filter {i+1}", parent=self)
            filter_layout = QHBoxLayout()
            
            # Enable checkbox
            enable_check = AnimatedCheckBox("Active")
            enable_check.setChecked(i == 0)
            filter_layout.addWidget(enable_check)
            
            # Column
            column_combo = AnimatedComboBox()
            column_combo.addItems(self.columns)
            filter_layout.addWidget(QLabel("Column:"))
            filter_layout.addWidget(column_combo, 1)
            
            # Condition
            condition_combo = AnimatedComboBox()
            condition_combo.addItems(['==', '!=', '>', '<', '>=', '<=', 'contains'])
            filter_layout.addWidget(QLabel("Condition:"))
            filter_layout.addWidget(condition_combo, 1)
            
            # Value
            value_input = AnimatedLineEdit()
            value_input.setPlaceholderText("Value...")
            filter_layout.addWidget(QLabel("Value:"))
            filter_layout.addWidget(value_input, 2)
            
            filter_group.setLayout(filter_layout)
            layout.addWidget(filter_group)
            
            self.filter_rows.append({
                'group': filter_group,
                'active': enable_check,
                'column': column_combo,
                'condition': condition_combo,
                'value': value_input
            })
        
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()
        
        create_btn = AnimatedButton("Create" if not self.existing_subset else "Update", parent=self, base_color_hex="#4caf50", text_color_hex="white")
        create_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(create_btn)
        
        cancel_btn = AnimatedButton("Cancel", parent=self)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def load_existing_subset(self):
        """Load an existing subset into the form"""
        self.desc_input.setText(self.existing_subset.description)
        self.logic_combo.setCurrentText(self.existing_subset.logic)

        for i, filter_def in enumerate(self.existing_subset.filters):
            if i < len(self.filter_rows):
                row = self.filter_rows[i]
                row["active"].setChecked(True)
                row["column"].setCurrentText(filter_def["column"])
                row["condition"].setCurrentText(filter_def["condition"])
                row["value"].setText(str(filter_def["value"]))
    
    def validate_and_accept(self):
        """Validate and accept"""
        if not self.existing_subset:
            name = self.name_input.text().strip()
            if not name:
                QMessageBox.warning(self, "Validation Error", "Please enter a subset name")
                return
        
        #check if a filter is active
        active_count = sum(1 for row in self.filter_rows if row["active"].isChecked())
        if active_count == 0:
            QMessageBox.warning(self, "Validation Error", "Please activate at least one filter")
            return

        #check if active filters have a val
        for row in self.filter_rows:
            if row["active"].isChecked() and not row["value"].text().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter values for all active filters")
                return
        
        self.accept()

    def get_config(self):
        """Returns the subset config"""
        filters = []
        for row in self.filter_rows:
            if row['active'].isChecked():
                filters.append({
                    'column': row['column'].currentText(),
                    'condition': row['condition'].currentText(),
                    'value': row['value'].text().strip()
                })
        
        config = {
            'description': self.desc_input.text().strip(),
            'filters': filters,
            'logic': self.logic_combo.currentText()
        }
        
        if not self.existing_subset:
            config['name'] = self.name_input.text().strip()
        
        return config

class SubsetDataViewer(QDialog):
    """View data in a subset"""

    def __init__(self, df, subset_name, parent=None):
        super().__init__(parent)
        self.df = df
        self.setWindowTitle(f"Subset Data: {subset_name}")
        self.setGeometry(100, 100, 800, 600)

        layout = QVBoxLayout(self)

        # Info
        info = QLabel(f"Showing {len(df):,} rows × {len(df.columns)} columns")
        info.setStyleSheet("font-weight: bold;")
        layout.addWidget(info)
        
        # Table
        table = QTableWidget()
        table.setRowCount(len(df))
        table.setColumnCount(len(df.columns))
        table.setHorizontalHeaderLabels(df.columns.tolist())

        for row in range(len(df)):
            for col in range(len(df.columns)):
                value = df.iloc[row, col]
                item = QTableWidgetItem(str(value))
                table.setItem(row, col, item)

        table.resizeColumnsToContents()
        
        layout.addWidget(table)

        #export btn
        export_btn = AnimatedButton("Export this subset", parent=self)
        export_btn.clicked.connect(self.export_subset)
        layout.addWidget(export_btn)
        
        #close btn
        close_btn = AnimatedButton("Close", parent=self)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def export_subset(self):
        """Export the subset data into a file"""
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export Subset Data",
            "subset_data.csv",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;JSON Files (*.json)"
        )

        if filepath:
            try:
                if filepath.endswith(".csv"):
                    self.df.to_csv(filepath, index=False)
                elif filepath.endswith(".xlsx"):
                    self.df.to_excel(filepath, index=False)
                elif filepath.endswith(".json"):
                    self.df.to_json(filepath)

                QMessageBox.information(self, "Success", f"Subset exported to:\n{filepath}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to export: {str(e)}")

class FillMissingDialog(QDialog):
    """Dialog for the user to manipulate their data using the fill missing tool"""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.setWindowTitle("Fill Missing Values")
        self.setModal(True)
        self.resize(400, 300)

        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        info = QLabel("Select how to fill missing values (NaN) in your dataset.")
        info.setStyleSheet("color: #666;")
        layout.addWidget(info)

        layout.addSpacing(10)

        #this is the columns selection UI
        layout.addWidget(QLabel("Target Column:"))
        self.column_combo = AnimatedComboBox()
        self.column_combo.addItem("All Columns")
        self.column_combo.addItems(self.columns)
        layout.addWidget(self.column_combo)

        layout.addSpacing(10)

        #the user selects the method here
        layout.addWidget(QLabel("Fill Method:"))
        self.method_combo = AnimatedComboBox()
        self.method_combo.addItems([
            "Forward Fill (Previous Values)",
            "Backward Fill (Next Value)",
            "Static Value (Type Below)",
            "Mean (Average)",
            "Median (Middle Value)",
            "Mode (Most Common)"
        ])
        self.method_combo.currentTextChanged.connect(self.on_method_change)
        layout.addWidget(self.method_combo)

        #this is where the user types the value they want to fill. hidden by default unless method == staticvalue
        self.value_group = QWidget()
        value_layout = QVBoxLayout(self.value_group)
        value_layout.setContentsMargins(0,0,0,0)
        value_layout.addWidget(QLabel("Enter Value:"))
        self.value_input = AnimatedLineEdit()
        self.value_input.setPlaceholderText("e.g. 0, Unknown, 1.5")
        value_layout.addWidget(self.value_input)
        layout.addWidget(self.value_group)
        self.value_group.setVisible(False)

        layout.addStretch()

        #btns
        button_layout = QHBoxLayout()
        apply_btn = AnimatedButton(
            "Apply Fill",
            parent=self,
            base_color_hex="#4caf50",
            text_color_hex="white",
            font_weight="bold"
        )
        apply_btn.clicked.connect(self.accept)

        cancel_btn = AnimatedButton("Cancel", parent=self)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_method_change(self, text):
        """Show or hide the value intput box """
        is_static = "Static Value" in text
        self.value_group.setVisible(is_static)
    
    def get_config(self):
        """Get the user selection"""
        text = self.method_combo.currentText()
        method = "ffill"

        if "Forward" in text: method = "ffill"
        elif "Backward" in text: method = "bfill"
        elif "Static" in text: method = "static_value"
        elif "Mean" in text: method = "mean"
        elif "Median" in text: method = "median"
        elif "Mode" in text: method = "mode"

        return {
            "column": self.column_combo.currentText(),
            "method": method,
            "value": self.value_input.text()
        }

class DatabaseConnectionDialog(QDialog):
    """Dialog class for establishing a database connection and setup query"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Import from Database")
        self.setWindowIcon(QIcon("icons/menu_bar/database.png"))
        self.setMinimumWidth(600)

        self.details = {}

        main_layout = QVBoxLayout(self)

        #type selection
        db_type_layout = QHBoxLayout()
        db_type_layout.addWidget(QLabel("Database Type:"))
        self.db_type_combo = AnimatedComboBox()
        self.db_type_combo.addItems(["SQLite", "PostgreSQL", "MySQL"])
        self.db_type_combo.currentTextChanged.connect(self.on_db_type_changed)
        db_type_layout.addWidget(self.db_type_combo)
        main_layout.addLayout(db_type_layout)

        #connection details
        self.connection_group = AnimatedGroupBox("Connection Details", parent=self)
        self.connection_layout = QFormLayout()

        self.host_label = QLabel("Host:")
        self.host_input = AnimatedLineEdit("localhost")
        self.connection_layout.addRow(self.host_label, self.host_input)

        self.port_label = QLabel("Port:")
        self.port_input = AnimatedLineEdit()
        self.connection_layout.addRow(self.port_label, self.port_input)

        self.user_label = QLabel("User:")
        self.user_input = AnimatedLineEdit("postgres")
        self.connection_layout.addRow(self.user_label, self.user_input)

        self.password_label = QLabel("Password:")
        self.password_input = AnimatedLineEdit()
        self.password_input.setEchoMode(AnimatedLineEdit.EchoMode.Password)
        self.connection_layout.addRow(self.password_label, self.password_input)

        self.dbname_label = QLabel("Database:")
        self.dbname_input = AnimatedLineEdit("postgres")
        self.connection_layout.addRow(self.dbname_label, self.dbname_input)

        # SQLITE specific
        self.sqlite_layout = QHBoxLayout()
        self.sqlite_label = QLabel("Database File:")
        self.sqlite_path_input = AnimatedLineEdit()
        self.sqlite_path_input.setPlaceholderText("Click 'Browse' to select a .db, .sqlite, or .sqlite3 file")
        self.sqlite_browse_btn = AnimatedButton("Browse", parent=self)
        self.sqlite_browse_btn.clicked.connect(self.browse_sqlite_file)
        self.sqlite_layout.addWidget(self.sqlite_path_input)
        self.sqlite_layout.addWidget(self.sqlite_browse_btn)
        self.sqlite_widget = QWidget()
        self.sqlite_widget.setLayout(self.sqlite_layout)
        self.connection_layout.addRow(self.sqlite_label, self.sqlite_widget)

        self.connection_group.setLayout(self.connection_layout)
        main_layout.addWidget(self.connection_group)

        #querey editor
        query_group = AnimatedGroupBox("SQL Query", parent=self)
        query_layout = QVBoxLayout()
        self.query_editor = QTextEdit()
        self.query_editor.setPlaceholderText("Enter your SQL query here, e.g.,\nSELECT * FROM my_table LIMIT 1000;")
        self.query_editor.setFontFamily("Courier")
        self.query_editor.setMinimumHeight(150)
        query_layout.addWidget(self.query_editor)

        #query validation
        self.query_status_label = QLabel(" ")
        self.query_status_label.setStyleSheet("font-weight: bold;")
        query_layout.addWidget(self.query_status_label)

        query_group.setLayout(query_layout)
        main_layout.addWidget(query_group)

        #buttons
        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.on_accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)

        self.query_editor.textChanged.connect(self.on_query_changed)

        self.on_db_type_changed("SQLite")
        self.on_query_changed()
    
    def on_query_changed(self) -> None:
        """Validate the query"""
        query = self.query_editor.toPlainText().strip()

        if not query:
            self.query_status_label.setText("✘ Query cannot be empty")
            self.query_status_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
            self.query_status_label.setVisible(True)
        elif query.lower().startswith("select"):
            self.query_status_label.setText("✔ Valid Query")
            self.query_status_label.setStyleSheet("color: #388e3c; font-weight: bold;")
            self.query_status_label.setVisible(True)
        else:
            self.query_status_label.setText("✘ Invalid Query (Must be SELECT)")
            self.query_status_label.setStyleSheet("color: #d32f2f; font-weight: bold;")
            self.query_status_label.setVisible(True)

    def on_db_type_changed(self, db_type) -> None:
        """Show or hide fields based on db type"""
        is_sqlite = (db_type == "SQLite")

        #toggle server fields
        self.host_label.setVisible(not is_sqlite)
        self.host_input.setVisible(not is_sqlite)
        self.port_label.setVisible(not is_sqlite)
        self.port_input.setVisible(not is_sqlite)
        self.user_label.setVisible(not is_sqlite)
        self.user_input.setVisible(not is_sqlite)
        self.password_label.setVisible(not is_sqlite)
        self.password_input.setVisible(not is_sqlite)
        self.dbname_label.setVisible(not is_sqlite)
        self.dbname_input.setVisible(not is_sqlite)

        #toggle SQLITE fields
        self.sqlite_label.setVisible(is_sqlite)
        self.sqlite_widget.setVisible(is_sqlite)

        #set defaults on port and usr
        if db_type == "PostgreSQL":
            self.port_input.setText("5432")
            self.user_input.setText("postgres")
            self.dbname_input.setText("postgres")
        elif db_type == "MySQL":
            self.port_input.setText("3306")
            self.user_input.setText("root")
            self.dbname_input.setText("")
    
    def browse_sqlite_file(self) -> None:
        """Open a file dialog to find a local SQLite database file"""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select SQLite Database file",
            "",
            "Database Files (*.db *.sqlite *.sqlite3);;All Files (*)"
        )
        if filepath:
            self.sqlite_path_input.setText(filepath)
    
    def on_accept(self):
        """Validate the input and build connection string before acception"""
        db_type = self.db_type_combo.currentText()
        query = self.query_editor.toPlainText().strip()
        connection_string = ""

        if not query:
            QMessageBox.warning(self, "Input Error", "Please enter a SQL query.")
            return
        
        if not query.lower().startswith("select"):
            QMessageBox.warning(
                self,
                "Invalid Query Syntax",
                "The SQL query must be a 'SELECT' statement."
            )
            return
        
        try:
            if db_type == "SQLite":
                db_path = self.sqlite_path_input.text().strip()
                if not db_path:
                    QMessageBox.warning(self, "Input Error", "Please provide a path to the SQLite database file.")
                    return
                db_path_abs = str(Path(db_path).resolve())
                if sys.platform == "win32":
                    connection_string = f"sqlite:///{db_path_abs}"
                else:
                    connection_string = f"sqlite:///{db_path_abs}"
            
            else:
                host = self.host_input.text().strip()
                port = self.port_input.text().strip()
                user = self.user_input.text().strip()
                password = self.password_input.text().strip()
                dbname = self.dbname_input.text().strip()

                if not all([host, port, user, dbname]):
                    QMessageBox.warning(self, "Input Error", "Please fill in all connection details (Host, Port, User, Database).")
                    return
                
                if db_type == "PostgreSQL":
                    # postgresqsl+psycopg2://user:password@host:port/dbname
                    connection_string = f"Postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
                elif db_type == "MySQL":
                    # mysql+mysqlconnector://user:password@host:port/dbname
                    connection_string = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{dbname}"
            
            self.details = {
                "db_type": db_type,
                "connection_string": connection_string,
                "query": query
            }
            self.accept()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to establish a proper connection string: {str(e)}")
    
    def get_details(self):
        """Returns the connection string and query"""
        return self.details.get("db_type"), self.details.get("connection_string"), self.details.get("query")
