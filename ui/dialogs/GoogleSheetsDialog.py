from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox
import re

from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit


class GoogleSheetsDialog(QDialog):
    """Dialog for importing data from Google Sheets"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Import Google Sheets")
        self.setModal(True)
        self.resize(600, 300)
        self.gid = None

        self.init_ui()

    def init_ui(self) -> None:
        """Initialize dialog UI"""
        layout = QVBoxLayout(self)

        # Information label
        info_label = QLabel("Enter your Google Sheets details below:")
        info_label.setFont(QFont("Arial", 10))
        layout.addWidget(info_label)

        # Form layout for inputs
        form_layout = QFormLayout()

        # Sheet ID input
        sheet_id_label = QLabel("Google Sheet Link or Sheet ID:")
        self.sheet_id = DataPlotStudioLineEdit()
        self.sheet_id.setToolTip("Paste the full Google Sheets URL or the unique Sheet ID")
        self.sheet_id.setPlaceholderText("Paste URL (e.g., https://docs.google.com/.../edit#gid=0) or ID")
        self.sheet_id.setMinimumWidth(350)
        self.sheet_id.textChanged.connect(self.parse_input)
        form_layout.addRow(sheet_id_label, self.sheet_id)

        # Sheet Name input
        sheet_name_label = QLabel("Sheet Name:")
        self.sheet_name = DataPlotStudioLineEdit()
        self.sheet_name.setToolTip("This is the name of the sheet you want to import data from.")
        self.sheet_name.setPlaceholderText("e.g., Sheet1")
        form_layout.addRow(sheet_name_label, self.sheet_name)

        layout.addLayout(form_layout)

        layout.addSpacing(10)

        #delimter
        delimiter_group = DataPlotStudioGroupBox("CSV Delimtter Settings", parent=self)
        delimiter_layout = QVBoxLayout()

        delimiter_info = QLabel("Google Sheets exports data as a CSV. Choose the delimitter used in your sheet")
        delimiter_info.setWordWrap(True)
        delimiter_info.setStyleSheet("font-weight: normal; color: #555;")
        delimiter_layout.addWidget(delimiter_info)

        #delimter box
        delimiter_select_layout = QHBoxLayout()
        delimiter_select_layout.addWidget(QLabel("Delimiter:"))

        self.delimiter_combo = DataPlotStudioComboBox()
        self.delimiter_combo.addItems([
            "Comma (,) - Standard",
            "Semicolon (;) - European",
            "Tab (\\t) - Tab-separated",
            "Pipe (|) - Pipe-separated",
            "Space ( ) - Space-separated",
            "Custom"
        ])
        self.delimiter_combo.setCurrentIndex(0)
        self.delimiter_combo.currentTextChanged.connect(self.on_delimiter_changed)
        delimiter_select_layout.addWidget(self.delimiter_combo, 1)
        delimiter_layout.addLayout(delimiter_select_layout)

        #custom
        custom_delimiter_layout = QHBoxLayout()
        custom_delimiter_layout.addWidget(QLabel("Custom Delimiter:"))
        self.custom_delimiter_input = DataPlotStudioLineEdit()
        self.custom_delimiter_input.setPlaceholderText("Enter single delimiter character")
        self.custom_delimiter_input.setMaxLength(1)
        self.custom_delimiter_input.setEnabled(False)
        self.custom_delimiter_input.setMaximumWidth(100)
        custom_delimiter_layout.addWidget(self.custom_delimiter_input)
        custom_delimiter_layout.addStretch()
        delimiter_layout.addLayout(custom_delimiter_layout)

        #decimal sep
        decimal_layout = QHBoxLayout()
        decimal_layout.addWidget(QLabel("Decimal Separator:"))
        self.decimal_combo = DataPlotStudioComboBox()
        self.decimal_combo.addItems([
            "Dot (.) - UK/US",
            "Comma (,) - European",
        ])
        self.decimal_combo.setCurrentIndex(0)
        decimal_layout.addWidget(self.decimal_combo, 1)
        delimiter_layout.addLayout(decimal_layout)

        #1000sep
        thousands_layout = QHBoxLayout()
        thousands_layout.addWidget(QLabel("Thousands Separator"))
        self.thousands_combo = DataPlotStudioComboBox()
        self.thousands_combo.addItems([
            "None",
            "Comma (,) - US Style",
            "Dot (.) - European",
            "Space ( ) - International"
        ])
        self.thousands_combo.setCurrentIndex(0)
        thousands_layout.addWidget(self.thousands_combo, 1)
        delimiter_layout.addLayout(thousands_layout)

        delimiter_group.setLayout(delimiter_layout)
        layout.addWidget(delimiter_group)

        # Help text
        help_text = QLabel(
            "How to use:\n"
            "1. Open your Google Sheet in a browser\n"
            "2. Copy the ID from the URL:\n"
            "   docs.google.com/spreadsheets/d/[SHEET_ID]/edit\n"
            "3. Check the sheet tab name (bottom left corner)\n"
            "4. IMPORTANT: Share the sheet publicly\n"
            "   (File → Share → \"Anyone with the link\")\n"
            "5. Select appropriate delimiter and decimal for your region\n"
            "6. Paste the ID and sheet name below"
        )
        help_text.setFont(QFont("Arial", 9))
        help_text.setStyleSheet("color: #333333; background-color: #e8f4f8; padding: 12px; border-radius: 4px;")
        help_text.setWordWrap(True)
        layout.addWidget(help_text)

        # Button layout
        button_layout = QHBoxLayout()

        import_button = DataPlotStudioButton("Import", parent=self)
        import_button.setMinimumWidth(100)
        import_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(import_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        layout.addLayout(button_layout)
        layout.addStretch()

        self.setLayout(layout)

    def on_delimiter_changed(self, text) -> None:
        """Handle delimiter selection change"""
        self.custom_delimiter_input.setEnabled(text == "Custom")

    def parse_input(self, text: str) -> None:
        """Parse the input for URL and extract sheet ID and GID"""
        # Regex to match sheet id
        id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", text)

        if id_match:
            extracted_id = id_match.group(1)
            if self.sheet_id.text() != extracted_id:
                self.sheet_id.blockSignals(True)
                self.sheet_id.setText(extracted_id)
                self.sheet_id.blockSignals(False)
            
            # Look for a GID
            gid_match = re.search(r"[#&?]gid=([0-9]+)", text)
            if gid_match:
                self.gid = gid_match.group(1)
                # Disable the sheet name as input to avoid a situation where the a sheet name that doesnt match GID is given
                self.sheet_name.setEnabled(False)
                self.sheet_name.clear()
                self.sheet_name.setPlaceholderText(f"Connecting to sheet with GID: {self.gid}")
            else:
                self.gid = None
                self.sheet_name.setEnabled(True)
                self.sheet_name.setPlaceholderText("e.g., Sheet1")
        else:
            if not text.startswith("http"):
                self.gid = None
                self.sheet_name.setEnabled(True)
                self.sheet_name.setPlaceholderText("e.g., Sheet1")

    def validate_and_accept(self) -> None:
        """Validate inputs before accepting"""
        if not self.sheet_id.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a Sheet ID")
            return

        if not self.gid and not self.sheet_name.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter a Sheet Name or provide a URL with a 'gid'")
            return

        #validate custom delimiter
        if self.delimiter_combo.currentText() == "Custom":
            if not self.custom_delimiter_input.text().strip():
                QMessageBox.warning(self, "Validation Error", "Please enter delimiter")
                return

        self.accept()

    def get_inputs(self) -> tuple:
        """Return the sheet ID and name and delimiter settings"""
        sheet_id = self.sheet_id.text().strip()
        sheet_name = self.sheet_name.text().strip()

        #delimiter
        delimiter_text = self.delimiter_combo.currentText()
        if delimiter_text.startswith("Comma"):
            delimiter = ","
        elif delimiter_text.startswith("Semicolon"):
            delimiter = ";"
        elif delimiter_text.startswith("Tab"):
            delimiter = "\t"
        elif delimiter_text.startswith("Pipe"):
            delimiter = "|"
        elif delimiter_text.startswith("Space"):
            delimiter = " "
        elif delimiter_text == "Custom":
            delimiter = self.custom_delimiter_input.text().strip()
        else:
            delimiter = ","

        #get decimal separator
        decimal_text = self.decimal_combo.currentText()
        decimal = "," if decimal_text.startswith("Comma") else "."

        # get thousands sep
        thousands_text = self.thousands_combo.currentText()
        if thousands_text.startswith("None"):
            thousands = None
        elif thousands_text.startswith("Comma"):
            thousands = ","
        elif thousands_text.startswith("Dot"):
            thousands = "."
        elif thousands_text.startswith("Space"):
            thousands = " "
        else:
            thousands = None

        return sheet_id, sheet_name, delimiter, decimal, thousands, self.gid