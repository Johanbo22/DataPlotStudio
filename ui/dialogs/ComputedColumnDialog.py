# ui/dialogs/ComputedColumnDialog.py
import operator
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QListWidget, QAbstractItemView, QWidget, QGridLayout)
from PyQt6.QtCore import Qt
from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedListWidget import DataPlotStudioListWidget

class ComputedColumnDialog(QDialog):
    """Dialog for computing and creating new columns"""

    def __init__(self, columns, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create Computed Column")
        self.columns = columns
        self.resize(700, 650)
        self.init_ui()

    def init_ui(self) -> None:
        layout = QVBoxLayout()

        # Input boxes
        input_group = DataPlotStudioGroupBox("Column Details")
        input_layout = QVBoxLayout()

        input_layout.addWidget(QLabel("New Column Name"))
        self.name_input = DataPlotStudioLineEdit()
        self.name_input.setPlaceholderText("e.g., Total_Price")
        input_layout.addWidget(self.name_input)

        input_layout.addWidget(QLabel("Expression"))
        expression_layout = QHBoxLayout()
        equals_label = QLabel("=")
        equals_label.setStyleSheet("font-size: 14pt; font-weight: bold; margin-right: 5px;")
        expression_layout.addWidget(equals_label)

        self.expression_input = DataPlotStudioLineEdit()
        self.expression_input.setPlaceholderText("e.g., Price * Quantity")
        expression_layout.addWidget(self.expression_input)
        
        input_layout.addLayout(expression_layout)

        # Operator butons
        operators_layout = QGridLayout()
        operators_layout.setContentsMargins(0, 5, 0, 5)
        operators_layout.setSpacing(5)

        # three rows of operators: artihmetic, comparison, logical
        operators = [
            ("+", " + ", 0, 0), 
            ("-", " - ", 0, 1), 
            ("*", " * ", 0, 2), 
            ("/", " / ", 0, 3), 
            ("% (Mod)", " % ", 0, 4), 
            ("** (Pow)", " ** ", 0, 5),
            ("==", " == ", 1, 0), 
            ("!=", " != ", 1, 1), 
            (">", " > ", 1, 2), 
            ("<", " < ", 1, 3), 
            (">=", " >= ", 1, 4), 
            ("<=", " <= ", 1, 5),
            ("& (AND)", " & ", 2, 0), 
            ("| (OR)", " | ", 2, 1), 
            ("~ (NOT)", " ~", 2, 2),
            ("(", "(", 2, 3), 
            (")", ")", 2, 4)
        ]
        for label, value, row, column in operators:
            operator_button = DataPlotStudioButton(label)
            operator_button.setToolTip(f"Insert '{label}'")
            operator_button.clicked.connect(lambda checked, v=value: self.insert_text(v))
            operators_layout.addWidget(operator_button, row, column)

        input_layout.addLayout(operators_layout)

        help_text = QLabel(
            "Supported operators: +, -, *, /, ** (power).\n"
            "Use column names exactly as they appear below.\n"
            "If columns have spaces, wrap them in backticks: `Column Name`"
        )
        help_text.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        help_text.setWordWrap(True)
        input_layout.addWidget(help_text)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        # List of columns from the dataframe, helps with case sensitivity
        column_group = DataPlotStudioGroupBox("Available Columns")
        column_layout = QVBoxLayout()

        insert_column_info = QLabel("Double click to insert a column")
        insert_column_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        insert_column_info.setWordWrap(True)

        self.column_list = DataPlotStudioListWidget()
        self.column_list.setAlternatingRowColors(True)
        # Inorder for double click to properly work disable the editing trigger.
        self.column_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.column_list.addItems(self.columns)
        self.column_list.itemDoubleClicked.connect(self.insert_column_into_expression)
        column_layout.addWidget(insert_column_info)
        column_layout.addWidget(self.column_list)

        column_group.setLayout(column_layout)
        layout.addWidget(column_group)

        # Buttons
        button_layout = QHBoxLayout()
        self.create_button = DataPlotStudioButton("Create Column", parent=self, base_color_hex="#27ae60", text_color_hex="white", hover_color_hex="#2ecc71", pressed_color_hex="#1e8a4c", typewriter_effect=True)
        self.create_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.create_button)

        self.cancel_button = DataPlotStudioButton("Cancel", parent=self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def insert_text(self, text):
        """Insert the text at the current cursor position and refocus """
        self.expression_input.insert(text)
        self.expression_input.setFocus()
    
    def insert_column_into_expression(self, item) -> None:
        """Insert the selected column into the expression with backticks if nessecary"""
        column_name = item.text()
        
        # Check if string not a valid identifier and if not add backticks
        if not column_name.isidentifier():
            column_name = f"`{column_name}`"
        
        self.insert_text(column_name)
        
    def validate_and_accept(self) -> None:
        name = self.name_input.text().strip()
        expression = self.expression_input.text().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a column name")
            return
        if not expression:
            QMessageBox.warning(self, "Validation Error", "Please enter an expression")
        if name in self.columns:
            QMessageBox.warning(self, "Validation Error", f"Column '{name}' already exists. Please choose another name")
        
        self.accept()
    
    def get_data(self) -> tuple[str, str]:
        return self.name_input.text().strip(), self.expression_input.text().strip()