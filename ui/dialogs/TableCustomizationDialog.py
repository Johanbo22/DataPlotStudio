from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QDialogButtonBox, QWidget, QTabWidget, QFontComboBox, QAbstractItemView, QColorDialog
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox
from ui.widgets.AnimatedComboBox import DataPlotStudioComboBox
from ui.widgets.AnimatedGroupBox import DataPlotStudioGroupBox
from ui.widgets.AnimatedSpinBox import DataPlotStudioSpinBox
from ui.widgets.AnimatedTabWidget import DataPlotStudioTabWidget

class TableCustomizationDialog(QDialog):
    def __init__(self, current_settings: dict, parent: QWidget | None = None):
        super().__init__(parent)
        self.setWindowTitle("Customize data table")
        self.resize(400, 350)
        self.settings = current_settings or {}
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        
        self.tabs = DataPlotStudioTabWidget()
        self.tabs.addTab(self.create_appearance_tab(), "Appearance")
        self.tabs.addTab(self.create_font_tab(), "Font and Text")
        self.tabs.addTab(self.create_behavior_tab(), "Behavior")

        main_layout.addWidget(self.tabs)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
    
    def create_appearance_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        # General settings
        group = DataPlotStudioGroupBox("General")
        vbox = QVBoxLayout()

        hbox_alt = QHBoxLayout()
        self.alternating_check = DataPlotStudioCheckBox("Alternating Row Colors")
        self.alternating_check.setChecked(self.settings.get("alternating_rows", True))
        self.alternating_check.toggled.connect(self.toggle_alt_color_button)
        vbox.addWidget(self.alternating_check)

        self.alt_color_button = DataPlotStudioButton("Choose Color")
        self.alt_color_button.setFixedWidth(140)
        self.alt_color_button.setToolTip("Click to change the color of the alternating row")
        self.current_alt_color = self.settings.get("alt_color", "#F5F5F5")
        self.alt_color_button.updateColors(self.current_alt_color)
        self.alt_color_button.clicked.connect(self.pick_alt_color)

        hbox_alt.addWidget(self.alt_color_button)
        hbox_alt.addStretch()

        vbox.addLayout(hbox_alt)

        self.toggle_alt_color_button(self.alternating_check.isChecked())

        self.grid_check = DataPlotStudioCheckBox("Show Grid Lines")
        self.grid_check.setChecked(self.settings.get("show_grid", True))
        vbox.addWidget(self.grid_check)

        group.setLayout(vbox)
        layout.addWidget(group)

        # Headers
        header_group = DataPlotStudioGroupBox("Headers")
        header_vbox = QVBoxLayout()

        self.horizontal_header_check = DataPlotStudioCheckBox("Show Horizontal Headers")
        self.horizontal_header_check.setChecked(self.settings.get("show_h_headers", True))
        header_vbox.addWidget(self.horizontal_header_check)

        self.vertical_header_check = DataPlotStudioCheckBox("Show Vertical Headers (Index)")
        self.vertical_header_check.setChecked(self.settings.get("show_v_header", True))
        header_vbox.addWidget(self.vertical_header_check)

        header_group.setLayout(header_vbox)
        layout.addWidget(header_group)

        layout.addStretch()
        return widget
    
    def create_font_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        font_group = DataPlotStudioGroupBox("Table Font")
        vbox = QVBoxLayout()

        # Font Family of the data table
        hbox_family = QHBoxLayout()
        hbox_family.addWidget(QLabel("Font Family:"))
        self.font_combo = QFontComboBox()
        current_font = self.settings.get("font_family")
        if current_font:
            self.font_combo.setCurrentFont(QFont(current_font))
        hbox_family.addWidget(self.font_combo, 1)
        vbox.addLayout(hbox_family)

        # Font size
        hbox_size = QHBoxLayout()
        hbox_size.addWidget(QLabel("Font Size:"))
        self.font_size_spin = DataPlotStudioSpinBox()
        self.font_size_spin.setRange(6, 72)
        self.font_size_spin.setValue(self.settings.get("font_size", 10))
        hbox_size.addWidget(self.font_size_spin)
        hbox_size.addStretch()
        vbox.addLayout(hbox_size)

        font_group.setLayout(vbox)
        layout.addWidget(font_group)

        # Text Options
        text_group = DataPlotStudioGroupBox("Text Display")
        text_vbox = QVBoxLayout()

        self.word_wrap_check = DataPlotStudioCheckBox("Word Wrap Long Text")
        self.word_wrap_check.setChecked(self.settings.get("word_wrap", False))
        text_vbox.addWidget(self.word_wrap_check)

        text_group.setLayout(text_vbox)
        layout.addWidget(text_group)

        layout.addStretch()
        return widget
    
    def create_behavior_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        selelection_group = DataPlotStudioGroupBox("Selection Mode")
        vbox = QVBoxLayout()

        hbox_mode = QHBoxLayout()
        hbox_mode.addWidget(QLabel("Selection Behavior:"))
        self.selection_behavior_combo = DataPlotStudioComboBox()
        self.selection_behavior_combo.addItems(["Select Items", "Select Rows", "Select Columns"])

        # those settings are mapped to index
        current_behavior = self.settings.get("selection_behavior", QAbstractItemView.SelectionBehavior.SelectItems)
        if current_behavior == QAbstractItemView.SelectionBehavior.SelectRows:
            self.selection_behavior_combo.setCurrentIndex(1)
        elif current_behavior == QAbstractItemView.SelectionBehavior.SelectColumns:
            self.selection_behavior_combo.setCurrentIndex(2)
        else:
            self.selection_behavior_combo.setCurrentIndex(0)
        
        hbox_mode.addWidget(self.selection_behavior_combo)
        vbox.addLayout(hbox_mode)

        selelection_group.setLayout(vbox)
        layout.addWidget(selelection_group)

        layout.addStretch()
        return widget
    
    def toggle_alt_color_button(self, checked: bool):
        self.alt_color_button.setEnabled(checked)

    def pick_alt_color(self):
        color = QColorDialog.getColor(QColor(self.current_alt_color), self, "Select Alternating Row Color")
        if color.isValid():
            self.current_alt_color = color.name()

    def get_settings(self) -> dict:
        """Configured settings"""
        selection_index = self.selection_behavior_combo.currentIndex()
        if selection_index == 1:
            selection_behavior = QAbstractItemView.SelectionBehavior.SelectRows
        elif selection_index == 2:
            selection_behavior = QAbstractItemView.SelectionBehavior.SelectColumns
        else:
            selection_behavior = QAbstractItemView.SelectionBehavior.SelectItems
        
        return {
            "alternating_rows": self.alternating_check.isChecked(),
            "alt_color": self.current_alt_color,
            "show_grid": self.grid_check.isChecked(),
            "show_h_header": self.horizontal_header_check.isChecked(),
            "show_v_header": self.vertical_header_check.isChecked(),
            "font_family": self.font_combo.currentFont().family(),
            "font_size": self.font_size_spin.value(),
            "word_wrap": self.word_wrap_check.isChecked(),
            "selection_behavior": selection_behavior
        }
