from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox
from ui.dialogs import CodeEditor
from ui.PythonHighlighter import PythonHighlighter

import sys
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QPlainTextEdit


from datetime import datetime

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox
from ui.animations.PlotGeneratedAnimation import PlotGeneratedAnimation

class StreamRedirector:
    """Redirects stdout/stderr to a plain text widget from the code editor"""
    def __init__(self, widget: QPlainTextEdit, original_stream, color: str = None):
        self.widget = widget
        self.original_stream = original_stream
        self.color = color
    
    def write(self, text: str):
        if self.original_stream:
            self.original_stream.write(text)
        
        cursor = self.widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if self.color:
            fmt = cursor.charFormat()
            original_format = cursor.charFormat()
            fmt.setForeground(QColor(self.color))
            cursor.setCharFormat(fmt)
            cursor.insertText(text)
            cursor.setCharFormat(original_format)
        else:
            cursor.insertText(text)
        
        self.widget.setTextCursor(cursor)
        self.widget.ensureCursorVisible()
    
    def flush(self):
        if self.original_stream:
            self.original_stream.flush()


class ScriptEditorDialog(QDialog):
    """A dialog for editing and running custo python plotting scripts"""

    run_script_signal = pyqtSignal(str)

    def __init__(self, initial_code="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Python Console")
        self.resize(800, 600)
        self.setModal(False)

        self.script_history = []
        self.run_counter = 0

        self.init_ui(initial_code)
        
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        self.stdout_redirector = StreamRedirector(self.console_output, self.original_stdout, color="#f8f8f2")
        self.stderr_redirector = StreamRedirector(self.console_output, self.original_stderr, color="#ff5555")
        
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector
        
    def close_event(self, event):
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        super().closeEvent(event)

    def init_ui(self, code):
        layout = QVBoxLayout()
        self.setLayout(layout)

        #header and information
        info_layout = QHBoxLayout()
        info_label = QLabel("<b>Script</b><br>Edit the <code>create_plot(df)</code> function below. Click the 'Run' button to update the plot.")
        info_label.setStyleSheet("color: #333;")
        info_layout.addWidget(info_label)
        layout.addLayout(info_layout)

        #security
        security_label = QLabel("Restricted Environment: System calls are blocked in this editor.")
        security_label.setStyleSheet("color: #d32f2f; font-size: 11pt; font-style: italic;")
        layout.addWidget(security_label)

        #tools
        toolbar = QHBoxLayout()
        self.auto_sync_check = DataPlotStudioCheckBox("Auto-update from GUI (This will overwrite changes)")
        self.auto_sync_check.setChecked(True)
        self.auto_sync_check.setToolTip("If checked, changing settings from the GUI will overwrite the code here")
        toolbar.addWidget(self.auto_sync_check)

        toolbar.addSpacing(20)
        toolbar.addWidget(QLabel("History:"))
        self.history_combo = DataPlotStudioComboBox()
        self.history_combo.setMinimumWidth(400)
        self.history_combo.addItem("Select to restore...")
        self.history_combo.activated.connect(self.on_history_selected)
        toolbar.addWidget(self.history_combo)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        #editor
        self.editor = CodeEditor()
        self.editor.setPlainText(code if code else "")
        self.editor.setMinimumHeight(400)
        self.editor.setStyleSheet("""
            QPlainTextEdit {
                background-color: #2b2b2b; 
                color: #f8f8f2; 
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.editor.textChanged.connect(self.on_text_changed)

        # add python syntax highlighnign
        self.highlighter = PythonHighlighter(self.editor.document())
        layout.addWidget(self.editor, 3)
        
        # console pane
        layout.addWidget(QLabel("Console Output:"))
        self.console_output = QPlainTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(100)
        self.console_output.setMaximumHeight(200)
        self.console_output.setStyleSheet("""
            QPlainTextEdit {
                background-color: #1e1e1e; 
                color: #f8f8f2; 
                border: 1px solid #555;
                border-radius: 4px;
                padding: 5px;
                font-family: Consolas, Monaco, monospace;
            }
        """)
        layout.addWidget(self.console_output, 1)

        #buttons
        button_layout = QHBoxLayout()
        self.run_button = DataPlotStudioButton("Run Script", parent=self, base_color_hex="#4caf50", hover_color_hex="#5cb85c", pressed_color_hex="#4a9c4d", text_color_hex="white", padding="6px", typewriter_effect=True)
        self.run_button.setMinimumHeight(40)
        self.run_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.run_button.setShortcut("Ctrl+Shift+Return")
        self.run_button.setToolTip("Click to run the script and update the plot\nShortcut 'Ctrl+Shift+Enter'")
        self.run_button.clicked.connect(self.on_run_clicked)
        button_layout.addWidget(self.run_button)

        self.close_button = DataPlotStudioButton("Close", parent=self, typewriter_effect=True)
        self.close_button.setMinimumHeight(40)
        self.close_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def on_text_changed(self):
        """Tracker to to see if user modified code to prevent unwanted changes"""
        self.is_code_modified = True
        # set the autosync to off so the user does not lose data
        if self.auto_sync_check.isChecked() and self.editor.hasFocus():
            self.auto_sync_check.setChecked(False)

    def update_code(self, new_code):
        """Update the code from the GUI"""
        if self.auto_sync_check.isChecked():
            self.editor.blockSignals(True)
            cursor = self.editor.textCursor()
            scroll = self.editor.verticalScrollBar().value()
            self.editor.setPlainText(new_code)
            self.editor.setTextCursor(cursor)
            self.editor.verticalScrollBar().setValue(scroll)
            self.editor.blockSignals(False)

    def on_run_clicked(self):
        """Validate and emit code"""
        code = self.editor.toPlainText()

        blocked_keywords = [
            "import os", "from os", "import sys", "from sys", "subprocess", "eval(", "exec(", "__import__", "shutil", "pathlib", "socket", "requests"
        ]

        found_threats = [kw for kw in blocked_keywords if kw in code]

        if found_threats:
            QMessageBox.critical(self, "Security Alert", f"Unintended keywords detected!\nBlocked keywords: {', '.join(found_threats)}\n\n"
            "Please remove these to run the script")
            return

        self.save_to_history(code)

        self.run_script_signal.emit(code)

        self.run_script_animation = PlotGeneratedAnimation(parent=self, message="Run Script")
        self.run_script_animation.start(target_widget=self)


    def save_to_history(self, code):
        """Save the current code to a list, cannot go more than 5, """
        #no saving dups
        if self.script_history and self.script_history[-1]["code"] == code:
            return

        self.run_counter = 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        label = f"Edition: #{self.run_counter} - {timestamp}"

        self.script_history.append({'code': code, 'label': label})

        #max 5 copyes
        if len(self.script_history) > 5:
            self.script_history.pop(0)

        self.update_history_combo()

    def update_history_combo(self):
        """update the box of code history"""
        self.history_combo.blockSignals(True)
        self.history_combo.clear()
        self.history_combo.addItem(f"Select to restore ({len(self.script_history)} available editions)...")

        #reverse order neweest first
        for item in reversed(self.script_history):
            self.history_combo.addItem(item["label"], item["code"])

        self.history_combo.blockSignals(False)

    def on_history_selected(self, index):
        """Restore the selected edition"""
        if index == 0: return

        code = self.history_combo.currentData()
        if code:
            reply = QMessageBox.question(
                self, "Restore Version",
                "Do you want to restore this version?\nCurrent code in the editor will be replaced.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.editor.setPlainText(code)
                self.auto_sync_check.setChecked(False)
                self.history_combo.setCurrentIndex(0)