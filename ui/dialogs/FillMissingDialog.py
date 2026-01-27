from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox


from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
    QProgressBar,
    QFrame,
)
import pandas as pd

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit


class FillMissingDialog(QDialog):
    """Dialog for the user to manipulate their data using the fill missing tool"""

    def __init__(self, columns: list[str], df: pd.DataFrame = None, parent=None):
        super().__init__(parent)
        self.columns = columns
        self.df = df
        self.setWindowTitle("Fill Missing Values")
        self.setModal(True)
        self.resize(400, 300)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        info = QLabel("Select how to fill missing values (NaN) in your dataset.")
        info.setStyleSheet("color: #666;")
        layout.addWidget(info)

        layout.addSpacing(10)

        # this is the columns selection UI
        layout.addWidget(QLabel("Target Column:"))
        self.column_combo = DataPlotStudioComboBox()
        self.column_combo.addItem("All Columns")
        self.column_combo.addItems(self.columns)
        self.column_combo.currentTextChanged.connect(self.update_stats)
        layout.addWidget(self.column_combo)

        # Stats frame
        self.stats_frame = QFrame()
        self.stats_frame.setStyleSheet(
            "background-color: #2b2b2b; border-radius: 5px; padding: 5px;"
        )
        stats_layout = QVBoxLayout(self.stats_frame)

        self.stats_label = QLabel("Missing Values: N/A")
        self.stats_label.setStyleSheet("color: #ddd; font-size: 11px;")
        stats_layout.addWidget(self.stats_label)

        self.missing_progress = QProgressBar()
        self.missing_progress.setTextVisible(False)
        self.missing_progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 3px;
                background-color: #333;
                height: 8px;
            }
            QProgressBar::chunk {
                background-color: #ff5252;
            }
        """)
        stats_layout.addWidget(self.missing_progress)

        layout.addWidget(self.stats_frame)

        layout.addSpacing(10)

        # the user selects the method here
        layout.addWidget(QLabel("Fill Method:"))
        self.method_combo = DataPlotStudioComboBox()
        self.method_combo.addItems(
            [
                "Forward Fill (Previous Values)",
                "Backward Fill (Next Value)",
                "Linear Interpolation",
                "Time Interpolation",
                "Static Value (Type Below)",
                "Mean (Average)",
                "Median (Middle Value)",
                "Mode (Most Common)",
            ]
        )
        self.method_combo.currentTextChanged.connect(self.on_method_change)
        layout.addWidget(self.method_combo)

        layout.addSpacing(10)

        # grouping option
        self.group_check = DataPlotStudioCheckBox("Group By another Column")
        self.group_check.setToolTip(
            "Calculate the fill value based on groups (e.g., Mean_Salary byt Job_title)"
        )
        self.group_check.toggled.connect(self.toggle_group_combo)
        layout.addWidget(self.group_check)

        self.group_combo = DataPlotStudioComboBox()
        self.group_combo.addItems(self.columns)
        self.group_combo.setEnabled(False)
        self.group_combo.setVisible(False)
        layout.addWidget(self.group_combo)

        layout.addSpacing(10)

        # this is where the user types the value they want to fill. hidden by default unless method == staticvalue
        self.value_group = QWidget()
        value_layout = QVBoxLayout(self.value_group)
        value_layout.setContentsMargins(0, 0, 0, 0)
        value_layout.addWidget(QLabel("Enter Value:"))
        self.value_input = DataPlotStudioLineEdit()
        self.value_input.setPlaceholderText("e.g. 0, Unknown, 1.5")
        value_layout.addWidget(self.value_input)
        layout.addWidget(self.value_group)
        self.value_group.setVisible(False)

        layout.addStretch()

        # btns
        button_layout = QHBoxLayout()
        apply_btn = DataPlotStudioButton(
            "Apply Fill",
            parent=self,
            base_color_hex="#4caf50",
            text_color_hex="white",
            font_weight="bold",
        )
        apply_btn.clicked.connect(self.accept)

        cancel_btn = DataPlotStudioButton("Cancel", parent=self)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

        self.update_stats()

    def on_method_change(self, text):
        """Show or hide the value intput box"""
        is_static = "Static Value" in text
        self.value_group.setVisible(is_static)

        is_interpol = "Interpolation" in text
        if is_static or is_interpol:
            self.group_check.setChecked(False)
            self.group_check.setEnabled(False)
        else:
            self.group_check.setEnabled(True)

    def toggle_group_combo(self, checked: bool):
        """Show or hide the group selection box"""
        self.group_combo.setVisible(checked)
        self.group_combo.setEnabled(checked)

    def update_stats(self):
        """Calculate and display nussubg value stats for the selected column"""
        if self.df is None:
            self.stats_frame.setVisible(False)
            return

        col = self.column_combo.currentText()
        total_rows = len(self.df)

        if total_rows == 0:
            return

        missing_count = 0
        if col == "All Columns":
            missing_count = self.df.isnull().sum().sum()
            total_cells = self.df.size
            percentage = (missing_count / total_cells) * 100
            self.stats_label.setText(
                f"Total Missing Values: {missing_count:,} / {total_cells:,} ({percentage:.1f})%"
            )
            self.missing_progress.setMaximum(total_cells)
        else:
            if col in self.df.columns:
                missing_count = self.df[col].isnull().sum()
                percentage = (missing_count / total_rows) * 100
                self.stats_label.setText(
                    f"Missing in '{col}': {missing_count:,} / {total_rows:,} ({percentage:.1f}%)"
                )
                self.missing_progress.setMaximum(total_rows)
        
        self.missing_progress.setValue(int(missing_count))

        if percentage == 0:
            self.missing_progress.setStyleSheet(self.missing_progress.styleSheet().replace("#ff5252", "#4caf50"))
        elif percentage < 10:
            self.missing_progress.setStyleSheet(self.missing_progress.styleSheet().replace("#4caf50", "#ffb74d"))
        else:
            self.missing_progress.setStyleSheet(self.missing_progress.styleSheet().replace("#4caf50", "#ff5252"))

    def get_config(self):
        """Get the user selection"""
        text = self.method_combo.currentText()
        method = "ffill"

        if "Forward" in text:
            method = "ffill"
        elif "Backward" in text:
            method = "bfill"
        elif "Linear" in text:
            method = "linear_interpolation"
        elif "Time" in text:
            method = "time_interpolation"
        elif "Static" in text:
            method = "static_value"
        elif "Mean" in text:
            method = "mean"
        elif "Median" in text:
            method = "median"
        elif "Mode" in text:
            method = "mode"

        return {
            "column": self.column_combo.currentText(),
            "method": method,
            "value": self.value_input.text(),
            "group_by": self.group_combo.currentText() if self.group_check.isChecked() else None
        }
