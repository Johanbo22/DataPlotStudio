# ui/dialogs/ComputedColumnDialog.py
import ast
import re
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QAbstractItemView,
    QGridLayout,
    QTreeWidget,
    QTreeWidgetItem,
    QSplitter,
    QWidget,
)
from PyQt6.QtCore import Qt
from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedListWidget import DataPlotStudioListWidget
from ui.dialogs.CodeEditor import CodeEditor
from ui.PythonHighlighter import PythonHighlighter


class ComputedColumnDialog(QDialog):
    """Dialog for computing and creating new columns"""

    def __init__(self, columns, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create Computed Column")
        self.columns = columns
        self.resize(900, 700)
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
        equals_label.setStyleSheet(
            "font-size: 14pt; font-weight: bold; margin-right: 5px;"
        )
        expression_layout.addWidget(equals_label)

        self.expression_input = CodeEditor()
        self.expression_input.setPlaceholderText("e.g., Price * Quantity")
        self.expression_input.setMaximumHeight(100)
        self.highlighter = PythonHighlighter(self.expression_input.document())
        self.expression_input.setStyleSheet("""
            QPlainTextEdit {
                background-color: #282a36;
                color: #f8f8f2;
                border: 1px solid #555;
                border-radius: 4px;
            }
        """)
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
            (")", ")", 2, 4),
        ]
        for label, value, row, column in operators:
            operator_button = DataPlotStudioButton(label)
            operator_button.setToolTip(f"Insert '{label}'")
            operator_button.clicked.connect(
                lambda checked, v=value: self.insert_text(v)
            )
            operators_layout.addWidget(operator_button, row, column)

        input_layout.addLayout(operators_layout)

        help_text = QLabel(
            "Use column names exactly as they appear below.\n"
            "If columns have spaces, wrap them in backticks: `Column Name`"
        )
        help_text.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        help_text.setWordWrap(True)
        input_layout.addWidget(help_text)

        input_group.setLayout(input_layout)
        layout.addWidget(input_group)

        helpers_splitter = QSplitter(Qt.Orientation.Horizontal)

        column_widget = QWidget()
        column_layout = QVBoxLayout(column_widget)
        column_layout.setContentsMargins(0, 0, 5, 0)

        insert_column_info = QLabel("Available Columns:")
        insert_column_info.setStyleSheet(
            "color: 666; font-weight: bold; font-size: 9pt;"
        )
        insert_column_info.setWordWrap(True)
        column_layout.addWidget(insert_column_info)

        self.column_list = DataPlotStudioListWidget()
        self.column_list.setAlternatingRowColors(True)
        self.column_list.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.column_list.addItems(self.columns)
        self.column_list.itemDoubleClicked.connect(self.insert_column_into_expression)
        column_layout.addWidget(self.column_list)

        helpers_splitter.addWidget(column_widget)

        # Fcuntoions math
        function_widget = QWidget()
        function_layout = QVBoxLayout(function_widget)
        function_layout.setContentsMargins(5, 0, 0, 0)

        insert_func_info = QLabel("Function Library:")
        insert_func_info.setStyleSheet(
            "color: #666; font-weight: bold; font-size: 9pt;"
        )
        function_layout.addWidget(insert_func_info)

        self.function_tree = QTreeWidget()
        self.function_tree.setHeaderHidden(True)
        self.function_tree.itemDoubleClicked.connect(self.insert_function)
        self.populate_functions()
        function_layout.addWidget(self.function_tree)

        helpers_splitter.addWidget(function_widget)

        helpers_splitter.setStretchFactor(0, 1)
        helpers_splitter.setStretchFactor(1, 1)

        layout.addWidget(helpers_splitter, 1)

        # Buttons
        button_layout = QHBoxLayout()
        self.create_button = DataPlotStudioButton(
            "Create Column",
            parent=self,
            base_color_hex="#27ae60",
            text_color_hex="white",
            hover_color_hex="#2ecc71",
            pressed_color_hex="#1e8a4c",
            typewriter_effect=True,
        )
        self.create_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.create_button)

        self.cancel_button = DataPlotStudioButton("Cancel", parent=self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)

    def populate_functions(self):
        """Populate the function library with some functions (math, trigs, etc)"""
        functions = {
            "Math": ["abs", "sqrt", "log", "exp", "round", "ceil", "floor", "pow"],
            "Trigonometry": ["sin", "cos", "tan", "degrees", "radians"],
            "String Accessor": [
                ".str.upper()",
                ".str.lower()",
                ".str.title()",
                ".str.strip()",
                ".str.len()",
                ".str.replace('old', 'new')",
            ],
        }
        for category, funcs in functions.items():
            parent = QTreeWidgetItem(self.function_tree)
            parent.setText(0, category)
            parent.setExpanded(True)
            for func in funcs:
                item = QTreeWidgetItem(parent)
                item.setText(0, func)

    def insert_function(self, item, column):
        """Insert the selected function into the expression"""
        if item.childCount() > 0:
            return

        func_text = item.text(0)
        self.insert_text(func_text)

    def insert_text(self, text):
        """Insert the text at the current cursor position and refocus"""
        self.expression_input.insertPlainText(text)
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
        expression = self.expression_input.toPlainText().strip()

        if not name:
            QMessageBox.warning(self, "Validation Error", "Please enter a column name")
            return
        if not name.isidentifier():
            QMessageBox.warning(
                self,
                "Validation Error",
                "Column name must be a valid Python identifier.",
            )
            return
        if not expression:
            QMessageBox.warning(self, "Validation Error", "Please enter an expression")
            return
        if name in self.columns:
            QMessageBox.warning(
                self,
                "Validation Error",
                f"Column '{name}' already exists. Please choose another name",
            )
            return

        try:
            sanitized_expr = re.sub(r"`[^`]+`", "variable", expression)
            ast.parse(sanitized_expr)
        except SyntaxError as Error:
            QMessageBox.warning(
                self,
                "Syntax Error",
                f"Invalid expression syntax:\n{Error.msg}\nLine: {Error.lineno}",
            )
            return
        except Exception as Error:
            QMessageBox.warning(
                self, "Validation Error", f"Error validating expression: {str(Error)}"
            )
            return

        self.accept()

    def get_data(self) -> tuple[str, str]:
        return (
            self.name_input.text().strip(),
            self.expression_input.toPlainText().strip(),
        )
