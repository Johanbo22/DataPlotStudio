from PyQt6.QtWidgets import (QTextEdit, QVBoxLayout, QWidget)
from PyQt6.QtCore import Qt

class LogHistoryPopup(QWidget):
    """Popup dialog for the viewing of log"""
    def __init__(self, history: list[str], parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.setFixedSize(600, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #252526;
                border: 1px solid #454545;
                border-radius: 4px;
            }
            QTextEdit {
                background-color: transparent;
                color: #cccccc;
                font-family: Consolas, monospace;
                font-size: 11px;
                border: none;
                padding: 8px;
            }
            /* Custom Scrollbar */
            QScrollBar:vertical {
                background: #252526;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background: #424242;
                min-height: 20px;
                border-radius: 5px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background: #686868;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(1, 1, 1, 1)

        text_view = QTextEdit()
        text_view.setReadOnly(True)

        if not history:
            text_view.setHtml("<i style='color: #888'>Nothing logged yet.</i>")
        else:
            html_content = "<br>".join(history)
            text_view.setHtml(f"<div>{html_content}</div>")
        
        cursor = text_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        text_view.setTextCursor(cursor)

        layout.addWidget(text_view)