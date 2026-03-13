from PyQt6.QtWidgets import (QVBoxLayout, QListWidgetItem, QDialog, QDialogButtonBox, QLabel, QAbstractItemView, QMenu, QApplication)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QKeySequence, QShortcut

from ui.widgets import DataPlotStudioButton, DataPlotStudioListWidget, DataPlotStudioLineEdit

class SearchResultsDialog(QDialog):
    """Dialog to display search results from a table search"""
    
    def __init__(self, matches: list, parent=None):
        super().__init__(parent)
        # Storing results as a list of (row_index, column_index, column_name, value)
        self.matches = matches
        self.selected_match = None
        self.init_ui()

    def init_ui(self) -> None:
        self.setWindowTitle(f"Search Results ({len(self.matches)} matches)")
        self.resize(450, 350)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        instruction_label = QLabel("Select a search result to navigate to its location")
        instruction_label.setProperty("styleClass", "search_instruction")
        layout.addWidget(instruction_label)
        
        self.filter_input = DataPlotStudioLineEdit()
        self.filter_input.setPlaceholderText("Filter results...")
        self.filter_input.setClearButtonEnabled(True)
        self.filter_input.textChanged.connect(self.filter_results)
        layout.addWidget(self.filter_input)
        
        self.status_label = QLabel(f"Showing {len(self.matches)} of {len(self.matches)} matches")
        self.status_label.setProperty("styleClass", "muted_text")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.status_label)
        
        self.list_widget = DataPlotStudioListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        
        if not self.matches:
            instruction_label.setText("No matches found for the search query")
            self.list_widget.setEnabled(False)
        else:
            monospace_font = QFont("Consolas")
            monospace_font.setStyleHint(QFont.StyleHint.Monospace)
            for index, (row_index, column_index, column_name, value) in enumerate(self.matches):
                
                display_value = str(value).replace("\n", " ↵ ").replace("\r", "").replace("\t", "    ")
                if len(display_value) > 80:
                    display_value = display_value[:77] + "..."
                
                item_text = f"Row {row_index:<5}  |  Column: '{column_name:<15}'  |  Value: {display_value}"
                item = QListWidgetItem(item_text)
                item.setFont(monospace_font)
                
                tooltip_text = f"Row: {row_index}\nColumn: {column_name}\nFull Value: {value}"
                item.setData(Qt.ItemDataRole.ToolTipRole, tooltip_text)
                item.setData(Qt.ItemDataRole.UserRole, index)
                self.list_widget.addItem(item)
            
            self.list_widget.setCurrentRow(0)
            self.list_widget.setFocus()
            
            self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
            self.list_widget.customContextMenuRequested.connect(self.show_context_menu)
            
            self.copy_shortcut = QShortcut(QKeySequence.StandardKey.Copy, self.list_widget)
            self.copy_shortcut.activated.connect(self.copy_selected_result)
            
            self.focus_filter_shortcut = QShortcut(QKeySequence("Ctrl+F"), self)
            self.focus_filter_shortcut.activated.connect(self.filter_input.setFocus)
        
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox()
        self.ok_button = DataPlotStudioButton("OK")
        cancel_button = DataPlotStudioButton("Cancel")
        self.ok_button.setDefault(True)
        
        if not self.matches:
            self.ok_button.setEnabled(False)
        
        buttons.addButton(self.ok_button, QDialogButtonBox.ButtonRole.AcceptRole)
        buttons.addButton(cancel_button, QDialogButtonBox.ButtonRole.RejectRole)
        buttons.accepted.connect(self.accept_selection)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
    
    def accept_selection(self) -> None:
        if len(self.list_widget.selectedItems()) > 0:
            index = self.list_widget.selectedItems()[0].data(Qt.ItemDataRole.UserRole)
            self.selected_match = self.matches[index]
            self.accept()
        else:
            if self.list_widget.count() > 0:
                self.selected_match = self.matches[0]
                self.accept()
    
    def filter_results(self, text: str) -> None:
        search_query = text.lower()
        visible_count = 0
        first_visible_item = None
        for row in range(self.list_widget.count()):
            item = self.list_widget.item(row)
            is_hidden = search_query not in item.text().lower()
            item.setHidden(is_hidden)
            
            if not is_hidden:
                visible_count += 1
                if first_visible_item is None:
                    first_visible_item = item
        
        self.status_label.setText(f"Showing {visible_count} of {len(self.matches)} matches")
        
        if first_visible_item:
            self.list_widget.setCurrentItem(first_visible_item)
        
        self.ok_button.setEnabled(visible_count > 0)
    
    def show_context_menu(self, position: QPoint) -> None:
        if not self.list_widget.selectedItems():
            return
        
        menu = QMenu()
        copy_action = menu.addAction("Copy Result")
        
        action = menu.exec(self.list_widget.mapToGlobal(position))
        if action == copy_action:
            self.copy_selected_result()
    
    def copy_selected_result(self) -> None:
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            clipboard = QApplication.clipboard()
            clipboard.setText(selected_items[0].text())