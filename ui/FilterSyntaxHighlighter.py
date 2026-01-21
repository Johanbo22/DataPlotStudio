from PyQt6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QFont
import re

class FilterSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.column_names = []

        self.operator_format = QTextCharFormat()
        self.operator_format.setFontWeight(QFont.Weight.Bold)
        self.operator_format.setForeground(QColor("#d32f2f"))

        self.column_format = QTextCharFormat()
        self.column_format.setFontItalic(True)
        self.column_format.setForeground(QColor("#1976d2"))

        operators = [
            "==", "!=", "<=", ">=", "<", ">", " and ", " or ", " not ", " in ", "&", "|", "~"
        ]
        self.operator_patterns = [re.escape(op).strip() for op in operators]

    def set_columns(self, columns):
        self.column_names = columns
        self.rehighlight()
    
    def highlightBlock(self, text):
        ## Highlight the operators
        for pattern in self.operator_patterns:
            regex_pattern = r'\b' + pattern + 'r\b' if pattern.isalpha() else re.escape(pattern)
            expression = re.compile(regex_pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), self.operator_format)
        
        # Hightligh columns
        for col in sorted(self.column_names, key=len, reverse=True):
            pattern = re.escape(col)
            expression = re.compile(pattern)
            for match in expression.finditer(text):
                self.setFormat(match.start(), match.end() - match.start(), self.column_format)