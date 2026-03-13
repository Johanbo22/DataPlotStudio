import re

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QLabel, QMessageBox, QVBoxLayout, QScrollArea, QWidget

from ui.widgets import DataPlotStudioButton, DataPlotStudioGroupBox, DataPlotStudioLineEdit, DataPlotStudioComboBox
from ui.theme import ThemeColors


class GoogleSheetsDialog(QDialog):
    """Dialog for importing data from Google Sheets"""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Import from Google Sheets")
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)
        self.setModal(True)
        self.resize(650, 650)
        self.setMinimumWidth(500)
        self.gid = None

        self.init_ui()

    def init_ui(self) -> None:
        """Initialize dialog UI"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll_area.setProperty("styleClass", "transparent_scroll_area")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("TransparentScrollContent")
        content_layout = QVBoxLayout(scroll_content)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)

        # Information label
        info_label = QLabel("Enter your Google Sheets details below:")
        info_label.setObjectName("google_sheets_info_label")
        content_layout.addWidget(info_label)

        # Form layout for inputs
        connection_group = DataPlotStudioGroupBox("Connection Details", parent=self)
        connection_layout = QFormLayout()

        # Sheet ID input
        sheet_id_label = QLabel("Google Sheet Link or Sheet ID:")
        self.sheet_id = DataPlotStudioComboBox()
        self.sheet_id.setEditable(True)
        self.sheet_id.setToolTip("Paste the full Google Sheets URL or the unique Sheet ID")
        self.sheet_id.lineEdit().setPlaceholderText("Paste URL (e.g., https://docs.google.com/.../edit#gid=0) or ID")
        self.sheet_id.lineEdit().setClearButtonEnabled(True)
        self.sheet_id.setMinimumWidth(350)
        self.sheet_id.editTextChanged.connect(self.parse_input)
        connection_layout.addRow(sheet_id_label, self.sheet_id)

        # Sheet Name input
        sheet_name_label = QLabel("Sheet Name:")
        self.sheet_name = DataPlotStudioLineEdit()
        self.sheet_name.setToolTip("This is the name of the sheet you want to import data from.")
        self.sheet_name.setPlaceholderText("e.g., Sheet1")
        self.sheet_name.setClearButtonEnabled(True)
        connection_layout.addRow(sheet_name_label, self.sheet_name)

        connection_group.setLayout(connection_layout)
        content_layout.addWidget(connection_group)

        #delimter
        delimiter_group = DataPlotStudioGroupBox("CSV Delimiter Settings", parent=self)
        delimiter_layout = QVBoxLayout()

        delimiter_info = QLabel("Google Sheets exports data as a CSV. Choose the delimiter used in your sheet")
        delimiter_info.setWordWrap(True)
        delimiter_info.setProperty("styleClass", "muted_text")
        delimiter_layout.addWidget(delimiter_info)

        #delimter box
        delimiter_form_layout = QFormLayout()

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
        delimiter_form_layout.addRow("Delimiter:",self.delimiter_combo)

        #custom
        self.custom_delimiter_input = DataPlotStudioLineEdit()
        self.custom_delimiter_input.setPlaceholderText("Enter single delimiter character")
        self.custom_delimiter_input.setMaxLength(1)
        self.custom_delimiter_input.setEnabled(False)
        self.custom_delimiter_input.setMaximumWidth(100)
        
        custom_delimiter_hbox = QHBoxLayout()
        custom_delimiter_hbox.addWidget(self.custom_delimiter_input)
        custom_delimiter_hbox.addStretch()
        delimiter_form_layout.addRow("Custom Delimiter:", custom_delimiter_hbox)

        #decimal sep
        self.decimal_combo = DataPlotStudioComboBox()
        self.decimal_combo.addItems([
            "Dot (.) - UK/US",
            "Comma (,) - European",
        ])
        self.decimal_combo.setCurrentIndex(0)
        delimiter_form_layout.addRow("Decimal Separator:", self.decimal_combo)

        #1000sep
        self.thousands_combo = DataPlotStudioComboBox()
        self.thousands_combo.addItems([
            "None",
            "Comma (,) - US Style",
            "Dot (.) - European",
            "Space ( ) - International"
        ])
        self.thousands_combo.setCurrentIndex(0)
        delimiter_form_layout.addRow("Thousands Separator:", self.thousands_combo)

        delimiter_layout.addLayout(delimiter_form_layout)
        delimiter_group.setLayout(delimiter_layout)
        content_layout.addWidget(delimiter_group)

        # Help text
        help_text = QLabel(
            "<b>How to use:</b><br><br>"
            "1. Open your Google Sheet in a browser.<br>"
            "2. Copy the ID from the URL:<br>"
            "&nbsp;&nbsp;&nbsp;<span style='color: #555555;'>docs.google.com/spreadsheets/d/<b>[SHEET_ID]</b>/edit</span><br>"
            "3. Check the sheet tab name (bottom left corner).<br>"
            "4. <b>IMPORTANT:</b> Share the sheet publicly<br>"
            "&nbsp;&nbsp;&nbsp;<i>(File → Share → \"Anyone with the link\")</i>.<br>"
            "5. Select appropriate delimiter and decimal for your region.<br>"
            "6. Paste the ID and sheet name above."
        )
        help_text.setTextFormat(Qt.TextFormat.RichText)
        help_text.setFont(QFont("Arial", 9))
        help_text.setProperty("styleClass", "blue_help_box")
        help_text.setWordWrap(True)
        content_layout.addWidget(help_text)
        
        content_layout.addStretch()
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        # Button layout
        button_container = QWidget()
        button_layout = QHBoxLayout(button_container)
        button_layout.setContentsMargins(20, 10, 20, 20)
        button_layout.addStretch()

        self.import_button = DataPlotStudioButton("Import", base_color_hex=ThemeColors.MainColor, parent=self)
        self.import_button.setDefault(True)
        self.import_button.setMinimumWidth(100)
        self.import_button.setEnabled(False)
        self.import_button.clicked.connect(self.validate_and_accept)
        button_layout.addWidget(self.import_button)

        cancel_button = DataPlotStudioButton("Cancel", parent=self)
        cancel_button.setMinimumWidth(100)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        main_layout.addWidget(button_container)
        self.setLayout(main_layout)

        self.load_history()
        self.sheet_id.setFocus()

    def on_delimiter_changed(self, text) -> None:
        """Handle delimiter selection change"""
        is_custom = (text == "Custom")
        self.custom_delimiter_input.setEnabled(is_custom)
        if is_custom:
            self.custom_delimiter_input.setFocus()

    def parse_input(self, text: str) -> None:
        """Parse the input for URL and extract sheet ID and GID"""
        self.import_button.setEnabled(bool(text.strip()))
        # Regex to match sheet id
        id_match = re.search(r"/d/([a-zA-Z0-9-_]+)", text)

        if id_match:
            extracted_id = id_match.group(1)
            if self.sheet_id.currentText() != extracted_id:
                self.sheet_id.blockSignals(True)
                self.sheet_id.setCurrentText(extracted_id)
                self.sheet_id.blockSignals(False)
            
            # Look for a GID
            gid_match = re.search(r"[#&?]gid=([0-9]+)", text)
            if gid_match:
                self.gid = gid_match.group(1)
                # Disable the sheet name as input to avoid a situation where the a sheet name that doesnt match GID is given
                self.sheet_name.setEnabled(False)
                self.sheet_name.clear()
                self.sheet_name.setPlaceholderText(f"Locked: Using GID from URL ({self.gid})")
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
        for widget in [self.sheet_name, self.custom_delimiter_input]:
            widget.setProperty("validationState", "normal")
            widget.style().unpolish(widget)
            widget.style().polish(widget)
        
        if not self.gid and not self.sheet_name.text().strip():
            self.sheet_name.setProperty("validationState", "error")
            self.sheet_name.style().unpolish(self.sheet_name)
            self.sheet_name.style().polish(self.sheet_name)
            self.sheet_name.setFocus()
            QMessageBox.warning(self, "Validation Error", "Please enter a Sheet Name or provide a URL with a 'gid'.")
            return
        
        if self.delimiter_combo.currentText() == "Custom":
            if not self.custom_delimiter_input.text().strip():
                self.custom_delimiter_input.setProperty("validationState", "error")
                self.custom_delimiter_input.style().unpolish(self.custom_delimiter_input)
                self.custom_delimiter_input.style().polish(self.custom_delimiter_input)
                self.custom_delimiter_input.setFocus()
                QMessageBox.warning(self, "Validation Error", "Please enter a single delimiter character.")
                return
        
        self.save_history()
        self.accept()

    def get_inputs(self) -> tuple:
        """Return the sheet ID and name and delimiter settings"""
        sheet_id = self.sheet_id.currentText().strip()
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

    def load_history(self) -> None:
        """Load sheet ID history from settings"""
        settings = QSettings("DataPlotStudio", "GoogleSheetsImport")
        history = settings.value("history", [], type=list)

        history = [str(item) for item in history if isinstance(item, (str, int))]

        self.sheet_id.clear()
        self.sheet_id.addItems(history)
        self.sheet_id.setCurrentIndex(-1)
    
    def save_history(self) -> None:
        """Save the current sheet id to history"""
        current_id = self.sheet_id.currentText().strip()
        if not current_id:
            return
        
        settings = QSettings("DataPlotStudio", "GoogleSheetsImport")
        history = settings.value("history", [], type=list)

        history = [str(item) for item in history if isinstance(item, (str, int))]

        if current_id in history:
            history.remove(current_id)
        
        history.insert(0, current_id)
        history = history[:10]

        settings.setValue("history", history)