import keyword
from typing import Optional, List
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout
from ui.widgets import DataPlotStudioButton, DataPlotStudioLineEdit


class RenameColumnDialog(QDialog):
    """Dialog for renaming a column"""

    def __init__(self, column_name: str, existing_columns: Optional[List[str]] = None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Rename Column")
        self.setModal(True)
        self.resize(400, 150)

        self.column_name: str = column_name
        self.existing_columns: List[str] = existing_columns if existing_columns else []
        self.new_name_input: Optional[DataPlotStudioLineEdit] = None
        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        # Old name display
        old_name_layout = QHBoxLayout()
        old_name_layout.addWidget(QLabel("Current Name:"))
        old_name_display = DataPlotStudioLineEdit()
        old_name_display.setText(self.column_name)
        old_name_display.setReadOnly(True)
        old_name_layout.addWidget(old_name_display)
        layout.addLayout(old_name_layout)

        # New name input
        new_name_layout = QHBoxLayout()
        new_name_layout.addWidget(QLabel("New Name:"))
        self.new_name_input = DataPlotStudioLineEdit()
        self.new_name_input.setPlaceholderText(f"Enter new name for '{self.column_name}'")
        self.new_name_input.setMinimumWidth(200)
        new_name_layout.addWidget(self.new_name_input)
        layout.addLayout(new_name_layout)

        layout.addSpacing(20)

        # Button layout
        button_layout = QHBoxLayout()

        ok_button = DataPlotStudioButton("Rename", parent=self)
        ok_button.setMinimumWidth(100)
        ok_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(ok_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def validate_and_accept(self):
        """Validate new name before accepting"""
        if not self.new_name_input:
            return
        new_name: str = self.new_name_input.text().strip()

        if not new_name:
            QMessageBox.warning(self, "Validation Error", "New column name cannot be empty or whitespace only.")
            return
        if new_name == self.column_name:
            QMessageBox.warning(self, "Validation Error", "New name must be different from current name")
            return
        if new_name in self.existing_columns:
            QMessageBox.warning(self, "Validation Error", f"Column '{new_name}' already exists in the dataset.")
            return
        if keyword.iskeyword(new_name):
            QMessageBox.warning(self, "Validation Error", f"'{new_name}' is a reserved Python keyword and cannot be used as a column name.")
            return
        if "`" in new_name:
            QMessageBox.warning(self, "Validation Error", "Column names cannot contain backticks (`).")
            return

        self.accept()

    def get_new_name(self) -> str:
        """Return the new column name"""
        return self.new_name_input.text().strip()