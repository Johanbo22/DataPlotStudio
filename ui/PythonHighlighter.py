from PyQt6.QtGui import QColor, QFont, QSyntaxHighlighter, QTextCharFormat


import re


class PythonHighlighter(QSyntaxHighlighter):
    """Simple syntax highligher for Python code"""

    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        #keywords
        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#ff79c6"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = ["def", "class", "if", "else", "elif", "while", "for", "in",
            "return", "try", "except", "import", "from", "as", "True",
            "False", "None", "and", "or", "not", "break", "continue",
            "pass", "lambda", "with", "is", "global", "raise", "yield"]
        for word in keywords:
            pattern = re.compile(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, keyword_format))

        #builin funcs
        builtin_format = QTextCharFormat()
        builtin_format.setForeground(QColor("#8be9fd"))
        builtins = [
            "print", "range", "len", "list", "dict", "set", "str", "int",
            "float", "bool", "zip", "enumerate", "min", "max", "sum",
            "abs", "sorted", "tuple", "super", "isinstance", "open", "type"
        ]
        for word in builtins:
            pattern = re.compile(f"\\b{word}\\b")
            self.highlighting_rules.append((pattern, builtin_format))

        #self and cls
        self_format = QTextCharFormat()
        self_format.setForeground(QColor("#ffb86c"))
        self_format.setFontItalic(True)
        self.highlighting_rules.append((re.compile("\\bself\\b"), self_format))
        self.highlighting_rules.append((re.compile("\\bcls\\b"), self_format))

        #decorators
        decorator_format = QTextCharFormat()
        decorator_format.setForeground(QColor("#ffb86c"))
        self.highlighting_rules.append((re.compile("@[A-Za-z0-9_]+"), decorator_format))

        #

        #strings
        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#f1fa8c"))
        self.highlighting_rules.append((re.compile("\"\"\".*?\"\"\"", re.DOTALL), string_format))
        self.highlighting_rules.append((re.compile("\'\'\'.*?\'\'\'", re.DOTALL), string_format))
        self.highlighting_rules.append((re.compile("\".*?\""), string_format))
        self.highlighting_rules.append((re.compile("\'.*?\'"), string_format))

        #numbers
        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#bd93f9"))
        self.highlighting_rules.append((re.compile(r"\b[0-9]+\b"), number_format))
        self.highlighting_rules.append((re.compile(r"\b0x[0-9A-Fa-f]+\b"), number_format))
        self.highlighting_rules.append((re.compile(r"\b[0-9]*\.[0-9]+\b"), number_format))

        #functions
        func_format = QTextCharFormat()
        func_format.setForeground(QColor("#50fa7b"))
        self.highlighting_rules.append((re.compile("\\b[A-Za-z0-9_]+(?=\\()"), func_format))

        #comment
        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6272a4"))
        self.highlighting_rules.append((re.compile(r"(^|\s+)#[^\n]*"), comment_format))

    def highlightBlock(self, text):
        for pattern, format in self.highlighting_rules:
            if pattern.pattern.startswith("(^|\\s+)#"):
                match = pattern.search(text)
                while match:
                    start_index = match.start(0)
                    if match.group(1).strip() == "":
                        hash_index = text.find('#', start_index)
                        if hash_index != 1:
                            self.setFormat(hash_index, len(text) - hash_index, format)
                    else:
                        pass
                    match = pattern.search(text, match.end(0))
            else:
                expression = pattern.search(text)
                while expression:
                    index = expression.start()
                    length = expression.end() - index
                    self.setFormat(index, length, format)
                    expression = pattern.search(text, index + length)