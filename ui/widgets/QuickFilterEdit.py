from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, pyqtProperty, Qt
from PyQt6.QtGui import QColor, QSyntaxHighlighter, QTextCharFormat, QFont
from PyQt6.QtWidgets import QLineEdit, QPlainTextEdit
import re
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

        self._base_border = "1.5px solid #a0a0a0"
        self._focus_border = "1.5px solid #0078d7"
        self._bg_empty = "white"
        self._bg_active = "#fffde7"

        self.update_style()
        self.textChanged.connect(self._on_text_changed)
    
    def set_columns(self, columns):
        self.highlighter.set_columns(columns)
    
    def _on_text_changed(self):
        self.update_style()
    
    def update_style(self):
        has_text = len(self.toPlainText().strip()) > 0
        bg = self._bg_active if has_text else self._bg_empty

        self.setStyleSheet(f"""
            QPlainTextEdit {{
                border: {self._base_border};
                border-radius: 3px;
                padding: 4px;
                background-color: {bg};
                font-family: Consolas, monospace;
                font-size: 10pt;
            }}
            QPlainTextEdit:focus {{
                border: {self._focus_border};
            }}
        """)
    
    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            event.ignore()
            return
        super().keyPressEvent(event)
    
    def text(self):
        return self.toPlainText()

    def setText(self, text):
        self.setPlainText(text)
    
    def clear(self):
        self.setPlainText("")