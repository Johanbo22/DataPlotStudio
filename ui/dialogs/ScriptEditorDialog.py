from ui.theme import ThemeColors
from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox
from ui.dialogs import CodeEditor
from ui.PythonHighlighter import PythonHighlighter

import sys
import ast
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from PyQt6.QtGui import QTextCursor, QColor, QFont, QFontMetrics, QShortcut, QKeySequence
from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QPlainTextEdit, QMenu, QSplitter, QTreeWidget, QTreeWidgetItem, QWidget, QApplication


from datetime import datetime

from ui.widgets import DataPlotStudioButton, DataPlotStudioComboBox, DataPlotStudioLineEdit
from ui.animations.PlotGeneratedAnimation import PlotGeneratedAnimation

class StreamRedirector:
    """Redirects stdout/stderr to a plain text widget from the code editor"""
    def __init__(self, widget: QPlainTextEdit, original_stream, color: str = None):
        self.widget = widget
        self.original_stream = original_stream
        self.color = color
        
    def write(self, text) -> int:
        text_str = str(text)
        if self.original_stream:
            self.original_stream.write(text_str)
            
        
        cursor = self.widget.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        
        if self.color:
            fmt = cursor.charFormat()
            original_format = cursor.charFormat()
            fmt.setForeground(QColor(self.color))
            cursor.setCharFormat(fmt)
            cursor.insertText(text_str)
            cursor.setCharFormat(original_format)
        else:
            cursor.insertText(text_str)
        
        self.widget.setTextCursor(cursor)
        self.widget.ensureCursorVisible()
        
        QApplication.processEvents()
        
        return len(text_str)
    
    def flush(self) -> None:
        self.original_stream.flush()


