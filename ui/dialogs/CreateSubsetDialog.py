from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox


from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit


class CreateSubsetDialog(QDialog):
    """Dialog for creating andediting subsets"""

    def __init__(self, columns, parent=None, existing_subset=None):
        super().__init__(parent)
        self.columns = columns
        self.existing_subset = existing_subset
        self.filter_rows = []

        self.setWindowTitle("Create Subset" if not existing_subset else "Edit Subset")
        self.setModal(True)
        self.resize(650, 500)

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

        # Logic selection
        logic_layout = QHBoxLayout()
        logic_layout.addWidget(QLabel("Combine filters using:"))
        self.logic_combo = DataPlotStudioComboBox()
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
            filter_group = DataPlotStudioGroupBox(f"Filter {i+1}", parent=self)
            filter_layout = QHBoxLayout()

            # Enable checkbox
            enable_check = DataPlotStudioCheckBox("Active")
            enable_check.setChecked(i == 0)
            filter_layout.addWidget(enable_check)

            # Column
            column_combo = DataPlotStudioComboBox()
            column_combo.addItems(self.columns)
            filter_layout.addWidget(QLabel("Column:"))
            filter_layout.addWidget(column_combo, 1)

            # Condition
            condition_combo = DataPlotStudioComboBox()
            condition_combo.addItems(['==', '!=', '>', '<', '>=', '<=', 'contains'])
            filter_layout.addWidget(QLabel("Condition:"))
            filter_layout.addWidget(condition_combo, 1)

            # Value
            value_input = DataPlotStudioLineEdit()
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

        create_btn = DataPlotStudioButton("Create" if not self.existing_subset else "Update", parent=self, base_color_hex="#4caf50", text_color_hex="white")
        create_btn.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(create_btn)

        cancel_btn = DataPlotStudioButton("Cancel", parent=self)
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