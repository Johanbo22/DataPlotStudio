from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat, QTextDocument
from typing import List, Tuple, Pattern
import re


class PythonHighlighter(QSyntaxHighlighter):
    """Simple syntax highligher for Python code"""

    def __init__(self, document: QTextDocument) -> None:
        super().__init__(document)
        self.highlighting_rules: List[Tuple[Pattern[str], QTextCharFormat]] = []

        #keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#ff79c6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ["def", "class", "if", "else", "elif", "while", "for", "in",
            "return", "try", "except", "import", "from", "as", "True",
            "False", "None", "and", "or", "not", "break", "continue",
            "pass", "lambda", "with", "is", "global", "raise", "yield", "async", "await", "match", "case"]
        keywords_pattern = r'\b(?:' + '|'.join(keywords) + r')\b'
        self.highlighting_rules.append((re.compile(keywords_pattern), keyword_format))
        

        #builin funcs
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#8be9fd"))
        builtins = [
            "print", "range", "len", "list", "dict", "set", "str", "int",
            "float", "bool", "zip", "enumerate", "min", "max", "sum",
            "abs", "sorted", "tuple", "super", "isinstance", "open", "type"
        ]
        builtins_pattern = r'\b(?:' + '|'.join(builtins) + r')\b'
        self.highlighting_rules.append((re.compile(builtins_pattern), builtin_format))

        #self and cls
        self_format = QTextCharFormat()
        self_format.setForeground(QColor("#ffb86c"))
        self_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile("\\bself\\b"), self_format))
        self.highlighting_rules.append((re.compile("\\bcls\\b"), self_format))

        #decorators
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#ffb86c"))
        self.highlighting_rules.append((re.compile(r"@[A-Za-z0-9_\.]+"), decorator_format))

        #strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#f1fa8c"))
        self.highlighting_rules.append((re.compile(r'"[^"\\]*(\\.[^"\\]*)*"'), string_format))
        self.highlighting_rules.append((re.compile(r"'[^'\\]*(\\.[^'\\]*)*'"), string_format))
        
        # multi line strings
        self.multi_string_format = QTextCharFormat()
        self.multi_string_format.setForeground(QColor("#f1fa8c"))
        
        self.double_multi_pattern = re.compile(r'"""')
        self.single_multi_pattern = re.compile(r"'''")

        #numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#bd93f9"))
        self.highlighting_rules.append((re.compile(r"\b(?:0[xX][0-9A-Fa-f]+|0[bB][01]+|0[oO][0-7]+|[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)\b"), number_format))

        #functions
        func_format = QTextCharFormat()
        func_format.setForeground(QColor("#50fa7b"))
        self.highlighting_rules.append((re.compile(r"\b[A-Za-z0-9_]+(?=\()"), func_format))
        #comment
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6272a4"))
        self.highlighting_rules.append((re.compile(r"#[^\n]*"), comment_format))
        
    def highlightBlock(self, text: str) -> None:
        """
        Applies syntax highlighting for a single block of text,\n
        including multi line strings
        """
        for pattern, text_format in self.highlighting_rules:
            expression_match = pattern.search(text)
            while expression_match:
                start_index = expression_match.start()
                match_length = expression_match.end() - start_index
                self.setFormat(start_index, match_length, text_format)
                expression_match = pattern.search(text, start_index + match_length)
        
        default_state: int = 0
        self.setCurrentBlockState(default_state)
        
        double_quote_multiline_state: int = 1
        self._highlight_multiline(text, double_quote_multiline_state, self.double_multi_pattern)
        
        single_quote_multiline_state: int = 2
        if self.currentBlockState() == default_state:
            self._highlight_multiline(text, single_quote_multiline_state, self.single_multi_pattern)
    
    def _highlight_multiline(self, text: str, state_id: int, delimiter_pattern: re.Pattern) -> None:
        start_index: int = 0
        
        if self.previousBlockState() == state_id:
            start_index = 0
        else:
            match = delimiter_pattern.search(text)
            start_index = match.start() if match else -1
        
        while start_index >= 0:
            match = delimiter_pattern.search(text, start_index + 3)
            if match:
                end_index = match.start()
                match_length = end_index - start_index + 3
                self.setFormat(start_index, match_length, self.multi_string_format)
                
                next_match = delimiter_pattern.search(text, start_index + match_length)
                start_index = next_match.start() if next_match else -1
            else:
                self.setCurrentBlockState(state_id)
                self.setFormat(start_index, len(text) - start_index, self.multi_string_format)
                break