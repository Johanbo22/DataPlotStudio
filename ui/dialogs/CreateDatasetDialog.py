from typing import Dict, Any
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QPushButton, QListWidget, QListWidgetItem, QFormLayout, QAbstractItemView, QTableWidget, QTableWidgetItem, QHeaderView, QFrame, QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.widgets import DataPlotStudioSpinBox, DataPlotStudioButton, DataPlotStudioLineEdit, DataPlotStudioComboBox
from ui.theme import ThemeColors
from ui.icons import IconBuilder, IconType

class CreateDatasetDialog(QDialog):
    """
    Dialog for configuring parameters when creating a new empty dataset.
    Allows specifying row count, column count, and customizing column names.
    """
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Create New Dataset")
        self.setWindowIcon(IconBuilder.build(IconType.NewProject))
        self.resize(750, 580)
        
        self._default_prefix: str = "Column"
        
        self.init_ui()
    
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(24)
        main_layout.setContentsMargins(28, 28, 28, 28)
        
        header_layout = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(IconBuilder.build(IconType.DataExplorerIcon).pixmap(48, 48))
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        
        title_label = QLabel("Configure New Dataset")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        
        subtitle_label = QLabel("Define initial dimensions, initial cell states and customize column names")
        subtitle_label.setProperty("styleClass", "muted_text")
        
        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        
        header_layout.addWidget(icon_label)
        header_layout.addSpacing(16)
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        main_layout.addLayout(header_layout)
        
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        left_card = QFrame()
        left_card.setObjectName("PanelFrame")
        
        controls_layout = QVBoxLayout(left_card)
        controls_layout.setContentsMargins(20, 20, 20, 20)
        controls_layout.setSpacing(24)
        
        config_section = QVBoxLayout()
        config_section.setSpacing(12)
        
        config_label = QLabel("Dataset Configuration")
        config_label.setFont(QFont("", -1, QFont.Weight.Bold))
        controls_layout.addWidget(config_label)
        
        form_layout = QFormLayout()
        form_layout.setSpacing(16)
        
        self.rows_spinbox = DataPlotStudioSpinBox()
        self.rows_spinbox.setRange(1, 1_000_000)
        self.rows_spinbox.setValue(10)
        self.rows_spinbox.setGroupSeparatorShown(True)
        self.rows_spinbox.setMinimumHeight(34)
        
        self.cols_spinbox = DataPlotStudioSpinBox()
        self.cols_spinbox.setRange(1, 1_000)
        self.cols_spinbox.setValue(3)
        self.cols_spinbox.setMinimumHeight(34)
        self.cols_spinbox.valueChanged.connect(self._on_column_count_changed)
        
        self.fill_combo = DataPlotStudioComboBox()
        self.fill_combo.setMinimumHeight(34)
        self.fill_combo.addItems(["NaN (Missing Data)", "0 (Zeroes)", "1 (Ones)", '"" (Empty String)'])
        
        form_layout.addRow("Number of Rows:", self.rows_spinbox)
        form_layout.addRow("Number of Columns:", self.cols_spinbox)
        form_layout.addRow("Initial Fill State:", self.fill_combo)
        config_section.addLayout(form_layout)
        controls_layout.addLayout(config_section)
        
        gen_section = QVBoxLayout()
        gen_section.setSpacing(8)
        
        gen_label = QLabel("Bulk Naming")
        gen_label.setFont(QFont("", -1, QFont.Weight.Bold))
        gen_section.addWidget(gen_label)
        
        gen_desc = QLabel("Set a prefix to auto-generate names")
        gen_desc.setProperty("styleClass", "muted_text")
        gen_section.addWidget(gen_desc)
        
        prefix_layout = QHBoxLayout()
        prefix_layout.setSpacing(8)
        self.prefix_input = DataPlotStudioLineEdit()
        self.prefix_input.setText(self._default_prefix)
        self.prefix_input.setPlaceholderText("e.g. Var")
        self.prefix_input.setMinimumHeight(34)
        
        self.btn_apply_prefix = DataPlotStudioButton("Apply", parent=self)
        self.btn_apply_prefix.setMinimumHeight(34)
        self.btn_apply_prefix.clicked.connect(self._apply_prefix_to_table)
        self.prefix_input.returnPressed.connect(self.btn_apply_prefix.click)
        
        prefix_layout.addWidget(self.prefix_input)
        prefix_layout.addWidget(self.btn_apply_prefix)
        gen_section.addLayout(prefix_layout)
        
        controls_layout.addLayout(gen_section)
        controls_layout.addStretch()
        content_layout.addWidget(left_card, stretch=4)
        
        right_card = QFrame()
        right_card.setObjectName("PanelFrame")
        table_layout = QVBoxLayout(right_card)
        table_layout.setContentsMargins(20, 20, 20, 20)
        table_layout.setSpacing(12)
        
        table_label = QLabel("Column Name Editor:")
        table_label.setFont(QFont("", -1, QFont.Weight.Bold))
        table_layout.addWidget(table_label)
        
        self.col_table = QTableWidget(0, 1)
        self.col_table.setObjectName("CreateDatasetColumnTable")
        self.col_table.setFrameShape(QFrame.Shape.NoFrame)
        self.col_table.setHorizontalHeaderLabels(["Column Name"])
        self.col_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.col_table.verticalHeader().setDefaultSectionSize(36)
        self.col_table.setAlternatingRowColors(True)
        self.col_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectItems)
        self.col_table.itemChanged.connect(self._validate_schema)
        table_layout.addWidget(self.col_table)
        
        content_layout.addWidget(right_card, stretch=5)
        main_layout.addLayout(content_layout)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        main_layout.addWidget(separator)
        
        btn_layout = QHBoxLayout()
        
        self.btn_reset = DataPlotStudioButton("Reset Defaults", parent=self)
        self.btn_reset.setIcon(IconBuilder.build(IconType.Redo))
        self.btn_reset.setToolTip("Reset dimensions and column names to default")
        self.btn_reset.clicked.connect(self._reset_defaults)
        
        self.btn_cancel = DataPlotStudioButton("Cancel", parent=self)
        self.btn_cancel.clicked.connect(self.reject)
        
        self.btn_create = DataPlotStudioButton(
            "Create Dataset",
            parent=self,
            base_color_hex=ThemeColors.MainColor,
            text_color_hex="white",
            font_weight="bold"
        )
        self.btn_create.setIcon(IconBuilder.build(IconType.Checkmark))
        self.btn_create.setMinimumWidth(160)
        self.btn_create.clicked.connect(self.accept)
        
        btn_layout.addWidget(self.btn_reset)
        btn_layout.addStretch()
        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addSpacing(12)
        btn_layout.addWidget(self.btn_create)
        
        main_layout.addLayout(btn_layout)
        
        self._on_column_count_changed(self.cols_spinbox.value())
        
    def _on_column_count_changed(self, target_cols: int) -> None:
        """Updates table rows based on requestsx"""
        current_rows = self.col_table.rowCount()
        prefix = self.prefix_input.text().strip() or self._default_prefix
        
        self.col_table.blockSignals(True)
        if target_cols > current_rows:
            self.col_table.setRowCount(target_cols)
            for i in range(current_rows, target_cols):
                item = QTableWidgetItem(f"{prefix}_{i+1}")
                item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
                self.col_table.setItem(i, 0, item)
            self.col_table.scrollToBottom()
        elif target_cols < current_rows:
            self.col_table.setRowCount(target_cols)
        self.col_table.blockSignals(False)
        self._validate_schema()
    
    def _apply_prefix_to_table(self) -> None:
        prefix = self.prefix_input.text().strip() or self._default_prefix
        self.col_table.blockSignals(True)
        for i in range(self.col_table.rowCount()):
            item = self.col_table.item(i, 0)
            if item:
                item.setText(f"{prefix}_{i+1}")
        self.col_table.blockSignals(False)
        self._validate_schema
    
    def _reset_defaults(self) -> None:
        self.prefix_input.setText(self._default_prefix)
        self.rows_spinbox.setValue(10)
        self.cols_spinbox.setValue(3)
        self.fill_combo.setCurrentIndex(0)
        self._apply_prefix_to_table()
    
    def _validate_schema(self, *args) -> None:
        """Hlighlighs duplicate column names in table"""
        seen = set()
        has_duplicates = False
        
        self.col_table.blockSignals(True)
        for i in range(self.col_table.rowCount()):
            item = self.col_table.item(i, 0)
            if not item:
                continue
            
            text = item.text().strip()
            if text in seen:
                item.setForeground(QColor("#E74C3C"))
                item.setToolTip("Duplicate detected.")
                has_duplicates = True
            else:
                item.setForeground(QColor("#2c3e50"))
                item.setToolTip("")
                if text:
                    seen.add(text)
        self.col_table.blockSignals(False)
        
        if has_duplicates:
            self.btn_create.setText("Create (Auto-Resovle duplicate entries)")
        else:
            self.btn_create.setText("Create Dataset")
    
    def get_dataset_parameters(self) -> Dict[str, Any]:
        col_names = []
        for i in range(self.col_table.rowCount()):
            item = self.col_table.item(i, 0)
            text = item.text().strip() if item else ""
            col_names.append(text if text else f"Unnamed_{i+1}")
        
        seen = set()
        unique_col_names = []
        for name in col_names:
            final_name = name
            counter = 1
            while final_name in seen:
                final_name = f"{name}_{counter}"
                counter += 1
            seen.add(final_name)
            unique_col_names.append(final_name)
        
        fill_text = self.fill_combo.currentText()
        if fill_text.startswith("0"):
            fill_val = 0
        elif fill_text.startswith("1"):
            fill_val = 1
        elif fill_text.startswith('""'):
            fill_val = ""
        else:
            fill_val = "NaN"
        
        return {
            "rows": self.rows_spinbox.value(),
            "columns": self.cols_spinbox.value(),
            "column_names": unique_col_names,
            "fill_value": fill_val
        }