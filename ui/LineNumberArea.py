from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QWidget


class LineNumberArea(QWidget):
    """widget to draw line numbers in editor"""
    def __init__(self, editor) -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:
        return QSize(self.editor.lineNumberAreaWidth(), 0)

    def paintEvent(self, event):
        self.editor.lineNumberAreaPaintEvent(event)