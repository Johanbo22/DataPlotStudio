from PyQt6.QtWidgets import (QVBoxLayout, QListWidgetItem, QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedListWidget import DataPlotStudioListWidget

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
        self.resize(400, 300)
        
        layout = QVBoxLayout(self)
        self.list_widget = DataPlotStudioListWidget()
        for index, (row_index, column_index, column_name, value) in enumerate(self.matches):
            item_text = f"Row {row_index}, Column: '{column_name}': {value}"
            item = QListWidgetItem(item_text)
            item.setData(Qt.ItemDataRole.UserRole, index)
            self.list_widget.addItem(item)
        
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)

        buttons = QDialogButtonBox()
        ok_button = DataPlotStudioButton("OK")
        cancel_button = DataPlotStudioButton("Cancel")
        buttons.addButton(ok_button, QDialogButtonBox.ButtonRole.AcceptRole)
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