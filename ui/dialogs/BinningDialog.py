from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QWidget
from PyQt6.QtCore import Qt, QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from ui.widgets import DataPlotStudioButton, DataPlotStudioLineEdit, DataPlotStudioComboBox, DataPlotStudioSpinBox, DataPlotStudioGroupBox, DataPlotStudioCheckBox

import pandas as pd
from typing import Any
from enum import Enum

class BinningMethod(Enum):
    """Enumeration of supported binning strategies."""
    FIXED_BINS = "Fixed Number of Bins"
    QUANTILES = "Quantiles"
    CUSTOM_EDGES = "Custom Edges"

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
        self.method_combo.addItems([method.value for method in BinningMethod])
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
        
        # Validate input to allow numbers, commas, periods, spaces and negative signs
        edge_regex = QRegularExpression(r"^[0-9.,\s\-]+$")
        self.edges_input.setValidator(QRegularExpressionValidator(edge_regex, self.edges_input))
        custom_edges_layout.addWidget(self.edges_input)
        
        self.catch_all_checkbox = DataPlotStudioCheckBox("Add -∞ and ∞ to edges to catch out-of-bounds data")
        self.catch_all_checkbox.setChecked(True)
        self.catch_all_checkbox.setToolTip("Ensures no data becomes 'NaN' by extending the first and last bins to infinity.")
        custom_edges_layout.addWidget(self.catch_all_checkbox)
        
        settings_layout.addWidget(self.custom_edges_widget)
        
        settings_layout.addSpacing(10)
        
        # labels
        settings_layout.addWidget(QLabel("Labeling Properties:"))
        self.labels_strategy_combo = DataPlotStudioComboBox()
        self.labels_strategy_combo.addItems(["Default Intervals (eg., (0, 10])", "Custom Comma-Separated", "Sequential Prefix"])
        self.labels_strategy_combo.currentIndexChanged.connect(self._update_input_visibility)
        settings_layout.addWidget(self.labels_strategy_combo)
        
        self.custom_labels_widget = QWidget()
        custom_labels_layout = QVBoxLayout(self.custom_labels_widget)
        custom_labels_layout.setContentsMargins(0, 0, 0, 0)
        custom_labels_layout.addWidget(QLabel("Custom Labels:"))
        self.labels_input = DataPlotStudioLineEdit()
        self.labels_input.setPlaceholderText("e.g., Low, Medium, High")
        custom_labels_layout.addWidget(self.labels_input)
        settings_layout.addWidget(self.custom_labels_widget)
        
        self.prefix_labels_widget = QWidget()
        prefix_labels_layout = QVBoxLayout(self.prefix_labels_widget)
        prefix_labels_layout.setContentsMargins(0, 0, 0, 0)
        prefix_labels_layout.addWidget(QLabel("Prefix for Sequential Labels:"))
        self.prefix_input = DataPlotStudioLineEdit()
        self.prefix_input.setPlaceholderText("e.g., Group (results in Group 1, Group 2...)")
        prefix_labels_layout.addWidget(self.prefix_input)
        settings_layout.addWidget(self.prefix_labels_widget)
        
        # Additional binning settings
        self.right_inclusive_checkbox = DataPlotStudioCheckBox("Right-inclusive intervals (e.g. (0-10])")
        self.right_inclusive_checkbox.setChecked(True)
        settings_layout.addWidget(self.right_inclusive_checkbox)
        
        self.drop_original_checkbox = DataPlotStudioCheckBox("Drop Original column after binning")
        self.drop_original_checkbox.setChecked(False)
        settings_layout.addWidget(self.drop_original_checkbox)
        
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
        selected_method_text = self.method_combo.currentText()
        is_custom = selected_method_text == BinningMethod.CUSTOM_EDGES.value
        
        self.bin_count_widget.setVisible(not is_custom)
        self.custom_edges_widget.setVisible(is_custom)
        
        strategy_idx = self.labels_strategy_combo.currentIndex()
        self.custom_labels_widget.setVisible(strategy_idx == 1)
        self.prefix_labels_widget.setVisible(strategy_idx == 2)
    
    def _auto_generate_name(self) -> None:
        """Suggest names for the new column"""
        col = self.column_combo.currentText()
        if col:
            self.new_name_input.setText(f"{col}_binned")
    
    def validate_and_accept(self) -> None:
        column = self.column_combo.currentText()
        new_name = self.new_name_input.text().strip()
        selected_method_text = self.method_combo.currentText()
        
        if not new_name:
            QMessageBox.warning(self, "Input Error", "Please enter a name for the new column.")
            return
        if not new_name.isidentifier():
            QMessageBox.warning(self, "Input Error", "New column name must be a valid identifier.\nNo spaces or special characters allowed.")
            return
        
        bins = None
        pd_method = "cut"
        
        try:
            if selected_method_text == BinningMethod.FIXED_BINS.value:
                bins = self.bin_count_spin.value()
                pd_method = "cut"
            elif selected_method_text == BinningMethod.QUANTILES.value:
                bins = self.bin_count_spin.value()
                pd_method = "qcut"
            elif selected_method_text == BinningMethod.CUSTOM_EDGES.value:
                edges_str = self.edges_input.text()
                if not edges_str:
                    QMessageBox.warning(self, "Input Error", "Please enter bin edges")
                    return
                try:
                    # Parse the edges
                    bins = [float(x.strip()) for x in edges_str.split(",") if x.strip()]
                    if len(bins) < 1:
                        raise ValueError("At least one numerical edge are required")
                    
                    # Ensure strict monotonically increasing order
                    if any(bins[i] >= bins[i+1] for i in range(len(bins) - 1)):
                        raise ValueError("Edges must be strictly increasing without duplicates")

                    if self.catch_all_checkbox.isChecked():
                        if bins[0] != float("-inf"):
                            bins.insert(0, float("-fint"))
                        if bins[-1] != float("inf"):
                            bins.append(float("inf"))
                    
                    if len(bins) < 2:
                        raise ValueError("At least two valid numerical edges are required after processing.")
                except ValueError as error:
                    QMessageBox.warning(self, "Input Error", f"Invalid edges: {error}")
                    return
                pd_method = "cut"
            
            expected_bins = len(bins) - 1 if isinstance(bins, list) else bins
            
            labels = None
            comma_separated = 1
            sequential_prefix = 2
            strategy_idx = self.labels_strategy_combo.currentIndex()
            if strategy_idx == comma_separated:
                labels_str = self.labels_input.text().strip()
                if labels_str:
                    labels = [x.strip() for x in labels_str.split(",")]
                    if len(labels) != expected_bins:
                        QMessageBox.warning(self, "Input Error", f"Number of labels ({len(labels)}) does not match number of expected bins ({expected_bins}).")
                        return
                    if len(labels) != len(set(labels)):
                        QMessageBox.warning(self, "Input Error", "Custom labels must be unique.")
                        return
            elif strategy_idx == sequential_prefix:
                prefix = self.prefix_input.text().strip()
                if not prefix:
                    QMessageBox.warning(self, "Input Error", "Please enter a prefix for the sequential labels.")
                    return
                labels = [f"{prefix} {i+1}" for i in range(expected_bins)]
            
            self.result_config = {
                "column": column,
                "new_column": new_name,
                "method": pd_method,
                "bins": bins,
                "labels": labels,
                "right_inclusive": self.right_inclusive_checkbox.isChecked(),
                "drop_original": self.drop_original_checkbox.isChecked()
            }
            self.accept()
        except Exception as Error:
            QMessageBox.critical(self, "Execution Error", str(Error))
    
    def get_config(self) -> dict[str, Any] | None:
        return self.result_config