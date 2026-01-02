from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtWidgets import QDialog, QPushButton


class ColormapButton(QPushButton):
    currentTextChanged = pyqtSignal(str)
    currentIndexChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_colormap = "viridis"
        self.setText("viridis")
        self.setIconSize(QSize(100, 20))

        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 4px;
                background-color: white;
            }
            QPushButton:hover {
                border-color: #aaa;
                background-color: #f0f0f0;
            }
        """)

        self.clicked.connect(self._open_picker)
        self._update_display()

    def _open_picker(self):
        from ui.dialogs import ColormapPickerDialog
        dialog = ColormapPickerDialog(self.current_colormap, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_colormap = dialog.get_selected_colormap()
            if new_colormap and new_colormap != self.current_colormap:
                self.setCurrentText(new_colormap)

    def setCurrentText(self, text):
        self.current_colormap = text
        self._update_display()
        self.currentTextChanged.emit(text)

    def currentText(self):
        return self.current_colormap

    def setCurrentIndex(self, index):
        pass

    def _update_display(self):
        from ui.dialogs import ColormapPickerDialog
        self.setText(f" {self.current_colormap}")
        dialog = ColormapPickerDialog(parent=None)
        icon = dialog._generate_icon(self.current_colormap)
        self.setIcon(icon)