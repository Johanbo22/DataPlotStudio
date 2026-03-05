from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea

from ui.theme import ThemeColors
from ui.widgets import DataPlotStudioGroupBox, DataPlotStudioToggleSwitch, DataPlotStudioSpinBox, DataPlotStudioDoubleSpinBox, DataPlotStudioButton, DataPlotStudioComboBox, DataPlotStudioLineEdit
from ui.widgets.AnimatedListWidget import DataPlotStudioListWidget

class AnnotationsSettingsTab(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._init_ui()

    def _init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        
        scroll_widget = QWidget()
        scroll_widget.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)

        self._setup_manual_annotations_group(scroll_layout)
        scroll_layout.addSpacing(15)
        self._setup_auto_annotations_group(scroll_layout)
        self._setup_textbox_group(scroll_layout)
        scroll_layout.addSpacing(15)
        self._setup_datatable_group(scroll_layout)
        scroll_layout.addSpacing(15)
        self._setup_annotations_list_group(scroll_layout)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def _setup_manual_annotations_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Manual Annotations")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Annotation Text:"))
        self.annotation_text = DataPlotStudioLineEdit()
        self.annotation_text.setPlaceholderText("Enter text to add to plot")
        layout.addWidget(self.annotation_text)

        layout.addWidget(QLabel("X Position (0-1):"))
        self.annotation_x_spin = DataPlotStudioDoubleSpinBox()
        self.annotation_x_spin.setRange(0, 1)
        self.annotation_x_spin.setValue(0.5)
        self.annotation_x_spin.setSingleStep(0.05)
        layout.addWidget(self.annotation_x_spin)

        layout.addWidget(QLabel("Y Position (0-1):"))
        self.annotation_y_spin = DataPlotStudioDoubleSpinBox()
        self.annotation_y_spin.setRange(0, 1)
        self.annotation_y_spin.setValue(0.5)
        self.annotation_y_spin.setSingleStep(0.05)
        layout.addWidget(self.annotation_y_spin)

        layout.addWidget(QLabel("Font Size:"))
        self.annotation_fontsize_spin = DataPlotStudioSpinBox()
        self.annotation_fontsize_spin.setRange(6, 36)
        self.annotation_fontsize_spin.setValue(12)
        layout.addWidget(self.annotation_fontsize_spin)

        layout.addWidget(QLabel("Font Color:"))
        color_layout = QHBoxLayout()
        self.annotation_color_button = DataPlotStudioButton("Choose", parent=self)
        self.annotation_color_label = QLabel("Black")
        color_layout.addWidget(self.annotation_color_button)
        color_layout.addWidget(self.annotation_color_label)
        layout.addLayout(color_layout)

        self.add_annotation_button = DataPlotStudioButton("Add Annotation", parent=self)
        layout.addWidget(self.add_annotation_button)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_auto_annotations_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Annotate Data Points")
        layout = QVBoxLayout()

        self.auto_annotate_check = DataPlotStudioToggleSwitch("Annotate All points")
        self.auto_annotate_check.setToolTip("Automatically set text labels to all data points")
        layout.addWidget(self.auto_annotate_check)

        layout.addWidget(QLabel("Label Source Column:"))
        self.auto_annotate_col_combo = DataPlotStudioComboBox()
        self.auto_annotate_col_combo.setToolTip("Select the column to use for the point labels")
        self.auto_annotate_col_combo.addItem("Default (Y-value)")
        self.auto_annotate_col_combo.setEnabled(False)
        layout.addWidget(self.auto_annotate_col_combo)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_textbox_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Text Box")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Text Box Content:"))
        self.textbox_content = DataPlotStudioLineEdit()
        self.textbox_content.setPlaceholderText("Enter text for text box")
        layout.addWidget(self.textbox_content)

        layout.addWidget(QLabel("Text Box Position:"))
        self.textbox_position_combo = DataPlotStudioComboBox()
        self.textbox_position_combo.addItems([
            'upper left', 'upper center', 'upper right', 'center left', 
            'center', 'center right', 'lower left', 'lower center', 'lower right'
        ])
        layout.addWidget(self.textbox_position_combo)

        layout.addWidget(QLabel("Text Box Style:"))
        self.textbox_style_combo = DataPlotStudioComboBox()
        self.textbox_style_combo.addItems(['round', 'square', 'round,pad=1', 'round4,pad=0.5'])
        self.textbox_style_combo.setItemText(0, 'Rounded')
        self.textbox_style_combo.setItemText(1, 'Square')
        layout.addWidget(self.textbox_style_combo)

        layout.addWidget(QLabel("Background Color:"))
        bg_layout = QHBoxLayout()
        self.textbox_bg_button = DataPlotStudioButton("Choose", parent=self)
        self.textbox_bg_label = QLabel("White")
        bg_layout.addWidget(self.textbox_bg_button)
        bg_layout.addWidget(self.textbox_bg_label)
        layout.addLayout(bg_layout)

        self.textbox_enable_check = DataPlotStudioToggleSwitch("Enable Text Box")
        layout.addWidget(self.textbox_enable_check)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_datatable_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Data Table")
        layout = QVBoxLayout()

        self.table_enable_check = DataPlotStudioToggleSwitch("Show Data Table on plot")
        self.table_enable_check.setChecked(False)
        layout.addWidget(self.table_enable_check)

        controls_layout = QHBoxLayout()
        controls_layout.addWidget(QLabel("Type:"))
        self.table_type_combo = DataPlotStudioComboBox()
        self.table_type_combo.addItems(["Summary Stats", "First 5 Rows", "Last 5 Rows", "Correlation Matrix"])
        self.table_type_combo.setEnabled(False)
        self.table_type_combo.setVisible(False)
        controls_layout.addWidget(self.table_type_combo)

        controls_layout.addWidget(QLabel("Placement:"))
        self.table_location_combo = DataPlotStudioComboBox()
        self.table_location_combo.addItems(["bottom", "top", "right", "left", "center"])
        self.table_location_combo.setEnabled(False)
        self.table_location_combo.setVisible(False)
        controls_layout.addWidget(self.table_location_combo)
        layout.addLayout(controls_layout)

        settings_layout = QHBoxLayout()
        self.table_auto_font_size_check = DataPlotStudioToggleSwitch("Auto Font-Size")
        self.table_auto_font_size_check.setChecked(False)
        self.table_auto_font_size_check.setEnabled(False)
        settings_layout.addWidget(self.table_auto_font_size_check)

        settings_layout.addWidget(QLabel("Font Size:"))
        self.table_font_size_spin = DataPlotStudioSpinBox()
        self.table_font_size_spin.setRange(4, 40)
        self.table_font_size_spin.setValue(10)
        self.table_font_size_spin.setEnabled(False)
        self.table_font_size_spin.setVisible(False)
        settings_layout.addWidget(self.table_font_size_spin)

        settings_layout.addWidget(QLabel("Scale:"))
        self.table_scale_spin = DataPlotStudioDoubleSpinBox()
        self.table_scale_spin.setRange(0.5, 5.0)
        self.table_scale_spin.setValue(1.2)
        self.table_scale_spin.setSingleStep(0.1)
        self.table_scale_spin.setEnabled(False)
        self.table_scale_spin.setVisible(False)
        settings_layout.addWidget(self.table_scale_spin)

        layout.addLayout(settings_layout)
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_annotations_list_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Annotations List")
        layout = QVBoxLayout()

        self.annotations_list = DataPlotStudioListWidget()
        layout.addWidget(self.annotations_list)

        self.clear_annotations_button = DataPlotStudioButton("Clear All Annotations", parent=self)
        layout.addWidget(self.clear_annotations_button)

        group.setLayout(layout)
        parent_layout.addWidget(group)