from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea
from ui.widgets import DataPlotStudioGroupBox, DataPlotStudioToggleSwitch, DataPlotStudioSpinBox, DataPlotStudioDoubleSpinBox, DataPlotStudioButton, DataPlotStudioComboBox, DataPlotStudioLineEdit

class GeospatialSettingsTab(QWidget):
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

        self._setup_projection_group(scroll_layout)
        scroll_layout.addSpacing(10)
        self._setup_choropleth_group(scroll_layout)
        scroll_layout.addSpacing(10)
        self._setup_legend_group(scroll_layout)
        scroll_layout.addSpacing(10)
        self._setup_missing_data_group(scroll_layout)
        scroll_layout.addSpacing(10)
        self._setup_boundary_group(scroll_layout)

        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        main_layout.addWidget(scroll)

    def _setup_projection_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Projection and Basemap")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Target Coordinate System:"))
        self.geo_target_crs_input = DataPlotStudioLineEdit()
        self.geo_target_crs_input.setPlaceholderText("Leave empty to keep original coordinate system")
        self.geo_target_crs_input.setToolTip("Enter an EPSG code (e.g., EPSG:3857 for Web Mercator) to reproject map")
        layout.addWidget(self.geo_target_crs_input)

        layout.addSpacing(10)

        self.geo_basemap_check = DataPlotStudioToggleSwitch("Add background Basemap")
        self.geo_basemap_check.setToolTip("Overlay data on top of a web map tile.\nRequires an internet connection")
        layout.addWidget(self.geo_basemap_check)

        layout.addWidget(QLabel("Basemap Source:"))
        self.geo_basemap_style_combo = DataPlotStudioComboBox()
        self.geo_basemap_style_combo.addItems([
            "OpenStreetMap",
            "CartoDB Positron",
            "CartoDB DarkMatter",
            "Esri Satellite",
            "Esri Street"
        ])
        self.geo_basemap_style_combo.setToolTip("Select the provider for the basemap tile")
        layout.addWidget(self.geo_basemap_style_combo)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_choropleth_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Choropleth and Classification")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Classification Scheme:"))
        self.geo_scheme_combo = DataPlotStudioComboBox()
        self.geo_scheme_combo.addItems([
            "None", "quantiles", "equal_interval", "fisher_jenks", "natural_breaks", "box_plot", "breaks"
        ])
        layout.addWidget(self.geo_scheme_combo)

        layout.addWidget(QLabel("Number of classes:"))
        self.geo_k_spin = DataPlotStudioSpinBox()
        self.geo_k_spin.setRange(2, 20)
        self.geo_k_spin.setValue(5)
        layout.addWidget(self.geo_k_spin)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_legend_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Map Legend and Axes")
        layout = QVBoxLayout()

        self.geo_legend_check = DataPlotStudioToggleSwitch("Show Map Legend")
        layout.addWidget(self.geo_legend_check)
        
        self.geo_legend_loc_combo = DataPlotStudioComboBox()
        self.geo_legend_loc_combo.addItems(["vertical", "horizontal"])
        layout.addWidget(self.geo_legend_loc_combo)

        self.geo_use_divider_check = DataPlotStudioToggleSwitch("Use Divider")
        self.geo_use_divider_check.setToolTip("Use mpl_toolkits divider to align legend")
        layout.addWidget(self.geo_use_divider_check)

        self.geo_cax_check = DataPlotStudioToggleSwitch("Plot on Separate CAX")
        self.geo_cax_check.setToolTip("Plot legend/colorbar on a separate axis")
        layout.addWidget(self.geo_cax_check)

        self.geo_axis_off_check = DataPlotStudioToggleSwitch("Turn Off Axis")
        self.geo_axis_off_check.setChecked(False)
        layout.addWidget(self.geo_axis_off_check)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_missing_data_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Missing Data Handling")
        layout = QVBoxLayout()

        layout.addWidget(QLabel("Missing Data Label:"))
        self.geo_missing_label_input = DataPlotStudioLineEdit()
        self.geo_missing_label_input.setPlaceholderText("NaN")
        layout.addWidget(self.geo_missing_label_input)

        layout.addWidget(QLabel("Missing Data Color:"))
        color_layout = QHBoxLayout()
        self.geo_missing_color_btn = DataPlotStudioButton("Choose", parent=self)
        self.geo_missing_color_label = QLabel("Light Gray")
        self.geo_missing_color: str = "lightgray"  
        
        color_layout.addWidget(self.geo_missing_color_btn)
        color_layout.addWidget(self.geo_missing_color_label)
        layout.addLayout(color_layout)

        layout.addWidget(QLabel("Hatch Pattern:"))
        self.geo_hatch_combo = DataPlotStudioComboBox()
        self.geo_hatch_combo.addItems(["None", "/", "\\", "|", "-", "+", "x", "o", "O", ".", "*"])
        layout.addWidget(self.geo_hatch_combo)

        group.setLayout(layout)
        parent_layout.addWidget(group)

    def _setup_boundary_group(self, parent_layout: QVBoxLayout) -> None:
        group = DataPlotStudioGroupBox("Boundary Customization")
        layout = QVBoxLayout()

        self.geo_boundary_check = DataPlotStudioToggleSwitch("Plot Boundary Only")
        layout.addWidget(self.geo_boundary_check)

        layout.addWidget(QLabel("Edge Color:"))
        bound_color_layout = QHBoxLayout()
        self.geo_edge_color_btn = DataPlotStudioButton("Choose", parent=self)
        self.geo_edge_color_label = QLabel("Black")
        self.geo_edge_color: str = "black"
        
        bound_color_layout.addWidget(self.geo_edge_color_btn)
        bound_color_layout.addWidget(self.geo_edge_color_label)
        layout.addLayout(bound_color_layout)

        layout.addWidget(QLabel("Line Width:"))
        self.geo_linewidth_spin = DataPlotStudioDoubleSpinBox()
        self.geo_linewidth_spin.setRange(0.1, 10.0)
        self.geo_linewidth_spin.setValue(1.0)
        layout.addWidget(self.geo_linewidth_spin)

        group.setLayout(layout)
        parent_layout.addWidget(group)