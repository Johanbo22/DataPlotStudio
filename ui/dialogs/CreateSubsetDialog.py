from turtle import textinput
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QStackedWidget, QDateEdit, QWidget, QSizePolicy
from PyQt6.QtCore import QDate
import pandas as pd

from ui.widgets import (
    DataPlotStudioButton,
    DataPlotStudioComboBox,
    DataPlotStudioGroupBox,
    DataPlotStudioLineEdit,
    DataPlotStudioDoubleSpinBox,
    DataPlotStudioCheckBox
)


class CreateSubsetDialog(QDialog):
    """Dialog for creating andediting subsets"""

    def __init__(self, data_handler, parent=None, existing_subset=None):
        super().__init__(parent)
        self.data_handler = data_handler
        self.columns = list(self.data_handler.df.columns) if self.data_handler.df is not None else []
        self.existing_subset = existing_subset
        self.filter_rows = []

        self.setWindowTitle("Create Subset" if not existing_subset else "Edit Subset")
        self.setModal(True)
        self.resize(750, 600)

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
            self.name_input = DataPlotStudioLineEdit()
            self.name_input.setPlaceholderText("e.g. high_values, location_A, etc")
            name_layout.addWidget(self.name_input)
            layout.addLayout(name_layout)

        #description
        desc_layout = QHBoxLayout()
        desc_layout.addWidget(QLabel("Description:"))
        self.desc_input = DataPlotStudioLineEdit()
        self.desc_input.setPlaceholderText("Optional description")
        desc_layout.addWidget(self.desc_input)
        layout.addLayout(desc_layout)

        layout.addSpacing(10)
        
        #filter headers
        layout.addWidget(QLabel("Filters:"))
        
        for i in range(5):
            filter_group = DataPlotStudioGroupBox(f"Filter {i+1}", parent=self)
            filter_layout = QHBoxLayout()
            
            logic_combo = DataPlotStudioComboBox()
            logic_combo.addItems(["AND", "OR"])
            logic_combo.setFixedWidth(70)
            logic_combo.setToolTip("Operator with previeous result")
            
            if i == 0:
                logic_combo.setVisible(False)
                filter_layout.addWidget(QLabel("       "))
            else:
                filter_layout.addWidget(logic_combo)

            # activation checkbox
            enable_check = DataPlotStudioCheckBox("Active")
            enable_check.setChecked(i == 0)
            filter_layout.addWidget(enable_check)
            
            column_combo = DataPlotStudioComboBox()
            column_combo.addItems(self.columns)
            column_combo.setMinimumWidth(120)
            filter_layout.addWidget(QLabel("Column:"))
            filter_layout.addWidget(column_combo, 2)

            condition_combo = DataPlotStudioComboBox()
            condition_combo.addItems(['==', '!=', '>', '<', '>=', '<=', 'contains', 'in', 'Is Null', 'Is Not Null'])
            condition_combo.setMinimumWidth(100)
            filter_layout.addWidget(QLabel("Condition:"))
            filter_layout.addWidget(condition_combo, 1)
            
            # Stacking widget
            input_stack = QStackedWidget()
            
            # 0 == text 
            text_input = DataPlotStudioLineEdit()
            text_input.setPlaceholderText("Value...")
            input_stack.addWidget(text_input)
            
            # 1 == numbers
            number_input = DataPlotStudioDoubleSpinBox()
            number_input.setRange(-999999999.0, 999999999.0)
            number_input.setDecimals(4)
            input_stack.addWidget(number_input)
            
            # 2 == categories
            category_input = DataPlotStudioComboBox()
            input_stack.addWidget(category_input)
            
            # 3 == dates
            date_input = QDateEdit()
            date_input.setCalendarPopup(True)
            date_input.setDate(QDate.currentDate())
            input_stack.addWidget(date_input)
            
            # 4 == empty
            input_stack.addWidget(QWidget())
            
            filter_layout.addWidget(QLabel("Value:"))
            filter_layout.addWidget(input_stack, 3)
            
            filter_group.setLayout(filter_layout)
            layout.addWidget(filter_group)
            
            row_data = {
                'group': filter_group,
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
                }
            }
            self.filter_rows.append(row_data)
            
            # Signals
            column_combo.currentTextChanged.connect(lambda _, idx=i: self.update_row_ui(idx))
            condition_combo.currentTextChanged.connect(lambda _, idx=i: self.update_row_ui(idx))
            
            self.update_row_ui(i)
        layout.addStretch()

        # Buttons
        button_layout = QHBoxLayout()

        create_btn = DataPlotStudioButton("Create" if not self.existing_subset else "Update", parent=self, base_color_hex="#4caf50", text_color_hex="white")
        create_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(create_btn)

        cancel_btn = DataPlotStudioButton("Cancel", parent=self)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)

        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def update_row_ui(self, row_index):
        """Updates the input widget based on the column data type"""
        row = self.filter_rows[row_index]
        col_name = row["column"].currentText()
        condition = row["condition"].currentText()
        stack = row["stack"]
        
        if condition in ["Is Null", "Is Not Null"]:
            stack.setCurrentIndex(4)
            return
        
        df = self.data_handler.df
        if df is None or col_name not in df.columns:
            stack.setCurrentIndex(0)
            return
        
        col_dtype = df[col_name].dtype
        
        if pd.api.types.is_numeric_dtype(col_dtype):
            stack.setCurrentIndex(1)
        elif pd.api.types.is_datetime64_any_dtype(col_dtype):
            stack.setCurrentIndex(3)
        elif pd.api.types.is_object_dtype(col_dtype) or pd.api.types.is_categorical_dtype(col_dtype):
            unique_vals = df[col_name].dropna().unique()
            if len(unique_vals) < 50:
                stack.setCurrentIndex(2)
                combo = row["inputs"]["category"]
                current_text = combo.currentText()
                if combo.count() != len(unique_vals):
                    combo.clear()
                    combo.addItems([str(value) for value in sorted(unique_vals)])
                    combo.setCurrentText(current_text)
            else:
                stack.setCurrentIndex(0)
        else:
            stack.setCurrentIndex(0)
    
    def get_current_value(self, row):
        """Retrieve the value from the active widget"""
        idx = row["stack"].currentIndex()
        if idx == 0:
            return row["inputs"]["text"].text()
        if idx == 1:
            return row["inputs"]["number"].value()
        if idx == 2:
            return row["inputs"]["category"].currentText()
        if idx == 3:
            return row["inputs"]["date"].date().toString("yyyy-MM-dd")
        return None

    def load_existing_subset(self):
        """Load an existing subset into the form"""
        self.desc_input.setText(self.existing_subset.description)
        
        filters = self.existing_subset.filters
        
        legacy_logic = getattr(self.existing_subset, "logic", "AND")
        
        for i, row in enumerate(self.filter_rows):
            if i < len(filters):
                f_def = filters[i]
                row["active"].setChecked(True)
                row["column"].setCurrentText(f_def["column"])
                row["condition"].setCurrentText(f_def["condition"])
                
                val = f_def["value"]
                row["inputs"]["text"].setText(str(val))
                try:
                    if isinstance(val, (int, float)):
                        row["inputs"]["number"].setValue(float(val))
                except:
                    pass
                
                if i > 0:
                    op = f_def.get("operator", legacy_logic)
                    row["logic"].setCurrentIndex(op if op else "AND")

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

        for row in self.filter_rows:
            if row["active"].isChecked():
                cond = row["condition"].currentText()
                val = self.get_current_value(row)
                if cond not in ["Is Null", "Is Not Null"] and (val is None or (isinstance(val, str) and not val.strip())):
                    QMessageBox.warning(self, "Validation Error", "Please enter values for all active filters")
                    return
        self.accept()

    def get_config(self):
        """Returns the subset config"""
        filters = []
        for i, row in enumerate(self.filter_rows):
            if row['active'].isChecked():
                filters.append({
                    'operator': row['logic'].currentText() if i > 0 else None,
                    'column': row['column'].currentText(),
                    'condition': row['condition'].currentText(),
                    'value': self.get_current_value(row)
                })

        config = {
            'description': self.desc_input.text().strip(),
            'filters': filters,
            'logic': "COMPLEX"
        }

        if not self.existing_subset:
            config['name'] = self.name_input.text().strip()

        return config