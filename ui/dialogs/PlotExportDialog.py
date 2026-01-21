

from PyQt6.QtWidgets import QDialog, QFileDialog, QHBoxLayout, QLabel, QVBoxLayout

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedSpinBox import DataPlotStudioSpinBox

class PlotExportDialog(QDialog):
    """Dialog for exporting plots"""

    def __init__(self, current_dpi=100, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Save Plot")
        self.setModal(True)
        self.resize(400, 280)
        self.current_dpi = current_dpi
        self.filepath = None
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        # Format selection
        layout.addWidget(QLabel("Format:"))
        self.format_combo = DataPlotStudioComboBox()
        self.format_combo.addItems(["PNG", "PDF", "SVG", "JPEG"])
        layout.addWidget(self.format_combo)

        layout.addSpacing(10)

        settings_group = DataPlotStudioGroupBox("Export Settings", parent=self)
        settings_layout = QVBoxLayout()

        #Dpi esttings
        dpi_layout = QHBoxLayout()
        dpi_layout.addWidget(QLabel("DPI:"))
        self.dpi_spin = DataPlotStudioSpinBox()
        self.dpi_spin.setRange(50, 1200)
        self.dpi_spin.setValue(self.current_dpi)
        dpi_layout.addWidget(self.dpi_spin)
        settings_layout.addLayout(dpi_layout)

        #transparency
        self.transparent_check = DataPlotStudioButton("Transparent Background")
        self.transparent_check.setChecked(False)
        self.transparent_check.setToolTip("Save with a transparent background (PNG/PDF/SVG)")
        settings_layout.addWidget(self.transparent_check)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        layout.addStretch()

        # buttons
        button_layout = QHBoxLayout()

        export_button = DataPlotStudioButton("Save", parent=self)
        export_button.clicked.connect(self.on_save_clicked)
        button_layout.addWidget(export_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
    
    def on_save_clicked(self):
        extension = self.format_combo.currentText().lower()
        if extension == "jpeg": extension = "jpg"

        filters = {
            "png": "PNG Image (*.png)",
            "pdf": "PDF Document (*.pdf)",
            "svg": "SVG Image (*.svg)",
            "jpg": "JPEG Image (*.jpg)"
        }
        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Save Plot",
            f"plot.{extension}",
            filters.get(extension, "All Files (*)")
        )
        if filepath:
            self.filepath = filepath
            self.accept()
    
    def get_config(self):
        return {
            "filepath": self.filepath,
            "dpi": self.dpi_spin.value(),
            "transparent": self.transparent_check.isChecked(),
            "format": self.format_combo.currentText().lower()
        }