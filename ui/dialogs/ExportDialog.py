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

        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        self.description_label.setStyleSheet("color: #888888; font-style: italic; font-size: 11px;")
        options_layout.addWidget(self.description_label)

        options_group.setLayout(options_layout)
        layout.addWidget(options_group)

        self.format_combo.currentTextChanged.connect(self.update_format_info)
        self.include_index_check.stateChanged.connect(self.update_format_info)

        self.update_format_info()

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

    def update_format_info(self) -> None:
        """Update a description label based on selected format and current optins"""
        format = self.format_combo.currentText()
        include_index = self.include_index_check.isChecked()

        if format == "JSON":
            if include_index:
                self.description_label.setText("Export as a 'columns' oriented JSON.")
            else:
                self.description_label.setText("Export as a 'records' oriented JSON.")
        elif format == "CSV":
            self.description_label.setText("Standard Comma Separated Values file.")
        elif format == "XLSX":
            self.description_label.setText("Microsoft Excel Spreadsheet format.")
        else:
            self.description_label.setText("")

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
            "Export Data",
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