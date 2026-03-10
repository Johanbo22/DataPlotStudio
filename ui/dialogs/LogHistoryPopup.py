from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QWidget, QLabel, QApplication, QHBoxLayout, QPushButton, QSizeGrip, QLineEdit, QScrollBar
from PyQt6.QtCore import Qt, QTimer, QPoint
from PyQt6.QtGui import QClipboard, QMouseEvent, QKeyEvent
from typing import List, Optional, Any
from ui.styles.widget_styles import Dialog

class LogHistoryPopup(QWidget):
    """Popup dialog for the viewing of log"""
    def __init__(self, history: List[str], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowFlags(Qt.WindowType.Popup | Qt.WindowType.FramelessWindowHint)
        self.resize(600, 400)
        self.setMinimumSize(450, 250)
        self._full_history: List[str] = history.copy()
        self._drag_pos: Optional[QPoint] = None
        self.setStyleSheet(Dialog.LogHistoryPopup)
        self.setObjectName("LogPopup")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)
        
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(8, 8, 8, 8)

        title_label = QLabel("Log History")
        title_label.setObjectName("HeaderTitle")
        
        self.search_bar = QLineEdit()
        self.search_bar.setObjectName("SearchBar")
        self.search_bar.setPlaceholderText("Filter logs...")
        self.search_bar.setFixedWidth(180)
        self.search_bar.textChanged.connect(self._apply_filters)
        
        self.error_filter_btn = QPushButton("Errors")
        self.error_filter_btn.setObjectName("ErrorFilter")
        self.error_filter_btn.setProperty("class", "FilterPill")
        self.error_filter_btn.setCheckable(True)
        self.error_filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.error_filter_btn.clicked.connect(self._apply_filters)
        
        self.warn_filter_btn = QPushButton("Warnings")
        self.warn_filter_btn.setObjectName("WarningFilter")
        self.warn_filter_btn.setProperty("class", "FilterPill")
        self.warn_filter_btn.setCheckable(True)
        self.warn_filter_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.warn_filter_btn.clicked.connect(self._apply_filters)
        
        self.wrap_btn = QPushButton("Wrap")
        self.wrap_btn.setObjectName("WrapToggle")
        self.wrap_btn.setProperty("class", "FilterPill")
        self.wrap_btn.setCheckable(True)
        self.wrap_btn.setChecked(True)
        self.wrap_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.wrap_btn.clicked.connect(self._toggle_word_wrap)
        
        # copy to clipboard functionality
        self.copy_btn = QPushButton("Copy")
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setProperty("class", "IconButton")
        self.copy_btn.clicked.connect(self._copy_to_clipboard)
        
        self.clear_btn = QPushButton("Clear")
        self.clear_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clear_btn.setProperty("class", "IconButton")
        self.clear_btn.clicked.connect(self._clear_logs)

        close_btn = QPushButton("✕")
        close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        close_btn.setProperty("class", "IconButton")
        close_btn.clicked.connect(self.close)
        
        header_layout.addWidget(title_label)
        header_layout.addSpacing(15)
        header_layout.addWidget(self.search_bar)
        header_layout.addWidget(self.error_filter_btn)
        header_layout.addWidget(self.warn_filter_btn)
        header_layout.addWidget(self.wrap_btn)
        header_layout.addStretch()
        header_layout.addWidget(self.copy_btn)
        header_layout.addWidget(self.clear_btn)
        header_layout.addWidget(close_btn)
        
        main_layout.addLayout(header_layout)

        self.text_view = QTextEdit()
        self.text_view.setReadOnly(True)
        
        self._render_logs(self._full_history)
        
        main_layout.addWidget(self.text_view)

        grip_layout = QHBoxLayout()
        grip_layout.setContentsMargins(0, 0, 0, 0)
        grip_layout.addStretch()
        size_grip = QSizeGrip(self)
        size_grip.setFixedSize(12, 12)
        grip_layout.addWidget(size_grip, 0, Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight)
        
        main_layout.addLayout(grip_layout)
        self.search_bar.setFocus()

    def _render_logs(self, log_list: List[str]) -> None:
        """Method to place HTML logs and scrolls to the bottom"""
        if not log_list:
            self.text_view.setHtml("<i style='color: #888'>No logs to display.</i>")
        else:
            html_content = "<br>".join(log_list)
            self.text_view.setHtml(f"<div>{html_content}</div>")
        
        cursor = self.text_view.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        self.text_view.setTextCursor(cursor)
    
    def _apply_filters(self, *args: Any) -> None:
        """Search bar and quick.filter to find logs"""
        query_lower = self.search_bar.text().lower()
        show_errors_only = self.error_filter_btn.isChecked()
        show_warnings_only = self.warn_filter_btn.isChecked()
        
        error_hex = "#ff0000"
        warning_hex = "#ffaa00"
        
        filtered: List[str] = []
        for log in self._full_history:
            if query_lower and query_lower not in log.lower():
                continue
            
            if show_errors_only or show_warnings_only:
                is_error = error_hex in log.lower()
                is_warn = warning_hex in log.lower()
                
                if show_errors_only and show_warnings_only:
                    if not (is_error or is_warn):
                        continue
                elif show_errors_only and not is_error:
                    continue
                elif show_warnings_only and not is_warn:
                    continue
            
            filtered.append(log)
        
        self._render_logs(filtered)
    
    def append_live_log(self, html_log: str) -> None:
        """Updater from StatusBar"""
        self._full_history.append(html_log)
        
        history_log_max_length = 200
        if len(self._full_history) > history_log_max_length:
            self._full_history.pop(0)
            if not self.search_bar.text() and not self.error_filter_btn.isChecked() and not self.warn_filter_btn.isChecked():
                self._render_logs(self._full_history)
                return
        
        if self.search_bar.text() or self.error_filter_btn.isChecked() or self.warn_filter_btn.isChecked():
            self._apply_filters()
            return
        
        current_filter = self.search_bar.text().lower()
        if current_filter and current_filter not in html_log.lower():
            return
        
        v_bar = self.text_view.verticalScrollBar()
        is_at_bottom = v_bar.value() >= (v_bar.maximum() - 10)
        self.text_view.append(html_log)
        
        if is_at_bottom:
            cursor = self.text_view.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            self.text_view.setTextCursor(cursor)
    
    def _copy_to_clipboard(self) -> None:
        """Copy plain text of the logs to the system clipboard."""
        clipboard: QClipboard = QApplication.clipboard()
        clipboard.setText(self.text_view.toPlainText())
        
        self.copy_btn.setText("Copied!")
        
        QTimer.singleShot(2000, lambda: self.copy_btn.setText("Copy"))
    
    def _clear_logs(self) -> None:
        """Clear local text view and flush the parent status's log history"""
        self._full_history.clear()
        self._render_logs(self._full_history)
        parent = self.parent()
        if hasattr(parent, "log_history"):
            parent.log_history.clear()
            
    def _toggle_word_wrap(self) -> None:
        """Toggle between wrapped words and straight text"""
        if self.wrap_btn.isChecked():
            self.text_view.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        else:
            self.text_view.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_F:
            self.search_bar.setFocus()
            self.search_bar.selectAll()
            event.accept()
            return
        
        if event.key() == Qt.Key.Key_Escape:
            if self.search_bar.text():
                self.search_bar.clear()
                self.search_bar.setFocus()
            else:
                self.close()
            event.accept()
            return
        
        super().keyPressEvent(event)
    
    def mousePressEvent(self, event: QMouseEvent) -> None:
        """Capture initial click position for window dragging"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        """Move the window relative to mouse drag"""
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos is not None:
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()