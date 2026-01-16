from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox


from PyQt6.QtWidgets import QDialog, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit


class FillMissingDialog(QDialog):
    """Dialog for the user to manipulate their data using the fill missing tool"""

    def __init__(self, columns, parent=None):
        super().__init__(parent)
        self.columns = columns
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

        #this is the columns selection UI
        layout.addWidget(QLabel("Target Column:"))
        self.column_combo = DataPlotStudioComboBox()
        self.column_combo.addItem("All Columns")
        self.column_combo.addItems(self.columns)
        layout.addWidget(self.column_combo)

        layout.addSpacing(10)

        #the user selects the method here
        layout.addWidget(QLabel("Fill Method:"))
        self.method_combo = DataPlotStudioComboBox()
        self.method_combo.addItems([
            "Forward Fill (Previous Values)",
            "Backward Fill (Next Value)",
            "Linear Interpolation",
            "Time Interpolation",
            "Static Value (Type Below)",
            "Mean (Average)",
            "Median (Middle Value)",
            "Mode (Most Common)"
        ])
        self.method_combo.currentTextChanged.connect(self.on_method_change)
        layout.addWidget(self.method_combo)

        #this is where the user types the value they want to fill. hidden by default unless method == staticvalue
        self.value_group = QWidget()
        value_layout = QVBoxLayout(self.value_group)
        value_layout.setContentsMargins(0,0,0,0)
        value_layout.addWidget(QLabel("Enter Value:"))
        self.value_input = DataPlotStudioLineEdit()
        self.value_input.setPlaceholderText("e.g. 0, Unknown, 1.5")
        value_layout.addWidget(self.value_input)
        layout.addWidget(self.value_group)
        self.value_group.setVisible(False)

        layout.addStretch()

        #btns
        button_layout = QHBoxLayout()
        apply_btn = DataPlotStudioButton(
            "Apply Fill",
            parent=self,
            base_color_hex="#4caf50",
            text_color_hex="white",
            font_weight="bold"
        )
        apply_btn.clicked.connect(self.accept)

        cancel_btn = DataPlotStudioButton("Cancel", parent=self)
        cancel_btn.clicked.connect(self.reject)

        button_layout.addWidget(apply_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    def on_method_change(self, text):
        """Show or hide the value intput box """
        is_static = "Static Value" in text
        self.value_group.setVisible(is_static)

    def get_config(self):
        """Get the user selection"""
        text = self.method_combo.currentText()
        method = "ffill"

        if "Forward" in text: method = "ffill"
        elif "Backward" in text: method = "bfill"
        elif "Linear" in text: method = "linear_interpolation"
        elif "Time" in text: method = "time_interpolation"
        elif "Static" in text: method = "static_value"
        elif "Mean" in text: method = "mean"
        elif "Median" in text: method = "median"
        elif "Mode" in text: method = "mode"

        return {
            "column": self.column_combo.currentText(),
            "method": method,
            "value": self.value_input.text()
        }