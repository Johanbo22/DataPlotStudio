from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox


from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QFileDialog, QHBoxLayout, QLabel, QVBoxLayout

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox


class ExportDialog(QDialog):
    """Dialog for exporting data"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Export Data")
        self.setModal(True)
        self.resize(500, 250)

        self.init_ui()

    def init_ui(self):
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        # Export format selection
        format_label = QLabel("Export Format:")
        format_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(format_label)

        self.format_combo = DataPlotStudioComboBox()
        self.format_combo.addItems(['CSV', 'XLSX', 'JSON'])
        layout.addWidget(self.format_combo)

        layout.addSpacing(10)

        # Options
        options_group = DataPlotStudioGroupBox("Options", parent=self)
        options_layout = QVBoxLayout()

        self.include_index_check = DataPlotStudioCheckBox("Include Index")
        self.include_index_check.setChecked(False)
        options_layout.addWidget(self.include_index_check)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        layout.addStretch()

        # Button layout
        button_layout = QHBoxLayout()

        export_button = DataPlotStudioButton("Export", parent=self)
        export_button.setMinimumWidth(100)
        export_button.clicked.connect(self.on_export_clicked)
        button_layout.addWidget(export_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_export_clicked(self):
        """Handle export button click"""
        export_format = self.format_combo.currentText()

        # Determine file filter and extension
        if export_format == 'CSV':
            file_filter = "CSV Files (*.csv)"
            default_ext = ".csv"
        elif export_format == 'XLSX':
            file_filter = "Excel Files (*.xlsx)"
            default_ext = ".xlsx"
        else:  # JSON
            file_filter = "JSON Files (*.json)"
            default_ext = ".json"

        filepath, _ = QFileDialog.getSaveFileName(
            self,
            "Export_Data",
            f"export{default_ext}",
            file_filter
        )

        if filepath:
            self.filepath = filepath
            self.accept()

    def get_export_config(self):
        """Return export configuration"""
        return {
            'format': self.format_combo.currentText().lower(),
            'filepath': getattr(self, 'filepath', None),
            'include_index': self.include_index_check.isChecked()
        }