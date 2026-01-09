from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox


from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit


class FilterAdvancedDialog(QDialog):
    """Dialog for advanced filtering with multiple conditions"""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Advanced Filter")
        self.setModal(True)
        self.resize(650, 450)

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
        self.logic_combo = DataPlotStudioComboBox()
        self.logic_combo.addItems(["AND", "OR"])
        self.logic_combo.setToolTip("AND = All conditions must be True\nOR = Any condition can be True")
        logic_layout.addWidget(self.logic_combo)
        logic_layout.addStretch()
        layout.addLayout(logic_layout)

        layout.addSpacing(19)


        self.filter_rows = []
        for i in range(5):
            #create group bxo ofr each filter element
            filter_group = DataPlotStudioGroupBox(f"Filter {i+1}", parent=self)
            filter_layout = QHBoxLayout()

            #checkbox
            enable_check = DataPlotStudioCheckBox("Active")
            enable_check.setChecked(i == 0)
            filter_layout.addWidget(enable_check)

            # Column selector
            column_combo = DataPlotStudioComboBox()
            column_combo.addItems(self.columns)
            filter_layout.addWidget(QLabel("Column:"))
            filter_layout.addWidget(column_combo, 1)

            # Condition selector
            condition_combo = DataPlotStudioComboBox()
            condition_combo.addItems(['==', '!=', '>', '<', '>=', '<=', 'contains', 'in'])
            filter_layout.addWidget(QLabel("Condition:"))
            filter_layout.addWidget(condition_combo, 1)

            # Value input
            value_input = DataPlotStudioLineEdit()
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

        apply_button = DataPlotStudioButton("Apply Filters", parent=self, base_color_hex="#e8f5fa")
        apply_button.setMinimumWidth(120)
        apply_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(apply_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self, base_color_hex="#e8f5fa")
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