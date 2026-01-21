# ui/dialogs/OutlierDetectionDialog.py
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTableView, QMessageBox)
from ui.widgets import DataPlotStudioComboBox, DataPlotStudioDoubleSpinBox
from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.data_table_model import DataTableModel

class OutlierDetectionDialog(QDialog):
    def __init__(self, data_handler, method="z_score", parent=None):
        super().__init__(parent)
        self.data_handler = data_handler
        self.method = method
        self.outlier_indices = []

        self.setWindowTitle(f"Outlier Detection Tool - {method.replace("_", " ").title()}")
        self.resize(900, 600)
        self.init_ui()
        self.apply_detection()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # This is a settings panel
        settings_group = DataPlotStudioGroupBox("Settings")
        settings_layout = QHBoxLayout()

        #Controls to chose methods and columns
        self.numeric_columns = self.data_handler.df.select_dtypes(include=["number"]).columns.tolist()

        settings_layout.addWidget(QLabel("Target Column(s):"))
        self.column_combo = DataPlotStudioComboBox()
        self.column_combo.addItems(self.numeric_columns)

        if self.method == "isolation_forest":
            self.column_combo.addItem("All Numeric Columns")
            self.column_combo.setCurrentText("All Numeric Columns")
        
        self.column_combo.currentTextChanged.connect(self.apply_detection)
        settings_layout.addWidget(self.column_combo)

        if self.method == "z_score":
            settings_layout.addWidget(QLabel("Threshold (Standard Deviation):"))
            self.parameter_spin = DataPlotStudioDoubleSpinBox()
            self.parameter_spin.setRange(1.0, 10.0)
            self.parameter_spin.setValue(3.0)
            self.parameter_spin.setSingleStep(0.1)
            self.parameter_spin.valueChanged.connect(self.apply_detection)
            settings_layout.addWidget(self.parameter_spin)
        
        elif self.method == "iqr":
            settings_layout.addWidget(QLabel("IQR Multiplier:"))
            self.parameter_spin = DataPlotStudioDoubleSpinBox()
            self.parameter_spin.setRange(0.5, 5.0)
            self.parameter_spin.setValue(1.5)
            self.parameter_spin.setSingleStep(0.1)
            self.parameter_spin.valueChanged.connect(self.apply_detection)
            settings_layout.addWidget(self.parameter_spin)
        
        elif self.method == "isolation_forest":
            settings_layout.addWidget(QLabel("Contamination:"))
            self.parameter_spin = DataPlotStudioDoubleSpinBox()
            self.parameter_spin.setRange(0.01, 0.5)
            self.parameter_spin.setValue(0.05)
            self.parameter_spin.setSingleStep(0.01)
            self.parameter_spin.valueChanged.connect(self.apply_detection)
            settings_layout.addWidget(self.parameter_spin)
        
        refresh_button = DataPlotStudioButton("Recalculate", base_color_hex="#3498DB")
        refresh_button.clicked.connect(self.apply_detection)
        settings_layout.addWidget(refresh_button)

        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)

        # INfo
        self.info_label = QLabel("Ready")
        self.info_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        layout.addWidget(self.info_label)

        # The Preview table
        self.table_view = QTableView()
        layout.addWidget(self.table_view)

        # Action buttons
        button_layout = QHBoxLayout()

        self.remove_button = DataPlotStudioButton("Remove Outliers", base_color_hex="#e74c3c", text_color_hex="white")
        self.remove_button.clicked.connect(self.remove_outliers)
        button_layout.addWidget(self.remove_button)

        close_button = DataPlotStudioButton("Close")
        close_button.clicked.connect(self.reject)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

    def apply_detection(self):
        try:
            selected_col_text = self.column_combo.currentText()
            columns = self.numeric_columns if selected_col_text == "All Numeric Columns" else [selected_col_text]

            param = self.parameter_spin.value()
            kwargs = {}

            if self.method == "z_score": kwargs["threshold"] = param
            if self.method == "iqr": kwargs["multiplier"] = param
            if self.method == "isolation_forest": kwargs["contamination"] = param

            self.outlier_indices = self.data_handler.detect_outliers(self.method, columns, **kwargs)

            self.model = DataTableModel(self.data_handler, highlighted_rows=self.outlier_indices)
            self.table_view.setModel(self.model)
            self.info_label.setText(f"Found {len(self.outlier_indices)} outliers.")
        
        except Exception as ApplyOutlierDetectionError:
            self.info_label.setText(f"ApplyOutlierDetectionError: {str(ApplyOutlierDetectionError)}")
            self.outlier_indices = []

    def remove_outliers(self):
        if not self.outlier_indices:
            return
        
        reply = QMessageBox.question(
            self,
            "Confirm Removal",
            f"Are you sure you wan to remove: {len(self.outlier_indices)} rows from the current dataset?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.data_handler.clean_data("remove_rows", rows=self.outlier_indices)
            self.accept()