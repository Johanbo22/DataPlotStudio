from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QFormLayout, QGroupBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QMessageBox, QPushButton, QSplitter, QVBoxLayout, QWidget


class MeltDialog(QDialog):
    """Dialog for using the melt function"""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Melt Data")
        self.setModal(True)
        self.resize(700, 600)
        self.columns = columns
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

        layout.addStretch()

        #buttons
        button_layout = QHBoxLayout()

        apply_button = QPushButton("Melt Data")
        apply_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; font-weight: bold; }")
        apply_button.setMinimumWidth(120)
        apply_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(apply_button)

        cancel_button = QPushButton("Cancel")
        cancel_button.setMinimumWidth(120)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

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