from PyQt6.QtWidgets import (QTextEdit, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt

class LogHistoryPopup(QWidget):
    """Popup dialog for the viewing of log"""
    def __init__(self, history: list[str], parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(600, 400)
        self.setStyleSheet("background-color: #2b2b2b; border: 1px solid #555;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)

        text_view = QTextEdit()
        text_view.setReadOnly(True)
        text_view.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                font-family: Consolas, 'Courier New', monospace;
                border: none;
                padding: 5px;
            }
        """)

        if not history:
            text_view.setHtml("<i style='color: #888'>Nothing logged yet.</i>")
        else:
            html_content = "<br>".join(history)
            text_view.setHtml(f"<div>{html_content}</div>")
        
        cursor = text_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        text_view.setTextCursor(cursor)

        layout.addWidget(text_view)