class ScriptEditorDialog(QDialog):
    """A dialog for editing and running custom python plotting scripts"""

    run_script_signal = pyqtSignal(str)

    def __init__(self, initial_code: str = "", df=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Python Console")
        self.resize(1200, 900)
        self.setModal(False)

        self.df = df
        self.script_history: list[dict[str, str]] = []
        self.run_counter: int = 0
        self.is_code_modified: bool = False

        self.init_ui(initial_code)
        
        self.original_stdout = sys.stdout
        self.original_stderr = sys.stderr
        
        self.stdout_redirector = StreamRedirector(self.console_output, self.original_stdout, color="#f8f8f2")
        self.stderr_redirector = StreamRedirector(self.console_output, self.original_stderr, color="#ff5555")
        
        sys.stdout = self.stdout_redirector
        sys.stderr = self.stderr_redirector
        
        self.read_settings()
    
    def read_settings(self) -> None:
        """Restores the window size, position, and splitter layout from previous sessions."""
        settings = QSettings("DataPlotStudio", "ScriptEditor")
        saved_geometry = settings.value("geometry")
        if saved_geometry:
            self.restoreGeometry(saved_geometry)
        
        saved_splitter = settings.value("splitter_state")
        if saved_splitter and hasattr(self, "splitter"):
            self.splitter.restoreState(saved_splitter)
    
    def write_settings(self) -> None:
        """Saves the current window layout preferences to the system registry/config."""
        settings = QSettings("DataPlotStudio", "ScriptEditor")
        settings.setValue("geometry", self.saveGeometry())
        if hasattr(self, "splitter"):
            settings.setValue("splitter_state", self.splitter.saveState())
        
    def closeEvent(self, event):
        """
        Intercepts the dialog close event to restore system streams and 
        warn the user if there are unsaved code modifications.
        """
        if self.is_code_modified and not self.auto_sync_check.isChecked():
            reply = QMessageBox.question(
                self, 
                "Unsaved Changes",
                "You have modified the script. Are you sure you want to close without running?\n"
                "Any unexecuted changes will be lost.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            ) 
            if reply == QMessageBox.StandardButton.No:
                event.ignore()
                return
        
        self.write_settings()
        sys.stdout = self.original_stdout
        sys.stderr = self.original_stderr
        super().closeEvent(event)

    def init_ui(self, code):
        layout = QVBoxLayout()
        self.setLayout(layout)

        #header and information
        info_layout = QHBoxLayout()
        info_label = QLabel("<b>Script</b><br>Edit the <code>create_plot(df)</code> function below. Click the 'Run' button to update the plot.")
        info_label.setProperty("styleClass", "info_text")
        info_layout.addWidget(info_label)
        layout.addLayout(info_layout)

        #security
        security_label = QLabel("Restricted Environment: System calls are blocked in this editor.")
        security_label.setObjectName("script_security_label")
        layout.addWidget(security_label)

        #tools
        toolbar = QHBoxLayout()
        self.auto_sync_check = DataPlotStudioCheckBox("Auto-update from GUI (This will overwrite changes)")
        self.auto_sync_check.setChecked(True)
        self.auto_sync_check.setToolTip("If checked, changing settings from the GUI will overwrite the code here")
        toolbar.addWidget(self.auto_sync_check)
        
        # snippets menu
        toolbar.addSpacing(10)
        self.snippet_button = DataPlotStudioButton("Insert Snippet", parent=self, typewriter_effect=True)
        self.snippet_button.setFixedWidth(130)
        self.snippet_button.setToolTip("Insert common plotting code snippets")
        self.snippet_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.snippet_menu = QMenu(self)
        self.snippet_menu.setObjectName("script_snippet_menu")
        
        categorized_snippets: dict[str, dict[str, str]] = {
            "Reference Lines": {
                "Vertical Reference Line": "ax.axvline(x=0, color='red', linestyle='--', linewidth=1.5, label='Ref Line')\n",
                "Horizontal Reference Line": "ax.axhline(y=0, color='blue', linestyle=':', linewidth=1.5, label='Threshold')\n",
                "Diagonal Line": "ax.plot([0, 1], [0, 1], linestyle='-.', color='gray', linewidth=1.2)\n",
                "Custom Line Segment": "ax.plot([0.2, 0.8], [0.1, 0.9], color='black', linewidth=2.0)\n",
            },
            "Highlights & Regions": {
                "Highlight Vertical Region": "ax.axvspan(xmin=0, xmax=1, color='yellow', alpha=0.2)\n",
                "Highlight Horizontal Region": "ax.axhspan(ymin=0, ymax=1, color='green', alpha=0.2)\n",
            },
            "Markers": {
                "Star Marker": "ax.scatter(x=[0.5], y=[0.5], marker='*', s=200, color='gold')\n",
                "Cross Marker": "ax.scatter(x=[0.2], y=[0.8], marker='x', s=100, color='red')\n",
            }
        }
        
        for category_name, snippets in categorized_snippets.items():
            sub_menu = self.snippet_menu.addMenu(category_name)
            for name, code_snippet in snippets.items():
                action = sub_menu.addAction(name)
                action.triggered.connect(lambda checked, c=code_snippet: self.insert_snippet_into_code(c))
            
        self.snippet_button.setMenu(self.snippet_menu)
        toolbar.addWidget(self.snippet_button)

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
        self.editor.setObjectName("script_code_editor")
        self.editor.setPlainText(code if code else "")
        self.editor.setMinimumHeight(400)
        
        editor_font = QFont("Consolas", 11)
        editor_font.setStyleHint(QFont.StyleHint.Monospace)
        self.editor.setFont(editor_font)
        self.editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        
        font_metrics = QFontMetrics(editor_font)
        self.editor.setTabStopDistance(font_metrics.horizontalAdvance(" ")*4)
        self.editor.textChanged.connect(self.on_text_changed)
        
        self.comment_shortcut = QShortcut(QKeySequence("Ctrl+Shift+7"), self.editor)
        self.comment_shortcut.activated.connect(self.toggle_comments)

        # add python syntax highlighnign
        self.highlighter = PythonHighlighter(self.editor.document())
        layout.addWidget(self.editor, 3)
        
        # Splitter for variable panel and editor (left and right)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.editor)
        
        variable_panel = QVBoxLayout()
        variable_panel.setContentsMargins(0, 0, 0, 0)
        
        self.variable_search_bar = DataPlotStudioLineEdit()
        self.variable_search_bar.setObjectName("script_variable_search")
        self.variable_search_bar.setPlaceholderText("Search Columns...")
        self.variable_search_bar.textChanged.connect(self.filter_variables)
        variable_panel.addWidget(self.variable_search_bar)
        
        self.variable_explorer = self.create_variable_explorer()
        variable_panel.addWidget(self.variable_explorer)
        
        variable_container_widget = QWidget()
        variable_container_widget.setLayout(variable_panel)
        
        self.splitter.addWidget(variable_container_widget)
        
        self.splitter.setStretchFactor(0, 3)
        self.splitter.setStretchFactor(1, 1)
        
        layout.addWidget(self.splitter, 3)
        
        # console pane
        console_header_layout = QHBoxLayout()
        console_header_layout.addWidget(QLabel("Console Output:"))
        console_header_layout.addStretch()
        
        self.clear_console_button = DataPlotStudioButton("Clear Console", parent=self)
        self.clear_console_button.setToolTip("Clear the console")
        self.clear_console_button.clicked.connect(self.clear_console)
        console_header_layout.addWidget(self.clear_console_button)
        
        layout.addLayout(console_header_layout)
        
        self.console_output = QPlainTextEdit()
        self.console_output.setObjectName("script_console_output")
        self.console_output.setReadOnly(True)
        self.console_output.setMinimumHeight(50)
        self.console_output.setMaximumHeight(120)
        layout.addWidget(self.console_output, 1)
    
        #buttons
        button_layout = QHBoxLayout()
        self.run_button = DataPlotStudioButton("Run Script", parent=self, base_color_hex=ThemeColors.MainColor, text_color_hex="white", padding="6px", typewriter_effect=True)
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
        
    def create_variable_explorer(self) -> QTreeWidget:
        """
        Creates a side panel widget showing variables in scope from active dataframe
        Context menus for code insertion as well as double click event handling to cursor position
        """
        tree = QTreeWidget()
        tree.setObjectName("script_variable_explorer")
        tree.setHeaderLabels(["Variable", "Info"])
        tree.setColumnWidth(0, 160)
        tree.setIndentation(15)
        tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tree.customContextMenuRequested.connect(self.show_explorer_context_menu)
        tree.itemDoubleClicked.connect(self.on_explorer_double_click)
        
        if self.df is not None:
            root = QTreeWidgetItem(tree)
            root.setText(0, "df")
            root.setText(1, "DataFrame")
            root.setExpanded(True)
            root.setData(0, Qt.ItemDataRole.UserRole, "df")
            
            shape_item = QTreeWidgetItem(root)
            shape_item.setText(0, "Shape")
            shape_item.setText(1, str(self.df.shape))
            
            cols_root = QTreeWidgetItem(root)
            cols_root.setText(0, "Columns")
            cols_root.setText(1, f"{len(self.df.columns)}")
            cols_root.setExpanded(True)
            
            for col in self.df.columns:
                col_name = str(col)
                series = self.df[col]
                dtype = str(series.dtype)
                
                col_item = QTreeWidgetItem(cols_root)
                col_item.setText(0, col_name)
                col_item.setText(1, dtype)
                col_item.setData(0, Qt.ItemDataRole.UserRole, f"'{col_name}'")
                
                n_missing = series.isna().sum()
                if n_missing > 0:
                    miss_item = QTreeWidgetItem(col_item)
                    miss_item.setText(0, "Missing")
                    miss_item.setText(1, f"{n_missing} ({n_missing/len(self.df):.1%})")
                    miss_item.setForeground(1, Qt.GlobalColor.red)
                
                n_unique = series.unique()
                unique_item = QTreeWidgetItem(col_item)
                unique_item.setText(0, "Unique")
                unique_item.setText(1, str(n_unique))
                
                if series.dtype.kind in "bifc":
                    try:
                        min_item = QTreeWidgetItem(col_item)
                        min_item.setText(0, "Min")
                        min_item.setText(1, f"{series.min():.4g}")
                        
                        max_item = QTreeWidgetItem(col_item)
                        max_item.setText(0, "Max")
                        max_item.setText(1, f"{series.max():.4g}")
                        
                        if series.dtype.kind != "b":
                            mean_item = QTreeWidgetItem(col_item)
                            mean_item.setText(0, "Mean")
                            mean_item.setText(1, f"{series.mean():.4g}")
                    except Exception as aggregation_error:
                        pass
        else:
            item = QTreeWidgetItem(tree)
            item.setText(0, "No data")
            item.setText(1, "df is None")
        
        return tree
    
    def filter_variables(self, search_text: str) -> None:
        """
        Filters the variable explorer tree based on the user's search input.
        Hides columns that do not match the search string (case-insensitive).
        """
        if not hasattr(self, "variable_explorer") or self.variable_explorer.topLevelItemCount() == 0:
            return
        
        root_item = self.variable_explorer.topLevelItem(0)
        if not root_item:
            return
        
        # Locate the columns root node to search within
        columns_node: QTreeWidgetItem | None = None
        for i in range(root_item.childCount()):
            if root_item.child(i).text(0) == "Columns":
                columns_node = root_item.child(i)
                break
        
        if not columns_node:
            return
        
        search_text_lower: str = search_text.lower()
        
        # Iterate through columns and hide show based on search matches
        for i in range(columns_node.childCount()):
            col_item = columns_node.child(i)
            col_name: str = col_item.text(0).lower()
            
            # Show item if search string matches, hide otherwise
            col_item.setHidden(search_text_lower not in col_name)
    
    def on_explorer_double_click(self, item: QTreeWidgetItem, column: int):
        """
        Insert the items variable into editor on double click event
        """
        text_to_insert = item.data(0, Qt.ItemDataRole.UserRole)
        if text_to_insert:
            self.insert_snippet_into_code(text_to_insert)
    
    def show_explorer_context_menu(self, position):
        """Show the context menu for variable items"""
        item = self.variable_explorer.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        menu.setObjectName("script_snippet_menu")
        
        data = item.data(0, Qt.ItemDataRole.UserRole)
        node_text = item.text(0)
        
        if data:
            action_insert = menu.addAction(f"Insert {data}")
            action_insert.triggered.connect(lambda: self.insert_snippet_into_code(data))
            
            if item.parent() and item.parent().text(0) == "Columns":
                # Action: Insert df access
                df_access = f"df[{data}]"
                action_df = menu.addAction(f"Insert {df_access}")
                action_df.triggered.connect(lambda: self.insert_snippet_into_code(df_access))
        
        # Add bulk list insertion if the columns root node is clicked
        if node_text == "Columns" and hasattr(self, "df") and self.df is not None:
            col_list_str: str = "[" + ", ".join([f"'{col}'" for col in self.df.columns]) + "]"
            action_list = menu.addAction("Insert as List [...]")
            action_list.triggered.connect(lambda: self.insert_snippet_into_code(col_list_str))

        if not menu.isEmpty():
            menu.exec(self.variable_explorer.viewport().mapToGlobal(position))
    
    def insert_snippet_into_code(self, code: str) -> None:
        """Inserts the snippet code into the code editor at cursor position"""
        cursor = self.editor.textCursor()
        cursor.insertText(code)
        self.editor.setTextCursor(cursor)
        self.editor.setFocus()
        
        if self.auto_sync_check.isChecked():
            self.auto_sync_check.setChecked(False)

    def on_text_changed(self):
        """Tracker to to see if user modified code to prevent unwanted changes"""
        self.is_code_modified = True
        # set the autosync to off so the user does not lose data
        if self.auto_sync_check.isChecked() and self.editor.hasFocus():
            self.auto_sync_check.setChecked(False)
    
    def toggle_comments(self) -> None:
        """Toggles Python comments (#) on the currently selected lines."""
        cursor = self.editor.textCursor()
        cursor.beginEditBlock()
        
        start_block: int = self.editor.document().findBlock(cursor.selectionStart()).blockNumber()
        end_block: int = self.editor.document().findBlock(cursor.selectionEnd()).blockNumber()
        
        # Determine if we are commenting or uncommenting based on the first line
        comment_symbol = "#"
        first_block_text: str = self.editor.document().findBlockByNumber(start_block).text().lstrip()
        is_uncommenting: bool = first_block_text.startswith(comment_symbol)
        
        for i in range(start_block, end_block, 1):
            block = self.editor.document().findBlockByNumber(i)
            text: str = block.text()
            
            # Resposition cursor to the start of the current block
            cursor.setPosition(block.position())
            if is_uncommenting:
                idx: int = text.find(comment_symbol)
                if idx != -1:
                    cursor.setPosition(block.position() + idx)
                    cursor.deleteChar()
                    
                    space = " "
                    if len(text) > idx + 1 and text[idx + 1] == space:
                        cursor.deleteChar()
            else:
                cursor.insertText(comment_symbol)
        
        cursor.endEditBlock()
    
    def clear_console(self) -> None:
        self.console_output.clear()
    
    def goto_error_line(self, line_number: int) -> None:
        """
        Moves the editor's cursor to the specified line number and highlights it 
        to help the user quickly locate syntax errors.
        """
        if not line_number:
            return
        
        # Qt text blocks are 0-indexed, but AST is 1-indexed
        block = self.editor.document().findBlockByNumber(line_number - 1)
        if block.isValid():
            cursor = QTextCursor(block)
            # Hightlight the entire block with the error
            cursor.movePosition(QTextCursor.MoveOperation.EndOfBlock, QTextCursor.MoveMode.KeepAnchor)
            
            self.editor.setTextCursor(cursor)
            self.editor.setFocus()

    def update_code(self, new_code: str) -> None:
        """Update the code from the GUI"""
        if self.auto_sync_check.isChecked():
            self.editor.blockSignals(True)
            cursor = self.editor.textCursor()
            scroll = self.editor.verticalScrollBar().value()
            self.editor.setPlainText(new_code)
            self.editor.setTextCursor(cursor)
            self.editor.verticalScrollBar().setValue(scroll)
            self.editor.blockSignals(False)

    def on_run_clicked(self) -> None:
        """Validate and emit code"""
        code: str = self.editor.toPlainText()

        blocked_modules: set[str] = {"os", "sys", "subprocess", "shutil", "pathlib", "socket", "requests"}
        blocked_funcs: set[str] = {"eval", "exec", "__import__"}
        found_threats: list[str] = []
        
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in blocked_modules:
                            found_threats.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module in blocked_modules:
                        found_threats.append(node.module)
                elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                    if node.func.id in blocked_funcs:
                        found_threats.append(node.func.id)
                elif isinstance(node, ast.While):
                    found_threats.append("while, infinite loop protection")
        except SyntaxError as syntaxerror:
            sys.stderr.write(syntaxerror)
            # Navigate to the syntax error
            if syntaxerror.lineno:
                self.goto_error_line(syntaxerror.lineno)
            QMessageBox.critical(self, "Syntax Error", f"Cannot run script due to syntax error:\n{syntaxerror}")
            return
        
        if found_threats:
            unique_threats = sorted(list(set(found_threats)))
            QMessageBox.critical(
                self, 
                "Potential Unsafe Script Notice", 
                f"Unintended modules or functions detected\nBlocked usage: {', '.join(unique_threats)}\n\n"
                "Please remove these to run the script."
            )
            return

        self.save_to_history(code)

        self.run_script_signal.emit(code)
        
        # Reset the modified flag since current code is now executed
        self.is_code_modified = False

        self.run_script_animation = PlotGeneratedAnimation(parent=self, message="Run Script")
        self.run_script_animation.start(target_widget=self)

    def save_to_history(self, code: str) -> None:
        """Save the current code to a list, cannot go more than 5, """
        #no saving dups
        if self.script_history and self.script_history[-1]["code"] == code:
            return

        self.run_counter += 1
        timestamp = datetime.now().strftime("%H:%M:%S")
        label = f"Edition: #{self.run_counter} - {timestamp}"

        self.script_history.append({'code': code, 'label': label})

        #max 5 copyes
        MAX_HISTORY_ITEMS: int = 5
        if len(self.script_history) > MAX_HISTORY_ITEMS:
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