import json
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QTextEdit, QLabel, QMessageBox, QInputDialog
from PyQt6.QtGui import QFont

from ui.widgets.AnimatedButton import DataPlotStudioButton

class ThemeEditorDialog(QDialog):
    
    def __init__(self, theme_name, theme_content, is_protected=False, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Edit theme - {theme_name}")
        self.resize(600, 700)
        self.theme_name = theme_name
        self.is_protected = is_protected
        self.new_theme_name = None
        self.final_content = None

        layout = QVBoxLayout(self)

        info_label = QLabel(f"Editing: <b>{theme_name}</b>")
        if is_protected:
            info_label.setText(f"Editing: <b>{theme_name}</b> (Read-Only Default)<br><i style='color:orange'>Changes must be saved as a new theme.</i>")
        layout.addWidget(info_label)

        # Text editor
        self.editor = QTextEdit()
        self.editor.setFont(QFont("Consolas", 10))
        self.editor.setPlainText(json.dumps(theme_content, indent=4))
        layout.addWidget(self.editor)

        # Buttons
        button_layout = QHBoxLayout()
        self.cancel_button = DataPlotStudioButton("Cancel")
        self.save_button = DataPlotStudioButton("Save As..." if is_protected else "Save")

        self.cancel_button.clicked.connect(self.reject)
        self.save_button.clicked.connect(self.handle_save)

        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.save_button)
        layout.addLayout(button_layout)

    def handle_save(self):
        try:
            content = json.loads(self.editor.toPlainText())
        except json.JSONDecodeError as Error:
            QMessageBox.critical(self, "Invalid JSON", f"Error parsing JSON:\n{str(Error)}")
            return
        
        self.final_content = content

        if self.is_protected:
            name, ok = QInputDialog.getText(self, "Save theme as", "Enter new theme name:", text=f"{self.theme_name}_Copy")
            if ok and name:
                self.new_theme_name = name
                self.accept()
        else:
            self.accept()