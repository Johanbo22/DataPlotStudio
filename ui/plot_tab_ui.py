# ui/plot_tab_ui.py

from PyQt6.QtWidgets import (
    QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea,
    QFontComboBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from ui.animated_widgets import AnimatedButton, AnimatedGroupBox, AnimatedComboBox, AnimatedDoubleSpinBox, AnimatedLineEdit, AnimatedSpinBox, AnimatedCheckBox, AnimatedTabWidget, AnimatedListWidget, AnimatedSlider


class PlotTabUI(QWidget):
    """
    UI for the Plotting Tab.
    """
    
    def __init__(self) -> None:
        super().__init__()
    
    def init_ui(self, canvas: FigureCanvas, toolbar: NavigationToolbar) -> None:
        """Initialize the plotting/plot customization tab UI"""
        main_layout = QHBoxLayout(self)
        
        left_layout = QVBoxLayout()
        
        self.canvas = canvas
        self.toolbar = toolbar
        
        left_layout.addWidget(self.toolbar)
        left_layout.addWidget(self.canvas, 1)
        
        right_layout = QVBoxLayout()
        
        
        custom_tabs = AnimatedTabWidget()
        
        #TAB 1: BASIC 
        basic_tab = self._create_basic_tab()
        basic_tab_icon = QIcon("icons/plot_tab/customization_tabs/general.png")
        custom_tabs.addTab(basic_tab, basic_tab_icon, "General")
        
        # TAB 2: APPEARANCE
        appearance_tab = self._create_appearance_tab()
        appearance_tab_icon = QIcon("icons/plot_tab/customization_tabs/appearance.png")
        custom_tabs.addTab(appearance_tab, appearance_tab_icon, "Appearance")
        
        # TAB 3: AXES 
        axes_tab = self._create_axes_tab()
        axes_tab_icon = QIcon("icons/plot_tab/customization_tabs/axis.png")
        custom_tabs.addTab(axes_tab, axes_tab_icon, "Axes")
        
        # TAB 4: LEGENDand GRID 
        legend_tab = self._create_legend_tab()
        legend_tab_icon = QIcon("icons/plot_tab/customization_tabs/gridlines.png")
        custom_tabs.addTab(legend_tab, legend_tab_icon, "Legend and Grid")
        
        # TAB 5: ADVANCED (customi)
        advanced_tab = self._create_advanced_tab()
        advanced_tab_icon = QIcon("icons/plot_tab/customization_tabs/customization.png")
        custom_tabs.addTab(advanced_tab, advanced_tab_icon, "Customization") 
        
        #  TAB 6: ANNOTATIONS 
        annotations_tab = self._create_annotations_tab()
        annotations_tab_icon = QIcon("icons/plot_tab/customization_tabs/annotation.png")
        custom_tabs.addTab(annotations_tab, annotations_tab_icon, "Annotations")

        # TAB 7. GEO
        geospatial_tab = self._create_geospatial_tab()
        geospatial_tab_icon = QIcon("icons/plot_tab/customization_tabs/geospatial.png")
        custom_tabs.addTab(geospatial_tab, geospatial_tab_icon, "GeoSpatial")
        
        right_layout.addWidget(custom_tabs, 1)
        
        # Buttons at bottom
        button_layout = QHBoxLayout()
        
        self.plot_button = AnimatedButton(
            "Generate Plot",
            parent=self,
            base_color_hex="#4CAF50",    
            hover_color_hex="#5cb85c",
            pressed_color_hex="#4a9c4d",
            text_color_hex="#FFFFFF",
            border_style="none"
        )
        self.plot_button.setMinimumHeight(40)
        self.plot_button.setIcon(QIcon("icons/generate_plot.png"))
        self.plot_button.setShortcut("Ctrl+Return")
        button_layout.addWidget(self.plot_button)
        
        self.clear_button = AnimatedButton(
            "Clear",
            parent=self,
            base_color_hex="#ededed",    
            hover_color_hex="#f5f5f5",
            pressed_color_hex="#dcdcdc",
            text_color_hex="#000000",
            border_style="1px solid #c9c9c9"
        )
        self.clear_button.setMinimumHeight(40)
        self.clear_button.setIcon(QIcon("icons/clean.png"))
        button_layout.addWidget(self.clear_button)
        
        self.editor_button = AnimatedButton(
            "Open Python Editor",
            parent=self,
            base_color_hex="#2196F3",
            hover_color_hex="#42A5F5",
            pressed_color_hex="#1e88e5",
            text_color_hex="#ffffff",
            border_style="none"
        )
        self.editor_button.setMinimumHeight(40)
        self.editor_button.setIcon(QIcon("icons/code_edit.png"))
        self.editor_button.setToolTip("Open the code editor to view/write python code for the plot.")
        button_layout.addWidget(self.editor_button)
        
        right_layout.addLayout(button_layout)
        
        # Set layouts
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        # Create splitter
        splitter: QSplitter = self._create_splitter(left_widget, right_widget)
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
    
    def _create_basic_tab(self):
        """Create basic settings tab"""
        basic_tab = QWidget()
        layout = QVBoxLayout(basic_tab)
        
        # plot type
        self.plot_type_group = AnimatedGroupBox("Plot Type")
        plot_type_layout = QVBoxLayout()
        self.plot_type = AnimatedComboBox()
        # bith plot type is in the plotTab.py
        plot_type_layout.addWidget(self.plot_type)

        #checkbox for addings ubplots
        self.add_subplots_check = AnimatedCheckBox("Add subplots")
        self.add_subplots_check.setChecked(False)
        plot_type_layout.addWidget(self.add_subplots_check)
        
        self.plot_type_group.setLayout(plot_type_layout)
        layout.addWidget(self.plot_type_group)

        #subplots
        self.subplot_group = AnimatedGroupBox("Subplot Configeration")
        self.subplot_group.setVisible(False)
        subplot_layout = QVBoxLayout()
        subplot_info = QLabel("This tool allows you to control how many subplots you wish to add to the current canvas\nThe rows adjust the number of horizontal plots added and the columns control the number of vertical plots added. Together they make up a array of plots. So if you add 2 rows and 2 columns you get 4 plots.")
        subplot_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        subplot_info.setWordWrap(True)
        subplot_layout.addWidget(subplot_info)

        #grids
        grid_config_layout = QHBoxLayout()
        grid_config_layout.addWidget(QLabel("Rows:"))
        self.subplot_rows_spin = AnimatedSpinBox()
        self.subplot_rows_spin.setToolTip("Adds specified numbers of horizontal subplots")
        self.subplot_rows_spin.setRange(1, 5)
        self.subplot_rows_spin.setValue(1)
        grid_config_layout.addWidget(self.subplot_rows_spin)

        grid_config_layout.addWidget(QLabel("Columns:"))
        self.subplot_cols_spin = AnimatedSpinBox()
        self.subplot_cols_spin.setToolTip("Adds specified numbers of vertical subplots")
        self.subplot_cols_spin.setRange(1, 5)
        self.subplot_cols_spin.setValue(1)
        grid_config_layout.addWidget(self.subplot_cols_spin)

        subplot_layout.addLayout(grid_config_layout)

        #apply subplotlayout button
        self.apply_subplot_layout_button = AnimatedButton("Update Subplot Layout", parent=self)
        self.apply_subplot_layout_button.setToolTip("Warning: This will clear the entire figure")
        subplot_layout.addWidget(self.apply_subplot_layout_button)

        #select an active subplot
        active_subplot_layout = QHBoxLayout()
        active_subplot_layout.addWidget(QLabel("Active Subplot:"))
        self.active_subplot_combo = AnimatedComboBox()
        self.active_subplot_combo.setToolTip("This will set the specified plot to be the active subplot.")
        self.active_subplot_combo.addItem("Plot 1")
        active_subplot_layout.addWidget(self.active_subplot_combo, 1)
        subplot_layout.addLayout(active_subplot_layout)

        self.subplot_group.setLayout(subplot_layout)
        layout.addWidget(self.subplot_group)

        layout.addSpacing(10)

        # data selection
        data_group = AnimatedGroupBox("Data")
        data_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        data_layout = QVBoxLayout()

        # x column selection
        x_layout = QHBoxLayout()
        x_layout.addWidget(QLabel("X Column:"))
        self.x_column = AnimatedComboBox()
        x_layout.addWidget(self.x_column, 1)
        data_layout.addLayout(x_layout)

        # ycols, try for multiple 
        y_label_layout = QHBoxLayout()
        y_label_layout.addWidget(QLabel("Y Columns (s)"))
        y_label_layout.addStretch()

        #toggle between two and more ycols
        self.multi_y_check = AnimatedCheckBox("Multiple Y Columns")
        self.multi_y_check.setChecked(False)
        y_label_layout.addWidget(self.multi_y_check)
        data_layout.addLayout(y_label_layout)

        #single y cols selection
        self.y_column = AnimatedComboBox()
        data_layout.addWidget(self.y_column)

        # multiple ycols list
        self.y_columns_list = AnimatedListWidget()
        self.y_columns_list.setSelectionMode(AnimatedListWidget.SelectionMode.MultiSelection)
        self.y_columns_list.setMaximumHeight(150)
        self.y_columns_list.setVisible(False)
        data_layout.addWidget(self.y_columns_list)

        #btns for multi ycols
        multi_y_buttons = QHBoxLayout()
        self.select_all_y_btn = AnimatedButton("Select All", parent=self)
        self.select_all_y_btn.setVisible(False)
        multi_y_buttons.addWidget(self.select_all_y_btn)

        self.clear_all_y_btn = AnimatedButton("Clear All", parent=self)
        self.clear_all_y_btn.setVisible(False)
        multi_y_buttons.addWidget(self.clear_all_y_btn)
        data_layout.addLayout(multi_y_buttons)
        
        #info for multiplaye
        self.multi_y_info = QLabel("Tip: Hold Ctrl/Cmd to select multiple columns")
        self.multi_y_info.setStyleSheet("color: #7f8c8d; font-size: 9.5pt; font-style: italic;")
        self.multi_y_info.setVisible(False)
        data_layout.addWidget(self.multi_y_info)

        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        hue_group = AnimatedGroupBox("Hue/Group:")
        hue_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        hue_layout = QVBoxLayout()
        self.hue_column = AnimatedComboBox()
        self.hue_column.addItem("None")
        hue_layout.addWidget(self.hue_column)
        hue_group.setLayout(hue_layout)
        layout.addWidget(hue_group)

        #  SUBSEts
        subset_group = AnimatedGroupBox("Data Subset (Optional)")
        subset_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        subset_layout = QVBoxLayout()

        subset_info = QLabel(
            "Plot a specific subset of your data instead of the full dataset.\n"
            "Create subsets in the Data Explorer tab."
        )
        subset_info.setWordWrap(True)
        subset_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        subset_layout.addWidget(subset_info)

        self.use_subset_check = AnimatedCheckBox("Use Subset")
        self.use_subset_check.setChecked(False)
        subset_layout.addWidget(self.use_subset_check)

        self.subset_combo = AnimatedComboBox()
        self.subset_combo.addItem("(Full Dataset)")
        self.subset_combo.setEnabled(False)
        subset_layout.addWidget(self.subset_combo)

        #connect checkbox
        self.use_subset_check.stateChanged.connect(
            lambda state: self.subset_combo.setEnabled(state == Qt.CheckState.Checked.value)
        )
        refresh_subsets_btn = AnimatedButton("Refresh Subset List", parent=self)
        refresh_subsets_btn.clicked.connect(self.refresh_subset_list)
        subset_layout.addWidget(refresh_subsets_btn)

        subset_group.setLayout(subset_layout)
        layout.addWidget(subset_group)


        layout.addSpacing(10)

        #plot description tab
        description_group = AnimatedGroupBox(f"Plot Description: ")
        description_group.setStyleSheet("AnimatedGroupBox { font-size: 16pt; font-weight: bold;}")
        description_layout = QVBoxLayout()
        self.description_label = QLabel()
        self.description_label.setWordWrap(True)
        description_font = QFont()
        description_font.setPointSize(12)
        self.description_label.setFont(description_font)

        description_layout.addWidget(self.description_label)


        description_group.setLayout(description_layout)
        layout.addWidget(description_group)
        
        layout.addStretch()
        return basic_tab
    
    def _create_appearance_tab(self):
        """Create appearance customization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)

        # Font FAMILY
        font_group = AnimatedGroupBox("Font Settings")
        font_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        font_layout = QVBoxLayout()

        font_layout.addWidget(QLabel("Font Family:"))
        self.font_family_combo = QFontComboBox()
        self.font_family_combo.setCurrentFont(QFont("Arial")) #defal
        font_layout.addWidget(self.font_family_combo)
        
        font_group.setLayout(font_layout)
        scroll_layout.addWidget(font_group)

        scroll_layout.addSpacing(15)
        
        # Title
        title_group = AnimatedGroupBox("Title Options")
        title_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        title_layout = QVBoxLayout()
        self.title_check = AnimatedCheckBox("Show Title")
        self.title_check.setChecked(True)
        title_layout.addWidget(self.title_check)
        title_group.setLayout(title_layout)
        
        # enter title
        title_layout.addWidget(QLabel("Title:"))
        self.title_input = AnimatedLineEdit()
        self.title_input.setPlaceholderText("Enter plot title")
        title_layout.addWidget(self.title_input)
        title_group.setLayout(title_layout)
        
        # Title font size
        title_layout.addWidget(QLabel("Title Size:"))
        self.title_size_spin = AnimatedSpinBox()
        self.title_size_spin.setRange(8, 32)
        self.title_size_spin.setValue(14)
        title_layout.addWidget(self.title_size_spin)
        title_group.setLayout(title_layout)

        # title font weight
        title_layout.addWidget(QLabel("Title Font Weight:"))
        self.title_weight_combo = AnimatedComboBox()
        self.title_weight_combo.addItems(["normal", "bold", "light", "heavy"])
        self.title_weight_combo.setCurrentText("bold")
        title_layout.addWidget(self.title_weight_combo)
        title_group.setLayout(title_layout)
        
        #add all to title group
        scroll_layout.addWidget(title_group)

        # X Label
        xlabel_group = AnimatedGroupBox("X Label Options")
        xlabel_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        xlabel_layout = QVBoxLayout()
        self.xlabel_check = AnimatedCheckBox("Show X Label")
        self.xlabel_check.setChecked(True)
        xlabel_layout.addWidget(self.xlabel_check)
        xlabel_group.setLayout(xlabel_layout)
        
        xlabel_layout.addWidget(QLabel("X Label:"))
        self.xlabel_input = AnimatedLineEdit()
        self.xlabel_input.setPlaceholderText("X axis label")
        xlabel_layout.addWidget(self.xlabel_input)
        xlabel_group.setLayout(xlabel_layout)

        xlabel_layout.addWidget(QLabel("X Label fontsize:"))
        self.xlabel_size_spin = AnimatedSpinBox()
        self.xlabel_size_spin.setRange(5, 32)
        self.xlabel_size_spin.setValue(12)
        xlabel_layout.addWidget(self.xlabel_size_spin)
        xlabel_group.setLayout(xlabel_layout)

        #xlabel font weight
        xlabel_layout.addWidget(QLabel("X Label Font Weight"))
        self.xlabel_weight_combo = AnimatedComboBox()
        self.xlabel_weight_combo.addItems(["normal", "bold", "light", "heavy"])
        self.xlabel_weight_combo.setCurrentText("normal")
        xlabel_layout.addWidget(self.xlabel_weight_combo)
        xlabel_group.setLayout(xlabel_layout)

        scroll_layout.addWidget(xlabel_group)
        
        # Y Label
        ylabel_group = AnimatedGroupBox("Y Label Options")
        ylabel_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        ylabel_layout = QVBoxLayout()
        self.ylabel_check = AnimatedCheckBox("Show Y Label")
        self.ylabel_check.setChecked(True)
        ylabel_layout.addWidget(self.ylabel_check)
        ylabel_group.setLayout(ylabel_layout)
        
        ylabel_layout.addWidget(QLabel("Y Label:"))
        self.ylabel_input = AnimatedLineEdit()
        self.ylabel_input.setPlaceholderText("Y axis label")
        ylabel_layout.addWidget(self.ylabel_input)
        ylabel_group.setLayout(ylabel_layout)

        ylabel_layout.addWidget(QLabel("Y Label fontsize:"))
        self.ylabel_size_spin = AnimatedSpinBox()
        self.ylabel_size_spin.setRange(5, 32)
        self.ylabel_size_spin.setValue(12)
        ylabel_layout.addWidget(self.ylabel_size_spin)
        ylabel_group.setLayout(ylabel_layout)

        # ylabel font weight
        ylabel_layout.addWidget(QLabel("Y Label Font Weight:"))
        self.ylabel_weight_combo = AnimatedComboBox()
        self.ylabel_weight_combo.addItems(["normal", "bold", "light", "heavy"])
        self.ylabel_weight_combo.setCurrentText("normal")
        ylabel_layout.addWidget(self.ylabel_weight_combo)
        ylabel_group.setLayout(ylabel_layout)
        
        scroll_layout.addWidget(ylabel_group)

        #### PLOTBORDERS aka spines
        spines_group = AnimatedGroupBox("Plot Spines (Borders)")
        spines_layout = QVBoxLayout()

        #inf label
        spines_info = QLabel("Customize the four borders (spines) of the plotting axes")
        spines_info.setStyleSheet("color: #666; font-style: italic; font-size: 9pt;")
        spines_layout.addWidget(spines_info)

        spines_layout.addSpacing(10)

        #top spine
        top_spine_group = AnimatedGroupBox("Top Spine")
        top_spine_layout = QVBoxLayout()

        self.top_spine_visible_check = AnimatedCheckBox("Show Top Spine")
        self.top_spine_visible_check.setChecked(True)
        top_spine_layout.addWidget(self.top_spine_visible_check)

        top_spine_layout.addWidget(QLabel("Line Width:"))
        self.top_spine_width_spin = AnimatedDoubleSpinBox()
        self.top_spine_width_spin.setRange(0.1, 5.0)
        self.top_spine_width_spin.setValue(1.0)
        self.top_spine_width_spin.setSingleStep(0.1)
        top_spine_layout.addWidget(self.top_spine_width_spin)
        
        top_spine_layout.addWidget(QLabel("Color:"))
        top_spine_color_layout = QHBoxLayout()
        self.top_spine_color_button = AnimatedButton("Choose Color", parent=self)
        self.top_spine_color_label = QLabel("Black")
        top_spine_color_layout.addWidget(self.top_spine_color_button)
        top_spine_color_layout.addWidget(self.top_spine_color_label)
        top_spine_layout.addLayout(top_spine_color_layout)

        top_spine_group.setLayout(top_spine_layout)
        spines_layout.addWidget(top_spine_group)

        # Bottom Spine
        bottom_spine_group = AnimatedGroupBox("Bottom Spine")
        bottom_spine_layout = QVBoxLayout()
        
        self.bottom_spine_visible_check = AnimatedCheckBox("Show Bottom Spine")
        self.bottom_spine_visible_check.setChecked(True)
        bottom_spine_layout.addWidget(self.bottom_spine_visible_check)
        
        bottom_spine_layout.addWidget(QLabel("Line Width:"))
        self.bottom_spine_width_spin = AnimatedDoubleSpinBox()
        self.bottom_spine_width_spin.setRange(0.1, 5.0)
        self.bottom_spine_width_spin.setValue(1.0)
        self.bottom_spine_width_spin.setSingleStep(0.1)
        bottom_spine_layout.addWidget(self.bottom_spine_width_spin)
        
        bottom_spine_layout.addWidget(QLabel("Color:"))
        bottom_spine_color_layout = QHBoxLayout()
        self.bottom_spine_color_button = AnimatedButton("Choose Color", parent=self)
        self.bottom_spine_color_label = QLabel("Black")
        bottom_spine_color_layout.addWidget(self.bottom_spine_color_button)
        bottom_spine_color_layout.addWidget(self.bottom_spine_color_label)
        bottom_spine_layout.addLayout(bottom_spine_color_layout)
        
        bottom_spine_group.setLayout(bottom_spine_layout)
        spines_layout.addWidget(bottom_spine_group)
        
        # Left Spine
        left_spine_group = AnimatedGroupBox("Left Spine")
        left_spine_layout = QVBoxLayout()
        
        self.left_spine_visible_check = AnimatedCheckBox("Show Left Spine")
        self.left_spine_visible_check.setChecked(True)
        left_spine_layout.addWidget(self.left_spine_visible_check)
        
        left_spine_layout.addWidget(QLabel("Line Width:"))
        self.left_spine_width_spin = AnimatedDoubleSpinBox()
        self.left_spine_width_spin.setRange(0.1, 5.0)
        self.left_spine_width_spin.setValue(1.0)
        self.left_spine_width_spin.setSingleStep(0.1)
        left_spine_layout.addWidget(self.left_spine_width_spin)
        
        left_spine_layout.addWidget(QLabel("Color:"))
        left_spine_color_layout = QHBoxLayout()
        self.left_spine_color_button = AnimatedButton("Choose Color", parent=self)
        self.left_spine_color_label = QLabel("Black")
        left_spine_color_layout.addWidget(self.left_spine_color_button)
        left_spine_color_layout.addWidget(self.left_spine_color_label)
        left_spine_layout.addLayout(left_spine_color_layout)
        
        left_spine_group.setLayout(left_spine_layout)
        spines_layout.addWidget(left_spine_group)
        
        # Right Spine
        right_spine_group = AnimatedGroupBox("Right Spine")
        right_spine_layout = QVBoxLayout()
        
        self.right_spine_visible_check = AnimatedCheckBox("Show Right Spine")
        self.right_spine_visible_check.setChecked(True)
        right_spine_layout.addWidget(self.right_spine_visible_check)
        
        right_spine_layout.addWidget(QLabel("Line Width:"))
        self.right_spine_width_spin = AnimatedDoubleSpinBox()
        self.right_spine_width_spin.setRange(0.1, 5.0)
        self.right_spine_width_spin.setValue(1.0)
        self.right_spine_width_spin.setSingleStep(0.1)
        right_spine_layout.addWidget(self.right_spine_width_spin)
        
        right_spine_layout.addWidget(QLabel("Color:"))
        right_spine_color_layout = QHBoxLayout()
        self.right_spine_color_button = AnimatedButton("Choose Color", parent=self)
        self.right_spine_color_label = QLabel("Black")
        right_spine_color_layout.addWidget(self.right_spine_color_button)
        right_spine_color_layout.addWidget(self.right_spine_color_label)
        right_spine_layout.addLayout(right_spine_color_layout)
        
        right_spine_group.setLayout(right_spine_layout)
        spines_layout.addWidget(right_spine_group)

        #QUICK presents?
        spines_layout.addSpacing(10)
        presets_label = QLabel("Quick Presets")
        presets_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        spines_layout.addWidget(presets_label)

        presets_button_layout = QHBoxLayout()
        
        #all spines
        self.all_spines_btn = AnimatedButton("All Spines", parent=self)
        self.all_spines_btn.setToolTip("Show all four spines")
        presets_button_layout.addWidget(self.all_spines_btn)

        #box only (Lshape)
        self.box_only_btn = AnimatedButton("Box Only", parent=self)
        self.box_only_btn.setToolTip("Show only left and bottom spines")
        presets_button_layout.addWidget(self.box_only_btn)

        #no spines preset
        self.no_spines_btn = AnimatedButton("No Spines", parent=self)
        self.no_spines_btn.setToolTip("Hide all spines")
        presets_button_layout.addWidget(self.no_spines_btn)

        spines_layout.addLayout(presets_button_layout)

        spines_group.setLayout(spines_layout)
        scroll_layout.addWidget(spines_group)

        # Figure size
        figure_size_group = AnimatedGroupBox("Figure Settings")
        figure_size_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        figure_size_layout = QVBoxLayout()
        figure_size_layout.addWidget(QLabel("Figure Width:"))
        self.width_spin = AnimatedSpinBox()
        self.width_spin.setRange(4, 20)
        self.width_spin.setValue(12)
        figure_size_layout.addWidget(self.width_spin)
        figure_size_group.setLayout(figure_size_layout)
        
        figure_size_layout.addWidget(QLabel("Figure Height:"))
        self.height_spin = AnimatedSpinBox()
        self.height_spin.setRange(4, 20)
        self.height_spin.setValue(8)
        figure_size_layout.addWidget(self.height_spin)
        figure_size_group.setLayout(figure_size_layout)

        # DPI
        figure_size_layout.addWidget(QLabel("DPI (Resolution):"))
        self.dpi_spin = AnimatedSpinBox()
        self.dpi_spin.setRange(50, 300)
        self.dpi_spin.setValue(100)
        figure_size_layout.addWidget(self.dpi_spin)
        figure_size_group.setLayout(figure_size_layout)
        
        # Background color
        figure_size_layout.addWidget(QLabel("Background Color:"))
        bg_layout = QHBoxLayout()
        self.bg_color_button = AnimatedButton("Choose Color", parent=self)
        self.bg_color_label = QLabel("White")
        bg_layout.addWidget(self.bg_color_button)
        bg_layout.addWidget(self.bg_color_label)
        figure_size_layout.addLayout(bg_layout)

        #facecolor color color color color color color colorcolorcolor color color color color
        figure_size_layout.addWidget(QLabel("Plot Area Color"))
        face_layout = QHBoxLayout()
        self.face_color_button = AnimatedButton("Choose Color", parent=self)
        self.face_color_label = QLabel("White")
        face_layout.addWidget(self.face_color_button)
        face_layout.addWidget(self.face_color_label)
        figure_size_layout.addLayout(face_layout)
        
        # Color palette
        figure_size_layout.addWidget(QLabel("Color Palette:"))
        self.palette_combo = AnimatedComboBox()
        self.palette_combo.addItems(['viridis','deep', 'muted', 'pastel', 'bright', 'dark', 'colorblind', 'husl', 'Set2'])
        figure_size_layout.addWidget(self.palette_combo)
    
        # === OTHER SETTINGS ===
        
        figure_size_layout.addWidget(QLabel("Layout:"))
        self.tight_layout_check = AnimatedCheckBox("Tight Layout")
        self.tight_layout_check.setChecked(True)
        figure_size_layout.addWidget(self.tight_layout_check)
        
        figure_size_layout.addWidget(QLabel("Style:"))
        self.style_combo = AnimatedComboBox()
        self.style_combo.addItems(['default', 'ggplot', 'seaborn', 'dark_background', 'bmh'])
        figure_size_layout.addWidget(self.style_combo)

        scroll_layout.addWidget(figure_size_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        return tab
    
    def _create_axes_tab(self):
        """Create axes customization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # X-axis limits
        xaxis_limit_group = AnimatedGroupBox("X-axis Options")
        xaxis_limit_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        xaxis_limit_layout = QVBoxLayout()

        xaxis_limit_layout.addWidget(QLabel("X-axis - Auto Limit:"))
        self.x_auto_check = AnimatedCheckBox("Auto")
        self.x_auto_check.setChecked(True)
        xaxis_limit_layout.addWidget(self.x_auto_check)
        xaxis_limit_group.setLayout(xaxis_limit_layout)

        self.x_invert_axis_check = AnimatedCheckBox("Invert X-axis")
        self.x_invert_axis_check.setChecked(False)
        self.x_invert_axis_check.setToolTip("Reverses the direction of data on the x-axis")
        xaxis_limit_layout.addWidget(self.x_invert_axis_check)

        self.x_top_axis_check = AnimatedCheckBox("Move X-axis to top")
        self.x_top_axis_check.setChecked(False)
        self.x_top_axis_check.setToolTip("Moves the x-axis ticks and labels to the top of the plot")
        xaxis_limit_layout.addWidget(self.x_top_axis_check)
        
        xaxis_limit_layout.addWidget(QLabel("X Min:"))
        self.x_min_spin = AnimatedDoubleSpinBox()
        self.x_min_spin.setRange(-1000000, 1000000)
        self.x_min_spin.setEnabled(False)
        xaxis_limit_layout.addWidget(self.x_min_spin)
        xaxis_limit_group.setLayout(xaxis_limit_layout)
        
        xaxis_limit_layout.addWidget(QLabel("X Max:"))
        self.x_max_spin = AnimatedDoubleSpinBox()
        self.x_max_spin.setRange(-1000000, 1000000)
        self.x_max_spin.setEnabled(False)
        xaxis_limit_layout.addWidget(self.x_max_spin)

        # x-axis label size
        xaxis_limit_layout.addWidget(QLabel("X-axis Tick Label Size:"))
        self.xtick_label_size_spin = AnimatedSpinBox()
        self.xtick_label_size_spin.setRange(6, 20)
        self.xtick_label_size_spin.setValue(10)
        xaxis_limit_layout.addWidget(self.xtick_label_size_spin)

        #xaxus rotation
        xaxis_limit_layout.addWidget(QLabel("X-axis Tick Rotation:"))
        self.xtick_rotation_spin = AnimatedSpinBox()
        self.xtick_rotation_spin.setRange(-90, 90)
        self.xtick_rotation_spin.setValue(0)
        xaxis_limit_layout.addWidget(self.xtick_rotation_spin)
        
        xaxis_limit_layout.addWidget(QLabel("Max Number of Ticks"))
        self.x_max_ticks_spin = AnimatedSpinBox()
        self.x_max_ticks_spin.setRange(3, 30)
        self.x_max_ticks_spin.setValue(10)
        self.x_max_ticks_spin.setToolTip("Maximum number of tick labels on the x-axis")
        xaxis_limit_layout.addWidget(self.x_max_ticks_spin)
        
        xaxis_limit_layout.addSpacing(5)
        # X-axis minor ticks
        #visibility of the ticks
        
        self.x_show_minor_ticks_check = AnimatedCheckBox("Show Minor X-axis Ticks")
        self.x_show_minor_ticks_check.setChecked(False)
        self.x_show_minor_ticks_check.setToolTip("Display the minor tick marks and labels on the x-axis")
        xaxis_limit_layout.addWidget(self.x_show_minor_ticks_check)

        xaxis_limit_layout.addSpacing(5)
        #Direction of ticks (major)
        xaxis_limit_layout.addWidget(QLabel("X-axis major Tick Direction:"))
        self.x_major_tick_direction_combo = AnimatedComboBox()
        self.x_major_tick_direction_combo.addItems(["out", "in", "inout"])
        self.x_major_tick_direction_combo.setToolTip("Direction of the major tick marks")
        xaxis_limit_layout.addWidget(self.x_major_tick_direction_combo)

        #width of the major ticks [major]
        xaxis_limit_layout.addWidget(QLabel("X-axis Major Tick Width"))
        self.x_major_tick_width_spin = AnimatedDoubleSpinBox()
        self.x_major_tick_width_spin.setRange(0.1, 5.0)
        self.x_major_tick_width_spin.setValue(1.0)
        self.x_major_tick_width_spin.setSingleStep(0.1)
        self.x_major_tick_width_spin.setToolTip("Width/thickness of the major tick marks")
        xaxis_limit_layout.addWidget(self.x_major_tick_width_spin)

        #ticks direction (minor)
        xaxis_limit_layout.addWidget(QLabel("X-axis Minor Tick Direction"))
        self.x_minor_tick_direction_combo = AnimatedComboBox()
        self.x_minor_tick_direction_combo.addItems(["out", "in", "inout"])
        self.x_minor_tick_direction_combo.setToolTip("Direction of the minor tick marks")
        xaxis_limit_layout.addWidget(self.x_minor_tick_direction_combo)

        #tick width (minor)
        xaxis_limit_layout.addWidget(QLabel("X-axis Minor Tick Width"))
        self.x_minor_tick_width_spin = AnimatedDoubleSpinBox()
        self.x_minor_tick_width_spin.setRange(0.1, 5.0)
        self.x_minor_tick_width_spin.setValue(0.5)
        self.x_minor_tick_width_spin.setSingleStep(0.1)
        self.x_minor_tick_width_spin.setToolTip("Width/thickness of minor tick marks")
        xaxis_limit_layout.addWidget(self.x_minor_tick_width_spin)

        #xaxis scale
        xaxis_limit_layout.addWidget(QLabel("X Scale:"))
        self.x_scale_combo = AnimatedComboBox()
        self.x_scale_combo.addItems(['linear', 'log', 'symlog'])
        xaxis_limit_layout.addWidget(self.x_scale_combo)

        xaxis_limit_layout.addSpacing(5)
        xaxis_limit_layout.addWidget(QLabel("X-axis Display Units:"))
        self.x_display_units_combo = AnimatedComboBox()
        self.x_display_units_combo.addItems(["None", "Hundreds (100s)", "Thousands", "Millions", "Billions"])
        self.x_display_units_combo.setToolTip("Format axis labels to display in units")
        xaxis_limit_layout.addWidget(self.x_display_units_combo)
        xaxis_limit_group.setLayout(xaxis_limit_layout)

        scroll_layout.addWidget(xaxis_limit_group)
        
        scroll_layout.addSpacing(15)
        
        # Y-axis limits
        yaxis_limit_group = AnimatedGroupBox("Y-axis Options")
        yaxis_limit_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        yaxis_limit_layout = QVBoxLayout()
        yaxis_limit_layout.addWidget(QLabel("Y-axis - Auto Limit:"))
        self.y_auto_check = AnimatedCheckBox("Auto")
        self.y_auto_check.setChecked(True)
        yaxis_limit_layout.addWidget(self.y_auto_check)

        self.y_invert_axis_check = AnimatedCheckBox("Invert Y-axis")
        self.y_invert_axis_check.setChecked(False)
        self.y_invert_axis_check.setToolTip("Reverses the direction of data on the y-axis")
        yaxis_limit_layout.addWidget(self.y_invert_axis_check)
        
        yaxis_limit_layout.addWidget(QLabel("Y Min:"))
        self.y_min_spin = AnimatedDoubleSpinBox()
        self.y_min_spin.setRange(-1000000, 1000000)
        self.y_min_spin.setEnabled(False)
        yaxis_limit_layout.addWidget(self.y_min_spin)
        
        yaxis_limit_layout.addWidget(QLabel("Y Max:"))
        self.y_max_spin = AnimatedDoubleSpinBox()
        self.y_max_spin.setRange(-1000000, 1000000)
        self.y_max_spin.setEnabled(False)
        yaxis_limit_layout.addWidget(self.y_max_spin)

        # y-axis label size
        yaxis_limit_layout.addWidget(QLabel("Y-axis Tick Label Size:"))
        self.ytick_label_size_spin = AnimatedSpinBox()
        self.ytick_label_size_spin.setRange(6, 20)
        self.ytick_label_size_spin.setValue(10)
        yaxis_limit_layout.addWidget(self.ytick_label_size_spin)

        #yaxus rotation
        yaxis_limit_layout.addWidget(QLabel("Y-axis Tick Rotation:"))
        self.ytick_rotation_spin = AnimatedSpinBox()
        self.ytick_rotation_spin.setRange(-90, 90)
        self.ytick_rotation_spin.setValue(0)
        yaxis_limit_layout.addWidget(self.ytick_rotation_spin)

        yaxis_limit_layout.addWidget(QLabel("Max Number of Ticks"))
        self.y_max_ticks_spin = AnimatedSpinBox()
        self.y_max_ticks_spin.setRange(3, 30)
        self.y_max_ticks_spin.setValue(10)
        self.y_max_ticks_spin.setToolTip("Maximum number of tick labels on the y-axis")
        yaxis_limit_layout.addWidget(self.y_max_ticks_spin)

        yaxis_limit_layout.addSpacing(5)
        #YAXIS minors
        #visibility
        self.y_show_minor_ticks_check = AnimatedCheckBox("Show Y-axis Minor Ticks")
        self.y_show_minor_ticks_check.setChecked(False)
        self.y_show_minor_ticks_check.setToolTip("Display the minor tick marks and labels on yhe y-axis")
        yaxis_limit_layout.addWidget(self.y_show_minor_ticks_check)
        
        yaxis_limit_layout.addSpacing(5)
        #yaxis tickdirection (major)
        yaxis_limit_layout.addWidget(QLabel("Y-axis Major Tick Direction:"))
        self.y_major_tick_direction_combo = AnimatedComboBox()
        self.y_major_tick_direction_combo.addItems(["out", "in", "inout"])
        self.y_major_tick_direction_combo.setToolTip("Direction of the major tick marks on the Y-axis")
        yaxis_limit_layout.addWidget(self.y_major_tick_direction_combo)

        #major tickwidth
        yaxis_limit_layout.addWidget(QLabel("Y-axis Major Tick Width:"))
        self.y_major_tick_width_spin = AnimatedDoubleSpinBox()
        self.y_major_tick_width_spin.setRange(0.1, 5.0)
        self.y_major_tick_width_spin.setValue(1.0)
        self.y_major_tick_width_spin.setSingleStep(0.1)
        self.y_major_tick_width_spin.setToolTip("Width/thickness of the major tick marks")
        yaxis_limit_layout.addWidget(self.y_major_tick_width_spin)

        #mino direction
        yaxis_limit_layout.addWidget(QLabel("Y-axis Minor Tick Direction"))
        self.y_minor_tick_direction_combo = AnimatedComboBox()
        self.y_minor_tick_direction_combo.addItems(["out", "in", "inout"])
        self.y_minor_tick_direction_combo.setToolTip("Direction of the minor tick marks on the Y-axis")
        yaxis_limit_layout.addWidget(self.y_minor_tick_direction_combo)

        yaxis_limit_layout.addWidget(QLabel("Y-axis Minor Tick Width:"))
        self.y_minor_tick_width_spin = AnimatedDoubleSpinBox()
        self.y_minor_tick_width_spin.setRange(0.1, 5.0)
        self.y_minor_tick_width_spin.setValue(0.5)
        self.y_minor_tick_width_spin.setSingleStep(0.1)
        self.y_minor_tick_width_spin.setToolTip("Width/thickness of minor tick marks")
        yaxis_limit_layout.addWidget(self.y_minor_tick_width_spin)

        # yaxis scale
        yaxis_limit_layout.addWidget(QLabel("Y Scale:"))
        self.y_scale_combo = AnimatedComboBox()
        self.y_scale_combo.addItems(['linear', 'log', 'symlog'])
        yaxis_limit_layout.addWidget(self.y_scale_combo)
        
        yaxis_limit_layout.addSpacing(5)
        yaxis_limit_layout.addWidget(QLabel("Y-axis Display Units"))
        self.y_display_units_combo = AnimatedComboBox()
        self.y_display_units_combo.addItems(["None", "Hundreds (100s)", "Thousands", "Millions", "Billions"])
        self.y_display_units_combo.setToolTip("Format axis labels to display in units")
        yaxis_limit_layout.addWidget(self.y_display_units_combo)

        yaxis_limit_group.setLayout(yaxis_limit_layout)

        scroll_layout.addWidget(yaxis_limit_group)

        # FLiping axis feature
        flip_axes_group = AnimatedGroupBox("Axis Orientation")
        flip_axes_group.setStyleSheet("AnimatedGroupBox { font-size: 14pt; font-weight: bold;}")
        flip_axes_layout = QVBoxLayout()

        self.flip_axes_check = AnimatedCheckBox("Flip Axis (Swap X and Y axis)")
        self.flip_axes_check.setChecked(False)
        flip_axes_layout.addWidget(self.flip_axes_check)

        flip_axes_group.setLayout(flip_axes_layout)
        scroll_layout.addWidget(flip_axes_group)

        #datetime formatting
        datetime_format_group = AnimatedGroupBox("DateTime Formatting")
        datetime_format_layout = QVBoxLayout()

        #enable custom datetimeformatting
        self.custom_datetime_check = AnimatedCheckBox("Enable Custom formatting of DateTime Axis")
        self.custom_datetime_check.setChecked(False)
        datetime_format_layout.addWidget(self.custom_datetime_check)

        #for the xaxis
        self.format_x_datetime_label = QLabel("Format for the X-axis")
        self.format_x_datetime_label.setVisible(False)
        datetime_format_layout.addWidget(self.format_x_datetime_label)
        self.x_datetime_format_combo = AnimatedComboBox()
        self.x_datetime_format_combo.setVisible(False)
        self.x_datetime_format_combo.setEnabled(False)
        self.x_datetime_format_combo.addItems([
            "Auto",
            "%Y-%m-%d (2024-01-15)",
            "%d/%m/%Y (15/01/2024)",
            "%m/%d/%Y (01/15/2024)",
            "%Y/%m/%d (2024/01/15)",
            "%d-%m-%Y (15-01-2024)",
            "%d/%m/%y (15/01/24)",
            "%m/%d/%y (01/15/24)",
            "%b %d, %Y (Jan 15, 2024)",
            "%d %b %Y (15 Jan 2024)",
            "%B %d, %Y (January 15, 2024)",
            "%Y-%m-%d %H:%M (2024-01.15 14:30)",
            "%d/%m/%Y %H:%M (15/01/2024 14:30)",
            "%Y-%m-%d %H:%M:%S (2024-01-15 14:30:45)",
            "%H:%M (14:30)",
            "%H:%M:%S (14:30:45)",
            "%I:%M %p (02:30 PM)",
            "%Y-W%W (2024-W03)",
            "%Y-Q%q (2024-Q1)",
            "Custom"
        ])
        datetime_format_layout.addWidget(self.x_datetime_format_combo)

        #custom format input for the xaxis
        self.custom_x_axis_format_label = QLabel("Custom X-axis Format")
        self.custom_x_axis_format_label.setVisible(False)
        datetime_format_layout.addWidget(self.custom_x_axis_format_label)
        self.x_custom_datetime_input = AnimatedLineEdit()
        self.x_custom_datetime_input.setPlaceholderText("e.g. %d/%m/%Y %H:%M")
        self.x_custom_datetime_input.setEnabled(False)
        self.x_custom_datetime_input.setVisible(False)
        self.x_custom_datetime_input.setToolTip(
            "Use strftime format codes:\n"
            "%Y = Year (4-digit), %y = Year (2-digit)\n"
            "%m = Month (01-12), %B = Month name, %b = Short month\n"
            "%d = Day (01-31)\n"
            "%H = Hour (00-23), %I = Hour (01-12)\n"
            "%M = Minute (00-59), %S = Second (00-59)\n"
            "%p = AM/PM\n"
            "%A = Weekday name, %a = Short weekday\n"
            "%W = Week number"
        )
        datetime_format_layout.addWidget(self.x_custom_datetime_input)

        datetime_format_layout.addSpacing(10)

        # do te same for the yxaxis
        self.format_y_datetime_label = QLabel("Format for the Y-axis")
        datetime_format_layout.addWidget(self.format_y_datetime_label)
        self.format_y_datetime_label.setVisible(False)
        self.y_datetime_format_combo = AnimatedComboBox()
        self.y_datetime_format_combo.setEnabled(False)
        self.y_datetime_format_combo.setVisible(False)
        self.y_datetime_format_combo.addItems([
            "Auto",
            "%Y-%m-%d (2024-01-15)",
            "%d/%m/%Y (15/01/2024)",
            "%m/%d&Y (01/15/2024)",
            "%Y/%m%d (2024/01/15)",
            "%d-%m-%Y (15-01-2024)",
            "%d/%m/&y (15/01/24)",
            "%m/%d/%y (01/15/24)",
            "%b %d, %Y (Jan 15, 2024)",
            "%d %b %Y (15 Jan 2024)",
            "%B %d, %Y (January 15, 2024)",
            "%Y-m-%d %H:%M (2024-01.15 14:30)",
            "%d/%m/%Y %H:%M (15/01/2024 14:30)",
            "%Y-%m-%d %H:%M:%S (2024-01-15 14:30:45)",
            "%H:%M (14:30)",
            "%H:%M:%S (14:30:45)",
            "%I:%M %p (02:30 PM)",
            "%Y-W%W (2024-W03)",
            "%Y-Q%q (2024-Q1)",
            "Custom"
        ])
        datetime_format_layout.addWidget(self.y_datetime_format_combo)

        #custom input for yaxis
        self.custom_y_axis_format_label = QLabel("Custom Y-axis Format")
        datetime_format_layout.addWidget(self.custom_y_axis_format_label)
        self.custom_y_axis_format_label.setVisible(False)
        self.y_custom_datetime_format_input = AnimatedLineEdit()
        self.y_custom_datetime_format_input.setPlaceholderText("e.g. %d/%m/%Y %H:%M")
        self.y_custom_datetime_format_input.setEnabled(False)
        self.y_custom_datetime_format_input.setVisible(False)
        self.y_custom_datetime_format_input.setToolTip(
            "Use strftime format codes:\n"
            "%Y = Year (4-digit), %y = Year (2-digit)\n"
            "%m = Month (01-12), %B = Month name, %b = Short month\n"
            "%d = Day (01-31)\n"
            "%H = Hour (00-23), %I = Hour (01-12)\n"
            "%M = Minute (00-59), %S = Second (00-59)\n"
            "%p = AM/PM\n"
            "%A = Weekday name, %a = Short weekday\n"
            "%W = Week number"
        )
        datetime_format_layout.addWidget(self.y_custom_datetime_format_input)

        #format guide
        self.format_help = QLabel(
            "<b>Common Format Codes:</b><br>"
            "<font size='2'>"
            "%Y = 2024 (4-digit year)<br>"
            "%y = 24 (2-digit year)<br>"
            "%m = 01-12 (month)<br>"
            "%d = 01-31 (day)<br>"
            "%H = 00-23 (hour 24h)<br>"
            "%I = 01-12 (hour 12h)<br>"
            "%M = 00-59 (minute)<br>"
            "%S = 00-59 (second)<br>"
            "%p = AM/PM<br>"
            "%b = Jan, Feb... (short month)<br>"
            "%B = January, February... (full month)<br>"
            "%a = Mon, Tue... (short day)<br>"
            "%A = Monday, Tuesday... (full day)"
            "</font>"
        )
        self.format_help.setVisible(False)
        self.format_help.setWordWrap(True)
        self.format_help.setStyleSheet("background-color: #f0f0f0; padding: 8px; border-radius: 4px; margin-top: 10px;")
        datetime_format_layout.addWidget(self.format_help)

        datetime_format_group.setLayout(datetime_format_layout)
        scroll_layout.addWidget(datetime_format_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        return tab
    
    def _create_legend_tab(self):
        """Create legend and grid tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # === LEGEND SETTINGS ===
        legend_group = AnimatedGroupBox("Legend")
        legend_layout = QVBoxLayout()
        
        self.legend_check = AnimatedCheckBox("Show Legend")
        self.legend_check.setChecked(False)
        legend_layout.addWidget(self.legend_check)
        
        self.legend_location_label = QLabel("Legend Placement:")
        self.legend_location_label.setVisible(False)
        legend_layout.addWidget(self.legend_location_label)
        self.legend_loc_combo = AnimatedComboBox()
        self.legend_loc_combo.addItems(['best', 'upper right', 'upper left', 'lower left', 'lower right', 'right', 'center left', 'center right', 'lower center', 'upper center', 'center'])
        self.legend_loc_combo.setVisible(False)
        legend_layout.addWidget(self.legend_loc_combo)
        
        self.legend_title_label = QLabel("Legend Title:")
        self.legend_title_label.setVisible(False)
        legend_layout.addWidget(self.legend_title_label)
        self.legend_title_input = AnimatedLineEdit()
        self.legend_title_input.setPlaceholderText("Enter legend title")
        self.legend_title_input.setVisible(False)
        legend_layout.addWidget(self.legend_title_input)
        
        self.legend_font_size_label = QLabel("Legend Font Size:")
        self.legend_font_size_label.setVisible(False)
        legend_layout.addWidget(self.legend_font_size_label)
        self.legend_size_spin = AnimatedSpinBox()
        self.legend_size_spin.setRange(6, 20)
        self.legend_size_spin.setValue(10)
        self.legend_size_spin.setVisible(False)
        legend_layout.addWidget(self.legend_size_spin)
        
        self.legend_ncols_label = QLabel("Number of Columns:")
        self.legend_ncols_label.setVisible(False)
        legend_layout.addWidget(self.legend_ncols_label)
        self.legend_columns_spin = AnimatedSpinBox()
        self.legend_columns_spin.setRange(1, 5)
        self.legend_columns_spin.setValue(1)
        self.legend_columns_spin.setVisible(False)
        legend_layout.addWidget(self.legend_columns_spin)
        
        self.legend_column_spacing_label = QLabel("Column Spacing:")
        self.legend_column_spacing_label.setVisible(False)
        legend_layout.addWidget(self.legend_column_spacing_label)
        self.legend_colspace_spin = AnimatedDoubleSpinBox()
        self.legend_colspace_spin.setRange(0.5, 5.0)
        self.legend_colspace_spin.setValue(1.0)
        self.legend_colspace_spin.setSingleStep(0.1)
        self.legend_colspace_spin.setVisible(False)
        legend_layout.addWidget(self.legend_colspace_spin)
        
        legend_group.setLayout(legend_layout)
        scroll_layout.addWidget(legend_group)

        scroll_layout.addSpacing(10)
        
        # === LEGEND BOX STYLING ===
        self.box_styling_group = AnimatedGroupBox("Legend Box Styling")
        self.box_styling_group.setVisible(False)
        box_styling_layout = QVBoxLayout()
        
        self.legend_frame_check = AnimatedCheckBox("Show Frame")
        self.legend_frame_check.setChecked(True)
        box_styling_layout.addWidget(self.legend_frame_check)
        
        self.legend_fancybox_check = AnimatedCheckBox("Fancy Box (Rounded Corners)")
        self.legend_fancybox_check.setChecked(True)
        box_styling_layout.addWidget(self.legend_fancybox_check)
        
        self.legend_shadow_check = AnimatedCheckBox("Show Shadow")
        self.legend_shadow_check.setChecked(False)
        box_styling_layout.addWidget(self.legend_shadow_check)
        
        box_styling_layout.addWidget(QLabel("Background Color:"))
        legend_bg_layout = QHBoxLayout()
        self.legend_bg_button = AnimatedButton("Choose", parent=self)
        self.legend_bg_label = QLabel("White")
        legend_bg_layout.addWidget(self.legend_bg_button)
        legend_bg_layout.addWidget(self.legend_bg_label)
        box_styling_layout.addLayout(legend_bg_layout)
        
        box_styling_layout.addWidget(QLabel("Edge Color:"))
        legend_edge_layout = QHBoxLayout()
        self.legend_edge_button = AnimatedButton("Choose", parent=self)
        self.legend_edge_label = QLabel("Black")
        legend_edge_layout.addWidget(self.legend_edge_button)
        legend_edge_layout.addWidget(self.legend_edge_label)
        box_styling_layout.addLayout(legend_edge_layout)
        
        box_styling_layout.addWidget(QLabel("Edge Width:"))
        self.legend_edge_width_spin = AnimatedDoubleSpinBox()
        self.legend_edge_width_spin.setRange(0.5, 3.0)
        self.legend_edge_width_spin.setValue(1.0)
        self.legend_edge_width_spin.setSingleStep(0.1)
        box_styling_layout.addWidget(self.legend_edge_width_spin)
        
        box_styling_layout.addWidget(QLabel("Box Alpha (Transparency):"))
        self.legend_alpha_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.legend_alpha_slider.setRange(10, 100)
        self.legend_alpha_slider.setValue(100)
        box_styling_layout.addWidget(self.legend_alpha_slider)
        
        self.legend_alpha_label = QLabel("100%")
        box_styling_layout.addWidget(self.legend_alpha_label)
        
        self.box_styling_group.setLayout(box_styling_layout)
        scroll_layout.addWidget(self.box_styling_group)

        scroll_layout.addSpacing(10)
        
        # === GRID SETTINGS ===
        #docs https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.grid.html
        grid_group = AnimatedGroupBox("Gridlines")
        grid_layout = QVBoxLayout()

        self.grid_check = AnimatedCheckBox("Show Gridlines") # set visible in docs
        grid_layout.addWidget(self.grid_check)

        grid_layout.addSpacing(10)

        #GLOBAL gridline settings
        self.global_grid_group = AnimatedGroupBox("Global Gridline Settings")
        self.global_grid_group.setVisible(False)
        global_grid_layout = QVBoxLayout()

        #gridline type
        global_grid_layout.addWidget(QLabel("Type:"))
        self.grid_which_type_combo = AnimatedComboBox()
        self.grid_which_type_combo.addItems(["major", "minor", "both"])
        self.grid_which_type_combo.setToolTip("major = Primary gridlines\nminor = Secondary gridlines\nboth = All gridlines")
        self.grid_which_type_combo.setEnabled(False)
        global_grid_layout.addWidget(self.grid_which_type_combo)

        #which axis
        global_grid_layout.addWidget(QLabel("Apply to which axis:"))
        self.grid_axis_combo = AnimatedComboBox()
        self.grid_axis_combo.addItems(["both", "x", "y"])
        self.grid_axis_combo.setToolTip("Choose which axis to show gridlines")
        global_grid_layout.addWidget(self.grid_axis_combo)

        global_grid_layout.addWidget(QLabel("Grid Alpha (Transparency):"))
        self.global_grid_alpha_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.global_grid_alpha_slider.setRange(10, 100)
        self.global_grid_alpha_slider.setValue(100)
        global_grid_layout.addWidget(self.global_grid_alpha_slider)
        self.global_grid_alpha_label = QLabel("100%")
        global_grid_layout.addWidget(self.global_grid_alpha_label)
        
        self.global_grid_group.setLayout(global_grid_layout)
        grid_layout.addWidget(self.global_grid_group)

        # INDEPENDENTA AXIS
        self.independent_grid_check = AnimatedCheckBox("Enable Independent Axis Customization")
        self.independent_grid_check.setChecked(False)
        grid_layout.addWidget(self.independent_grid_check)

        #Tabs for x and y axis ad thier gridlines
        self.grid_axis_tab = AnimatedTabWidget()
        self.grid_axis_tab.setVisible(False)

        #X AXIS GRIDLINES
        x_grid_tab = QWidget()
        x_grid_layout = QVBoxLayout(x_grid_tab)

        # X major gridline
        x_major_group = AnimatedGroupBox("X-axis Major Gridlines")
        x_major_layout = QVBoxLayout()

        self.x_major_grid_check = AnimatedCheckBox("Show X major gridlines")
        self.x_major_grid_check.setChecked(True)
        x_major_layout.addWidget(self.x_major_grid_check)

        x_major_layout.addWidget(QLabel("Linestyle:"))
        self.x_major_grid_style_combo = AnimatedComboBox()
        self.x_major_grid_style_combo.addItems(["-", "--", "-.", ":"])
        self.x_major_grid_style_combo.setItemText(0, "Solid (-)")
        self.x_major_grid_style_combo.setItemText(1, "Dashed (--)")
        self.x_major_grid_style_combo.setItemText(2, "Dash-dot (-.)")
        self.x_major_grid_style_combo.setItemText(3, "Dotted (:)")
        x_major_layout.addWidget(self.x_major_grid_style_combo)

        x_major_layout.addWidget(QLabel("Linewidth:"))
        self.x_major_grid_linewidth_spin = AnimatedDoubleSpinBox()
        self.x_major_grid_linewidth_spin.setRange(0.1, 5.0)
        self.x_major_grid_linewidth_spin.setValue(0.8)
        self.x_major_grid_linewidth_spin.setSingleStep(0.1)
        x_major_layout.addWidget(self.x_major_grid_linewidth_spin)

        x_major_layout.addWidget(QLabel("Color"))
        x_major_color_layout = QHBoxLayout()
        self.x_major_grid_color_button = AnimatedButton("Choose Color", parent=self)
        self.x_major_grid_color_label = QLabel("Gray")
        x_major_color_layout.addWidget(self.x_major_grid_color_button)
        x_major_color_layout.addWidget(self.x_major_grid_color_label)
        x_major_layout.addLayout(x_major_color_layout)

        x_major_layout.addWidget(QLabel("Alpha (Transparency)"))
        self.x_major_grid_alpha_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.x_major_grid_alpha_slider.setRange(10, 100)
        self.x_major_grid_alpha_slider.setValue(75)
        x_major_layout.addWidget(self.x_major_grid_alpha_slider)
        self.x_major_grid_alpha_label = QLabel("75%")
        x_major_layout.addWidget(self.x_major_grid_alpha_label)
        
        x_major_group.setLayout(x_major_layout)
        x_grid_layout.addWidget(x_major_group)

        #X axis minor gridlines
        x_minor_group = AnimatedGroupBox("X-axis Minor Gridlines")
        x_minor_layout = QVBoxLayout()

        #check
        self.x_minor_grid_check = AnimatedCheckBox("Show minor X-axis Gridlines")
        self.x_minor_grid_check.setChecked(False)
        x_minor_layout.addWidget(self.x_minor_grid_check)

        #linestyle
        x_minor_layout.addWidget(QLabel("Linestyle:"))
        self.x_minor_grid_style_combo = AnimatedComboBox()
        self.x_minor_grid_style_combo.addItems(['-', '--', '-.', ':'])
        self.x_minor_grid_style_combo.setItemText(0, 'Solid (-)')
        self.x_minor_grid_style_combo.setItemText(1, 'Dashed (--)')
        self.x_minor_grid_style_combo.setItemText(2, 'Dash-dot (-.)')
        self.x_minor_grid_style_combo.setItemText(3, 'Dotted (:)')
        self.x_minor_grid_style_combo.setCurrentIndex(3)  #set Default tob e dotted
        x_minor_layout.addWidget(self.x_minor_grid_style_combo)

        #linewidth
        x_minor_layout.addWidget(QLabel("Linewidth:"))
        self.x_minor_grid_linewidth_spin = AnimatedDoubleSpinBox()
        self.x_minor_grid_linewidth_spin.setRange(0.1, 5.0)
        self.x_minor_grid_linewidth_spin.setValue(0.5)
        self.x_minor_grid_linewidth_spin.setSingleStep(0.1)
        x_minor_layout.addWidget(self.x_minor_grid_linewidth_spin)

        #color
        x_minor_layout.addWidget(QLabel("Color:"))
        x_minor_color_layout = QHBoxLayout()
        self.x_minor_grid_color_button = AnimatedButton("Choose Color", parent=self)
        self.x_minor_grid_color_label = QLabel("Light Gray")
        x_minor_color_layout.addWidget(self.x_minor_grid_color_button)
        x_minor_color_layout.addWidget(self.x_minor_grid_color_label)
        x_minor_layout.addLayout(x_minor_color_layout)

        #alpha
        x_minor_layout.addWidget(QLabel("Alpha (Transparency):"))
        self.x_minor_grid_alpha_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.x_minor_grid_alpha_slider.setRange(10, 100)
        self.x_minor_grid_alpha_slider.setValue(30)
        x_minor_layout.addWidget(self.x_minor_grid_alpha_slider)
        self.x_minor_grid_alpha_label = QLabel("30%")
        x_minor_layout.addWidget(self.x_minor_grid_alpha_label)
        
        x_minor_group.setLayout(x_minor_layout)
        x_grid_layout.addWidget(x_minor_group)

        x_grid_layout.addStretch()
        self.grid_axis_tab.addTab(x_grid_tab, "X-Axis Gridlines")
        
        # YAXIS
        y_grid_tab = QWidget()
        y_grid_layout = QVBoxLayout(y_grid_tab)

        y_major_group = AnimatedGroupBox("Y-Axis Major Gridlines")
        y_major_layout = QVBoxLayout()

        #check
        self.y_major_grid_check = AnimatedCheckBox("Show Major Y-axis Gridlines")
        self.y_major_grid_check.setChecked(True)
        y_major_layout.addWidget(self.y_major_grid_check)

        #linestyle
        y_major_layout.addWidget(QLabel("Linestyle:"))
        self.y_major_grid_style_combo = AnimatedComboBox()
        self.y_major_grid_style_combo.addItems(['-', '--', '-.', ':'])
        self.y_major_grid_style_combo.setItemText(0, 'Solid (-)')
        self.y_major_grid_style_combo.setItemText(1, 'Dashed (--)')
        self.y_major_grid_style_combo.setItemText(2, 'Dash-dot (-.)')
        self.y_major_grid_style_combo.setItemText(3, 'Dotted (:)')
        y_major_layout.addWidget(self.y_major_grid_style_combo)

        #linewidth
        y_major_layout.addWidget(QLabel("Linewidth:"))
        self.y_major_grid_linewidth_spin = AnimatedDoubleSpinBox()
        self.y_major_grid_linewidth_spin.setRange(0.1, 5.0)
        self.y_major_grid_linewidth_spin.setValue(0.8)
        self.y_major_grid_linewidth_spin.setSingleStep(0.1)
        y_major_layout.addWidget(self.y_major_grid_linewidth_spin)

        #color
        y_major_layout.addWidget(QLabel("Color:"))
        y_major_color_layout = QHBoxLayout()
        self.y_major_grid_color_button = AnimatedButton("Choose Color", parent=self)
        self.y_major_grid_color_label = QLabel("Gray")
        y_major_color_layout.addWidget(self.y_major_grid_color_button)
        y_major_color_layout.addWidget(self.y_major_grid_color_label)
        y_major_layout.addLayout(y_major_color_layout)

        #alpha
        y_major_layout.addWidget(QLabel("Alpha (Transparency):"))
        self.y_major_grid_alpha_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.y_major_grid_alpha_slider.setRange(10, 100)
        self.y_major_grid_alpha_slider.setValue(75)
        y_major_layout.addWidget(self.y_major_grid_alpha_slider)
        self.y_major_grid_alpha_label = QLabel("75%")
        y_major_layout.addWidget(self.y_major_grid_alpha_label)
        
        y_major_group.setLayout(y_major_layout)
        y_grid_layout.addWidget(y_major_group)

        # Y-Axis Minor Gridlines
        y_minor_group = AnimatedGroupBox("Y-Axis Minor Gridlines")
        y_minor_layout = QVBoxLayout()

        #check
        self.y_minor_grid_check = AnimatedCheckBox("Show Y Minor Gridlines")
        self.y_minor_grid_check.setChecked(False)
        y_minor_layout.addWidget(self.y_minor_grid_check)

        #linestyle
        y_minor_layout.addWidget(QLabel("Linestyle:"))
        self.y_minor_grid_style_combo = AnimatedComboBox()
        self.y_minor_grid_style_combo.addItems(['-', '--', '-.', ':'])
        self.y_minor_grid_style_combo.setItemText(0, 'Solid (-)')
        self.y_minor_grid_style_combo.setItemText(1, 'Dashed (--)')
        self.y_minor_grid_style_combo.setItemText(2, 'Dash-dot (-.)')
        self.y_minor_grid_style_combo.setItemText(3, 'Dotted (:)')
        self.y_minor_grid_style_combo.setCurrentIndex(3)  # Default to dotted
        y_minor_layout.addWidget(self.y_minor_grid_style_combo)

        #linewidth
        y_minor_layout.addWidget(QLabel("Linewidth:"))
        self.y_minor_grid_linewidth_spin = AnimatedDoubleSpinBox()
        self.y_minor_grid_linewidth_spin.setRange(0.1, 5.0)
        self.y_minor_grid_linewidth_spin.setValue(0.5)
        self.y_minor_grid_linewidth_spin.setSingleStep(0.1)
        y_minor_layout.addWidget(self.y_minor_grid_linewidth_spin)

        #color customization
        y_minor_layout.addWidget(QLabel("Color:"))
        y_minor_color_layout = QHBoxLayout()
        self.y_minor_grid_color_button = AnimatedButton("Choose Color", parent=self)
        self.y_minor_grid_color_label = QLabel("Light Gray")
        y_minor_color_layout.addWidget(self.y_minor_grid_color_button)
        y_minor_color_layout.addWidget(self.y_minor_grid_color_label)
        y_minor_layout.addLayout(y_minor_color_layout)

        #alha
        y_minor_layout.addWidget(QLabel("Alpha (Transparency):"))
        self.y_minor_grid_alpha_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.y_minor_grid_alpha_slider.setRange(10, 100)
        self.y_minor_grid_alpha_slider.setValue(30)
        y_minor_layout.addWidget(self.y_minor_grid_alpha_slider)
        self.y_minor_grid_alpha_label = QLabel("30%")
        y_minor_layout.addWidget(self.y_minor_grid_alpha_label)

        y_minor_group.setLayout(y_minor_layout)
        y_grid_layout.addWidget(y_minor_group)

        y_grid_layout.addStretch()
        self.grid_axis_tab.addTab(y_grid_tab, "Y-Axis Gridlines")

        #tabs to main layout
        grid_layout.addWidget(self.grid_axis_tab)
        grid_layout.addStretch()

        grid_group.setLayout(grid_layout)
        scroll_layout.addWidget(grid_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        return tab
    
    def _create_advanced_tab(self):
        """Create advanced customization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)

        #line properties
        
        line_group = AnimatedGroupBox("Line Properties")
        line_layout = QVBoxLayout()

        #multi line toggle
        self.multiline_custom_check = AnimatedCheckBox("Enable per-line customization")
        self.multiline_custom_check.setChecked(False)
        line_layout.addWidget(self.multiline_custom_check)

        #line selection
        self.line_selector_label = QLabel("Select Line to customize")
        self.line_selector_label.setVisible(False)
        line_layout.addWidget(self.line_selector_label)

        self.line_selector_combo = AnimatedComboBox()
        self.line_selector_combo.setVisible(False)
        line_layout.addWidget(self.line_selector_combo)
        
        line_layout.addWidget(QLabel("Line Width:"))
        self.linewidth_spin = AnimatedDoubleSpinBox()
        self.linewidth_spin.setRange(0.5, 5.0)
        self.linewidth_spin.setValue(1.5)
        self.linewidth_spin.setSingleStep(0.1)
        line_layout.addWidget(self.linewidth_spin)
        
        line_layout.addWidget(QLabel("Line Style:"))
        self.linestyle_combo = AnimatedComboBox()
        self.linestyle_combo.addItems(['-', '--', '-.', ':', 'None'])
        self.linestyle_combo.setItemText(0, 'Solid')
        self.linestyle_combo.setItemText(1, 'Dashed')
        self.linestyle_combo.setItemText(2, 'Dash-dot')
        self.linestyle_combo.setItemText(3, 'Dotted')
        line_layout.addWidget(self.linestyle_combo)
        
        line_layout.addWidget(QLabel("Line Color:"))
        line_color_layout = QHBoxLayout()
        self.line_color_button = AnimatedButton("Choose", parent=self)
        self.line_color_label = QLabel("Auto")
        line_color_layout.addWidget(self.line_color_button)
        line_color_layout.addWidget(self.line_color_label)
        line_layout.addLayout(line_color_layout)

        self.save_line_custom_button = AnimatedButton("Save Settings to Selected Line", parent=self)
        self.save_line_custom_button.setVisible(False)
        line_layout.addWidget(self.save_line_custom_button)

        line_group.setLayout(line_layout)
        scroll_layout.addWidget(line_group)
        
        scroll_layout.addSpacing(10)
        
        # === MARKER PROPERTIES ===
        marker_group = AnimatedGroupBox("Marker Properties")
        marker_layout = QVBoxLayout()

        marker_layout.addWidget(QLabel("Marker Shape:"))
        self.marker_combo = AnimatedComboBox()
        self.marker_combo.addItems(['None', 'o', 's', '^', 'v', 'D', '*', '+', 'x', '|', '_', 'p', 'H', 'h'])
        marker_layout.addWidget(self.marker_combo)
        
        marker_layout.addWidget(QLabel("Marker Size:"))
        self.marker_size_spin = AnimatedSpinBox()
        self.marker_size_spin.setRange(2, 20)
        self.marker_size_spin.setValue(6)
        marker_layout.addWidget(self.marker_size_spin)
        
        marker_layout.addWidget(QLabel("Marker Color:"))
        marker_color_layout = QHBoxLayout()
        self.marker_color_button = AnimatedButton("Choose", parent=self)
        self.marker_color_label = QLabel("Auto")
        marker_color_layout.addWidget(self.marker_color_button)
        marker_color_layout.addWidget(self.marker_color_label)
        marker_layout.addLayout(marker_color_layout)
        
        marker_layout.addWidget(QLabel("Marker Edge Color:"))
        marker_edge_layout = QHBoxLayout()
        self.marker_edge_button = AnimatedButton("Choose", parent=self)
        self.marker_edge_label = QLabel("Auto")
        marker_edge_layout.addWidget(self.marker_edge_button)
        marker_edge_layout.addWidget(self.marker_edge_label)
        marker_layout.addLayout(marker_edge_layout)
        
        marker_layout.addWidget(QLabel("Marker Edge Width:"))
        self.marker_edge_width_spin = AnimatedDoubleSpinBox()
        self.marker_edge_width_spin.setRange(0, 3)
        self.marker_edge_width_spin.setValue(1)
        self.marker_edge_width_spin.setSingleStep(0.1)
        marker_layout.addWidget(self.marker_edge_width_spin)

        marker_group.setLayout(marker_layout)
        scroll_layout.addWidget(marker_group)
        
        scroll_layout.addSpacing(10)
        
        # === BAR PROPERTIES ===
        self.bar_group = AnimatedGroupBox("Bar Properties")
        bar_layout = QVBoxLayout()

        # toggle for more bars to customize
        self.multibar_custom_check = AnimatedCheckBox("Enable per-bar customization")
        self.multibar_custom_check.setChecked(False)
        bar_layout.addWidget(self.multibar_custom_check)

        #bar selection
        self.bar_selector_label = QLabel("Select Bar Series to Customize")
        self.bar_selector_label.setVisible(False)
        bar_layout.addWidget(self.bar_selector_label)

        #selectionboc
        self.bar_selector_combo = AnimatedComboBox()
        self.bar_selector_combo.setVisible(False)
        bar_layout.addWidget(self.bar_selector_combo)

        bar_layout.addWidget(QLabel("Bar Width:"))
        self.bar_width_spin = AnimatedDoubleSpinBox()
        self.bar_width_spin.setRange(0.1, 1.0)
        self.bar_width_spin.setValue(0.8)
        self.bar_width_spin.setSingleStep(0.05)
        bar_layout.addWidget(self.bar_width_spin)
        
        bar_layout.addWidget(QLabel("Bar Color:"))
        bar_color_layout = QHBoxLayout()
        self.bar_color_button = AnimatedButton("Choose Color", parent=self)
        self.bar_color_label = QLabel("Auto")
        bar_color_layout.addWidget(self.bar_color_button)
        bar_color_layout.addWidget(self.bar_color_label)
        bar_layout.addLayout(bar_color_layout)
        
        bar_layout.addWidget(QLabel("Bar Edge Color:"))
        bar_edge_layout = QHBoxLayout()
        self.bar_edge_button = AnimatedButton("Choose", parent=self)
        self.bar_edge_label = QLabel("Auto")
        bar_edge_layout.addWidget(self.bar_edge_button)
        bar_edge_layout.addWidget(self.bar_edge_label)
        bar_layout.addLayout(bar_edge_layout)
        
        bar_layout.addWidget(QLabel("Bar Edge Width:"))
        self.bar_edge_width_spin = AnimatedDoubleSpinBox()
        self.bar_edge_width_spin.setRange(0, 3)
        self.bar_edge_width_spin.setValue(1)
        self.bar_edge_width_spin.setSingleStep(0.1)
        bar_layout.addWidget(self.bar_edge_width_spin)

        #Button to save customization for a bar to generate
        self.save_bar_custom_button = AnimatedButton("Save Customization to Selected Bar", parent=self)
        self.save_bar_custom_button.setVisible(False)
        bar_layout.addWidget(self.save_bar_custom_button)

        self.bar_group.setLayout(bar_layout)
        scroll_layout.addWidget(self.bar_group)
        
        scroll_layout.addSpacing(10)

        # === Histogram Properties ===
        self.histogram_group = AnimatedGroupBox("Histogram Properties")
        histogram_layout = QVBoxLayout()
        
        histogram_layout.addWidget(QLabel("Number of Bins:"))
        self.histogram_bins_spin = AnimatedSpinBox()
        self.histogram_bins_spin.setRange(5, 200)
        self.histogram_bins_spin.setValue(30)
        histogram_layout.addWidget(self.histogram_bins_spin)

        #normal distribution curve
        self.histogram_show_normal_check = AnimatedCheckBox("Overlay a Normal Distribution Curve")
        self.histogram_show_normal_check.setChecked(False)
        histogram_layout.addWidget(self.histogram_show_normal_check)

        self.histogram_show_kde_check = AnimatedCheckBox("Overlay Kernel Density Estimate")
        self.histogram_show_kde_check.setChecked(False)
        histogram_layout.addWidget(self.histogram_show_kde_check)

        self.histogram_group.setLayout(histogram_layout)
        scroll_layout.addWidget(self.histogram_group)

        scroll_layout.addSpacing(10)
        
        # === TRANSPARENCY ===
        alpha_group = AnimatedGroupBox("Transparency")
        alpha_layout = QVBoxLayout()
        
        alpha_layout.addWidget(QLabel("Alpha/Transparency:"))
        self.alpha_slider = AnimatedSlider(Qt.Orientation.Horizontal)
        self.alpha_slider.setRange(10, 100)
        self.alpha_slider.setValue(100)
        alpha_layout.addWidget(self.alpha_slider)
        
        self.alpha_label = QLabel("100%")
        alpha_layout.addWidget(self.alpha_label)
        
        alpha_group.setLayout(alpha_layout)
        scroll_layout.addWidget(alpha_group)
        
        scroll_layout.addSpacing(10)

        # === SCatter stats ===
        self.scatter_group = AnimatedGroupBox("Scatter Plot Analysis")
        scatter_layout = QVBoxLayout()

        self.regression_line_check = AnimatedCheckBox("Show Linear Regresssion Line")
        scatter_layout.addWidget(self.regression_line_check)

        self.confidence_interval_check = AnimatedCheckBox("Show 95% confidence interval")
        scatter_layout.addWidget(self.confidence_interval_check)

        self.show_r2_check = AnimatedCheckBox("Show R² score")
        self.show_r2_check.setChecked(False)
        scatter_layout.addWidget(self.show_r2_check)

        self.show_rmse_check = AnimatedCheckBox("Show Root Mean Square Error (RMSE)")
        scatter_layout.addWidget(self.show_rmse_check)

        self.show_equation_check = AnimatedCheckBox("Show Regression Equation")
        scatter_layout.addWidget(self.show_equation_check)

        scatter_layout.addWidget(QLabel("Error Bars:"))
        self.error_bars_combo = AnimatedComboBox()
        self.error_bars_combo.addItems(["None", "Standard Deviation", "Standard Error", "Custom"])
        scatter_layout.addWidget(self.error_bars_combo)

        scatter_layout.addWidget(QLabel("Confidence Level (%):"))
        self.confidence_level_spin = AnimatedSpinBox()
        self.confidence_level_spin.setRange(80, 99)
        self.confidence_level_spin.setValue(95)
        scatter_layout.addWidget(self.confidence_level_spin)

        self.scatter_group.setLayout(scatter_layout)
        scroll_layout.addWidget(self.scatter_group)

        scroll_layout.addSpacing(10)
        
        # === PiE CHART PROPERTIRES
        self.pie_group = AnimatedGroupBox("Pie Chart Properties")
        pie_layout = QVBoxLayout()

        self.pie_show_percentages_check = AnimatedCheckBox("Show % on slices")
        self.pie_show_percentages_check.setChecked(False)
        pie_layout.addWidget(self.pie_show_percentages_check)

        pie_layout.addWidget(QLabel("Start Angle (degress):"))
        self.pie_start_angle_spin = AnimatedSpinBox()
        self.pie_start_angle_spin.setRange(0, 360)
        self.pie_start_angle_spin.setValue(0)
        pie_layout.addWidget(self.pie_start_angle_spin)

        self.pie_explode_check = AnimatedCheckBox("Explode First Slice")
        self.pie_explode_check.setChecked(False)
        pie_layout.addWidget(self.pie_explode_check)

        pie_layout.addWidget(QLabel("Explode Distance:"))
        self.pie_explode_distance_spin = AnimatedDoubleSpinBox()
        self.pie_explode_distance_spin.setRange(0.0, 0.5)
        self.pie_explode_distance_spin.setValue(0.1)
        self.pie_explode_distance_spin.setSingleStep(0.05)
        pie_layout.addWidget(self.pie_explode_distance_spin)

        self.pie_shadow_check = AnimatedCheckBox("Add Shadow")
        self.pie_shadow_check.setChecked(False)
        pie_layout.addWidget(self.pie_shadow_check)

        self.pie_group.setLayout(pie_layout)
        scroll_layout.addWidget(self.pie_group)

        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        return tab
    
    def _create_annotations_tab(self):
        """Create annotations and text customization tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # TEXT ANNOTATIONS 
        annotations_group = AnimatedGroupBox("Manual Annotations")
        annotations_layout = QVBoxLayout()
        
        annotations_layout.addWidget(QLabel("Annotation Text:"))
        self.annotation_text = AnimatedLineEdit()
        self.annotation_text.setPlaceholderText("Enter text to add to plot")
        annotations_layout.addWidget(self.annotation_text)
        
        annotations_layout.addWidget(QLabel("X Position (0-1):"))
        self.annotation_x_spin = AnimatedDoubleSpinBox()
        self.annotation_x_spin.setRange(0, 1)
        self.annotation_x_spin.setValue(0.5)
        self.annotation_x_spin.setSingleStep(0.05)
        annotations_layout.addWidget(self.annotation_x_spin)
        
        annotations_layout.addWidget(QLabel("Y Position (0-1):"))
        self.annotation_y_spin = AnimatedDoubleSpinBox()
        self.annotation_y_spin.setRange(0, 1)
        self.annotation_y_spin.setValue(0.5)
        self.annotation_y_spin.setSingleStep(0.05)
        annotations_layout.addWidget(self.annotation_y_spin)
        
        annotations_layout.addWidget(QLabel("Font Size:"))
        self.annotation_fontsize_spin = AnimatedSpinBox()
        self.annotation_fontsize_spin.setRange(6, 36)
        self.annotation_fontsize_spin.setValue(12)
        annotations_layout.addWidget(self.annotation_fontsize_spin)
        
        annotations_layout.addWidget(QLabel("Font Color:"))
        annotation_color_layout = QHBoxLayout()
        self.annotation_color_button = AnimatedButton("Choose", parent=self)
        self.annotation_color_label = QLabel("Black")
        annotation_color_layout.addWidget(self.annotation_color_button)
        annotation_color_layout.addWidget(self.annotation_color_label)
        annotations_layout.addLayout(annotation_color_layout)
        
        self.add_annotation_button = AnimatedButton("Add Annotation", parent=self)
        annotations_layout.addWidget(self.add_annotation_button)

        annotations_group.setLayout(annotations_layout)
        scroll_layout.addWidget(annotations_group)
        
        scroll_layout.addSpacing(15)

        # automated annotations based on datapoints
        auto_annotate_group = AnimatedGroupBox("Annotate Data Points")
        auto_annotate_layout = QVBoxLayout()

        self.auto_annotate_check = AnimatedCheckBox("Annotate All points")
        self.auto_annotate_check.setToolTip("Automatically set text labels to all data points")
        auto_annotate_layout.addWidget(self.auto_annotate_check)

        auto_annotate_layout.addWidget(QLabel("Label Source Column:"))
        self.auto_annotate_col_combo = AnimatedComboBox()
        self.auto_annotate_col_combo.setToolTip("Select the column to use for the point labels")
        self.auto_annotate_col_combo.addItem("Default (Y-value)")
        self.auto_annotate_col_combo.setEnabled(False)
        auto_annotate_layout.addWidget(self.auto_annotate_col_combo)

        auto_annotate_group.setLayout(auto_annotate_layout)
        scroll_layout.addWidget(auto_annotate_group)
        
        #  TEXT BOX 
        text_box_group = AnimatedGroupBox("Text Box")
        text_box_layout = QVBoxLayout()
        
        text_box_layout.addWidget(QLabel("Text Box Content:"))
        self.textbox_content = AnimatedLineEdit()
        self.textbox_content.setPlaceholderText("Enter text for text box")
        text_box_layout.addWidget(self.textbox_content)
        
        text_box_layout.addWidget(QLabel("Text Box Position:"))
        self.textbox_position_combo = AnimatedComboBox()
        self.textbox_position_combo.addItems(['upper left', 'upper center', 'upper right','center left', 'center', 'center right', 'lower left', 'lower center', 'lower right'])
        text_box_layout.addWidget(self.textbox_position_combo)
        
        text_box_layout.addWidget(QLabel("Text Box Style:"))
        self.textbox_style_combo = AnimatedComboBox()
        self.textbox_style_combo.addItems(['round', 'square', 'round,pad=1', 'round4,pad=0.5'])
        self.textbox_style_combo.setItemText(0, 'Rounded')
        self.textbox_style_combo.setItemText(1, 'Square')
        text_box_layout.addWidget(self.textbox_style_combo)
        
        text_box_layout.addWidget(QLabel("Background Color:"))
        textbox_bg_layout = QHBoxLayout()
        self.textbox_bg_button = AnimatedButton("Choose", parent=self)
        self.textbox_bg_label = QLabel("White")
        textbox_bg_layout.addWidget(self.textbox_bg_button)
        textbox_bg_layout.addWidget(self.textbox_bg_label)
        text_box_layout.addLayout(textbox_bg_layout)
        
        self.textbox_enable_check = AnimatedCheckBox("Enable Text Box")
        text_box_layout.addWidget(self.textbox_enable_check)

        text_box_group.setLayout(text_box_layout)
        scroll_layout.addWidget(text_box_group)
        
        scroll_layout.addSpacing(15)

        #datatable
        table_group = AnimatedGroupBox("Data Table")
        table_layout = QVBoxLayout()

        self.table_enable_check = AnimatedCheckBox("Show Data Table on plot")
        self.table_enable_check.setChecked(False)
        table_layout.addWidget(self.table_enable_check)

        table_controls_layout = QHBoxLayout()
        table_controls_layout.addWidget(QLabel("Type:"))
        self.table_type_combo = AnimatedComboBox()
        self.table_type_combo.addItems(["Summary Stats", "First 5 Rows", "Last 5 Rows", "Correlation Matrix"])
        self.table_type_combo.setEnabled(False)
        self.table_type_combo.setVisible(False)
        table_controls_layout.addWidget(self.table_type_combo)

        table_controls_layout.addWidget(QLabel("Placement:"))
        self.table_location_combo = AnimatedComboBox()
        self.table_location_combo.addItems(["bottom", "top", "right", "left", "center"])
        self.table_location_combo.setEnabled(False)
        self.table_location_combo.setVisible(False)
        table_controls_layout.addWidget(self.table_location_combo)

        table_layout.addLayout(table_controls_layout)

        table_settings_layout = QHBoxLayout()
        self.table_auto_font_size_check = AnimatedCheckBox("Auto Font-Size")
        self.table_auto_font_size_check.setChecked(False)
        self.table_auto_font_size_check.setEnabled(False)
        table_settings_layout.addWidget(self.table_auto_font_size_check)

        table_settings_layout.addWidget(QLabel("Font Size:"))
        self.table_font_size_spin = AnimatedSpinBox()
        self.table_font_size_spin.setRange(4, 40)
        self.table_font_size_spin.setValue(10)
        self.table_font_size_spin.setEnabled(False)
        self.table_font_size_spin.setVisible(False)
        table_settings_layout.addWidget(self.table_font_size_spin)

        table_settings_layout.addWidget(QLabel("Scale:"))
        self.table_scale_spin = AnimatedDoubleSpinBox()
        self.table_scale_spin.setRange(0.5, 5.0)
        self.table_scale_spin.setValue(1.2)
        self.table_scale_spin.setSingleStep(0.1)
        self.table_scale_spin.setEnabled(False)
        self.table_scale_spin.setVisible(False)
        table_settings_layout.addWidget(self.table_scale_spin)

        table_layout.addLayout(table_settings_layout)

        table_group.setLayout(table_layout)
        scroll_layout.addWidget(table_group)
        
        scroll_layout.addSpacing(15)
        #  ANNOTATIONS LIST 
        annotation_list_group = AnimatedGroupBox("Annotations List")
        annotation_list_layout = QVBoxLayout()
        
        self.annotations_list = AnimatedListWidget()
        annotation_list_layout.addWidget(self.annotations_list)
        
        self.clear_annotations_button = AnimatedButton("Clear All Annotations", parent=self)
        annotation_list_layout.addWidget(self.clear_annotations_button)

        annotation_list_group.setLayout(annotation_list_layout)
        scroll_layout.addWidget(annotation_list_group)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_geospatial_tab(self):
        """Create the geospatial tab"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_widget.setObjectName("ScrollContent")
        scroll_layout = QVBoxLayout(scroll_widget)

        #settings for choropleth mapping
        choro_group = AnimatedGroupBox("Choropleth and Classification")
        choro_layout = QVBoxLayout()

        choro_layout.addWidget(QLabel("Classification Scheme:"))
        self.geo_scheme_combo = AnimatedComboBox()
        self.geo_scheme_combo.addItems([
            "None", "quantiles", "equal_interval", "fisher_jenks", "natural_breaks", "box_plot", "breaks"
        ])
        choro_layout.addWidget(self.geo_scheme_combo)

        choro_layout.addWidget(QLabel("Number of classes:"))
        self.geo_k_spin = AnimatedSpinBox()
        self.geo_k_spin.setRange(2, 20)
        self.geo_k_spin.setValue(5)
        choro_layout.addWidget(self.geo_k_spin)

        choro_group.setLayout(choro_layout)
        scroll_layout.addWidget(choro_group)
        scroll_layout.addSpacing(10)

        #legend axes
        geo_legend_group = AnimatedGroupBox("Map Legend and Axes")
        geo_legend_layout = QVBoxLayout()

        self.geo_legend_check = AnimatedCheckBox("Show Map Legend")
        self.geo_legend_loc_combo = AnimatedComboBox()
        self.geo_legend_loc_combo.addItems(["vertical", "horizontal"])
        geo_legend_layout.addWidget(self.geo_legend_loc_combo)

        self.geo_use_divider_check = AnimatedCheckBox("Use Divider")
        self.geo_use_divider_check.setToolTip("Use mpl_toolkits divider to align legend")
        geo_legend_layout.addWidget(self.geo_use_divider_check)

        self.geo_cax_check = AnimatedCheckBox("Plot on Separate CAX")
        self.geo_cax_check.setToolTip("Plot legend/colorbar on a separate axis")
        geo_legend_layout.addWidget(self.geo_cax_check)

        self.geo_axis_off_check = AnimatedCheckBox("Turn Off Axis")
        self.geo_axis_off_check.setChecked(False)
        geo_legend_layout.addWidget(self.geo_axis_off_check)

        geo_legend_group.setLayout(geo_legend_layout)
        scroll_layout.addWidget(geo_legend_group)
        scroll_layout.addSpacing(10)

        missing_group = AnimatedGroupBox("Missing Data Handling")
        missing_layout = QVBoxLayout()
        
        missing_layout.addWidget(QLabel("Missing Data Label:"))
        self.geo_missing_label_input = AnimatedLineEdit()
        self.geo_missing_label_input.setPlaceholderText("NaN")
        missing_layout.addWidget(self.geo_missing_label_input)

        missing_layout.addWidget(QLabel("Missing Data Color:"))
        missing_color_layout = QHBoxLayout()
        self.geo_missing_color_btn = AnimatedButton("Choose", parent=self)
        self.geo_missing_color_label = QLabel("Light Gray")
        self.geo_missing_color = "lightgray" # Default storage
        missing_color_layout.addWidget(self.geo_missing_color_btn)
        missing_color_layout.addWidget(self.geo_missing_color_label)
        missing_layout.addLayout(missing_color_layout)

        missing_layout.addWidget(QLabel("Hatch Pattern:"))
        self.geo_hatch_combo = AnimatedComboBox()
        self.geo_hatch_combo.addItems(["None", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"])
        missing_layout.addWidget(self.geo_hatch_combo)

        missing_group.setLayout(missing_layout)
        scroll_layout.addWidget(missing_group)
        scroll_layout.addSpacing(10)

        boundary_group = AnimatedGroupBox("Boundary Customization")
        boundary_layout = QVBoxLayout()

        self.geo_boundary_check = AnimatedCheckBox("Plot Boundary Only")
        boundary_layout.addWidget(self.geo_boundary_check)

        boundary_layout.addWidget(QLabel("Edge Color:"))
        bound_color_layout = QHBoxLayout()
        self.geo_edge_color_btn = AnimatedButton("Choose", parent=self)
        self.geo_edge_color_label = QLabel("Black")
        self.geo_edge_color = "black"
        bound_color_layout.addWidget(self.geo_edge_color_btn)
        bound_color_layout.addWidget(self.geo_edge_color_label)
        boundary_layout.addLayout(bound_color_layout)

        boundary_layout.addWidget(QLabel("Line Width:"))
        self.geo_linewidth_spin = AnimatedDoubleSpinBox()
        self.geo_linewidth_spin.setRange(0.1, 10.0)
        self.geo_linewidth_spin.setValue(1.0)
        boundary_layout.addWidget(self.geo_linewidth_spin)

        boundary_group.setLayout(boundary_layout)
        scroll_layout.addWidget(boundary_group)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        layout.addWidget(scroll)
        return tab

    def _create_splitter(self, left, right) -> QSplitter:
        """Create a splitter for resizable panels"""
        from PyQt6.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([700, 300])
        return splitter