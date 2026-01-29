from flask.config import T
from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox


from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QStackedWidget, QDateEdit, QSizePolicy, QWidget
from PyQt6.QtCore import QDate
import pandas as pd

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox
from ui.widgets.AnimatedDoubleSpinBox import DataPlotStudioDoubleSpinBox
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit


class FilterAdvancedDialog(QDialog):
    """Dialog for advanced filtering with multiple conditions"""

    def __init__(self, data_handler, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Filter")
        self.setModal(True)
        self.resize(800, 500)

        self.data_handler = data_handler
        self.columns = list(self.data_handler.df.columns) if self.data_handler.df is not None else []
        self.filters = []
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        instruction_label = QLabel("Construct filter query:")
        instruction_label.setFont(QFont("Consolas", 10, QFont.Weight.Bold))
        layout.addWidget(instruction_label)
        layout.addSpacing(10)

        layout.addSpacing(19)

        # preview text
        self.preview_label = QLabel("Preview: No filters active")
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; color: #d0d0d0; padding: 10px; border: 1px solid #ccc;")

        self.filter_rows = []
        for i in range(5):
            #create group bxo ofr each filter element
            filter_group = DataPlotStudioGroupBox(f"Filter {i+1}", parent=self)
            filter_layout = QHBoxLayout()
            
            logic_combo = DataPlotStudioComboBox()
            logic_combo.addItems(["AND", "OR"])
            logic_combo.setFixedWidth(70)
            if i == 0:
                logic_combo.setVisible(False)
                filter_layout.addWidget(QLabel("       "))
            else:
                filter_layout.addWidget(logic_combo)

            #checkbox
            enable_check = DataPlotStudioCheckBox("On")
            enable_check.setChecked(i == 0)
            filter_layout.addWidget(enable_check)

            # Column selector
            column_combo = DataPlotStudioComboBox()
            column_combo.addItems(self.columns)
            column_combo.setMinimumWidth(120)
            filter_layout.addWidget(QLabel("Column:"))
            filter_layout.addWidget(column_combo, 2)

            # Condition selector
            condition_combo = DataPlotStudioComboBox()
            condition_combo.addItems(['==', '!=', '>', '<', '>=', '<=', 'contains', 'in', "Is Null", "Is Not Null"])
            condition_combo.setMinimumWidth(100)
            filter_layout.addWidget(QLabel("Condition:"))
            filter_layout.addWidget(condition_combo, 1)
            
            input_stack = QStackedWidget()

            # text input
            text_input = DataPlotStudioLineEdit()
            text_input.setPlaceholderText("Enter value...")
            input_stack.addWidget(text_input)
            
            # Numerical inputs
            number_input = DataPlotStudioDoubleSpinBox()
            number_input.setRange(-999999999, 999999999)
            number_input.setDecimals(4)
            input_stack.addWidget(number_input)
            
            # categorical INputs
            category_input = DataPlotStudioComboBox()
            input_stack.addWidget(category_input)
            
            # date input
            date_input = QDateEdit()
            date_input.setCalendarPopup(True)
            date_input.setDate(QDate.currentDate())
            input_stack.addWidget(date_input)
            
            empty_widget = QWidget()
            input_stack.addWidget(empty_widget)
            
            filter_layout.addWidget(QLabel("Value:"))
            filter_layout.addWidget(input_stack, 3)

            filter_group.setLayout(filter_layout)
            layout.addWidget(filter_group)

            row_data = {
                'logic': logic_combo,
                'active': enable_check,
                'column': column_combo,
                'condition': condition_combo,
                'stack': input_stack,
                'inputs': {
                    'text': text_input,
                    'number': number_input,
                    'category': category_input,
                    'date': date_input
                },
                'group': filter_group
            }
            self.filter_rows.append(row_data)
            
            column_combo.currentTextChanged.connect(lambda _, idx=i: self.update_row_ui(idx))
            condition_combo.currentTextChanged.connect(lambda _, idx=i: self.update_row_ui(idx))
            
            enable_check.stateChanged.connect(self.update_preview)
            logic_combo.currentTextChanged.connect(self.update_preview)
            text_input.textChanged.connect(self.update_preview)
            number_input.valueChanged.connect(self.update_preview)
            category_input.currentTextChanged.connect(self.update_preview)
            date_input.dateChanged.connect(self.update_preview)
            
            self.update_row_ui(i)
        layout.addSpacing(15)

        
        layout.addWidget(self.preview_label)

        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()

        apply_button = DataPlotStudioButton("Apply Filters", parent=self, base_color_hex="#e8f5fa")
        apply_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(apply_button)

        clear_button = DataPlotStudioButton("Clear Filters", parent=self, base_color_hex="#ffebee")
        clear_button.clicked.connect(self.clear_fields)
        button_layout.addWidget(clear_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self, base_color_hex="#e8f5fa")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.update_preview()
    
    def update_row_ui(self, row_index):
        """Update the input widget based on the datatype of selected column and the selected condition"""
        row = self.filter_rows[row_index]
        col_name = row["column"].currentText()
        condition = row["condition"].currentText()
        stack = row["stack"]
        
        # First handle null checks 
        if condition in ["Is Null", "Is Not Null"]:
            stack.setCurrentIndex(4)
            return
        
        # Determine the datatype from the dataframe
        df = self.data_handler.df
        if df is None or col_name not in df.columns:
            stack.setCurrentIndex(0)
            return
        
        col_dtype = df[col_name].dtype
        
        if pd.api.types.is_numeric_dtype(col_dtype):
            stack.setCurrentIndex(1)
            # maybe change the range of the spinny box to adapt to data range?
            # TODO row["inputs"]["number"].setRange(min_val, max_val)
        elif pd.api.types.is_datetime64_any_dtype(col_dtype):
            stack.setCurrentIndex(3)
        
        elif pd.api.types.is_object_dtype(col_dtype) or pd.api.types.is_categorical_dtype(col_dtype):
            unique_values = df[col_name].dropna().unique()
            if len(unique_values) < 50:
                stack.setCurrentIndex(2)
                combo = row["inputs"]["category"]
                if combo.count() != len(unique_values):
                    combo.clear()
                    combo.addItems([str(value) for value in sorted(unique_values)])
            else:
                stack.setCurrentIndex(0)
        else:
            stack.setCurrentIndex(0)
        
        self.update_preview()
    
    def get_current_value(self, row):
        """Retrieve the value from the current active widget"""
        stack_index = row["stack"].currentIndex()
        
        if stack_index == 0:
            return row["inputs"]["text"].text()
        elif stack_index == 1:
            return row["inputs"]["number"].value()
        elif stack_index == 2:
            return row["inputs"]["category"].currentText()
        elif stack_index == 3:
            return row["inputs"]["date"].date().toString("yyyy-MM-dd")
        elif stack_index == 4:
            return None
        return ""

    def clear_fields(self):
        """Reset the filter fields to default"""
        for i, row in enumerate(self.filter_rows):
            row["active"].setChecked(i == 0)
            row['inputs']['text'].clear()
            row['inputs']['number'].setValue(0)
            if i > 0:
                row['logic'].setCurrentIndex(0)

        self.update_preview()

    def update_preview(self):
        """update the filter preview"""
        preview_parts = []
        
        for i, row in enumerate(self.filter_rows):
            if not row["active"].isChecked():
                continue
            
            col = row["column"].currentText()
            cond = row["condition"].currentText()
            val = self.get_current_value(row)
            
            part = ""
            if cond in ["Is Null", "Is Not Null"]:
                part = f"{col} {cond}"
            else:
                part = f"{col} {cond} '{val}'"
            
            if i > 0:
                logic = row["logic"].currentText()
                if preview_parts:
                    part = f" {logic} {part}"
            
            preview_parts.append(part)
        
        text = "".join(preview_parts)
        if text:
            self.preview_label.setText(f"Preview: {text}")
        else:
            self.preview_label.setText("Preview: No filters active")

    def validate_and_accept(self):
        """Validate filters before accepting"""
        active_count = sum(1 for row in self.filter_rows if row['active'].isChecked())

        if active_count == 0:
            QMessageBox.warning(self, "Validation Error", "Please activate at least one filter")
            return

        # Check that active filters have values
        for row in self.filter_rows:
            if row["active"].isChecked():
                cond = row["condition"].currentText()
                val = self.get_current_value(row)
                if cond in ["Is Null", "Is Not Null"]:
                    if isinstance(val, str) and not val.strip():
                        QMessageBox.warning(self, "Validation Error", "Please enter a value for all active filters")
                        return
        self.accept()

    def get_filters(self):
        """Return active filters with logical operator"""
        filters = []
        for i, row in enumerate(self.filter_rows):
            if row["active"].isChecked():
                filters.append({
                    "operator": row["logic"].currentText() if i > 0 else None,
                    "column": row["column"].currentText(),
                    "condition": row["condition"].currentText(),
                    "value": self.get_current_value(row)
                })
        
        return {
            "logic": "COMPLEX",
            "filters": filters
        }