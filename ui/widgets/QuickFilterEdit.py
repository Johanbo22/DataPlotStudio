from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QTextCursor, QIcon, QKeyEvent
from PyQt6.QtWidgets import QPlainTextEdit, QCompleter, QToolButton, QStyle
from ui.FilterSyntaxHighlighter import FilterSyntaxHighlighter

class QuickFilterEdit(QPlainTextEdit):
    """A qplaintext edit that is a one line that supports the filter syntax highlighting found in FilterSyntaxhighliter. Used to highligh syntax witin the quickfilter option in the plotting canvas"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.highlighter = FilterSyntaxHighlighter(self.document())
        
        # setyp to be one line
        self.setFixedHeight(34)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self.setTabChangesFocus(True)
        self.setPlaceholderText("Enter filter expression...")
        
        # Autocompleter
        self.completer = QCompleter(self)
        self.completer.setWidget(self)
        self.completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.completer.activated.connect(self.insert_completion)
        # keywords
        self.base_keywords = [
            "mean", "sum", "min", "max", "count", "std", "var", "median", "and", "or", "not", "in", "is", "NaN", "None", "True", "False", "abs", "round", "len", "str", "int", "float"
        ]
        self.current_keywords = list(self.base_keywords)
        self.update_completer_model()
        
        # Setyp for clear button
        self.clear_button = QToolButton(self)
        self.clear_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_DialogCloseButton))
        self.clear_button.setCursor(Qt.CursorShape.ArrowCursor)
        self.clear_button.setStyleSheet("QToolButton { border: none; background: transparent; }")
        self.clear_button.clicked.connect(self.clear)
        self.clear_button.hide()

        self._base_border = "1.5px solid #a0a0a0"
        self._focus_border = "1.5px solid #0078d7"
        self._bg_empty = "white"
        self._bg_active = "#fffde7"
        
        self.setStyleSheet(f"""
            QPlainTextEdit {{
                border: {self._base_border};
                border-radius: 3px;
                padding: 4px;
                padding-right: 25px;
                background-color: white; /* Default empty state */
                color: black; 
                font-family: Consolas, monospace;
                font-size: 10pt;
            }}
            QPlainTextEdit[hasText="true"] {{
                background-color: #fffde7;
            }}
            QPlainTextEdit:focus {{
                border: {self._focus_border};
            }}
        """)
        self.setProperty("hasText", False)
        self.textChanged.connect(self._on_text_changed)
    
    def set_columns(self, columns):
        self.highlighter.set_columns(columns)
        self.current_keywords = sorted(list(set(self.base_keywords + columns)))
        self.update_completer_model()
    
    def update_completer_model(self):
        model = QStringListModel(self.current_keywords, self.completer)
        self.completer.setModel(model)
    
    def insert_completion(self, completion: str):
        tc = self.textCursor()
        extra = len(completion) - len(self.completer.completionPrefix())
        tc.movePosition(QTextCursor.MoveOperation.Left)
        tc.movePosition(QTextCursor.MoveOperation.EndOfWord)
        tc.insertText(completion[-extra:])
        self.setTextCursor(tc)
    
    def text_under_cursor(self) -> str:
        tc = self.textCursor()
        tc.select(QTextCursor.SelectionType.WordUnderCursor)
        return tc.selectedText()
    
    def _on_text_changed(self):
        has_text = bool(self.toPlainText().strip())
        self.clear_button.setVisible(has_text)
        
        if self.property("hasText") != has_text:
            self.setProperty("hasText", has_text)
            self.style().unpolish(self)
            self.style().polish(self)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        sz = self.clear_button.sizeHint()
        x = self.width() - sz.width() - 5
        y = (self.height() - sz.height()) // 2
        self.clear_button.move(x, y)
    
    def keyPressEvent(self, event: QKeyEvent):
        if self.completer and self.completer.popup().isVisible():
            if event.key() in (Qt.Key.Key_Enter, Qt.Key.Key_Return, Qt.Key.Key_Escape, 
                                Qt.Key.Key_Tab, Qt.Key.Key_Backtab, 
                                Qt.Key.Key_Up, Qt.Key.Key_Down):
                event.ignore()
                return

        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            event.ignore()
            return
        
        is_shortcut = (event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_Space)

        if not self.completer or not self.completer.popup().isVisible():
            super().keyPressEvent(event)
        else:
            super().keyPressEvent(event)

        ctrl_or_shift = event.modifiers() & (Qt.KeyboardModifier.ControlModifier | Qt.KeyboardModifier.ShiftModifier)
        if not is_shortcut and (ctrl_or_shift or not self.toPlainText()):
            return

        completion_prefix = self.text_under_cursor()

        if not is_shortcut and (len(completion_prefix) < 1):
            self.completer.popup().hide()
            return

        if completion_prefix != self.completer.completionPrefix():
            self.completer.setCompletionPrefix(completion_prefix)
            self.completer.popup().setCurrentIndex(self.completer.completionModel().index(0, 0))

        cr = self.cursorRect()
        cr.setWidth(self.completer.popup().sizeHintForColumn(0) + self.completer.popup().verticalScrollBar().sizeHint().width())
        self.completer.complete(cr)
    
    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)
    
    def clear(self):
        self.setPlainText("")