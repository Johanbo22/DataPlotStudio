from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QWidget,
)
from PyQt6.QtCore import Qt
from ui.widgets import (
    DataPlotStudioButton,
    DataPlotStudioLineEdit,
    DataPlotStudioComboBox,
    DataPlotStudioSpinBox,
    DataPlotStudioGroupBox
)
import pandas as pd
from typing import Any

class BinningDialog(QDialog):
    """Dialog for binning continious variables"""
    
    def __init__(self, columns: list, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Bin data")
        self.resize(500, 450)
        self.columns = columns
        self.result_config = None
        self.init_ui()
    
    def init_ui(self) -> None:
        layout = QVBoxLayout(self)
        
        # settings
        settings_group = DataPlotStudioGroupBox("Binning Configuration")
        settings_layout = QVBoxLayout()
        
        # source column
        settings_layout.addWidget(QLabel("Select Numeric Column:"))
        self.column_combo = DataPlotStudioComboBox()
        self.column_combo.addItems(self.columns)
        self.column_combo.currentIndexChanged.connect(self._auto_generate_name)
        settings_layout.addWidget(self.column_combo)
        
        # new column name
        settings_layout.addWidget(QLabel("New Column Name:"))
        self.new_name_input = DataPlotStudioLineEdit()
        self.new_name_input.setPlaceholderText("e.g., Age_Group")
        settings_layout.addWidget(self.new_name_input)
        
        settings_layout.addSpacing(10)
        
        # chooseing methods
        settings_layout.addWidget(QLabel("Binning Method:"))
        self.method_combo = DataPlotStudioComboBox()
        self.method_combo.addItems(["Fixed Number of Bins", "Quantiles", "Custom Edges"])
        self.method_combo.currentIndexChanged.connect(self._update_input_visibility)
        settings_layout.addWidget(self.method_combo)
        
        # Bin count inputs
        self.bin_count_widget = QWidget()
        bin_count_layout = QVBoxLayout(self.bin_count_widget)
        bin_count_layout.setContentsMargins(0, 0, 0, 0)
        bin_count_layout.addWidget(QLabel("Number of Bins:"))
        self.bin_count_spin = DataPlotStudioSpinBox()
        self.bin_count_spin.setRange(2, 100)
        self.bin_count_spin.setValue(5)
        bin_count_layout.addWidget(self.bin_count_spin)
        settings_layout.addWidget(self.bin_count_widget)
        
        self.custom_edges_widget = QWidget()
        custom_edges_layout = QVBoxLayout(self.custom_edges_widget)
        custom_edges_layout.setContentsMargins(0, 0, 0, 0)
        custom_edges_layout.addWidget(QLabel("Bin Edges (comma-separated, min to max):"))
        self.edges_input = DataPlotStudioLineEdit()
        self.edges_input.setPlaceholderText("e.g., 0, 18, 35, 60, 100")
        custom_edges_layout.addWidget(self.edges_input)
        settings_layout.addWidget(self.custom_edges_widget)
        
        settings_layout.addSpacing(10)
        
        # labels
        settings_layout.addWidget(QLabel("Custom Labels:"))
        self.labels_input = DataPlotStudioLineEdit()
        self.labels_input.setPlaceholderText("e.g., Low, Medium, High")
        self.labels_input.setToolTip("Leave empty to generate labels like (0, 10])")
        settings_layout.addWidget(self.labels_input)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        layout.addStretch()
        
        # buttons
        button_layout = QHBoxLayout()
        self.apply_button = DataPlotStudioButton(
            "Create Bins",
            parent=self,
            base_color_hex="#27ae60",
            text_color_hex="white"
        )
        self.apply_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.apply_button)
        
        self.cancel_button = DataPlotStudioButton("Cancel", parent=self)
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        self._update_input_visibility()
        self._auto_generate_name()
    
    def _update_input_visibility(self) -> None:
        """Toggle inputs on the selected method"""
        #define index as 0, 1, 2
        # 1 is uniform so we show bin counts
        # 2 is quantile so we show bin counts
        # 3 is custom so we show edges input
        method_idx = self.method_combo.currentIndex()
        is_custom = method_idx == 2
        
        self.bin_count_widget.setVisible(not is_custom)
        self.custom_edges_widget.setVisible(is_custom)
    
    def _auto_generate_name(self) -> None:
        """Suggest names for the new column"""
        col = self.column_combo.currentText()
        if col:
            self.new_name_input.setText(f"{col}_binned")
    
    def validate_and_accept(self) -> None:
        column = self.column_combo.currentText()
        new_name = self.new_name_input.text().strip()
        method_idx = self.method_combo.currentIndex()
        
        if not new_name:
            QMessageBox.warning(self, "Input Error", "Please enter a name for the new column")
            return
        if not new_name.isidentifier():
            QMessageBox.warning(self, "Input Error", "New column name must be a valid identifier\nNo Spaces or special characters")
            return
        
        bins = None
        pd_method = "cut"
        
        try:
            if method_idx == 0:
                bins = self.bin_count_spin.value()
                pd_method = "cut"
            elif method_idx == 1:
                bins = self.bin_count_spin.value()
                pd_method = "qcut"
            else:
                edges_str = self.edges_input.text()
                if not edges_str:
                    QMessageBox.warning(self, "Input Error", "Please enter bin edges.")
                    return
                try:
                    # parse the edges
                    bins = [float(x.strip() for x in edges_str.split(","))]
                    if len(bins) < 2:
                        raise ValueError("At least two edges are required")
                    if bins != sorted(bins):
                        raise ValueError("Edges has to be increasing")
                except ValueError as Error:
                    QMessageBox.warning(self, "Input Error", f"Invalid edges: {Error}")
                    return
                pd_method = "cut"
            
            labels = None
            labels_str = self.labels_input.text().strip()
            if labels_str:
                labels = [x.strip() for x in labels_str.split(",")]
                expected_bins = len(bins) -1 if isinstance(bins, list) else bins
                if len(labels) != expected_bins:
                    QMessageBox.warning(self, "Input Error", f"Number of labels ({len(labels)}) does not match number of bins ({expected_bins})")
                    return
            
            self.result_config = {
                "column": column,
                "new_column": new_name,
                "method": pd_method,
                "bins": bins,
                "labels": labels
            }
            self.accept()
        except Exception as Error:
            QMessageBox.critical(self, "Error", {str(Error)})
    
    def get_config(self) -> dict[str, Any] | None:
        return self.result_config