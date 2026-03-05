from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, QToolBox, QFrame
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from ui.theme import ThemeColors
from ui.widgets import DataPlotStudioGroupBox, DataPlotStudioToggleSwitch, DataPlotStudioSpinBox, DataPlotStudioButton, DataPlotStudioComboBox, DataPlotStudioListWidget, QuickFilterEdit, HelpIcon
from ui.styles.widget_styles import ToolBox

class GeneralSettingsTab(QWidget):
    help_requested = pyqtSignal(str)
    
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0,0,0,0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        scroll_widget = QWidget()
        scroll_widget.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self._setup_plot_type_group(scroll_layout)
        self._setup_subplot_group(scroll_layout)
        scroll_layout.addSpacing(10)
        self._setup_data_group(scroll_layout)
        self._setup_subset_group(scroll_layout)
        self._setup_hue_group(scroll_layout)
        scroll_layout.addSpacing(10)
        self._setup_description_group(scroll_layout)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)
    
    def _setup_plot_type_group(self, parent_layout: QVBoxLayout) -> None:
        self.plot_type_group = DataPlotStudioGroupBox("Plot Type")
        layout = QVBoxLayout()

        self.current_plot_label = QLabel("Selected Plot: None")
        self.current_plot_label.setStyleSheet(ThemeColors.SectionHeaderStylesheet)
        layout.addWidget(self.current_plot_label)

        self.plot_type = QToolBox()
        self.plot_type.setMinimumHeight(350)
        self.plot_type.setStyleSheet(ToolBox.PlotToolBoxStylesheet)
        layout.addWidget(self.plot_type)

        self.add_subplots_check = DataPlotStudioToggleSwitch("Add subplots")
        self.add_subplots_check.setChecked(False)
        layout.addWidget(self.add_subplots_check)

        self.use_plotly_check = DataPlotStudioToggleSwitch("Use Plotly backend")
        self.use_plotly_check.setChecked(False)
        self.use_plotly_check.setToolTip("Switch to the Plotly backend")
        layout.addWidget(self.use_plotly_check)

        self.use_subset_check = DataPlotStudioToggleSwitch("Use Subset")
        self.use_subset_check.setChecked(False)
        layout.addWidget(self.use_subset_check)

        self.plot_type_group.setLayout(layout)
        parent_layout.addWidget(self.plot_type_group)
    
    def _setup_subplot_group(self, parent_layout: QVBoxLayout) -> None:
        self.subplot_group = DataPlotStudioGroupBox("Subplot Configuration")
        self.subplot_group.setVisible(False)
        layout = QVBoxLayout()

        info = QLabel(
            "This tool allows you to control how many subplots you wish to add to the current canvas.\n"
            "The rows adjust horizontal plots and columns control vertical plots."
        )
        info.setStyleSheet(ThemeColors.InfoStylesheet)
        info.setWordWrap(True)
        layout.addWidget(info)

        grid_layout = QHBoxLayout()
        grid_layout.addWidget(QLabel("Rows:"))
        self.subplot_rows_spin = DataPlotStudioSpinBox()
        self.subplot_rows_spin.setRange(1, 5)
        self.subplot_rows_spin.setValue(1)
        grid_layout.addWidget(self.subplot_rows_spin)

        grid_layout.addWidget(QLabel("Columns:"))
        self.subplot_cols_spin = DataPlotStudioSpinBox()
        self.subplot_cols_spin.setRange(1, 5)
        self.subplot_cols_spin.setValue(1)
        grid_layout.addWidget(self.subplot_cols_spin)
        layout.addLayout(grid_layout)

        share_layout = QHBoxLayout()
        self.subplot_sharex_check = DataPlotStudioToggleSwitch("Share X-axis")
        share_layout.addWidget(self.subplot_sharex_check)

        self.subplot_sharey_check = DataPlotStudioToggleSwitch("Share Y-axis")
        share_layout.addWidget(self.subplot_sharey_check)
        layout.addLayout(share_layout)

        btn_layout = QHBoxLayout()
        self.apply_subplot_layout_button = DataPlotStudioButton("Update Subplot Layout", parent=self)
        self.apply_subplot_help = HelpIcon("subplots")
        self.apply_subplot_help.clicked.connect(lambda: self.help_requested.emit("subplots"))
        btn_layout.addWidget(self.apply_subplot_layout_button)
        btn_layout.addWidget(self.apply_subplot_help)
        layout.addLayout(btn_layout)

        active_layout = QHBoxLayout()
        active_layout.addWidget(QLabel("Active Subplot:"))
        self.active_subplot_combo = DataPlotStudioComboBox()
        self.active_subplot_combo.addItem("Plot 1")
        active_layout.addWidget(self.active_subplot_combo, 1)
        layout.addLayout(active_layout)

        self.freeze_data_check = DataPlotStudioToggleSwitch("Freeze Data Selection for Subplots")
        layout.addWidget(self.freeze_data_check)

        self.subplot_group.setLayout(layout)
        parent_layout.addWidget(self.subplot_group)

    def _setup_data_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Data")
        group.setStyleSheet(ThemeColors.GroupBoxHeaderStyle)
        layout = QVBoxLayout()

        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Column:"))
        self.x_column = DataPlotStudioComboBox()
        x_layout.addWidget(self.x_column, 1)
        layout.addLayout(x_layout)

        y_lbl_layout = QHBoxLayout()
        y_lbl_layout.addWidget(QLabel("Y Column(s)"))
        y_lbl_layout.addStretch()

        self.multi_y_check = DataPlotStudioToggleSwitch("Multiple Y Columns")
        y_lbl_layout.addWidget(self.multi_y_check)
        layout.addLayout(y_lbl_layout)

        self.y_column = DataPlotStudioComboBox()
        layout.addWidget(self.y_column)

        self.y_columns_list = DataPlotStudioListWidget()
        self.y_columns_list.setSelectionMode(DataPlotStudioListWidget.SelectionMode.MultiSelection)
        self.y_columns_list.setMaximumHeight(150)
        self.y_columns_list.setVisible(False)
        layout.addWidget(self.y_columns_list)

        multi_btns = QHBoxLayout()
        self.select_all_y_btn = DataPlotStudioButton("Select All", parent=self)
        self.select_all_y_btn.setVisible(False)
        self.clear_all_y_btn = DataPlotStudioButton("Clear All", parent=self)
        self.clear_all_y_btn.setVisible(False)
        multi_btns.addWidget(self.select_all_y_btn)
        multi_btns.addWidget(self.clear_all_y_btn)
        layout.addLayout(multi_btns)

        self.multi_y_info = QLabel("Tip: Hold Ctrl/Cmd to select multiple columns")
        self.multi_y_info.setStyleSheet(ThemeColors.MutedTextStylesheet)
        self.multi_y_info.setVisible(False)
        layout.addWidget(self.multi_y_info)

        layout.addSpacing(10)
        sec_y_layout = QHBoxLayout()
        self.secondary_y_check = DataPlotStudioToggleSwitch("Secondary Y-Axis")
        sec_y_layout.addWidget(self.secondary_y_check)
        layout.addLayout(sec_y_layout)

        sec_config_layout = QHBoxLayout()
        self.secondary_y_column = DataPlotStudioComboBox()
        self.secondary_y_column.setEnabled(False)
        sec_config_layout.addWidget(self.secondary_y_column, stretch=2)

        self.secondary_plot_type_combo = DataPlotStudioComboBox()
        self.secondary_plot_type_combo.setEnabled(False)
        self.secondary_plot_type_combo.addItems(["Line", "Scatter", "Bar", "Area"])
        sec_config_layout.addWidget(self.secondary_plot_type_combo, stretch=1)
        layout.addLayout(sec_config_layout)

        layout.addSpacing(10)
        layout.addWidget(QLabel("Quick Filter:"))
        self.quick_filter_input = QuickFilterEdit()
        self.quick_filter_input.setPlaceholderText("e.g. value > 100 or category == 'A'")
        layout.addWidget(self.quick_filter_input)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_subset_group(self, parent_layout: QVBoxLayout) -> None:
        self.subset_group = DataPlotStudioGroupBox("Data Subset")
        self.subset_group.setVisible(False)
        self.subset_group.setStyleSheet(ThemeColors.GroupBoxHeaderStyle)
        layout = QVBoxLayout()

        info = QLabel("Plot a specific subset of your data instead of the full dataset.")
        info.setWordWrap(True)
        info.setStyleSheet(ThemeColors.InfoStylesheet)
        layout.addWidget(info)

        self.subset_combo = DataPlotStudioComboBox()
        self.subset_combo.addItem("(Full Dataset)")
        self.subset_combo.setEnabled(False)
        layout.addWidget(self.subset_combo)

        self.use_subset_check.stateChanged.connect(
            lambda state: self.subset_combo.setEnabled(state == Qt.CheckState.Checked.value)
        )

        self.refresh_subsets_btn = DataPlotStudioButton("Refresh Subset List", parent=self)
        layout.addWidget(self.refresh_subsets_btn)

        self.subset_group.setLayout(layout)
        parent_layout.addWidget(self.subset_group)

    def _setup_hue_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Hue/Group:")
        group.setStyleSheet(ThemeColors.GroupBoxHeaderStyle)
        layout = QVBoxLayout()
        self.hue_column = DataPlotStudioComboBox()
        self.hue_column.addItem("None")
        layout.addWidget(self.hue_column)
        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_description_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Plot Description: ")
        group.setStyleSheet(ThemeColors.GroupBoxHeaderLargeStyle)
        layout = QVBoxLayout()
        
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(12)
        self.description_label.setFont(font)
        
        layout.addWidget(self.description_label)
        group.setLayout(layout)
        parent_layout.addWidget(group)