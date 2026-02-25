# ui/plot_tab.py

from PyQt6.QtWidgets import QColorDialog, QApplication, QMessageBox, QListWidgetItem, QInputDialog
from PyQt6.QtCore import QTimer, QSize, Qt, pyqtSignal
from PyQt6.QtGui import QIcon, QColor, QFont
import json
import os
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from matplotlib.widgets import SpanSelector
from core.plot_engine import PlotEngine
from core.data_handler import DataHandler
from core.resource_loader import get_resource_path
from ui.SubplotOverlay import SubplotOverlay
from ui.components.plot_settings_panel import PlotSettingsPanel
from ui.status_bar import StatusBar
from core.code_exporter import CodeExporter
from ui.dialogs import ProgressDialog, ScriptEditorDialog
from ui.plot_tab_ui import PlotTabUI 
from ui.animations.PlotGeneratedAnimation import PlotGeneratedAnimation
from ui.animations.PlotClearedAnimation import PlotClearedAnimation
import pandas as pd
import numpy as np
from scipy import stats
from scipy.stats import t as t_dist
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator, FuncFormatter
import seaborn as sns
import matplotlib.pyplot as plt
import traceback
from matplotlib.colors import to_hex
from typing import Dict, Any
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.patches import Rectangle
from matplotlib.collections import PathCollection
from typing import Optional

from ui.widgets.AnimatedListWidget import DataPlotStudioListWidget
from ui.widgets.ColorBlindnessEffect import ColorBlindnessEffect
from ui.dialogs.PlotExportDialog import PlotExportDialog
from ui.dialogs.ThemeEditorDialog import ThemeEditorDialog
from core.plot_config_manager import PlotConfigManager
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from ui.plot_tab_ui import PlotSettingsPanel

class PlotTab(PlotTabUI):
    """Tab for creating and customizing plots"""
    
    brush_selection_made = pyqtSignal(set)
    
    def __init__(self, data_handler: DataHandler, status_bar: StatusBar, subset_manager=None) -> None:
        super().__init__()
        
        self.view: PlotSettingsPanel = None
        self.data_handler: DataHandler = data_handler
        self.status_bar: StatusBar = status_bar
        self.subset_manager = subset_manager
        if self.subset_manager:
            self.refresh_subset_list()
        self.plot_engine = PlotEngine()
        self.current_config = {}
        self.code_exporter = CodeExporter()
        self.script_editor = None
        self.script_sync_timer = QTimer()
        self.script_sync_timer.setSingleShot(True)
        self.script_sync_timer.setInterval(500)
        self.script_sync_timer.timeout.connect(self._perform_script_sync)
        self.current_plot_type_name = "Line"
        self.dragged_annotation = None
        self.ignore_next_click = False
        self.config_manager = PlotConfigManager(self)
        
        self._is_data_dirty = False
        self._is_clearing = False
        self.AUTO_UPDATE_THRESHOLD = 2000
        self.style_update_timer = QTimer()
        self.style_update_timer.setSingleShot(True)
        self.style_update_timer.setInterval(300)
        self.style_update_timer.timeout.connect(self._fast_render)
        
        self.bg_color = "white"
        self.face_color = "white"

        self.global_spine_color = "black"
        self.top_spine_color = "black"
        self.bottom_spine_color = "black"
        self.left_spine_color = "black"
        self.right_spine_color = "black"

        self.line_color = None
        self.marker_color = None
        self.marker_edge_color = None
        self.bar_color = None
        self.bar_edge_color = None
        self.annotation_color = "black"
        self.textbox_bg_color = "white"
        self.legend_bg_color = "white"
        self.legend_edge_color = "black"
        self.x_major_grid_color = "gray"
        self.x_minor_grid_color = "lightgray"
        self.y_major_grid_color = "gray"
        self.y_minor_grid_color = "lightgray"
        self.geo_missing_color = "lightgray"
        self.geo_edge_color = "black"

        self.line_customizations = {}
        self.bar_customizations = {}
        self.annotations = []
        self.subplot_data_configs = {}

        #plot dispatcher
        self.plot_strategies = {
            "Line": self.plot_engine.strategy_line,
            "Scatter": self.plot_engine.strategy_scatter,
            "Bar": self.plot_engine.strategy_bar,
            "Histogram": self.plot_engine.strategy_histogram,
            "Box": self.plot_engine.strategy_box,
            "Violin": self.plot_engine.strategy_violin,
            "Heatmap": self.plot_engine.strategy_heatmap,
            "KDE": self.plot_engine.strategy_kde,
            "Area": self.plot_engine.strategy_area,
            "Pie": self.plot_engine.strategy_pie,
            "Count Plot": self.plot_engine.strategy_count,
            "Hexbin": self.plot_engine.strategy_hexbin,
            "2D Density": self.plot_engine.strategy_2d_density,
            "Stem": self.plot_engine.strategy_stem,
            "Stackplot": self.plot_engine.strategy_stackplot,
            "Stairs": self.plot_engine.strategy_stairs,
            "Eventplot": self.plot_engine.strategy_eventplot,
            "ECDF": self.plot_engine.strategy_ecdf,
            "2D Histogram": self.plot_engine.strategy_hist2d,
            "Image Show (imshow)": self.plot_engine.strategy_imshow,
            "pcolormesh": self.plot_engine.strategy_pcolormesh,
            "Contour": self.plot_engine.strategy_contour,
            "Contourf": self.plot_engine.strategy_contourf,
            "Barbs": self.plot_engine.strategy_barbs,
            "Quiver": self.plot_engine.strategy_quiver,
            "Streamplot": self.plot_engine.strategy_streamplot,
            "Tricontour": self.plot_engine.strategy_tricontour,
            "Tricontourf": self.plot_engine.strategy_tricontourf,
            "Tripcolor": self.plot_engine.strategy_tripcolor,
            "Triplot": self.plot_engine.strategy_triplot,
            "GeoSpatial": self.plot_engine.strategy_geospatial
        }
        # Categories
        self.plot_categories = {
            "Basic & Relational": ["Line", "Scatter", "Bar", "Area", "Pie", "Stem", "Stairs"],
            "Distribution": ["Histogram", "Box", "Violin", "KDE", "ECDF", "Count Plot", "Eventplot"],
            "2D, Gridded & 3D": ["Heatmap", "Hexbin", "2D Density", "2D Histogram", "Image Show (imshow)", "pcolormesh", "Contour", "Contourf", "Stackplot"],
            "Vector Fields": ["Barbs", "Quiver", "Streamplot"],
            "Triangulation": ["Tricontour", "Tricontourf", "Tripcolor", "Triplot"],
            "Geospatial": ["GeoSpatial"]
        }
        
        # Create canvas and toolbar
        self.plot_engine.create_figure()
        canvas = FigureCanvas(self.plot_engine.get_figure())
        toolbar = NavigationToolbar(canvas, self)
        
        self.init_ui(canvas, toolbar)
        
        self.view = self.settings_panel
        
        #populate box in general tab with icons
        #
        self._populate_plot_toolbox()


        self.selection_overlay = SubplotOverlay(self.canvas)
        self.canvas.mpl_connect("resize_event", self.on_canvas_resize)
        self.canvas.mpl_connect("pick_event", self.on_pick)
        self.canvas.mpl_connect("draw_event", self._on_draw_event)
        
        # Load initial data
        self.update_column_combo()
        
        self._select_plot_in_toolbox("Line")

        # Initialize the themes
        self.theme_dir = os.path.join(os.getcwd(), "resources", "themes")
        if not os.path.exists(self.theme_dir):
            os.makedirs(self.theme_dir, exist_ok=True)
        self.default_theme_names = ["Dark_Mode", "Publication_Ready", "Presentation_Big", "Default"]
        self.refresh_theme_list()
        if hasattr(self, 'dpi_spin'):
            self.view.dpi_spin.setVisible(False)
        
        # Caching
        self._last_data_signature = None
        self._last_viz_signature = None
        self._cached_active_df = None
        
        # Connect all signals to their logic methods
        self._connect_signals()
    
    def _on_draw_event(self, event) -> None:
        """Handle canvas draw to link data points """
        if not self.plot_engine.current_ax:
            return
        
        if getattr(self, "span_selector", None) is not None:
            if self.span_selector.ax == self.plot_engine.current_ax:
                return
            else:
                self.span_selector = None
        
        self._setup_brush_and_link()
    
    def _setup_brush_and_link(self) -> None:
        """Sets up the Matplotlib SpanSelector"""
        if not self.plot_engine.current_ax:
            return
        
        # Only supported plots for now:
        supported_plots = ["Histogram", "Scatter", "Line", "Stem", "Stairs"]
        if self.current_plot_type_name not in supported_plots:
            self.span_selector = None
            return
        
        def on_select(xmin: float, xmax: float) -> None:
            self._handle_brush_selection(xmin, xmax)
        
        self.span_selector = SpanSelector(
            self.plot_engine.current_ax,
            on_select,
            "horizontal",
            useblit=True,
            props=dict(alpha=0.3, facecolor="#e74c3c"),
            interactive=True,
            button=3
        )
    
    def _handle_brush_selection(self, xmin: float, xmax: float) -> None:
        """Filters and highlights rows based on selection"""
        df = self.get_active_dataframe()
        x_col = self.view.x_column.currentText()
        
        if not x_col or x_col not in df.columns:
            return
        
        mask = (df[x_col] >= xmin) & (df[x_col] <= xmax)
        selected_indices = set(df[mask].index)
        
        if selected_indices:
            self.brush_selection_made.emit(selected_indices)
            self.status_bar.log(f"Selected {len(selected_indices)} points. Switching to Data Explorer to view", "INFO")

    def _connect_signals(self) -> None:
        """Connect all UI widget signals to their logic"""
        self._connect_main_controls()
        self._connect_basic_tab_signals()
        self._connect_appearance_tab_signals()
        self._connect_axes_tab_signals()
        self._connect_legend_grid_tab_signals()
        self._connect_advanced_tab_signals()
        self._connect_annotation_tab_signals()
        self._connect_geospatial_tab_signals()
        self._connect_theme_controls()
    
    def _connect_main_controls(self) -> None:
        """Connect the main action buttons and canvas events"""
        #  Main Buttons 
        self.plot_button.clicked.connect(self.generate_plot)
        self.editor_button.clicked.connect(self.open_script_editor)
        self.clear_button.clicked.connect(self.clear_plot)
        self.save_plot_button.clicked.connect(self.save_plot_image)

        # Connection of canvas events for anotations
        self.canvas.mpl_connect("button_press_event", self.on_mouse_press)
        self.canvas.mpl_connect("motion_notify_event", self.on_mouse_move)
        self.canvas.mpl_connect("button_release_event", self.on_mouse_release)

        #editor sync
        self.view.x_column.currentTextChanged.connect(self._sync_script_if_open)
    
    def _connect_basic_tab_signals(self) -> None:
        """Connect signals for the General tab """
        self.view.multi_y_check.stateChanged.connect(self.toggle_multi_y)
        self.view.select_all_y_btn.clicked.connect(self.select_all_y_columns)
        self.view.clear_all_y_btn.clicked.connect(self.clear_all_y_columns)
        
        self.view.x_column.currentTextChanged.connect(self.on_data_changed)
        self.view.y_column.currentTextChanged.connect(self.on_data_changed)
        self.view.y_columns_list.itemSelectionChanged.connect(self.on_data_changed)
        self.view.hue_column.currentTextChanged.connect(self.on_data_changed)
        self.view.subset_combo.currentIndexChanged.connect(self.on_data_changed)
        self.view.quick_filter_input.textChanged.connect(self.on_data_changed)
        
        self.view.apply_subplot_layout_button.clicked.connect(self.apply_subplot_layout)
        self.view.active_subplot_combo.currentIndexChanged.connect(self.on_active_subplot_changed)
        self.view.add_subplots_check.stateChanged.connect(self.on_subplot_active)
        self.view.use_subset_check.stateChanged.connect(self.use_subset)
        self.view.use_plotly_check.stateChanged.connect(self.toggle_plotly_backend)
        self.view.secondary_y_check.stateChanged.connect(lambda state: self._toggle_secondary_input(bool(state)))
    
    def _connect_appearance_tab_signals(self) -> None:
        """Connect signals for the Appearance tab"""
        self.view.individual_spines_check.stateChanged.connect(self.toggle_individual_spines)
        self.view.global_spine_color_button.clicked.connect(self.choose_global_spine_color)
        self.view.top_spine_color_button.clicked.connect(self.choose_top_spine_color)
        self.view.bottom_spine_color_button.clicked.connect(self.choose_bottom_spine_color)
        self.view.left_spine_color_button.clicked.connect(self.choose_left_spine_color)
        self.view.right_spine_color_button.clicked.connect(self.choose_right_spine_color)
        self.view.all_spines_btn.clicked.connect(self.preset_all_spines)
        self.view.box_only_btn.clicked.connect(self.preset_box_only)
        self.view.no_spines_btn.clicked.connect(self.preset_no_spines)
        self.view.bg_color_button.clicked.connect(self.choose_bg_color)
        self.view.face_color_button.clicked.connect(self.choose_face_color)
        self.view.width_spin.valueChanged.connect(lambda: self._setup_plot_figure(clear=False))
        self.view.height_spin.valueChanged.connect(lambda: self._setup_plot_figure(clear=False))
        self.view.colorblind_check.stateChanged.connect(self.update_colorblind_simulation)
        self.view.colorblind_type_combo.currentTextChanged.connect(self.update_colorblind_simulation)
        
        self.view.title_input.textChanged.connect(self.on_style_changed)
        self.view.title_size_spin.valueChanged.connect(self.on_style_changed)
        self.view.title_weight_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.title_position_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.title_check.stateChanged.connect(self.on_style_changed)
        self.view.xlabel_input.textChanged.connect(self.on_style_changed)
        self.view.xlabel_size_spin.valueChanged.connect(self.on_style_changed)
        self.view.xlabel_weight_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.xlabel_check.stateChanged.connect(self.on_style_changed)
        self.view.ylabel_input.textChanged.connect(self.on_style_changed)
        self.view.ylabel_size_spin.valueChanged.connect(self.on_style_changed)
        self.view.ylabel_weight_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.ylabel_check.stateChanged.connect(self.on_style_changed)
        self.view.font_family_combo.currentFontChanged.connect(self.on_style_changed)
        self.view.style_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.global_spine_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.top_spine_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.bottom_spine_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.left_spine_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.right_spine_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.palette_combo.currentTextChanged.connect(self.on_style_changed)
    
    def _connect_axes_tab_signals(self) -> None:
        """Connect signals for the Axes tab"""
        self.view.x_auto_check.stateChanged.connect(lambda: self.view.x_min_spin.setEnabled(not self.view.x_auto_check.isChecked()))
        self.view.x_auto_check.stateChanged.connect(lambda: self.view.x_max_spin.setEnabled(not self.view.x_auto_check.isChecked()))
        self.view.y_auto_check.stateChanged.connect(lambda: self.view.y_min_spin.setEnabled(not self.view.y_auto_check.isChecked()))
        self.view.y_auto_check.stateChanged.connect(lambda: self.view.y_max_spin.setEnabled(not self.view.y_auto_check.isChecked()))
        self.view.custom_datetime_check.stateChanged.connect(self.toggle_datetime_format)
        self.view.x_datetime_format_combo.currentTextChanged.connect(self.on_x_datetime_format_changed)
        self.view.y_datetime_format_combo.currentTextChanged.connect(self.on_y_datetime_format_changed)
        
        self.view.flip_axes_check.stateChanged.connect(self.on_data_changed)
        self.view.x_auto_check.stateChanged.connect(self.on_style_changed)
        self.view.y_auto_check.stateChanged.connect(self.on_style_changed)
        self.view.x_min_spin.valueChanged.connect(self.on_style_changed)
        self.view.x_max_spin.valueChanged.connect(self.on_style_changed)
        self.view.y_min_spin.valueChanged.connect(self.on_style_changed)
        self.view.y_max_spin.valueChanged.connect(self.on_style_changed)
        self.view.xtick_label_size_spin.valueChanged.connect(self.on_style_changed)
        self.view.ytick_label_size_spin.valueChanged.connect(self.on_style_changed)
        self.view.xtick_rotation_spin.valueChanged.connect(self.on_style_changed)
        self.view.ytick_rotation_spin.valueChanged.connect(self.on_style_changed)
        self.view.x_max_ticks_spin.valueChanged.connect(self.on_style_changed)
        self.view.y_max_ticks_spin.valueChanged.connect(self.on_style_changed)
        self.view.x_show_minor_ticks_check.stateChanged.connect(self.on_style_changed)
        self.view.y_show_minor_ticks_check.stateChanged.connect(self.on_style_changed)
        self.view.x_major_tick_direction_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.y_major_tick_direction_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.x_major_tick_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.y_major_tick_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.x_scale_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.y_scale_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.x_display_units_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.y_display_units_combo.currentTextChanged.connect(self.on_style_changed)
        
    def _connect_legend_grid_tab_signals(self) -> None:
        """Connect signals for the Legend and Grid tab"""
        self.view.legend_check.stateChanged.connect(self.on_legend_toggle)
        self.view.legend_bg_button.clicked.connect(self.choose_legend_bg_color)
        self.view.legend_edge_button.clicked.connect(self.choose_legend_edge_color)
        self.view.legend_alpha_slider.valueChanged.connect(lambda v: self.view.legend_alpha_label.setText(f"{v}%"))
        self.view.grid_check.stateChanged.connect(self.on_grid_toggle)
        self.view.global_grid_alpha_slider.valueChanged.connect(lambda v: self.view.global_grid_alpha_label.setText(f"{v}%"))
        self.view.independent_grid_check.stateChanged.connect(self.on_independent_grid_toggle)
        self.view.x_major_grid_color_button.clicked.connect(self.choose_x_major_grid_color)
        self.view.x_major_grid_alpha_slider.valueChanged.connect(lambda v: self.view.x_major_grid_alpha_label.setText(f"{v}%"))
        self.view.x_minor_grid_color_button.clicked.connect(self.choose_x_minor_grid_color)
        self.view.x_minor_grid_alpha_slider.valueChanged.connect(lambda v: self.view.x_minor_grid_alpha_label.setText(f"{v}%"))
        self.view.y_major_grid_color_button.clicked.connect(self.choose_y_major_grid_color)
        self.view.y_major_grid_alpha_slider.valueChanged.connect(lambda v: self.view.y_major_grid_alpha_label.setText(f"{v}%"))
        self.view.y_minor_grid_color_button.clicked.connect(self.choose_y_minor_grid_color)
        self.view.y_minor_grid_alpha_slider.valueChanged.connect(lambda v: self.view.y_minor_grid_alpha_label.setText(f"{v}%"))
        
        self.view.legend_loc_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.legend_title_input.textChanged.connect(self.on_style_changed)
        self.view.legend_size_spin.valueChanged.connect(self.on_style_changed)
        self.view.legend_columns_spin.valueChanged.connect(self.on_style_changed)
        self.view.legend_colspace_spin.valueChanged.connect(self.on_style_changed)
        self.view.legend_frame_check.stateChanged.connect(self.on_style_changed)
        self.view.legend_fancybox_check.stateChanged.connect(self.on_style_changed)
        self.view.legend_shadow_check.stateChanged.connect(self.on_style_changed)
        self.view.legend_edge_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.legend_alpha_slider.valueChanged.connect(self.on_style_changed)
        self.view.grid_which_type_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.grid_axis_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.global_grid_alpha_slider.valueChanged.connect(self.on_style_changed)
        self.view.x_major_grid_check.stateChanged.connect(self.on_style_changed)
        self.view.x_major_grid_style_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.x_major_grid_linewidth_spin.valueChanged.connect(self.on_style_changed)
        self.view.x_major_grid_alpha_slider.valueChanged.connect(self.on_style_changed)
        self.view.x_minor_grid_check.stateChanged.connect(self.on_style_changed)
        self.view.x_minor_grid_style_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.x_minor_grid_linewidth_spin.valueChanged.connect(self.on_style_changed)
        self.view.x_minor_grid_alpha_slider.valueChanged.connect(self.on_style_changed)
        self.view.y_major_grid_check.stateChanged.connect(self.on_style_changed)
        self.view.y_major_grid_style_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.y_major_grid_linewidth_spin.valueChanged.connect(self.on_style_changed)
        self.view.y_major_grid_alpha_slider.valueChanged.connect(self.on_style_changed)
        self.view.y_minor_grid_check.stateChanged.connect(self.on_style_changed)
        self.view.y_minor_grid_style_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.y_minor_grid_linewidth_spin.valueChanged.connect(self.on_style_changed)
        self.view.y_minor_grid_alpha_slider.valueChanged.connect(self.on_style_changed)
        
    def _connect_advanced_tab_signals(self) -> None:
        """Connect signals for the customization tab"""
        self.view.multiline_custom_check.stateChanged.connect(self.toggle_line_selector)
        self.view.line_selector_combo.currentTextChanged.connect(self.on_line_selected)
        self.view.line_color_button.clicked.connect(self.choose_line_color)
        self.view.save_line_custom_button.clicked.connect(self.save_line_customization)
        self.view.marker_color_button.clicked.connect(self.choose_marker_color)
        self.view.marker_edge_button.clicked.connect(self.choose_marker_edge_color)
        self.view.multibar_custom_check.stateChanged.connect(self.toggle_bar_selector)
        self.view.bar_selector_combo.currentTextChanged.connect(self.on_bar_selected)
        self.view.bar_color_button.clicked.connect(self.choose_bar_color)
        self.view.bar_edge_button.clicked.connect(self.choose_bar_edge_color)
        self.view.bar_edge_width_spin.valueChanged.connect(self._update_bar_customization_live)
        self.view.save_bar_custom_button.clicked.connect(self.save_bar_customization)
        self.view.alpha_slider.valueChanged.connect(lambda v: self.view.alpha_label.setText(f"{v}%"))
        
        # Style connections
        self.view.linewidth_spin.valueChanged.connect(self.on_style_changed)
        self.view.linestyle_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.marker_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.marker_size_spin.valueChanged.connect(self.on_style_changed)
        self.view.marker_edge_width_spin.valueChanged.connect(self.on_style_changed)
        self.view.alpha_slider.valueChanged.connect(self.on_style_changed)
        
        # Data connections
        self.view.histogram_bins_spin.valueChanged.connect(self.on_data_changed)
        self.view.histogram_show_normal_check.stateChanged.connect(self.on_data_changed)
        self.view.histogram_show_kde_check.stateChanged.connect(self.on_data_changed)
        self.view.bar_width_spin.valueChanged.connect(self.on_data_changed)
        self.view.regression_line_check.stateChanged.connect(self.on_data_changed)
        self.view.regression_type_combo.currentTextChanged.connect(self.on_data_changed)
        self.view.poly_degree_spin.valueChanged.connect(self.on_data_changed)
        self.view.confidence_interval_check.stateChanged.connect(self.on_data_changed)
        self.view.show_r2_check.stateChanged.connect(self.on_data_changed)
        self.view.show_rmse_check.stateChanged.connect(self.on_data_changed)
        self.view.show_equation_check.stateChanged.connect(self.on_data_changed)
        self.view.confidence_level_spin.valueChanged.connect(self.on_data_changed)
        self.view.pie_show_percentages_check.stateChanged.connect(self.on_data_changed)
        self.view.pie_start_angle_spin.valueChanged.connect(self.on_data_changed)
        self.view.pie_explode_check.stateChanged.connect(self.on_data_changed)
        self.view.pie_explode_distance_spin.valueChanged.connect(self.on_data_changed)
        self.view.pie_shadow_check.stateChanged.connect(self.on_data_changed)
        self.view.error_bars_combo.currentTextChanged.connect(self.on_data_changed)
        
    def _connect_annotation_tab_signals(self) -> None:
        """Connect signals for the Annotations tab"""
        self.view.annotation_color_button.clicked.connect(self.choose_annotation_color)
        self.view.auto_annotate_check.clicked.connect(self.toggle_auto_annotate)
        self.view.add_annotation_button.clicked.connect(self.add_annotation)
        self.view.textbox_bg_button.clicked.connect(self.choose_textbox_bg_color)
        self.view.annotations_list.itemClicked.connect(self.on_annotation_selected)
        self.view.clear_annotations_button.clicked.connect(self.clear_annotations)
        self.view.table_enable_check.stateChanged.connect(self.toggle_table_controls)
        self.view.table_auto_font_size_check.stateChanged.connect(self.toggle_table_font_controls)
        
        self.view.textbox_enable_check.stateChanged.connect(self.on_style_changed)
        self.view.textbox_content.textChanged.connect(self.on_style_changed)
        self.view.textbox_position_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.textbox_style_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.table_enable_check.stateChanged.connect(self.on_style_changed)
        self.view.table_type_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.table_location_combo.currentTextChanged.connect(self.on_style_changed)
        self.view.table_auto_font_size_check.stateChanged.connect(self.on_style_changed)
        self.view.table_font_size_spin.valueChanged.connect(self.on_style_changed)
        self.view.table_scale_spin.valueChanged.connect(self.on_style_changed)

    def _connect_geospatial_tab_signals(self) -> None:
        """Connect signals for the Geospatial tab"""
        self.view.geo_missing_color_btn.clicked.connect(self.choose_geo_missing_color)
        self.view.geo_edge_color_btn.clicked.connect(self.choose_geo_edge_color)
        
        self.view.geo_scheme_combo.currentTextChanged.connect(self.on_data_changed)
        self.view.geo_k_spin.valueChanged.connect(self.on_data_changed)
        self.view.geo_legend_check.stateChanged.connect(self.on_data_changed)
        self.view.geo_legend_loc_combo.currentTextChanged.connect(self.on_data_changed)
        self.view.geo_use_divider_check.stateChanged.connect(self.on_data_changed)
        self.view.geo_cax_check.stateChanged.connect(self.on_data_changed)
        self.view.geo_axis_off_check.stateChanged.connect(self.on_data_changed)
        self.view.geo_missing_label_input.textChanged.connect(self.on_data_changed)
        self.view.geo_hatch_combo.currentTextChanged.connect(self.on_data_changed)
        self.view.geo_boundary_check.stateChanged.connect(self.on_data_changed)
        self.view.geo_linewidth_spin.valueChanged.connect(self.on_data_changed)
        self.view.geo_target_crs_input.textChanged.connect(self.on_data_changed)
        self.view.geo_basemap_check.stateChanged.connect(self.on_data_changed)
        self.view.geo_basemap_style_combo.currentTextChanged.connect(self.on_data_changed)

    def _connect_theme_controls(self) -> None:
        """Connect signals for Theme management"""
        self.view.load_theme_button.clicked.connect(self.apply_selected_theme)
        self.view.save_theme_button.clicked.connect(self.save_custom_theme)
        self.view.edit_theme_button.clicked.connect(self.edit_custom_theme)
        self.view.delete_theme_button.clicked.connect(self.delete_custom_theme)
        self.refresh_theme_list()
    
    def showEvent(self, event) -> None:
        """Triggered on tab visibility. Clears selectons from plot"""
        super().showEvent(event)
        
        if getattr(self, "span_selector", None) is not None:
            if hasattr(self.span_selector, "clear"):
                self.span_selector.clear()
            elif hasattr(self.span_selector, "set_visible"):
                self.span_selector.set_visible(False)
            
            if hasattr(self, "canvas") and self.canvas is not None:
                self.canvas.draw_idle()

    def _populate_plot_toolbox(self):
        while self.view.plot_type.count() > 0:
            self.view.plot_type.removeItem(0)
        
        self.category_lists = []
        for category, plot_names in self.plot_categories.items():
            list_widget = DataPlotStudioListWidget()
            list_widget.setViewMode(DataPlotStudioListWidget.ViewMode.IconMode)
            list_widget.setResizeMode(DataPlotStudioListWidget.ResizeMode.Adjust)
            list_widget.setMovement(DataPlotStudioListWidget.Movement.Static)
            list_widget.setSpacing(8)
            list_widget.setIconSize(QSize(42, 42))
            list_widget.setStyleSheet("QListWidget { background-color: white; border: none; } QListWidget::item { padding: 5px; } QListWidget::item:selected { background-color: #e3f2fd; border-radius: 5px; color: black; border: 1px solid #2196F3; }")

            list_widget.itemClicked.connect(self._on_plot_list_item_clicked)

            for plot_name in plot_names:
                if plot_name in self.plot_engine.AVAILABLE_PLOTS:
                    icon_key = self.plot_engine.AVAILABLE_PLOTS[plot_name]
                    icon_path = get_resource_path(f"icons/plot_tab/plots/{icon_key}.png")

                    item = QListWidgetItem(QIcon(icon_path), plot_name)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setToolTip(self.plot_engine.PLOT_DESCRIPTIONS.get(plot_name, ""))
                    list_widget.addItem(item)
            
            self.view.plot_type.addItem(list_widget, category)
            self.category_lists.append(list_widget)
    
    def _on_plot_list_item_clicked(self, item):
        if not item: return

        plot_type = item.text()
        self.current_plot_type_name = plot_type
        self.view.current_plot_label.setText(f"Selected Plot: {plot_type}")

        for list_w in self.category_lists:
            if list_w != item.listWidget():
                list_w.clearSelection()
        
        self.on_plot_type_changed(plot_type)
        self.on_data_changed()
        self._sync_script_if_open()
    
    def _select_plot_in_toolbox(self, plot_type_name):
        self.current_plot_type_name = plot_type_name
        self.current_plot_label.setText(f"Selected Plot: {plot_type_name}")

        for i, (category, names) in enumerate(self.plot_categories.items()):
            if plot_type_name in names:
                self.view.plot_type.setCurrentIndex(i)
                list_widget = self.category_lists[i]

                items = list_widget.findItems(plot_type_name, Qt.MatchFlag.MatchExactly)
                if items:
                    list_widget.setCurrentItem(items[0])
                    for list_w in self.category_lists:
                        if list_w != list_widget:
                            list_w.clearSelection()
                    self.on_plot_type_changed(plot_type_name)
                break

    def toggle_plotly_backend(self):

        is_plotly = self.view.use_plotly_check.isChecked()

        if is_plotly:
            self.plot_stack.setCurrentIndex(1)
            self.toolbar.setVisible(False)

            self.view.add_subplots_check.setEnabled(False)
            self.view.add_subplots_check.setChecked(False)
        else:
            self.plot_stack.setCurrentIndex(0)
            self.toolbar.setVisible(True)
            self.view.add_subplots_check.setEnabled(True)

    
    def toggle_individual_spines(self):
        """Toggles the customization of spines for each"""
        checked  = self.view.individual_spines_check.isChecked()
        self.view.individual_spines_container.setVisible(checked)
        self.on_style_changed()
    
    def choose_global_spine_color(self):
        """Aplly the color and open diaglo"""
        color = QColorDialog.getColor(QColor(self.global_spine_color), self)
        if color.isValid():
            self.global_spine_color = color.name()
            self.view.global_spine_color_label.setText(self.global_spine_color)
            self.view.global_spine_color_button.updateColors(base_color_hex=self.global_spine_color)
            self.on_style_changed()
    
    def on_subplot_active(self):
        """Activate subplot group for visibility"""
        subplots_enabled = self.view.add_subplots_check.isChecked()

        self.view.subplot_group.setVisible(subplots_enabled)
    
    def use_subset(self):
        """Active subset on change"""
        subset_enabled = self.view.use_subset_check.isChecked()
        self.view.subset_group.setVisible(subset_enabled)
        
    
    def apply_subplot_layout(self):
        """Apply new grid layout to subplot context"""
        rows = self.view.subplot_rows_spin.value()
        cols = self.view.subplot_cols_spin.value()
        sharex = self.view.subplot_sharex_check.isChecked()
        sharey = self.view.subplot_sharey_check.isChecked()

        confirmation = QMessageBox.question(
            self, "Update Layout",
            "Updating subplot layout will clear all existing plots on the canvas.\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            self.plot_engine.setup_layout(rows, cols, sharex=sharex, sharey=sharey)

            max_plots = rows * cols
            self.view.active_subplot_combo.blockSignals(True)
            self.view.active_subplot_combo.clear()

            for i in range(max_plots):
                self.view.active_subplot_combo.addItem(f"Plot {i + 1}")
            self.view.active_subplot_combo.blockSignals(False)

            self.subplot_data_configs.clear()
            self.canvas.draw()

            #trigger overlay
            self.on_active_subplot_changed(0)

            self.status_bar.log(f"Layout updated to {rows}x{cols}", "INFO")
    
    def on_active_subplot_changed(self, index):
        """Change index for active subplot"""
        if index >= 0:
            self.plot_engine.set_active_subplot(index)
            self._update_overlay()
            self.status_bar.log(f"Active subplot set to: {index + 1}", "INFO")
    
    def _update_overlay(self, is_resize: bool = False):
        """Recalculate geometry and overlay widgets"""
        geometry = self.plot_engine.get_active_axis_geometry()

        if geometry:
            x, y, w, h = geometry
            current_text = self.view.active_subplot_combo.currentText()
            self.selection_overlay.update_info(current_text, (x, y, w, h), is_resize=is_resize)
    
    def on_canvas_resize(self, event):
        self._update_overlay(is_resize=True)
        self._setup_plot_figure(clear=False)
        self.canvas.draw_idle()

    def save_plot_image(self) -> None:
        """Save the plot to a file. This is the quick method for most common choices: png, pdf, and svg files"""
        if self.plot_engine.current_figure is None:
            QMessageBox.warning(self, "Warning", "No plot available to save")
            return
        
        try:
            default_export_dpi = 300
            dialog = PlotExportDialog(current_dpi=default_export_dpi, parent=self)
            if dialog.exec():
                config = dialog.get_config()
                filepath = config["filepath"]

                if filepath:
                    kwargs = {
                        "dpi": config["dpi"],
                        "bbox_inches": "tight" if self.view.tight_layout_check.isChecked() else None,
                        "transparent": config["transparent"]
                    }
                    if not config["transparent"]:
                        kwargs["facecolor"] = self.bg_color
                    
                    self.plot_engine.current_figure.savefig(filepath, **kwargs)
                    
                self.status_bar.log_action(f"Plot saved to {filepath}", level="SUCCESS")
                QMessageBox.information(self, "Success", f"Plot saved successfully to:\n{filepath}")
        except Exception as ExportPlotAsImageError:
            self.status_bar.log(f"Failed to save plot: {str(ExportPlotAsImageError)}", "ERROR")
            QMessageBox.critical(self, "Save Error", f"Could not save plot:\n{str(ExportPlotAsImageError)}")
            traceback.print_exc()
    
    def on_pick(self, event):
        """Handles the pick events from the main canvas"""
        artist = event.artist

        if isinstance(artist, Text):
            gid = artist.get_gid()
            if gid and str(gid).startswith("annotation_"):
                self.dragged_annotation = artist
                self.ignore_next_click = True
                self.custom_tabs.setCurrentIndex(5)
                try:
                    idx = int(gid.split("_")[1])
                    if idx < self.view.annotations_list.count():
                        self.view.annotations_list.setCurrentRow(idx)
                        self.on_annotation_selected(self.view.annotations_list.item(idx))
                        self.status_bar.log(f"Selected annotation: {artist.get_text()}", "INFO")
                except ValueError:
                    pass
                return
            self.custom_tabs.setCurrentIndex(1)
            if artist == self.plot_engine.current_ax.get_title():
                self.view.title_input.setFocus()
            elif artist == self.plot_engine.current_ax.xaxis.get_label():
                self.view.xlabel_input.setFocus()
            elif artist == self.plot_engine.current_ax.yaxis.get_label():
                self.view.ylabel_input.setFocus()
            
            self.status_bar.log(f"Selected text element: {artist.get_text()}", "INFO")
        
        elif isinstance(artist, Line2D):
            if artist.get_gid() in ["regression_line", "confidence_interval"]:
                return
            
            self.custom_tabs.setCurrentIndex(4)

            if not self.view.multiline_custom_check.isChecked():
                self.view.multiline_custom_check.setChecked(True)

            label = artist.get_label()
            if label:
                index = self.view.line_selector_combo.findText(label)
                if index >= 0:
                    self.view.line_selector_combo.setCurrentIndex(index)
                    self.status_bar.log(f"Selected line: {label}", "INFO")
                else:
                    lines = [l for l in self.plot_engine.current_ax.get_lines() if l.get_gid() not in ["regression_line", "confidence_interval"]]
                    if artist in lines:
                        idx = lines.index(artist)
                        if idx < self.view.line_selector_combo.count():
                            self.view.line_selector_combo.setCurrentIndex(idx)
                            self.status_bar.log(f"Selected line index: {idx}", "INFO")
        
        elif isinstance(artist, Rectangle):
            found_container = None
            if self.plot_engine.current_ax and self.plot_engine.current_ax.containers:
                for container in self.plot_engine.current_ax.containers:
                    if artist in container:
                        found_container = container
                        break
            
            if found_container:
                if hasattr(self, 'custom_tabs'):
                    self.custom_tabs.setCurrentIndex(4)
                
                if not self.view.multibar_custom_check.isChecked():
                    self.view.multibar_custom_check.setChecked(True)
                
                for i in range(self.view.bar_selector_combo.count()):
                    if self.view.bar_selector_combo.itemData(i) == found_container:
                        self.view.bar_selector_combo.setCurrentIndex(i)
                        label = self.view.bar_selector_combo.itemText(i)
                        self.status_bar.log(f"Selected bar series: {label}", "INFO")
                        break
        
        elif isinstance(artist, PathCollection):
            self.custom_tabs.setCurrentIndex(4)
            self.status_bar.log("Selected scatter points", "INFO")
    
    def on_mouse_press(self, event):
        """Handle mouse pressing events on canvas"""
        if event.button != 1 or not event.inaxes:
            return
        
        if self.ignore_next_click:
            self.ignore_next_click = False
            return
        
        if self.custom_tabs.currentIndex() == 5:
            ax = self.plot_engine.current_ax
            if ax:
                inv = ax.transAxes.inverted()
                x, y = inv.transform((event.x, event.y))
                
                x = max(0.0, min(1.0, x))
                y = max(0.0, min(1.0, y))

                self.view.annotation_x_spin.setValue(x)
                self.view.annotation_y_spin.setValue(y)
    
    def on_mouse_move(self, event):
        """Handle mouse movement for dragging an annotation"""
        if self.dragged_annotation and event.inaxes:
            ax = self.plot_engine.current_ax
            inv = ax.transAxes.inverted()
            x, y = inv.transform((event.x, event.y))

            # Update position
            self.dragged_annotation.set_position((x, y))
            self.canvas.draw_idle()

            self.view.annotation_x_spin.blockSignals(True)
            self.view.annotation_y_spin.blockSignals(True)
            self.view.annotation_x_spin.setValue(x)
            self.view.annotation_y_spin.setValue(y)
            self.view.annotation_x_spin.blockSignals(False)
            self.view.annotation_y_spin.blockSignals(False)
    
    def on_mouse_release(self, event):
        """Handle mouse release to stop draggng event"""
        if self.dragged_annotation:
            gid = self.dragged_annotation.get_gid()
            if gid and gid.startswith("annotation_"):
                try:
                    idx = int(gid.split("_")[1])
                    if 0 <= idx < len(self.annotations):
                        pos = self.dragged_annotation.get_position()
                        self.annotations[idx]["x"] = pos[0]
                        self.annotations[idx]["y"] = pos[1]

                        #update the widget
                        if idx < self.view.annotations_list.count():
                            item = self.view.annotations_list.item(idx)
                            item.setText(f"{self.annotations[idx]["text"]} @ ({pos[0]:.2f}, {pos[1]:.2f})")
                        
                        self.status_bar.log(f"Moved annotation to ({pos[0]:.2f}, {pos[1]:.2f})", "INFO")
                except ValueError:
                    pass
            
            self.dragged_annotation = None

    def choose_geo_missing_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.geo_missing_color = color.name()
            self.view.geo_missing_color_label.setText(self.geo_missing_color)
            self.view.geo_missing_color_btn.updateColors(base_color_hex=self.geo_missing_color)
            self.on_style_changed()

    def choose_geo_edge_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.geo_edge_color = color.name()
            self.view.geo_edge_color_label.setText(self.geo_edge_color)
            self.view.geo_edge_color_btn.updateColors(base_color_hex=self.geo_edge_color)
            self.on_style_changed()
    
    def toggle_auto_annotate(self):
        """Enable auto annotation controls"""
        is_enabled = self.view.auto_annotate_check.isChecked()
        self.view.auto_annotate_col_combo.setEnabled(is_enabled)
        self.on_style_changed()

    def activate_subset(self, subset_name: str):
        """Activates the 'Use Subset' checkbox and selects the selected subset"""
        if not self.subset_manager:
            self.status_bar.log("Cannot activate subset: SubsetManager not available", "ERROR")
            return
        
        self.refresh_subset_list()

        target_index = -1
        for i in range(self.view.subset_combo.count()):
            item_data = self.view.subset_combo.itemData(i)
            if item_data == subset_name:
                target_index = i
                break
        
        if target_index == -1:
            self.status_bar.log(f"Cannot activate subset: Subset '{subset_name}' not found", "WARNING")

        self.view.use_subset_check.setChecked(True)
        self.view.subset_combo.setCurrentIndex(target_index)

        self.status_bar.log_action(
            f"Activated subset: '{subset_name}' for ploting",
            details={"subset_name": subset_name, "source": "DataTab"},
            level="INFO"
        )

    def set_subset_manager(self, subset_manager) -> None:
        """Set the subset manager reference"""
        self.subset_manager = subset_manager
        self.refresh_subset_list()

    def refresh_subset_list(self):
        """Refresh the list of available subsets"""
        if not self.subset_manager:
            print("Warning: Subset manager not available")
            return
        
        if not hasattr(self, 'subset_combo'):
            print("Warning: Subset combo not initialized")
            return
        
        try:
            self.view.subset_combo.blockSignals(True)
            self.view.subset_combo.clear()
            self.view.subset_combo.addItem("(Full Dataset)")
            
            for name in self.subset_manager.list_subsets():
                subset = self.subset_manager.get_subset(name)
                self.view.subset_combo.addItem(f"{name} ({subset.row_count} rows)", userData=name)
            
            self.view.subset_combo.blockSignals(False)
            
            subset_count = len(self.subset_manager.list_subsets())
            if subset_count > 0:
                self.status_bar.log(f"Refreshed subset list: {subset_count} subsets available", "INFO")
        except Exception as RefreshSubsetListError:
            print(f"Warning: Could not refresh subset list: {RefreshSubsetListError}")
    
    def get_active_dataframe(self):
        """Get the active dataframe (full dataset or selected subset)"""
        # Check if subset UI exists
        if not hasattr(self, 'use_subset_check') or not hasattr(self, 'subset_combo'):
            return self.data_handler.df
        
        # Check if user wants to use subset
        if not self.view.use_subset_check.isChecked():
            return self.data_handler.df
        
        # Check if subset manager is available
        if not self.subset_manager:
            self.status_bar.log("Subset manager not available, using full dataset", "WARNING")
            return self.data_handler.df
        
        # Get selected subset name
        subset_name = self.view.subset_combo.currentData()
        if not subset_name:
            return self.data_handler.df
        
        # Try to apply subset
        try:
            subset_df = self.subset_manager.apply_subset(self.data_handler.df, subset_name)
            self.status_bar.log(f"Using subset: {subset_name} ({len(subset_df)} rows)", "INFO")
            return subset_df
        except Exception as ApplySubsetToActiveDataFrameError:
            self.status_bar.log(f"Failed to apply subset, using full dataset: {str(ApplySubsetToActiveDataFrameError)}", "WARNING")
            return self.data_handler.df
        
    
    def toggle_bar_selector(self) -> None:
        """Show/hide bar selection to customize more than one bar"""
        is_enabled = self.view.multibar_custom_check.isChecked()
        self.view.bar_selector_label.setVisible(is_enabled)
        self.view.bar_selector_combo.setVisible(is_enabled)
        self.view.save_bar_custom_button.setVisible(is_enabled)

        if is_enabled:
            self.update_bar_selector()
        
    def update_bar_selector(self) -> None:
        """Update the bar selection tool with the current patches in the plot"""
        self.view.bar_selector_combo.blockSignals(True)
        self.view.bar_selector_combo.clear()

        if self.plot_engine.current_ax and self.plot_engine.current_ax.containers:
            for i, container in enumerate(self.plot_engine.current_ax.containers):
                label = container.get_label()

                if not label or label.startswith("_"):
                    handles, labels = self.plot_engine.current_ax.get_legend_handles_labels()
                    if i < len(labels):
                        label = labels[i]
                    else:
                        label = f"Bar Series {i+1}"
                self.view.bar_selector_combo.addItem(label, userData=container)
        
        self.view.bar_selector_combo.blockSignals(False)

        if self.view.bar_selector_combo.count() > 0:
            self.on_bar_selected(self.view.bar_selector_combo.currentText())
    
    def on_bar_selected(self, bar_name: str) -> None:
        """Load settings for a selected bar series"""
        if not self.view.multibar_custom_check.isChecked():
            return
        
        container = self.view.bar_selector_combo.currentData()

        if not container or not hasattr(container, "patches") or not container.patches:
            return
        
        patch = container.patches[0]

        #load color
        facecolor = to_hex(patch.get_facecolor())
        if facecolor:
            self.bar_color = facecolor
            self.view.bar_color_label.setText(facecolor)
            self.view.bar_color_button.updateColors(base_color_hex=self.bar_color)
        
        #edge color
        edgecolor = to_hex(patch.get_edgecolor())
        if edgecolor:
            self.bar_edge_color = edgecolor
            self.view.bar_edge_label.setText(edgecolor)
            self.view.bar_edge_button.updateColors(base_color_hex=self.bar_edge_color)

        #load the bar edge width
        self.view.bar_edge_width_spin.blockSignals(True)
        self.view.bar_edge_width_spin.setValue(patch.get_linewidth())
        self.view.bar_edge_width_spin.blockSignals(False)
    
    def _update_bar_customization_live(self) -> None:
        """Saves the current temporary bar settings to self.bar_customizations if a bar series is selected"""
        if not self.view.multibar_custom_check.isChecked():
            return
        
        bar_name = self.view.bar_selector_combo.currentText()
        if not bar_name:
            return
        
        custom = self.bar_customizations.get(bar_name, {})
        custom["facecolor"] = self.bar_color
        custom["edgecolor"] = self.bar_edge_color
        custom["linewidth"] = self.view.bar_edge_width_spin.value()

        self.bar_customizations[bar_name] = custom
        self.status_bar.log(f"Updated customisation settings for: {bar_name}")


    def save_bar_customization(self) -> None:
        """Save current settings for a selected bar"""
        if not self.view.multibar_custom_check.isChecked():
            return
        
        bar_name = self.view.bar_selector_combo.currentText()
        if not bar_name:
            return
        
        #store the customizations made
        self.bar_customizations[bar_name] = {
            "facecolor": self.bar_color,
            "edgecolor": self.bar_edge_color,
            "linewidth": self.view.bar_edge_width_spin.value()
        }

        self.status_bar.log(f"Saved customization for: {bar_name}")
        QMessageBox.information(self, "Saved", f"Settings saved for '{bar_name}'.\nClick 'Generate Plot' to apply changes.")

    def on_grid_toggle(self) -> None:
        """Handle grid checkbox toggle"""
        is_enabled = self.view.grid_check.isChecked()
        self.view.global_grid_group.setVisible(is_enabled)
        self.view.grid_which_type_combo.setEnabled(is_enabled)
        self.view.grid_axis_combo.setEnabled(is_enabled)
        self.view.independent_grid_check.setEnabled(is_enabled)

        if not is_enabled:
            self.view.grid_axis_tab.setVisible(False)
            self.view.independent_grid_check.setChecked(False)
        self.on_style_changed()
    
    def on_legend_toggle(self) -> None:
        """Handle legend UI visibility"""
        is_enabled = self.view.legend_check.isChecked()
        self.view.legend_location_label.setVisible(is_enabled)
        self.view.legend_loc_combo.setVisible(is_enabled)
        self.view.legend_title_input.setVisible(is_enabled)
        self.view.legend_title_input.setVisible(is_enabled)
        self.view.legend_font_size_label.setVisible(is_enabled)
        self.view.legend_size_spin.setVisible(is_enabled)
        self.view.legend_ncols_label.setVisible(is_enabled)
        self.view.legend_columns_spin.setVisible(is_enabled)
        self.view.legend_column_spacing_label.setVisible(is_enabled)
        self.view.legend_colspace_spin.setVisible(is_enabled)
        self.view.box_styling_group.setVisible(is_enabled)
        
        self.on_style_changed()

    
    def on_independent_grid_toggle(self):
        """Handle indepeendent customization of axis grids toggle"""
        is_independent = self.view.independent_grid_check.isChecked()
        self.view.grid_axis_tab.setVisible(is_independent)

        #disable global control when independent axis controls are enabeld
        self.view.grid_which_type_combo.setEnabled(not is_independent)
        self.view.grid_axis_combo.setEnabled(not is_independent)
        self.on_style_changed()

    def choose_x_major_grid_color(self):
        """Choose color for x-axis major gridlines"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.x_major_grid_color = color.name()
            self.view.x_major_grid_color_label.setText(self.x_major_grid_color)
            self.view.x_major_grid_color_button.updateColors(base_color_hex=self.x_major_grid_color)
            self.on_style_changed()

    def choose_x_minor_grid_color(self):
        """Choose the colour for the minor x gridlnies"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.x_minor_grid_color = color.name()
            self.view.x_minor_grid_color_label.setText(self.x_minor_grid_color)
            self.view.x_minor_grid_color_button.updateColors(base_color_hex=self.x_minor_grid_color)
            self.on_style_changed()
    
    def choose_y_major_grid_color(self):
        """Choose color for x-axis major gridlines"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.y_major_grid_color = color.name()
            self.view.y_major_grid_color_label.setText(self.y_major_grid_color)
            self.view.y_major_grid_color_button.updateColors(base_color_hex=self.y_major_grid_color)
            self.on_style_changed()

    def choose_y_minor_grid_color(self):
        """Choose the colour for the minor x gridlnies"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.y_minor_grid_color = color.name()
            self.view.y_minor_grid_color_label.setText(self.y_minor_grid_color)
            self.view.y_minor_grid_color_button.updateColors(base_color_hex=self.y_minor_grid_color)
            self.on_style_changed()
    
    def toggle_multi_y(self):
        """Toggle between multi and single y slections"""
        is_multi = self.view.multi_y_check.isChecked()

        #show appropiate widgets
        self.view.y_column.setVisible(not is_multi)
        self.view.y_columns_list.setVisible(is_multi)
        self.view.select_all_y_btn.setVisible(is_multi)
        self.view.clear_all_y_btn.setVisible(is_multi)
        self.view.multi_y_info.setVisible(is_multi)

        #wen swhichtng to multi ycols, select the current ycol
        if is_multi and self.view.y_column.currentText():
            current_y = self.view.y_column.currentText()
            for i in range(self.view.y_columns_list.count()):
                if self.view.y_columns_list.item(i).text() == current_y:
                    self.view.y_columns_list.item(i).setSelected(True)
                    break
        self.on_data_changed()
    
    def select_all_y_columns(self):
        """Select all availalbe ycols"""
        self.view.y_columns_list.selectAll()
        self.on_data_changed()
    
    def clear_all_y_columns(self):
        """Clear all selected ycols"""
        self.view.y_columns_list.clearSelection()
        self.on_data_changed()
    
    def get_selected_y_columns(self):
        """Get list of selected ycols"""
        if self.view.multi_y_check.isChecked():
            selected_items = self.view.y_columns_list.selectedItems()
            return [item.text() for item in selected_items]
        else:
            y_col_text = self.view.y_column.currentText()
            return [y_col_text] if y_col_text else []
    
    def choose_bg_color(self) -> None:
        """Open color picker for background"""
        color = QColorDialog.getColor(QColor(self.bg_color), self)
        if color.isValid():
            self.bg_color = color.name()
            self.view.bg_color_label.setText(self.bg_color)
            self.view.bg_color_button.updateColors(base_color_hex=self.bg_color)
            self.on_style_changed()

    def choose_face_color(self) -> None:
        """Open the color picker tool for the face of the plotting axes"""
        color = QColorDialog.getColor(QColor(self.face_color), self)
        if color.isValid():
            self.face_color = color.name()
            self.view.face_color_label.setText(self.face_color)
            self.view.face_color_button.updateColors(base_color_hex=self.face_color)
            self.on_style_changed()
    
    def update_colorblind_simulation(self) -> None:
        """Applies or removes the SVG filter effect from canvas"""
        if self.view.colorblind_check.isChecked():
            sim_type = self.view.colorblind_type_combo.currentText()
            effect = ColorBlindnessEffect(sim_type)
            self.canvas.setGraphicsEffect(effect)
            self.status_bar.log(f"Color blindness mode enabled: {sim_type}", "INFO")
        else:
            self.canvas.setGraphicsEffect(None)
            self.status_bar.log("Color blindess mode disabled", "INFO")
        self.on_style_changed()

    def toggle_line_selector(self) -> None:
        """Show/enable line selection"""
        is_enabled = self.view.multiline_custom_check.isChecked()
        self.view.line_selector_label.setVisible(is_enabled)
        self.view.line_selector_combo.setVisible(is_enabled)
        self.view.save_line_custom_button.setVisible(is_enabled)

        if is_enabled:
            self.update_line_selector()
    
    def save_line_customization(self) -> None:
        """Save current settings for a line"""
        if not self.view.multiline_custom_check.isChecked():
            return
        
        line_name = self.view.line_selector_combo.currentText()
        if not line_name:
            return
        
        linestyle_map = {'Solid': '-', 'Dashed': '--', 'Dash-dot': '-.', 'Dotted': ':'}
        linestyle_val = linestyle_map.get(self.view.linestyle_combo.currentText(), '-')

        # Store customizations
        self.line_customizations[line_name] = {
            'linewidth': self.view.linewidth_spin.value(),
            'linestyle': linestyle_val,
            'color': self.line_color,
            'marker': self.view.marker_combo.currentText(),
            'markersize': self.view.marker_size_spin.value(),
            'markerfacecolor': self.marker_color,
            'markeredgecolor': self.marker_edge_color,
            'markeredgewidth': self.view.marker_edge_width_spin.value(),
            'alpha': self.view.alpha_slider.value() / 100.0,
        }

        self.status_bar.log(f"Saved customization for: {line_name}")
        QMessageBox.information(self, "Saved", f"Settings saved for '{line_name}'.\nClick 'Generate Plot' to apply changes.")

    
    def update_line_selector(self) -> None:
        """Update the line selection with the ucrrent lines in current_ax"""
        self.view.line_selector_combo.blockSignals(True)
        self.view.line_selector_combo.clear()

        if self.plot_engine.current_ax:
            lines = self.plot_engine.current_ax.get_lines()

            for i, line in enumerate(lines):
                # skip reg and confid lines
                if line.get_gid() in ["regression_line", "confidence_interval"]:
                    continue

                #get line
                label = line.get_label()
                if label.startswith("_"):
                    label = f"Line {i+1}"
                
                self.view.line_selector_combo.addItem(label, userData=i)
            
        self.view.line_selector_combo.blockSignals(False)

        # load
        if self.view.line_selector_combo.count() > 0:
            self.on_line_selected(self.view.line_selector_combo.currentText())
    
    def on_line_selected(self, line_name):
        """Load settings for a selected line"""
        if not self.view.multiline_custom_check.isChecked():
            return
        
        if not self.plot_engine.current_ax:
            return
        
        #get line idx
        line_idx = self.view.line_selector_combo.currentData()
        if line_idx is None:
            return
        
        lines = [l for l in self.plot_engine.current_ax.get_lines() if l.get_gid() not in ["regression_line", "confidence_interval"]]

        if line_idx < len(lines):
            line = lines[line_idx]

            #load current line props
            self.view.linewidth_spin.blockSignals(True)
            self.view.linewidth_spin.setValue(line.get_linewidth())
            self.view.linewidth_spin.blockSignals(False)

            linestyle_map_reverse = {"-": "Solid", "--": "Dashed", "-.": "Dash-dot", ":": "Dotted"}
            current_style = linestyle_map_reverse.get(line.get_linestyle(), "Solid")
            self.view.linestyle_combo.blockSignals(True)
            self.view.linestyle_combo.setCurrentText(current_style)
            self.view.linestyle_combo.blockSignals(False)

            #load color
            color = line.get_color()
            if color:
                self.line_color = to_hex(color)
                self.view.line_color_label.setText(self.line_color)
                self.view.line_color_button.updateColors(base_color_hex=self.line_color)

            #load markers
            marker = line.get_marker()
            if marker and marker != "None":
                self.view.marker_combo.blockSignals(True)
                self.view.marker_combo.setCurrentText(marker)
                self.view.marker_combo.blockSignals(False)

                self.view.marker_size_spin.blockSignals(True)
                self.view.marker_size_spin.setValue(int(line.get_markersize()))
                self.view.marker_size_spin.blockSignals(False)
    
    def choose_top_spine_color(self):
        """Open color picker for top spine"""
        color = QColorDialog.getColor(QColor(self.top_spine_color), self)
        if color.isValid():
            self.top_spine_color = color.name()
            self.view.top_spine_color_label.setText(self.top_spine_color)
            self.view.top_spine_color_button.updateColors(base_color_hex=self.top_spine_color)
            self.on_style_changed()
    
    def choose_bottom_spine_color(self):
        """Open color picker for bottom spine"""
        color = QColorDialog.getColor(QColor(self.bottom_spine_color), self)
        if color.isValid():
            self.bottom_spine_color = color.name()
            self.view.bottom_spine_color_label.setText(self.bottom_spine_color)
            self.view.bottom_spine_color_button.updateColors(base_color_hex=self.bottom_spine_color)
            self.on_style_changed()
    
    def choose_left_spine_color(self):
        """Open color picker for left spine"""
        color = QColorDialog.getColor(QColor(self.left_spine_color), self)
        if color.isValid():
            self.left_spine_color = color.name()
            self.view.left_spine_color_label.setText(self.left_spine_color)
            self.view.left_spine_color_button.updateColors(base_color_hex=self.left_spine_color)
            self.on_style_changed()
    
    def choose_right_spine_color(self):
        """Open color picker for right spine"""
        color = QColorDialog.getColor(QColor(self.right_spine_color), self)
        if color.isValid():
            self.right_spine_color = color.name()
            self.view.right_spine_color_label.setText(self.right_spine_color)
            self.view.right_spine_color_button.updateColors(base_color_hex=self.right_spine_color)
            self.on_style_changed()
    
    def preset_all_spines(self):
        """Preset: Show all spines"""
        self.view.top_spine_visible_check.setChecked(True)
        self.view.bottom_spine_visible_check.setChecked(True)
        self.view.left_spine_visible_check.setChecked(True)
        self.view.right_spine_visible_check.setChecked(True)
        self.status_bar.log("Applied preset: All Spines", "INFO")
        self.on_style_changed()

    def preset_box_only(self):
        """Preset: Show only left and buttom spines"""
        self.view.top_spine_visible_check.setChecked(False)
        self.view.bottom_spine_visible_check.setChecked(True)
        self.view.left_spine_visible_check.setChecked(True)
        self.view.right_spine_visible_check.setChecked(False)
        self.status_bar.log("Applied preset: Box Only", "INFO")
        self.on_style_changed()

    def preset_no_spines(self):
        """Preset: Hide all spines"""
        self.view.top_spine_visible_check.setChecked(False)
        self.view.bottom_spine_visible_check.setChecked(False)
        self.view.left_spine_visible_check.setChecked(False)
        self.view.right_spine_visible_check.setChecked(False)
        self.status_bar.log("Applied preset: No Spines", "INFO")
        self.on_style_changed()
    
    def choose_line_color(self) -> None:
        """Open color picker for line color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.line_color = color.name()
            self.view.line_color_label.setText(self.line_color)
            # Show color preview
            self.view.line_color_button.updateColors(base_color_hex=self.line_color)
            self.on_style_changed()
    
    def choose_marker_color(self):
        """Open color picker for marker color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.marker_color = color.name()
            self.view.marker_color_label.setText(self.marker_color)
            self.view.marker_color_button.updateColors(base_color_hex=self.marker_color)
            self.on_style_changed()
    
    def choose_marker_edge_color(self):
        """Open color picker for marker edge color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.marker_edge_color = color.name()
            self.view.marker_edge_label.setText(self.marker_edge_color)
            self.view.marker_edge_button.updateColors(base_color_hex=self.marker_edge_color)
            self.on_style_changed()
    
    def choose_bar_color(self):
        """Open color picker for bar color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bar_color = color.name()
            self.view.bar_color_label.setText(self.bar_color)
            self.view.bar_color_button.updateColors(base_color_hex=self.bar_color)
            self._update_bar_customization_live()
            self.on_style_changed()
    
    def choose_bar_edge_color(self):
        """Open color picker for bar edge color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bar_edge_color = color.name()
            self.view.bar_edge_label.setText(self.bar_edge_color)
            self.view.bar_edge_button.updateColors(base_color_hex=self.bar_edge_color)
            self._update_bar_customization_live()
            self.on_style_changed()
    
    def choose_annotation_color(self):
        """Open color picker for annotation color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.annotation_color = color.name()
            self.view.annotation_color_label.setText(self.annotation_color)
            self.view.annotation_color_button.updateColors(base_color_hex=self.annotation_color)
            self.on_style_changed()
    
    def choose_textbox_bg_color(self):
        """Open color picker for text box background"""
        color = QColorDialog.getColor(QColor(self.textbox_bg_color), self)
        if color.isValid():
            self.textbox_bg_color = color.name()
            self.view.textbox_bg_label.setText(self.textbox_bg_color)
            self.view.textbox_bg_button.updateColors(base_color_hex=self.textbox_bg_color)
            self.on_style_changed()
    
    def choose_legend_bg_color(self):
        """Open color picker for legend background"""
        color = QColorDialog.getColor(QColor(self.legend_bg_color), self)
        if color.isValid():
            self.legend_bg_color = color.name()
            self.view.legend_bg_label.setText(self.legend_bg_color)
            self.view.legend_bg_button.updateColors(base_color_hex=self.legend_bg_color)
            self.on_style_changed()
    
    def choose_legend_edge_color(self):
        """Open color picker for legend edge color"""
        color = QColorDialog.getColor(QColor(self.legend_edge_color), self)
        if color.isValid():
            self.legend_edge_color = color.name()
            self.view.legend_edge_label.setText(self.legend_edge_color)
            self.view.legend_edge_button.updateColors(base_color_hex=self.legend_edge_color)
            self.on_style_changed()
    
    def add_annotation(self):
        """Add text annotation to plot"""
        text = self.view.annotation_text.text().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter annotation text")
            return
        
        annotation = {
            'text': text,
            'x': self.view.annotation_x_spin.value(),
            'y': self.view.annotation_y_spin.value(),
            'fontsize': self.view.annotation_fontsize_spin.value(),
            'color': self.annotation_color
        }
        
        self.annotations.append(annotation)
        self.view.annotations_list.addItem(f"{text} @ ({annotation['x']:.2f}, {annotation['y']:.2f})")
        self.view.annotation_text.clear()
        self.status_bar.log(f"Added annotation: {text}")
        self.on_style_changed()
    
    def on_annotation_selected(self, item):
        """Handle annotation selection"""
        index = self.view.annotations_list.row(item)
        if 0 <= index < len(self.annotations):
            ann = self.annotations[index]
            self.view.annotation_text.setText(ann['text'])
            self.view.annotation_x_spin.setValue(ann['x'])
            self.view.annotation_y_spin.setValue(ann['y'])
            self.view.annotation_fontsize_spin.setValue(ann['fontsize'])
            self.annotation_color = ann['color']
            self.view.annotation_color_label.setText(self.annotation_color)
            self.on_style_changed()
    
    def clear_annotations(self):
        """Clear all annotations"""
        self.annotations.clear()
        self.view.annotations_list.clear()
        self.view.annotation_text.clear()
        self.status_bar.log("Cleared all annotations")
        self.on_style_changed()
    
    def update_column_combo(self):
        """Update column ComboBoxes with available columns"""
        if self.data_handler.df is None or len(self.data_handler.df.columns) == 0:
            return
        
        columns = list(self.data_handler.df.columns)
        self.view.quick_filter_input.set_columns(columns)

        # Preserve the current selection
        current_x = self.view.x_column.currentText()
        current_y = self.view.y_column.currentText()
        current_hue = self.view.hue_column.currentText()
        current_secondary_y = self.view.secondary_y_column.currentText()
        current_auto_annoate = self.view.auto_annotate_col_combo.currentText()
        current_multi_y = []
        if self.view.multi_y_check.isChecked():
            current_multi_y = [item.text() for item in self.view.y_columns_list.selectedItems()]

        # Block signals to prevent triggering callbacks
        self.view.x_column.blockSignals(True)
        self.view.y_column.blockSignals(True)
        self.view.hue_column.blockSignals(True)
        self.view.secondary_y_column.blockSignals(True)
        self.view.y_columns_list.blockSignals(True)
        self.view.auto_annotate_col_combo.blockSignals(True)
        
        #update xcol
        self.view.x_column.clear()
        self.view.x_column.addItems(columns)
        if current_x in columns:
            self.view.x_column.setCurrentText(current_x)

        #update singleular ycol
        self.view.y_column.clear()
        self.view.y_column.addItems(columns)
        if current_y in columns:
            self.view.y_column.setCurrentText(current_y)

        #update secondary y col
        self.view.secondary_y_column.clear()
        self.view.secondary_y_column.addItems(columns)
        if current_secondary_y in columns:
            self.view.secondary_y_column.setCurrentText(current_secondary_y)

        #update more ycols
        self.view.y_columns_list.clear()
        for col in columns:
            self.view.y_columns_list.addItem(col)
            if col in current_multi_y:
                item = self.view.y_columns_list.item(self.view.y_columns_list.count() - 1)
                item.setSelected(True)
        
        #update hue
        self.view.hue_column.clear()
        self.view.hue_column.addItem("None")
        self.view.hue_column.addItems(columns)
        if current_hue in columns:
            self.view.hue_column.setCurrentText(current_hue)
        else:
            self.view.hue_column.setCurrentIndex(0)

        #update auto annotations
        self.view.auto_annotate_col_combo.clear()
        self.view.auto_annotate_col_combo.addItem("Default (Y-value)")
        self.view.auto_annotate_col_combo.addItems(columns)

        if current_auto_annoate in columns:
            self.view.auto_annotate_col_combo.setCurrentText(current_auto_annoate)
        elif current_auto_annoate == "Default (Y-value)":
            self.view.auto_annotate_col_combo.setCurrentIndex(0)
        
        # Unblock signals
        self.view.x_column.blockSignals(False)
        self.view.y_column.blockSignals(False)
        self.view.hue_column.blockSignals(False)
        self.view.secondary_y_column.blockSignals(False)
        self.view.y_columns_list.blockSignals(False)
        self.view.auto_annotate_col_combo.blockSignals(False)
    
    def toggle_table_controls(self):
        """Enable and disable table controls for the user"""
        enabled = self.view.table_enable_check.isChecked()
        self.view.table_type_combo.setEnabled(enabled)
        self.view.table_type_combo.setVisible(enabled)
        self.view.table_location_combo.setEnabled(enabled)
        self.view.table_location_combo.setVisible(enabled)

        self.view.table_auto_font_size_check.setEnabled(enabled)
        self.view.table_scale_spin.setEnabled(enabled)
        self.view.table_scale_spin.setVisible(enabled)

        self.view.table_font_size_spin.setEnabled(enabled and not self.view.table_auto_font_size_check.isChecked())
        self.view.table_font_size_spin.setVisible(enabled and not self.view.table_auto_font_size_check.isChecked())
    
    def toggle_table_font_controls(self):
        self.view.table_font_size_spin.setEnabled(not self.view.table_auto_font_size_check.isChecked())
        self.view.table_font_size_spin.setVisible(not self.view.table_auto_font_size_check.isChecked())

    def _apply_table(self):
        """Generate the table and add it to the plot"""
        if not self.view.table_enable_check.isChecked():
            return
        
        df = self.get_active_dataframe()
        if df is None:
            return
        
        try:
            table_type = self.view.table_type_combo.currentText()
            x_col = self.view.x_column.currentText()
            y_cols = self.get_selected_y_columns()

            cols_to_use = []
            if x_col: cols_to_use.append(x_col)
            cols_to_use.extend(y_cols)

            if cols_to_use and all(column in df.columns for column in cols_to_use):
                target_df = df[cols_to_use]
            else:
                target_df = df.select_dtypes(include=[np.number])
            
            match table_type:
                case "Summary Stats":
                    data = target_df.describe().round(2)
                case "First 5 Rows":
                    data = target_df.head(5)
                case "Last 5 Rows":
                    data = target_df.tail(5)
                case "Correlation Matrix":
                    data = target_df.corr().round(2)
                case _:
                    data = target_df.head()
            
            loc = self.view.table_location_combo.currentText()
            auto_font = self.view.table_auto_font_size_check.isChecked()
            fontsize = self.view.table_font_size_spin.value()
            scale = self.view.table_scale_spin.value()

            self.plot_engine.add_table(
                data,
                loc=loc,
                auto_font_size=auto_font,
                fontsize=fontsize,
                scale_factor=scale
            )
    
        
        except Exception as PlotTableError:
            self.status_bar.log(f"Failed to add table to plot: {str(PlotTableError)}", "WARNING")
    
    def on_plot_type_changed(self, plot_type: str, log: bool = True):
        """Handle plot type change"""
        if log:
            self.status_bar.log(f"Plot type changed to: {plot_type}")

        description = self.plot_engine.PLOT_DESCRIPTIONS.get(plot_type, "")
        self.view.description_label.setText(description)
        
        self.view.custom_tabs.setTabVisible(6, plot_type == "GeoSpatial")

        line_plots = ["Line", "Area", "Step", "Stairs"]
        bar_plots = ["Bar", "Count Plot", "Stem"]
        hist_plots = ["Histogram"]
        scatter_plots = ["Scatter"]
        pie_plots = ["Pie"]

        show_markers = False
        show_error_bars = False
        
        if plot_type in line_plots:
            self.view.advanced_stack.setCurrentIndex(0)
            show_markers = True
            show_error_bars = True
        elif plot_type in hist_plots:
            self.view.advanced_stack.setCurrentIndex(1)
            self.view.histogram_group.setVisible(True)
            show_error_bars = False
        elif plot_type in bar_plots or plot_type in ["Box", "Violin"]:
            self.view.advanced_stack.setCurrentIndex(1)
            self.view.histogram_group.setVisible(False)
            show_error_bars = True
        elif plot_type in scatter_plots:
            self.view.advanced_stack.setCurrentIndex(2)
            show_markers = True
            show_error_bars = True
        elif plot_type in pie_plots:
            self.view.advanced_stack.setCurrentIndex(3)
        else:
            self.view.advanced_stack.setCurrentIndex(4)
        
        self.view.marker_group.setVisible(show_markers)
        self.view.error_bars_group.setVisible(show_error_bars)


        #plots with multiple ycols
        multi_y_supported = ["Line", "Bar", "Area", "Box", "Stackplot", "Eventplot", "Contour", "Contourf", "Barbs", "Quiver", "Streamplot", "Tricontour", "Tricontourf", "Tripcolor", "Triplot"]

        #enabled based on plottype
        if plot_type in multi_y_supported:
            self.view.multi_y_check.setEnabled(True)
            self.view.multi_y_check.setToolTip("")
        else:
            self.view.multi_y_check.setEnabled(False)
            self.view.multi_y_check.setChecked(False)
            self.view.multi_y_check.setToolTip(f"{plot_type} plots do not support multiple y columns")
        
        #Disbale plots with no dual yaxis support
        dual_axis_supported = ["Line", "Bar", "Scatter", "Area"]
        if plot_type in dual_axis_supported:
            self.view.secondary_y_check.setEnabled(True)
        else:
            self.view.secondary_y_check.setChecked(False)
            self.view.secondary_y_check.setEnabled(False)

        #disable hue for certain plots
        plots_without_hue: list[str] = [
            "Heatmap", "Pie", "Histogram", "KDE", "Count Plot", "Stackplot", "Eventplot",
            "Image Show (imshow)", "pcolormesh", "Contour", "Contourf", "Tricontour",
            "Tricontourf", "Tripcolor", "Triplot", "2D Histogram", "ECDF", "Stairs", "Stem",
            "Barbs", "Quiver", "Streamplot", "GeoSpatial"
        ]
        self.view.hue_column.setEnabled(plot_type not in plots_without_hue)

        if plot_type in plots_without_hue:
            self.view.hue_column.setCurrentText("None")

        #disable flipping axes on certain plots
        incompatible_plots: list[str] = [
            "Histogram", "Pie", "Heatmap", "KDE", "Stackplot", "Eventplot",
            "Image Show (imshow)", "pcolormesh", "Contour", "Contourf", "Barbs", "Quiver",
            "Streamplot", "Tricontour", "Tricontourf", "Tripcolor", "Triplot", "2D Histogram", "ECDF", "GeoSpatial"
        ]
        self.view.flip_axes_check.setEnabled(plot_type not in incompatible_plots)
        if plot_type in incompatible_plots:
            self.view.flip_axes_check.setChecked(False)

    def on_data_changed(self):
        """Handle data column selection change"""
        if self._is_clearing:
            return
        self._is_data_dirty = True
        df = self.get_active_dataframe()
        if df is not None and len(df) <= self.AUTO_UPDATE_THRESHOLD:
            self.style_update_timer.start()
        else:
            self._is_data_dirty = True
            self.selection_overlay.show_update_required(True)
            self.status_bar.log("Data change detected. Click 'Generate Plot' to update.", "WARNING")
    
    def on_style_changed(self) -> None:
        if self._is_clearing:
            return
        if self._is_data_dirty:
            return

        if self.style_update_timer:
            self.style_update_timer.start()
    
    def _fast_render(self) -> None:
        if self._is_clearing:
            return
        if getattr(self, '_is_data_dirty', False):
            self.generate_plot()
            return

        cached_df = getattr(self, '_cached_active_df', None)
        if cached_df is None:
            return
        
        current_subplot_index, _ = self._get_subplot_config()
        x_col = self.view.x_column.currentText()
        y_cols = self.get_selected_y_columns()
        hue = self.view.hue_column.currentText() if self.view.hue_column.currentText() != "None" else None
        subset_name = self.view.subset_combo.currentData() if self.view.use_subset_check.isChecked() else None
        quick_filter = self.view.quick_filter_input.text().strip()

        self._generate_main_plot(
            active_df=cached_df,
            plot_type=self.current_plot_type_name,
            x_col=x_col,
            y_cols=y_cols,
            hue=hue,
            subset_name=subset_name,
            current_subplot_index=current_subplot_index,
            quick_filter=quick_filter,
            keep_data=True,
            animate=False
        )

    def toggle_datetime_format(self):
        """Enabled/disable formating ctrsl for datetime"""
        is_enabled = self.view.custom_datetime_check.isChecked()
        self.view.x_datetime_format_combo.setEnabled(is_enabled)
        self.view.x_datetime_format_combo.setVisible(is_enabled)
        self.view.format_x_datetime_label.setVisible(is_enabled)
        self.view.custom_x_axis_format_label.setVisible(is_enabled)
        self.view.x_custom_datetime_input.setVisible(is_enabled)

        self.view.y_datetime_format_combo.setEnabled(is_enabled)
        self.view.y_datetime_format_combo.setVisible(is_enabled)
        self.view.format_y_datetime_label.setVisible(is_enabled)
        self.view.custom_y_axis_format_label.setVisible(is_enabled)
        self.view.y_custom_datetime_format_input.setVisible(is_enabled)

        self.view.format_help.setVisible(is_enabled)

        #enable the custom input if custom is selected from the box
        if is_enabled:
            self.view.x_custom_datetime_input.setEnabled(self.view.x_datetime_format_combo.currentText() == "Custom")
            self.view.x_custom_datetime_input.setEnabled(self.view.y_datetime_format_combo.currentText() == "Custom")
    
    def on_x_datetime_format_changed(self, text):
        """Handle x-axis format change"""
        self.view.x_custom_datetime_input.setEnabled(text == "Custom")
    
    def on_y_datetime_format_changed(self, text) -> None:
        """Handle y-axis format change"""
        self.view.x_custom_datetime_input.setEnabled(text == "Custom")
    
    def generate_plot(self):
        """Generate plot based on current settings"""
        if self._is_clearing:
            return
        if not self._validate_data_loaded():
            return

        # Get data configuration
        current_subplot_index, frozen_config = self._get_subplot_config()
        active_df, x_col, y_cols, hue, subset_name, quick_filter = self._resolve_data_config(current_subplot_index, frozen_config)

        if not self._validate_active_dataframe(active_df):
            return
        
        plot_type = self.current_plot_type_name

        data_params = [
            id(active_df),
            active_df.shape,
            plot_type,
            x_col,
            tuple(y_cols) if y_cols else None,
            subset_name,
            quick_filter
        ]
        current_data_signature = tuple(data_params)
        processed_df = None
        
        if (hasattr(self, "_last_data_signature") and self._last_data_signature == current_data_signature and hasattr(self, "_cached_active_df") and self._cached_active_df is not None):
            processed_df = self._cached_active_df
            self.status_bar.log("Using cached data for plotting", "INFO")
        else:
            processed_df = active_df.copy()
            if quick_filter:
                processed_df = self._apply_quick_filter(processed_df, quick_filter)
                if processed_df is None:
                    return
            
            processed_df = self._sample_data_if_needed(processed_df, plot_type)
            self._convert_datetime_columns(processed_df, x_col, y_cols)
            self._cached_active_df = processed_df
            self._last_data_signature = current_data_signature
        
        redraw_needed = True

        # Handle the plotly backend
        if self.view.use_plotly_check.isChecked():
            self._generate_plotly_plot(active_df, plot_type, x_col, y_cols, hue)
            return

        # Generate main plot
        self._generate_main_plot(
            active_df, plot_type, x_col, y_cols, hue, subset_name, current_subplot_index, quick_filter, keep_data=not redraw_needed
        )
    
    def _apply_quick_filter(self, df: pd.DataFrame, query: str) -> Optional[pd.DataFrame]:
        """Apply a pandas query to the dataframe"""
        try:
            filtered_df = df.query(query)
            if filtered_df.empty:
                QMessageBox.warning(self, "Empty Result", f"The filter {query} returned an empty dataset")
                self.status_bar.log(f"Filter {query} returned 0 rows", "WARNING")
                return None
            self.status_bar.log(f"Quick Filter applied: {query} ({len(df)} -> {len(filtered_df)} rows)", "INFO")
            return filtered_df
        except Exception as QuickFilterError:
            error_message = f"Invaid Quick Filter expression:\n{str(QuickFilterError)}"
            self.status_bar.log(f"Quick Filter error: {str(QuickFilterError)}", "ERROR")
            QMessageBox.critical(self, "Filter Error", error_message)
    
    def _validate_data_loaded(self) -> bool:
        """Check if data is loaded"""
        if self.data_handler.df is None:
            self.status_bar.log("No data loaded", "WARNING")
            QMessageBox.warning(self, "Warning", "No data loaded")
            return False
        return True
    
    def _get_subplot_config(self):
        """Get current subplot configuration"""
        current_subplot_index = self.view.active_subplot_combo.currentIndex()
        if current_subplot_index < 0:
            current_subplot_index = 0

        frozen_config = None
        if self.view.freeze_data_check.isChecked() and self.view.add_subplots_check.isChecked():
            if current_subplot_index in self.subplot_data_configs:
                frozen_config = self.subplot_data_configs[current_subplot_index]

        return current_subplot_index, frozen_config

    def _resolve_data_config(self, current_subplot_index, frozen_config: dict):
        """Resovle data configeration from frozen config"""
        if frozen_config:
            x_col = frozen_config.get("x_col")
            y_cols = frozen_config.get("y_cols")
            hue = frozen_config.get("hue")
            subset_name = frozen_config.get("subset_name")
            quick_filter = frozen_config.get("quick_filter", "")
            active_df = self._restore_frozen_data(subset_name)
            self.status_bar.log(f"Using data config for plot {current_subplot_index + 1}", "INFO")
        else:
            active_df = self.get_active_dataframe()
            x_col = self.view.x_column.currentText()
            y_cols = self.get_selected_y_columns()
            hue = (self.view.hue_column.currentText() if self.view.hue_column.currentText() != "None" else None)
            subset_name = (self.view.subset_combo.currentData() if self.view.use_subset_check.isChecked() else None)
            quick_filter = self.view.quick_filter_input.text().strip()

        return active_df, x_col, y_cols, hue, subset_name, quick_filter

    def _restore_frozen_data(self, subset_name):
        """Restore data from a frozen subset"""
        if subset_name:
            try:
                if self.subset_manager:
                    return self.subset_manager.apply_subset(
                        self.data_handler.df, subset_name
                    )
                else:
                    self.status_bar.log("Subset Manager not initialized, using full dataset", "WARNING")
                    return self.data_handler.df
            except Exception as UseSubsetError:
                self.status_bar.log(f"Could not restore subset '{subset_name}'. Error: {str(UseSubsetError)}", "ERROR")
                return self.data_handler.df
        else:
            return self.data_handler.df
        
    def _validate_active_dataframe(self, active_df) -> bool:
        """Validates the active dataframe (check if has data or nah)"""
        if active_df is None or len(active_df) == 0:
            QMessageBox.warning(self, "Warning", "Selected data is empty")
            return False
        return True
        
    def _generate_plotly_plot(self, active_df, plot_type, x_col, y_cols, hue):
        """Generate plot using the plotly backend"""
        try:
            self.status_bar.log(f"Generating {plot_type} using plotly...", "INFO")

            kwargs = self._build_plotly_kwargs(plot_type, x_col, y_cols, hue)
            
            result = self.plot_engine.generate_plotly_plot(
                active_df,
                plot_type,
                x_col,
                y_cols,
                **kwargs
            )

            if hasattr(result, "to_html"):
                fig = result
                self._apply_plotly_formatting(fig)
                
                html_content = fig.to_html(include_plotlyjs="cdn", full_html=True)

                if hasattr(self, "web_view") and hasattr(self.web_view, "setHtml"):
                    self.web_view.setHtml(html_content)
                    self.status_bar.log(f"{plot_type} plot generated with plotly")
                else:
                    self.status_bar.log("WebEngineView not available", "ERROR")
            
            elif isinstance(result, str):
                if hasattr(self, "web_view") and hasattr(self.web_view, "setHtml"):
                    self.web_view.setHtml(result)
                self.status_bar.log("Plotly generation returned a message (likely error)", "WARNING")
        
        except Exception as PlotlyFetchError:
            self.status_bar.log(f"Plotting {plot_type} using plotly has failed: {str(PlotlyFetchError)}", "ERROR")
            QMessageBox.critical(self, "Plotly Plotting Error", str(PlotlyFetchError))
            traceback.print_exc()

    def _apply_plotly_formatting(self, fig):
        """Apply the main formatting options to the plotly created figure"""
        #_Fonts 
        font_family = self.view.font_family_combo.currentFont().family()
        fig.update_layout(
            font=dict(family=font_family),
            paper_bgcolor=self.bg_color,
            plot_bgcolor=self.face_color
        )
        # Title
        if self.view.title_check.isChecked():
            fig.update_layout(
                title=dict(
                    text=self.view.title_input.text(),
                    font=dict(size=self.view.title_size_spin.value()),
                    x=0.5 if self.view.title_position_combo.currentText() == "center" else (0.05 if self.view.title_position_combo.currentText() == "left" else 0.95),
                    xanchor=self.view.title_position_combo.currentText()
                )
            )
        else:
            fig.update_layout(title=None)
        
        #Axes Formatting
        # X-Axis
        xaxis_update = dict(
            title=dict(
                text=self.view.xlabel_input.text() if self.view.xlabel_check.isChecked() else "",
                font=dict(size=self.view.xlabel_size_spin.value())
            ),
            showline=True,
            linecolor=self.bottom_spine_color if self.view.bottom_spine_visible_check.isChecked() else "rgba(0,0,0,0)",
            linewidth=self.view.bottom_spine_width_spin.value(),
            showgrid=self.view.grid_check.isChecked() and (self.view.x_major_grid_check.isChecked() if self.view.independent_grid_check.isChecked() else True),
            gridcolor=self.x_major_grid_color if self.view.independent_grid_check.isChecked() else "gray",
            tickfont=dict(size=self.view.xtick_label_size_spin.value()),
            tickangle=self.view.xtick_rotation_spin.value()
        )
        
        if not self.view.x_auto_check.isChecked():
            xaxis_update["range"] = [self.view.x_min_spin.value(), self.view.x_max_spin.value()]
        if self.view.x_scale_combo.currentText() == "log":
            xaxis_update["type"] = "log"

        # Y-Axis
        yaxis_update = dict(
            title=dict(
                text=self.view.ylabel_input.text() if self.view.ylabel_check.isChecked() else "",
                font=dict(size=self.view.ylabel_size_spin.value())
            ),
            showline=True,
            linecolor=self.left_spine_color if self.view.left_spine_visible_check.isChecked() else "rgba(0,0,0,0)",
            linewidth=self.view.left_spine_width_spin.value(),
            showgrid=self.view.grid_check.isChecked() and (self.view.y_major_grid_check.isChecked() if self.view.independent_grid_check.isChecked() else True),
            gridcolor=self.view.y_major_grid_color if self.view.independent_grid_check.isChecked() else "gray",
            tickfont=dict(size=self.view.ytick_label_size_spin.value()),
            tickangle=self.view.ytick_rotation_spin.value()
        )
        if not self.view.y_auto_check.isChecked():
            yaxis_update["range"] = [self.view.y_min_spin.value(), self.view.y_max_spin.value()]
        if self.view.y_scale_combo.currentText() == "log":
            yaxis_update["type"] = "log"

        fig.update_xaxes(**xaxis_update)
        fig.update_yaxes(**yaxis_update)

        # Legend
        if self.view.legend_check.isChecked():
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    bgcolor=self.legend_bg_color,
                    bordercolor=self.legend_edge_color,
                    borderwidth=self.view.legend_edge_width_spin.value(),
                    font=dict(size=self.view.legend_size_spin.value())
                )
            )
        else:
            fig.update_layout(showlegend=False)
            
        if self.view.top_spine_visible_check.isChecked():
            fig.update_xaxes(mirror=True)
    
    def _build_plotly_kwargs(self, plot_type, x_col, y_cols, hue):
        """Build kwargs for plotly plot"""
        kwargs = {
            "title": self.view.title_input.text() or f"{plot_type} plot",
            "xlabel": self.view.xlabel_input.text() or x_col,
            "ylabel": self.view.ylabel_input.text() or (y_cols[0] if y_cols else ""),
            "hue": hue,
            "show_regression": self.view.regression_line_check.isChecked(),
            "horizontal": self.view.flip_axes_check.isChecked()
        }

        if plot_type == "Histogram":
            kwargs["bins"] = self.view.histogram_bins_spin.value()
            kwargs["show_kde"] = self.view.histogram_show_kde_check.isChecked()

        return kwargs

    def _sample_data_if_needed(self, active_df, plot_type):
        """Sample data for better performance if necessary"""
        MAX_PLOT_POINTS = 500_000
        PLOTS_TO_SAMPLE = ["Scatter", "Line", "2D Density", "Hexbin", "Stem", "Stairs", "Eventplot", "ECDF", "2D Histogram", "Tricontour", "Tricontourf", "Tripcolor", "Triplot"]

        if len(active_df) > MAX_PLOT_POINTS and plot_type in PLOTS_TO_SAMPLE:
            self.status_bar.log(f"Dataset is too large ({len(active_df)} rows) for '{plot_type}' "
            f"Plotting a random sample of {MAX_PLOT_POINTS:,} points",
            "WARNING"
            )
            return active_df.sample(n=MAX_PLOT_POINTS, random_state=42)
        return active_df
    
    def _convert_datetime_columns(self, active_df, x_col, y_cols) -> None:
        """Convert datetime columns if needded"""
        try:
            if x_col and self.plot_engine._helper_is_datetime_column(self, active_df[x_col]):
                if not pd.api.types.is_datetime64_any_dtype(active_df[x_col]):
                    active_df[x_col] = pd.to_datetime(active_df[x_col], utc=True, errors="coerce")
                    self.status_bar.log(f"Converted column: '{x_col}' to datetime", "INFO")
            for y_col in y_cols:
                if y_col and self.plot_engine._helper_is_datetime_column(self, active_df[y_col]):
                    if not pd.api.types.is_datetime64_any_dtype(active_df[y_col]):
                        active_df[y_col] = pd.to_datetime(active_df[y_col], utc=True, errors="coerce")
                        self.status_bar.log(f"Converted column: '{y_col}' to datetime", "INFO")
        except Exception as ConvertColumnToDatetimeError:
            self.status_bar.log(f"Warning: Could not convert datetime columns: {str(ConvertColumnToDatetimeError)}", "ERROR")
    
    def _generate_main_plot(self, active_df, plot_type, x_col, y_cols, hue, subset_name, current_subplot_index, quick_filter="", keep_data=False, animate=True):
        """Generate plot using matplotlib settings"""
        data_size = len(self.data_handler.df)
        show_progress = (data_size > 1000 and not keep_data)
        progress_dialog = None

        try:
            progress_dialog = self._init_progress_dialog(show_progress, data_size)

            if not keep_data:
                if not self._validate_plot_requirements(plot_type, x_col, y_cols):
                    return
            
                self._update_progress(progress_dialog, 10, "Preparing data")

            #Build config
            axes_flipped = self.view.flip_axes_check.isChecked()
            font_family = self.view.font_family_combo.currentFont().family()

            self._update_progress(progress_dialog, 20, "Building plot configurations")

            general_kwargs = self._build_general_kwargs(plot_type, x_col, y_cols, hue)
            plot_kwargs = self._build_plot_specific_kwargs(plot_type)

            # Setup plot
            if not keep_data:
                self._update_progress(progress_dialog, 30, "Clearing previous plot")
                self._setup_plot_figure(clear=True)
            else:
                self._setup_plot_figure(clear=False)

            self._update_progress(progress_dialog, 35, "Setting plot style")
            self._apply_plot_style()
            self._set_axis_limits_and_scales()

            #Create
            if not keep_data:
                self._update_progress(progress_dialog, 40, f"Creating {plot_type} plot")

                if not self._execute_plot_strategy(plot_type, active_df, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
                    if progress_dialog:
                        progress_dialog.accept()
                    return
            
            # Apply formatting and customizations
            self._apply_plot_formatting(progress_dialog, x_col, y_cols, axes_flipped, font_family, general_kwargs, active_df)

            # Finalize
            self._update_progress(progress_dialog, 98, "Finising up")
            self._finalize_plot(current_subplot_index, x_col, y_cols, hue, subset_name, quick_filter, is_fast_render=keep_data)

            # Log
            if not keep_data:
                self._log_plot_message(
                    plot_type, x_col, y_cols, hue, subset_name, active_df, quick_filter
                )

            self._update_progress(progress_dialog, 100, "Complete")
            if progress_dialog:
                QTimer.singleShot(300, progress_dialog.accept)
            self._is_data_dirty = False

            if animate:
                self.plot_animation = PlotGeneratedAnimation(parent=self, message="Plot Generated")
                self.plot_animation.start(target_widget=self)
        
        except Exception as CreateMainPlotError:
            if progress_dialog:
                progress_dialog.accept()
            QMessageBox.critical(self, "Error", f"Failed to create plot: {str(CreateMainPlotError)}")
            self.status_bar.log(f"Plot generation failed: {str(CreateMainPlotError)}", "ERROR")
            traceback.print_exc()
        finally:
            if progress_dialog and progress_dialog.isVisible():
                progress_dialog.accept()
    
    def _init_progress_dialog(self, show_progress, data_size):
        """Initizalixze the progress dialog"""
        if show_progress:
            progress_dialog = ProgressDialog(
                title="Generating plot",
                message=f"Processing {data_size:,} data points",
                parent=self
            )
            progress_dialog.show()
            progress_dialog.update_progress(5, "Initializing plotting engine")
            QApplication.processEvents()
            return progress_dialog
        return None
    
    def _update_progress(self, progress_dialog, value, message):
        """Update the progress dialog anc check for cancellation"""
        if progress_dialog:
            progress_dialog.update_progress(value, message)
            if progress_dialog.is_cancelled():
                self.status_bar.log("Plot generation cancelled", "WARNING")
                raise InterruptedError("User cancelled")
    
    def _validate_plot_requirements(self, plot_type, x_col, y_cols) -> bool:
        """Validate the required are data is available"""
        plots_no_x = ["Box", "Histogram", "KDE", "Heatmap", "Pie", "ECDF", "Eventplot", "GeoSpatial"]

        plots_no_y = ["Count Plot", "Heatmap", "GeoSpatial"]
        plots_gridded = ["Image Show (imshow)", "pcolormesh", "Contour", "Contourf"]
        plots_vector = ["Barbs", "Quiver", "Streamplot"]
        plots_triangulation_z = ["Tricontour", "Tricontourf", "Tripcolor"]
        plots_triangulation_no_z = ["Triplot"]

        if not x_col and plot_type not in plots_no_x:
            QMessageBox.warning(self, "Warninig", f"Please select an X column for {plot_type}")
            return False
        
        if not y_cols and plot_type not in plots_no_y:
            QMessageBox.warning(self, "Warning", f"Please select at least one Y column for {plot_type}.")
            return False

        if plot_type in plots_gridded and len(y_cols) < 2:
            QMessageBox.warning(self, "Warning", f"{plot_type} requires 2 Y columns: (Y-position, Z-value)")
            return False

        if plot_type in plots_vector and len(y_cols) < 3:
            QMessageBox.warning(self, "Warning", f"{plot_type} requires 3 Y columns: (Y-position, U-component, V-component)")
            return False
        
        if plot_type in plots_triangulation_z and len(y_cols) < 2:
            QMessageBox.warning(self, "Warning", f"{plot_type} requires 2 Y columns: (Y-position, Z-value)")
            return False

        if plot_type in plots_triangulation_no_z and len(y_cols) < 1:
            QMessageBox.warning(self, "Warning", f"{plot_type} requires at least one Y columns: (Y-position)")
            return False
        
        return True

    def _build_general_kwargs(self, plot_type, x_col, y_cols, hue):
        """Build the general plotting kwargs"""
        plots_supporting_hue = ["Scatter", "Line", "Bar", "Violin", "2D Density", "Box", "Count Plot"]

        y_label_text = self._determine_y_label(plot_type, y_cols)

        general_kwargs = {
            "title": self.view.title_input.text() or plot_type,
            "xlabel": self.view.xlabel_input.text() or x_col,
            "ylabel": self.view.ylabel_input.text() or y_label_text,
            "legend": self.view.legend_check.isChecked()
        }

        # Add secondary y axis
        if self.view.secondary_y_check.isChecked() and self.view.secondary_y_check.isEnabled():
            general_kwargs["secondary_y"] = self.view.secondary_y_column.currentText()
            general_kwargs["secondary_plot_type"] = self.view.secondary_plot_type_combo.currentText()
        
        cmap = self.view.palette_combo.currentText()
        if cmap and cmap != "None":
            if plot_type in ["Bar", "Box", "Violin", "Count Plot"]:
                general_kwargs["palette"] = cmap
            else:
                general_kwargs["cmap"] = cmap

        if hue and plot_type in plots_supporting_hue:
            general_kwargs["hue"] = hue
        
        return general_kwargs

    def _determine_y_label(self, plot_type, y_cols):
        """Determine the correct ylabel based on type"""
        plots_gridded = ["Image Show (imshow)", "pcolormesh", "Contour", "Contourf"]
        plots_vector = ["Barbs", "Quiver", "Streamplot"]
        plots_triangulation = [
            "Tricontour", "Tricontourf", "Tripcolor", "Triplot"
        ]
        plots_no_x = [
            "Box", "Histogram", "KDE", "Heatmap", "Pie", 
            "ECDF", "Eventplot", "GeoSpatial"
        ]

        if plot_type in plots_gridded or plot_type in plots_vector or plot_type in plots_triangulation:
            return y_cols[0] if y_cols else "Value"
        elif plot_type in plots_no_x:
            return y_cols[0] if y_cols else "Value"
        elif len(y_cols) == 1:
            return y_cols[0]
        else:
            return str(y_cols)
    
    def _build_plot_specific_kwargs(self, plot_type):
        """Build plots specific kwargs"""

        plot_kwargs = {}
        if plot_type == "GeoSpatial":
            plot_kwargs = self._build_geospatial_kwargs()
        
        return plot_kwargs
    
    def _build_geospatial_kwargs(self):
        """Builds kwargs specific to the Geospatial plotting routine"""
        scheme_text = self.view.geo_scheme_combo.currentText()
        hatch_text = self.view.geo_hatch_combo.currentText()

        target_crs_input = getattr(self, "geo_target_crs_input", None)
        target_crs = target_crs_input.text() if target_crs_input else None

        basemap_check = getattr(self, "geo_basemap_check", None)
        add_basemap = basemap_check.isChecked() if basemap_check else False

        basemap_combo = getattr(self, "geo_basemap_style_combo", None)
        basemap_source = basemap_combo.currentText() if basemap_combo else "OpenStreetMap"

        kwargs = {
            "scheme": scheme_text if scheme_text != "None" else None,
            "k": self.view.geo_k_spin.value(),
            "cmap": self.view.palette_combo.currentText(),
            "legend": self.view.geo_legend_check.isChecked(),
            "legend_kwds": {
                "loc": "best",
                "orientation": self.view.geo_legend_loc_combo.currentText()
            },
            "use_divider": self.view.geo_use_divider_check.isChecked(),
            "cax_enabled": self.view.geo_cax_check.isChecked(),
            "axis_off": self.view.geo_axis_off_check.isChecked(),
            "missing_kwds": {
                "color": self.geo_missing_color,
                "label": self.view.geo_missing_label_input.text(),
                "hatch": hatch_text if hatch_text != "None" else None
            },
            "edgecolor": self.geo_edge_color,
            "linewidth": self.view.geo_linewidth_spin.value(),
            "target_crs": target_crs,
            "add_basemap": add_basemap,
            "basemap_source": basemap_source
        }
        if self.view.geo_boundary_check.isChecked():
            kwargs["facecolor"] = "none"
        
        return kwargs
    
    def _setup_plot_figure(self, clear: bool = True):
        """Setup plot figure with current settings"""
        if clear:
            self.plot_engine.clear_current_axis()

        target_width_inch = self.view.width_spin.value()
        target_height_inch = self.view.height_spin.value()

        canvas_width = self.canvas.width()
        canvas_height = self.canvas.height()

        if canvas_width <= 0: canvas_width = 800
        if canvas_height <= 0: canvas_height = 600

        dpi_w = canvas_width / target_width_inch
        dpi_h = canvas_height / target_height_inch
        
        calculated_dpi = min(dpi_w, dpi_h)
        calculated_dpi = max(calculated_dpi, 10)

        self.plot_engine.current_figure.set_size_inches(target_width_inch, target_height_inch)
        self.plot_engine.current_figure.set_dpi(calculated_dpi)
        self.plot_engine.current_figure.set_facecolor(self.bg_color)

    def _apply_plot_style(self):
        """Apply plotting style"""
        try:
            plt.style.use(self.view.style_combo.currentText())
            self.plot_engine.current_figure.set_facecolor(self.bg_color)
            self.plot_engine.current_ax.set_facecolor(self.face_color)
        except Exception as ApplyPlotStyleError:
            self.status_bar.log(f"Could not apply plotting style. {str(ApplyPlotStyleError)}", "WARNING")
            self.plot_engine.current_ax.set_facecolor(self.face_color)
    
    def _set_axis_limits_and_scales(self):
        """Set axis limits and scales"""
        if not self.view.x_auto_check.isChecked():
            self.plot_engine.current_ax.set_xlim(
                self.view.x_min_spin.value(), self.view.x_max_spin.value()
            )
        if not self.view.y_auto_check.isChecked():
            self.plot_engine.current_ax.set_ylim(
                self.view.y_min_spin.value(), self.view.y_max_spin.value()
            )
        
        self.plot_engine.current_ax.set_xscale(self.view.x_scale_combo.currentText())
        self.plot_engine.current_ax.set_yscale(self.view.y_scale_combo.currentText())

    def _execute_plot_strategy(self, plot_type, active_df, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Executes the correct plotting strategy"""
        if plot_type not in self.plot_strategies:
            raise ValueError(f"Unknown plot type: {plot_type}")
        
        original_df = self.data_handler.df
        self.data_handler.df = active_df

        try:
            strategy_func = self.plot_strategies[plot_type]
            error_message = strategy_func(
                self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs
            )

            if error_message:
                QMessageBox.warning(self, "Warning", error_message)
                return False

            return True
        finally:
            self.data_handler.df = original_df
    
    def _apply_plot_formatting(self, progress_dialog, x_col, y_cols, axes_flipped, font_family, general_kwargs, active_df):
        """Apply formatting """
        # Tick marks
        try:
            self.plot_engine.current_ax.xaxis.set_major_locator(MaxNLocator(nbins=self.view.x_max_ticks_spin.value()))
            self.plot_engine.current_ax.yaxis.set_major_locator(MaxNLocator(nbins=self.view.y_max_ticks_spin.value()))
        except:
            pass

        self._update_progress(progress_dialog, 70, "Applying formatting")

        if not axes_flipped:
            self._apply_plot_appearance(x_col, y_cols, font_family, general_kwargs)
        
        self._update_progress(progress_dialog, 75, "Applying customizations")
        self._apply_plot_customizations()
        
        self._update_progress(progress_dialog, 80, "Adding legend and gridlines")
        self._apply_legend_and_grid(general_kwargs, font_family)
        self._apply_spines_customization()
        
        self._update_progress(progress_dialog, 85, "Adding annotations")
        self._apply_annotations(active_df, x_col, y_cols)
        
        self._apply_tick_customization()
        self._apply_textbox()
        
        self._update_progress(progress_dialog, 95, "Adding data table")
        self._apply_table()

    def _apply_legend_and_grid(self, general_kwargs: dict, font_family):
        """Apply legend and gridlines"""
        if general_kwargs.get("legend", True):
            self._apply_legend(font_family)
        elif self.plot_engine.current_ax.get_legend():
            self.plot_engine.current_ax.get_legend().set_visible(False)
        
        if self.view.grid_check.isChecked():
            self._apply_gridlines_customizations()
        else:
            self.plot_engine.current_ax.grid(False)
    
    def _finalize_plot(self, current_subplot_index, x_col, y_cols, hue, subset_name, quick_filter, is_fast_render=False) -> None:
        """Finalize plot and save configs"""
        try:
            if self.view.tight_layout_check.isChecked():
                self.plot_engine.current_figure.tight_layout()
        except Exception as TightLayoutError:
            self.status_bar.log(f"Tight layout not applied due to error: {str(TightLayoutError)}", "ERROR")
        
        self.canvas.draw()

        if not is_fast_render:
            self._update_overlay()  

        if self.view.add_subplots_check.isChecked():
            self.subplot_data_configs[current_subplot_index] = {
            "x_col": x_col,
            "y_cols": y_cols,
            "hue": hue,
            "subset_name": subset_name,
            "quick_filter": quick_filter
        }
            
        self._sync_script_if_open()

    def _log_plot_message(self, plot_type, x_col, y_cols, hue, subset_name, active_df, quick_filter=""):
        """Log plot generation to log"""
        plot_details = {
            "plot_type": plot_type,
            "x_column": x_col,
            "y_column": str(y_cols),
            "data_points": len(self.data_handler.df),
            "annotations": len(self.annotations)
        }

        if hue:
            plot_details["hue"] = hue

        if quick_filter:
            plot_details["filter"] = quick_filter

        if self.view.use_subset_check.isChecked() and subset_name:
            plot_details["subset"] = subset_name
            plot_details["subset_rows"] = len(active_df)
            plot_details["total_rows"] = len(self.data_handler.df)
        
        status_message = f"{plot_type} plot created"
        if self.view.use_subset_check.isChecked() and subset_name:
            status_message += f" (Subset: {subset_name})"
        if len(self.annotations) > 0:
            status_message += f" with {len(self.annotations)} annotations"
        
        self.status_bar.log_action(status_message, details=plot_details, level="SUCCESS")
                
    def _apply_plot_appearance(self, x_col, y_cols, font_family, general_kwargs):
        """Apply title, fonts, and labels settings from the Appearance Tab"""
        # apply fonts to ticks
        for label in self.plot_engine.current_ax.get_xticklabels():
            label.set_fontfamily(font_family)
        for label in self.plot_engine.current_ax.get_yticklabels():
            label.set_fontfamily(font_family)

        # title
        if self.view.title_check.isChecked():
            self.plot_engine.current_ax.set_title("", loc='left')
            self.plot_engine.current_ax.set_title("", loc='center')
            self.plot_engine.current_ax.set_title("", loc='right')

            title_text = self.view.title_input.text() or general_kwargs.get("title", "Plot")
            self.plot_engine.current_ax.set_title(
                title_text, 
                fontsize=self.view.title_size_spin.value(), 
                fontweight=self.view.title_weight_combo.currentText(), 
                fontfamily=font_family,
                loc=self.view.title_position_combo.currentText()
            )
        else:
            #clear title
            self.plot_engine.current_ax.set_title("")
            self.plot_engine.current_ax.set_title("", loc='left')
            self.plot_engine.current_ax.set_title("", loc='right')
        
        #xlabel
        if self.view.xlabel_check.isChecked():
            xlabel_text = self.view.xlabel_input.text() or general_kwargs.get("xlabel", "")
            self.plot_engine.current_ax.set_xlabel(
                xlabel_text, 
                fontsize=self.view.xlabel_size_spin.value(), 
                fontweight=self.view.xlabel_weight_combo.currentText(), 
                fontfamily=font_family
            )
        else:
            self.plot_engine.current_ax.set_xlabel("")
        
        # ylabel
        if self.view.ylabel_check.isChecked():
            ylabel_text = self.view.ylabel_input.text() or general_kwargs.get("ylabel", "")
            self.plot_engine.current_ax.set_ylabel(
                ylabel_text, 
                fontsize=self.view.ylabel_size_spin.value(), 
                fontweight=self.view.ylabel_weight_combo.currentText(), 
                fontfamily=font_family
            )
        else:
            self.plot_engine.current_ax.set_ylabel("")

    
    def _apply_plot_customizations(self):
        """Apply customizations to lines, markers, bars etc"""
        #globals
        alpha = self.view.alpha_slider.value() / 100.0
        linewidth = self.view.linewidth_spin.value()
        linestyle = self.view.linestyle_combo.currentText()
        marker = self.view.marker_combo.currentText()
        marker_size = self.view.marker_size_spin.value()
        line_color = self.line_color
        marker_color = self.marker_color
        marker_edge_color = self.marker_edge_color
        marker_edge_width = self.view.marker_edge_width_spin.value()
        bar_color = self.bar_color
        bar_edge_color = self.bar_edge_color
        bar_edge_width = self.view.bar_edge_width_spin.value()

        linestyle_map = {'Solid': '-', 'Dashed': '--', 'Dash-dot': '-.', 'Dotted': ':'}
        linestyle_val = linestyle_map.get(linestyle, linestyle)
        marker_val = "None" if marker == "None" else marker

        # customize lines
        if self.view.multiline_custom_check.isChecked():
            lines = [l for l in self.plot_engine.current_ax.get_lines() if l.get_gid() not in ["regression_line", "confidence_interval"]]
            for i, line in enumerate(lines):
                line_name = line.get_label() if not line.get_label().startswith("_") else f"Line {i+1}"
                if line_name in self.line_customizations:
                    custom = self.line_customizations[line_name]
                    if "linestyle" in custom and custom["linestyle"] != "None":
                        line.set_linestyle(custom["linestyle"])
                    if "linewidth" in custom:
                        line.set_linewidth(custom["linewidth"])
                    if "color" in custom and custom["color"]:
                        line.set_color(custom["color"])
                    if "marker" in custom and custom["marker"] != "None":
                        line.set_marker(custom["marker"])
                        if "markersize" in custom:
                            line.set_markersize(custom["markersize"])
                        if "markerfacecolor" in custom and custom["markerfacecolor"]:
                            line.set_markerfacecolor(custom["markerfacecolor"])
                        if "markeredgecolor" in custom and custom["markeredgecolor"]:
                            line.set_markeredgecolor(custom["markeredgecolor"])
                        if "markeredgewidth" in custom:
                            line.set_markeredgewidth(custom["markeredgewidth"])
                    if "alpha" in custom:
                        line.set_alpha(custom["alpha"])
                else:
                    if linestyle_val != "None":
                        line.set_linestyle(linestyle_val)
                    line.set_linewidth(linewidth)
                    if line_color:
                        line.set_color(line_color)
                    if marker_val != "None":
                        line.set_marker(marker_val)
                        line.set_markersize(marker_size)
                        if marker_color:
                            line.set_markerfacecolor(marker_color)
                        if marker_edge_color:
                            line.set_markeredgecolor(marker_edge_color)
                        line.set_markeredgewidth(marker_edge_width)
                    line.set_alpha(alpha)

            self.update_line_selector()
        else:
            for line in self.plot_engine.current_ax.get_lines():
                if line.get_gid() in ["regression_line", "confidence_interval"]:
                    continue

                if linestyle_val != "None":
                    line.set_linestyle(linestyle_val)
                    line.set_linewidth(linewidth)
                if line_color:
                    line.set_color(line_color)
                if marker_val != "None":
                    line.set_marker(marker_val)
                    line.set_markersize(marker_size)
                    if marker_color:
                        line.set_markerfacecolor(marker_color)
                    if marker_edge_color:
                        line.set_markeredgecolor(marker_edge_color)
                        line.set_markeredgewidth(marker_edge_width)
                line.set_alpha(alpha)
        
        # apply to collections (e.g., scatter plots)
        for collection in self.plot_engine.current_ax.collections:
            if collection.get_gid() == "confidence_interval":
                continue
            collection.set_alpha(alpha)
            if marker_color:
                collection.set_facecolor(marker_color)
            if marker_edge_color:
                collection.set_edgecolor(marker_edge_color)
        
        #apply to patches (e.g., bar plots, histograms)
        if self.view.multibar_custom_check.isChecked():
            self.update_bar_selector()

            for i in range(self.view.bar_selector_combo.count()):
                bar_name = self.view.bar_selector_combo.itemText(i)
                container = self.view.bar_selector_combo.itemData(i)

                if not container or not hasattr(container, "patches"):
                    continue

                if bar_name in self.bar_customizations:
                    custom = self.bar_customizations[bar_name]

                    for patch in container.patches:
                        if "facecolor" in custom and custom["facecolor"]:
                            patch.set_facecolor(custom["facecolor"])
                        if "edgecolor" in custom and custom["edgecolor"]:
                            patch.set_edgecolor(custom["edgecolor"])
                        if "linewidth" in custom:
                            patch.set_linewidth(custom["linewidth"])
                        if "alpha" in custom:
                            patch.set_alpha(custom["alpha"])
                        else:
                            patch.set_alpha(alpha)
                else:
                    for patch in container.patches:
                        patch.set_alpha(alpha)
                        if bar_color:
                            patch.set_facecolor(bar_color)
                        if bar_edge_color:
                            patch.set_edgecolor(bar_edge_color)
                        patch.set_linewidth(bar_edge_width)
            
        else:
            #set globals
            for patch in self.plot_engine.current_ax.patches:
                patch.set_alpha(alpha)
                if bar_color:
                    patch.set_facecolor(bar_color)
                if bar_edge_color:
                    patch.set_edgecolor(bar_edge_color)
                patch.set_linewidth(bar_edge_width)


        
    def _apply_legend(self, font_family) -> None:
        """Apply legend"""
        if not self.view.legend_check.isChecked():
            if self.plot_engine.current_ax.get_legend():
                self.plot_engine.current_ax.get_legend().set_visible(False)
            return
            
        # Check if there's anything to make a legend for
        handles, labels = self.plot_engine.current_ax.get_legend_handles_labels()
        if not handles:
            return

        legend_kwargs = {
            "loc": self.view.legend_loc_combo.currentText(),
            "fontsize": self.view.legend_size_spin.value(),
            "ncol": self.view.legend_columns_spin.value(),
            "columnspacing": self.view.legend_colspace_spin.value(),
            "frameon": self.view.legend_frame_check.isChecked(),
            "fancybox": self.view.legend_fancybox_check.isChecked(),
            "shadow": self.view.legend_shadow_check.isChecked(),
            "framealpha": self.view.legend_alpha_slider.value() / 100.0,
            "facecolor": self.legend_bg_color,
            "edgecolor": self.legend_edge_color
        }

        try:
            legend = self.plot_engine.current_ax.legend(**legend_kwargs)

            # set edge width
            if legend and legend.get_frame():
                legend.get_frame().set_linewidth(self.view.legend_edge_width_spin.value())
            
            #set title
            if self.view.legend_title_input.text().strip():
                legend.set_title(self.view.legend_title_input.text().strip())
            
            # apply font
            for text in legend.get_texts():
                text.set_fontfamily(font_family)
            
            if legend.get_title():
                legend.get_title().set_fontfamily(font_family)
        except Exception as ApplyLegendError:
            self.status_bar.log(f"Failed to apply legend: {ApplyLegendError}", "WARNING")

    
    def _apply_annotations(self, df=None, x_col=None, y_cols=None):
        """Apply text annotations"""

        if self.plot_engine.current_ax:
            texts_to_remove = []
            for text in self.plot_engine.current_ax.texts:
                gid = text.get_gid()
                if gid and (str(gid).startswith("annotation_") or gid == "auto_annotation"):
                    texts_to_remove.append(text)
            
            for text in texts_to_remove:
                try:
                    text.remove()
                except ValueError:
                    pass

        #manual annotations
        for i, ann in enumerate(self.annotations):
            self.plot_engine.current_ax.text(
                ann["x"], ann["y"], ann["text"],
                transform=self.plot_engine.current_ax.transAxes,
                fontsize=ann["fontsize"],
                color=ann["color"],
                ha="center", va="center",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
                picker=True,
                gid=f"annotation_{i}"
            )
        
        #auto annotations based on datapoints
        if self.view.auto_annotate_check.isChecked() and df is not None and x_col and y_cols:
            try:
                label_choice = self.view.auto_annotate_col_combo.currentText()
                is_flipped = self.view.flip_axes_check.isChecked()

                MAX_POINTS = 2000
                if len(df) > MAX_POINTS:
                    self.status_bar.log(f"Auto-annotations is limited to first {MAX_POINTS} points for performance")
                    df_to_annotate = df.iloc[:MAX_POINTS]
                else:
                    df_to_annotate = df

                y_col_target = y_cols[0]
                font_size = self.view.annotation_fontsize_spin.value()
                font_color = self.annotation_color

                for idx, row in df_to_annotate.iterrows():
                    x_val = row[x_col]
                    y_val = row[y_col_target]

                    if label_choice == "Default (Y-value)":
                        text = f"{y_val:.2f}" if isinstance(y_val, (int, float)) else str(y_val)
                    else:
                        text = str(row[label_choice])
                    
                    #apply
                    if is_flipped:
                        self.plot_engine.current_ax.annotate(
                            text,
                            (y_val, x_val),
                            xytext=(5,5),
                            textcoords="offset points",
                            fontsize=font_size,
                            color=font_color if font_color else "black",
                            gid="auto_annotation"
                        )
                    else:
                        self.plot_engine.current_ax.annotate(
                            text,
                            (x_val, y_val),
                            xytext=(5,5),
                            textcoords="offset points",
                            fontsize=font_size,
                            color=font_color if font_color else "black",
                            gid="auto_annotation"
                        )
            except Exception as ApplyAnnotationsError:
                self.status_bar.log(f"Error applying annotations to data points: {str(ApplyAnnotationsError)}", "ERROR")
                print(f"Auto-annotation error: {str(ApplyAnnotationsError)}")

    def _apply_gridlines_customizations(self) -> None:
        """Apply gridlines customizations"""
        if not self.view.grid_check.isChecked():
            self.plot_engine.current_ax.grid(False)
            return
        
        # Ensure grid is on, but we'll style it below
        self.plot_engine.current_ax.grid(True)
        
        if self.view.independent_grid_check.isChecked():
            #  INDEPENDENT 
            
            # Helper to map text to symbol
            grid_style_map = {
                "Solid (-)": "-",
                "Dashed (--)": "--",
                "Dash-dot (-.)": "-.",
                "Dotted (:)": ":"
            }
            
            # X-Axis Major
            style = grid_style_map.get(self.view.x_major_grid_style_combo.currentText(), "-")
            self.plot_engine.current_ax.grid(
                visible=self.view.x_major_grid_check.isChecked(), which="major", axis="x",
                linestyle=style,
                linewidth=self.view.x_major_grid_linewidth_spin.value(),
                color=self.x_major_grid_color,
                alpha=self.view.x_major_grid_alpha_slider.value() / 100.0
            )
            
            # X-Axis Minor
            if self.view.x_minor_grid_check.isChecked():
                self.plot_engine.current_ax.minorticks_on()
                style = grid_style_map.get(self.view.x_minor_grid_style_combo.currentText(), ":")
                self.plot_engine.current_ax.grid(
                    visible=True, which="minor", axis="x",
                    linestyle=style,
                    linewidth=self.view.x_minor_grid_linewidth_spin.value(),
                    color=self.x_minor_grid_color,
                    alpha=self.view.x_minor_grid_alpha_slider.value() / 100.0
                )
            else:
                self.plot_engine.current_ax.grid(visible=False, which="minor", axis="x")

            # Y-Axis Major
            style = grid_style_map.get(self.view.y_major_grid_style_combo.currentText(), "-")
            self.plot_engine.current_ax.grid(
                visible=self.view.y_major_grid_check.isChecked(), which="major", axis="y",
                linestyle=style,
                linewidth=self.view.y_major_grid_linewidth_spin.value(),
                color=self.y_major_grid_color,
                alpha=self.view.y_major_grid_alpha_slider.value() / 100.0
            )

            # Y-Axis Minor
            if self.view.y_minor_grid_check.isChecked():
                self.plot_engine.current_ax.minorticks_on()
                style = grid_style_map.get(self.view.y_minor_grid_style_combo.currentText(), ":")
                self.plot_engine.current_ax.grid(
                    visible=True, which="minor", axis="y",
                    linestyle=style,
                    linewidth=self.view.y_minor_grid_linewidth_spin.value(),
                    color=self.y_minor_grid_color,
                    alpha=self.view.y_minor_grid_alpha_slider.value() / 100.0
                )
            else:
                self.plot_engine.current_ax.grid(visible=False, which="minor", axis="y")
        
        else:
            #  GLOBAL 
            which_type = self.view.grid_which_type_combo.currentText()
            axis = self.view.grid_axis_combo.currentText()

            if which_type in ["minor", "both"]:
                self.plot_engine.current_ax.minorticks_on()
            
            # Apply global settings
            self.plot_engine.current_ax.grid(
                visible=True,
                which=which_type,
                axis=axis,
                alpha=self.view.global_grid_alpha_slider.value() / 100.0
                # Use style-defined defaults for color/linestyle/width
            )

    
    def _apply_tick_customization(self):
        """Apply tick label customization"""
        #major ticks
        self.plot_engine.current_ax.tick_params(
            axis="x",
            labelsize=self.view.xtick_label_size_spin.value(),
            direction=self.view.x_major_tick_direction_combo.currentText(),
            width=self.view.x_major_tick_width_spin.value(),
            which="major"
        )
        self.plot_engine.current_ax.tick_params(
            axis="y",
            labelsize=self.view.ytick_label_size_spin.value(),
            direction=self.view.y_major_tick_direction_combo.currentText(),
            width=self.view.y_major_tick_width_spin.value(),
            which="major"
        )

        #xaxis position
        if self.view.x_top_axis_check.isChecked():
            self.plot_engine.current_ax.xaxis.tick_top()
            self.plot_engine.current_ax.xaxis.set_label_position("top")
        else:
            self.plot_engine.current_ax.xaxis.tick_bottom()
            self.plot_engine.current_ax.xaxis.set_label_position("bottom")


        #minor tickmarks
        if self.view.x_show_minor_ticks_check.isChecked():
            self.plot_engine.current_ax.minorticks_on()
            self.plot_engine.current_ax.tick_params(
                axis="x",
                which="minor",
                direction=self.view.x_minor_tick_direction_combo.currentText(),
                width=self.view.x_minor_tick_width_spin.value()
            )
        
        if self.view.y_show_minor_ticks_check.isChecked():
            self.plot_engine.current_ax.minorticks_on()
            self.plot_engine.current_ax.tick_params(
                axis="y",
                which="minor",
                direction=self.view.y_minor_tick_direction_combo.currentText(),
                width=self.view.y_minor_tick_width_spin.value()
            )
        
        # add formatts if user specified
        try:
            x_unit_str = self.view.x_display_units_combo.currentText()
            if x_unit_str != "None":
                x_formatter = self._create_axis_formatter(x_unit_str)
                if x_formatter:
                    self.plot_engine.current_ax.xaxis.set_major_formatter(x_formatter)
            
            y_unit_str = self.view.y_display_units_combo.currentText()
            if y_unit_str != "None":
                y_formatter = self._create_axis_formatter(y_unit_str)
                if y_formatter:
                    self.plot_engine.current_ax.yaxis.set_major_formatter(y_formatter)
        except Exception as ApplyDisplayUnitsError:
            self.status_bar.log(f"Failed to apply display units: {str(ApplyDisplayUnitsError)}", "WARNING")

        
        #rotation
        plt.setp(self.plot_engine.current_ax.get_xticklabels(), rotation=self.view.xtick_rotation_spin.value())
        plt.setp(self.plot_engine.current_ax.get_yticklabels(), rotation=self.view.ytick_rotation_spin.value())

        #axiss inversion
        if self.view.x_invert_axis_check.isChecked():
            if not self.plot_engine.current_ax.xaxis_inverted():
                self.plot_engine.current_ax.invert_xaxis()
        else:
            if self.plot_engine.current_ax.xaxis_inverted():
                self.plot_engine.current_ax.invert_xaxis()
        
        if self.view.y_invert_axis_check.isChecked():
            if not self.plot_engine.current_ax.yaxis_inverted():
                self.plot_engine.current_ax.invert_yaxis()
        else:
            if self.plot_engine.current_ax.yaxis_inverted():
                self.plot_engine.current_ax.invert_yaxis()

    def _apply_textbox(self):
        """Apply textbox"""
        if self.view.textbox_enable_check.isChecked():
            textbox_text = self.view.textbox_content.text().strip()
            if textbox_text:
                style_map = {
                    "Rounded": "round",
                    "Square": "square",
                    "round,pad=1": "round,pad=1",
                    "round4,pad=0.5": "round4,pad=0.5"
                }
                style = style_map.get(self.view.textbox_style_combo.currentText(), "round")

                position_coords = {
                    "upper left": (0.05, 0.95),
                    "upper center": (0.5, 0.95),
                    "upper right": (0.95, 0.95),
                    "center left": (0.05, 0.5),
                    "center": (0.5, 0.5),
                    "center right": (0.95, 0.5),
                    "lower left": (0.05, 0.05),
                    "lower center": (0.5, 0.05),
                    "lower right": (0.95, 0.05)
                }

                position_name = self.view.textbox_position_combo.currentText()
                x, y = position_coords.get(position_name, (0.5, 0.5)) # Default to center

                ha_map = {
                    "upper left": "left", "center left": "left", "lower left": "left",
                    "upper center": "center", "center": "center", "lower center": "center",
                    "upper right": "right", "center right": "right", "lower right": "right"
                }

                va_map = {
                    "upper left": "top", "upper center": "top", "upper right": "top",
                    "center left": "center", "center": "center", "center right": "center",
                    "lower left": "bottom", "lower center": "bottom", "lower right": "bottom"
                }

                ha = ha_map.get(position_name, "center")
                va = va_map.get(position_name, "center")

                self.plot_engine.current_ax.text(
                    x, y, textbox_text,
                    transform=self.plot_engine.current_ax.transAxes,
                    fontsize=11,
                    verticalalignment=va,
                    horizontalalignment=ha,
                    bbox=dict(boxstyle=style, facecolor=self.textbox_bg_color, alpha=0.8, pad=1)
                )
    
    def _create_axis_formatter(self, unit_str: str) -> FuncFormatter:
        """Create a matplitlib Funcfomatter based on the selected unit"""

        def formatter(x, pos):
            try:
                if unit_str == "Hundreds (100s)":
                    val = x / 1e2
                    return f"{val:.1f}H"
                elif unit_str == "Thousands":
                    val = x / 1e3
                    if abs(val) >= 1000:
                        return f"{val / 1e3:.1f}M"
                    return f"{val:.1f}K"
                elif unit_str == "Millions":
                    val = x / 1e6
                    if abs(val) >= 1000:
                        return f"{val / 1e3:.1f}B"
                    return f"{val:.1f}M"
                elif unit_str == "Billions":
                    val = x / 1e9
                    return f"{val:.1f}B"
                else:
                    return f"{x:g}"
            except (ValueError, TypeError):
                return f"{x:g}"

        if unit_str == "None":
            return None
        
        return FuncFormatter(formatter)
            

    def _apply_spines_customization(self):
        """Apply spines customization t the current ax"""
        if not self.plot_engine.current_ax:
            return
        
        try:
            spines = self.plot_engine.current_ax.spines
            is_individual = self.view.individual_spines_check.isChecked()
            
            # Prepare Global settings
            global_width = self.view.global_spine_width_spin.value()
            global_color = self.global_spine_color

            spine_map = [
                ("top", self.view.top_spine_visible_check, self.view.top_spine_width_spin, "top_spine_color"),
                ("bottom", self.view.bottom_spine_visible_check, self.view.bottom_spine_width_spin, "bottom_spine_color"),
                ("left", self.view.left_spine_visible_check, self.view.left_spine_width_spin, "left_spine_color"),
                ("right", self.view.right_spine_visible_check, self.view.right_spine_width_spin, "right_spine_color")
            ]

            for key, vis_check, width_spin, color_attr in spine_map:
                if key not in spines:
                    continue
                
                is_visible = vis_check.isChecked()
                
                if is_visible:
                    spines[key].set_visible(True)
                    
                    if is_individual:
                        width = width_spin.value()
                        color = getattr(self, color_attr, "black")
                    else:
                        width = global_width
                        color = global_color
                    
                    spines[key].set_linewidth(width)
                    spines[key].set_edgecolor(color)
                else:
                    spines[key].set_visible(False)
        
        except Exception as ApplySpineCustomizationError:
            self.status_bar.log(f"Failed to apply spine customization: {str(ApplySpineCustomizationError)}", "ERROR")
            traceback.print_exc()


    def clear_plot(self) -> None:
        """Clear the plot"""
        self._is_clearing = True
        self.style_update_timer.stop()
        self.plot_engine.clear_plot()

        self._last_data_signature = None
        self._last_viz_signature = None
        self._cached_active_df = None
        self._is_data_dirty = False

        self.view.subplot_rows_spin.blockSignals(True)
        self.view.subplot_cols_spin.blockSignals(True)
        self.view.active_subplot_combo.blockSignals(True)
        self.view.quick_filter_input.clear()

        self.view.subplot_rows_spin.setValue(1)
        self.view.subplot_cols_spin.setValue(1)
        self.view.active_subplot_combo.clear()
        self.view.active_subplot_combo.addItem("Plot 1")
        self.view.quick_filter_input.clear()

        self.view.subplot_rows_spin.blockSignals(False)
        self.view.subplot_cols_spin.blockSignals(False)
        self.view.active_subplot_combo.blockSignals(False)
        self.view.quick_filter_input.blockSignals(False)

        self.canvas.draw()
        self.selection_overlay.hide()

        if self.line_customizations is not None:
            self.line_customizations.clear()
        else:
            self.line_customizations = {}

        if self.bar_customizations is not None:
            self.bar_customizations.clear()
        else:
            self.bar_customizations = {}

        if self.annotations is not None:
            self.annotations.clear()
        else:
            self.annotations = []
            
        self.view.annotations_list.clear()
        
        if self.subplot_data_configs is not None:
            self.subplot_data_configs.clear()
        else:
            self.subplot_data_configs = {}

        self.plot_clear_animation = PlotClearedAnimation(parent=None, message="Plot Cleared")
        self.plot_clear_animation.start(target_widget=self)

        self.status_bar.log_action(
            "Plot cleared",
            details={"operation": "clear_plot"},
            level="INFO"
        )
        QTimer.singleShot(100, lambda: setattr(self, "_is_clearing", False))
    
    def _toggle_secondary_input(self, enabled: bool):
        is_enabled = bool(enabled)

        self.view.secondary_y_column.setEnabled(is_enabled)
        if hasattr(self.view, "secondary_plot_type_combo"):
            self.view.secondary_plot_type_combo.setEnabled(is_enabled)
    
    def load_config(self, config: dict) -> None:
        """Load plot configuration"""
        try:
            self.config_manager.load_config(config)
            self.status_bar.log("Plot Config loaded", "INFO")
        except Exception as LoadConfigError:
            self.status_bar.log(f"Error loading plot config from saved project: {str(LoadConfigError)}")
            traceback.print_exc()

    def get_config(self) -> Dict[str, Any]:
        """Get current plot configuration"""
        return self.config_manager.get_config()

    def clear(self) -> None:
        """Clear all plot data"""
        self.clear_plot()
        self.view.title_input.blockSignals(True)
        self.view.xlabel_input.blockSignals(True)
        self.view.ylabel_input.blockSignals(True)
        
        self.view.title_input.clear()
        self.view.xlabel_input.clear()
        self.view.ylabel_input.clear()
        
        self.view.title_input.blockSignals(False)
        self.view.xlabel_input.blockSignals(False)
        self.view.ylabel_input.blockSignals(False)
    
    def open_script_editor(self):
        """Open the Python Script Editor"""
        if self.data_handler.df is None:
            QMessageBox.warning(self, "No Data", "Please load data first before opening the editor")
            return
        
        #Start by generating the initialcode
        config = self.get_config()
        df = self.get_active_dataframe()
        if df is None: return

        code = self.code_exporter.get_plot_script_only(df, config)

        #open dialog
        if self.script_editor is None:
            self.script_editor = ScriptEditorDialog(code, df=df, parent=self)
            self.script_editor.run_script_signal.connect(self.run_custom_script)
        
        if not self.script_editor.isVisible():
            self.script_editor.update_code(code)
            self.script_editor.show()
        else:
            self.script_editor.raise_()
            self.script_editor.activateWindow()
            self._sync_script_if_open()
    
    def _sync_script_if_open(self):
        """Regenerate the script and update the editor if it is open and autosync is enabled"""
        if self.script_editor and self.script_editor.isVisible():
            self.script_sync_timer.start()
            config = self.get_config()
            df = self.get_active_dataframe()
            if df is not None:
                code = self.code_exporter.get_plot_script_only(df, config)
                self.script_editor.update_code(code)
    
    def _perform_script_sync(self):
        config = self.get_config()
        df = self.get_active_dataframe()
        if df is not None:
            code = self.code_exporter.get_plot_script_only(df, config)
            self.script_editor.update_code(code)
    
    def run_custom_script(self, script_content: str):
        """
        Execute the script from the editor
        Overrides the standard plot generatiom
        """
        self.status_bar.log("Running custom script...", "INFO")

        try:
            def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
                allowed_modules = {
                    "pandas", "numpy", "matplotlib", "seaborn", "scipy", "math", "datetime", "random", "re", "io", "typing", "collections", "itertools", "functools"
                }

                base_name = name.split(".")[0]
                if base_name not in allowed_modules:
                    raise ImportError(f"Security: Import of module: '{name}' is restricted.")
                
                return __import__(name, globals, locals, fromlist, level)

            safe_globals = {
                "__builtins__": {
                    "__import__": safe_import,
                    "print": print,
                    "range": range,
                    "len": len,
                    "list": list,
                    "dict": dict,
                    "set": set,
                    "str": str,
                    "int": int,
                    "float": float,
                    "bool": bool,
                    "zip": zip,
                    "enumerate": enumerate,
                    "min": min,
                    "max": max,
                    "sum": sum,
                    "abs": abs,
                    "sorted": sorted,
                    "tuple": tuple,
                    "None": None,
                    "True": True,
                    "False": False,
                    "hasattr": hasattr,
                    "getattr": getattr,
                    "isinstance": isinstance
                },
                "pd": pd,
                "np": np,
                "plt": plt,
                "sns": sns,
                "mdates": mdates,
                "stats": stats,
                "t_dist": t_dist,
                "MaxNLocator": MaxNLocator
            }

            df_active = self.get_active_dataframe().copy()
            local_vars = {"df": df_active}

            exec(script_content, safe_globals, local_vars)

            if "create_plot" not in local_vars:
                raise ValueError("Script must define a function name 'create_plot' that returns (fix, ax).")
            
            create_plot_func = local_vars["create_plot"]

            self.plot_engine.clear_plot()

            fig_result, ax_result = create_plot_func(df_active)

            old_fig = self.plot_engine.current_figure
            # Closing the previous figure to prevent references to past figures.
            if old_fig is not None:
                plt.close(old_fig)
            self.plot_engine.current_figure = fig_result
            self.plot_engine.current_ax = ax_result

            self.canvas.figure = fig_result
            fig_result.set_canvas(self.canvas)
            self.canvas.draw()

            self._sync_gui_from_ax(ax_result)

            self.status_bar.log("Script executed", "SUCCESS")
        
        except Exception as ExecuteScrptError:
            QMessageBox.critical(self, "Script Error", f"An error occurred while running the script:\n{str(ExecuteScrptError)}")
            self.status_bar.log(f"Script execution failed: {str(ExecuteScrptError)}", "ERROR")
            traceback.print_exc()
    
    def _sync_gui_from_ax(self, ax):
        """
        Attempt to update basic GUI fields from the resulting plot
        """
        try:
            title = ax.get_title()
            if title:
                self.view.title_input.setText(title)
                self.view.title_check.setChecked(True)
            
            xlabel = ax.get_xlabel()
            if xlabel:
                self.view.xlabel_input.setText(xlabel)
                self.view.xlabel_check.setChecked(True)
            
            ylabel = ax.get_ylabel()
            if ylabel:
                self.view.ylabel_input.setText(ylabel)
                self.view.ylabel_check.setChecked(True)
            
        except Exception as GUISyncError:
            print(f"Warning: Could not sync GUI from plot: {GUISyncError}")
    
    def refresh_theme_list(self):
        """Scane the theme directory to update theme selection box"""
        self.view.theme_combo.blockSignals(True)
        self.view.theme_combo.clear()
        self.view.theme_combo.addItem("Select a theme...")

        if os.path.exists(self.theme_dir):
            themes = [theme_file for theme_file in os.listdir(self.theme_dir) if theme_file.endswith(".json")]
            for theme in sorted(themes):
                self.view.theme_combo.addItem(theme.replace(".json", ""), userData=theme)
        
        self.view.theme_combo.blockSignals(False)
    
    def get_theme_config(self) -> Dict[str, Any]:
        theme_data = {
            "appearance": self.config_manager._get_appearance_config(),
            "axes": self.config_manager._get_axes_config(),
            "legend": self.config_manager._get_legend_config(),
            "grid": self.config_manager._get_grid_config(),
            "advanced": self.config_manager._get_advanced_config()
        }

        if "axes" in theme_data:
            theme_data["axes"]["x_axis"]["auto_limits"] = True
            theme_data["axes"]["y_axis"]["auto_limits"] = True
            theme_data["axes"]["x_axis"]["min"] = 0
            theme_data["axes"]["x_axis"]["max"] = 1
            theme_data["axes"]["y_axis"]["min"] = 0
            theme_data["axes"]["y_axis"]["max"] = 1
        
        return theme_data
    
    def save_custom_theme(self):
        """Save the current visual settings to a JSON file"""
        text, ok = QInputDialog.getText(self, "Save theme", "Enter theme name")
        if ok and text:
            if text in self.default_theme_names:
                QMessageBox.warning(self, "Action Denied", f"'{text}' is the name of a default theme. Please choose another theme name")
            filename = "".join(x for x in text if x.isalnum() or x in " _-") + ".json"
            filepath = os.path.join(self.theme_dir, filename)

            theme_data = self.get_theme_config()

            try:
                with open(filepath, "w") as file:
                    json.dump(theme_data, file, indent=4)
                self.status_bar.log(f"Theme '{text}' saved", "SUCCESS")
                self.refresh_theme_list()

                # Automaticaly seltect the new created theme
                index = self.view.theme_combo.findText(text)
                if index >= 0:
                    self.view.theme_combo.setCurrentIndex(index)
            
            except Exception as SaveThemeError:
                self.status_bar.log(f"Failed to save theme: {SaveThemeError}", "ERROR")
                QMessageBox.critical(self, "Error", f"Could not save theme: {str(SaveThemeError)}")
    
    def apply_selected_theme(self):
        """Load and apply the selected theme"""
        theme_file = self.view.theme_combo.currentData()
        if not theme_file:
            return
        
        filepath = os.path.join(self.theme_dir, theme_file)
        if not os.path.exists(filepath):
            self.status_bar.log(f"Theme file not found: {filepath}", "ERROR")
            return
        
        try:
            with open(filepath, "r") as file:
                theme_config = json.load(file)
            
            if "appearance" in theme_config: self.config_manager._load_appearance_config(theme_config["appearance"])
            if "axes" in theme_config: self.config_manager._load_axes_config(theme_config["axes"])
            if "legend" in theme_config: self.config_manager._load_legend_config(theme_config["legend"])
            if "grid" in theme_config: self.config_manager._load_grid_config(theme_config["grid"])
            if "advanced" in theme_config: self.config_manager._load_advanced_config(theme_config["advanced"])

            self.status_bar.log(f"Theme '{self.view.theme_combo.currentText()}' applied", "SUCCESS")

            # if data is present, create the plot again
            if self.data_handler.df is not None:
                self.generate_plot()
        
        except Exception as ApplyThemeError:
            self.status_bar.log(f"Failed to load theme: {ApplyThemeError}", "ERROR")
            QMessageBox.critical(self, "Error", f"Could not load theme: {str(ApplyThemeError)}")
            traceback.print_exc()
    
    def delete_custom_theme(self):
        """Delete the selected theme"""
        theme_file = self.view.theme_combo.currentData()
        theme_name = self.view.theme_combo.currentText()

        if not theme_file or theme_name == "Select a theme...":
            return
        
        clean_name = theme_file.replace(".json", "")
        if clean_name in self.default_theme_names:
            QMessageBox.warning(self, "Action Denied", f"'{theme_name}' is a default theme and cannot be deleted.")
            return
        
        confirm = QMessageBox.question(
            self, "Confrm Delete", f"Are you sure you want to delete theme '{theme_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            try:
                filepath = os.path.join(self.theme_dir, theme_file)
                if os.path.exists(filepath):
                    os.remove(filepath)
                    self.refresh_theme_list()
                    self.status_bar.log(f"Theme '{theme_name}' deleted", "INFO")
            except Exception as DeleteThemeError:
                self.status_bar.log(f"Failed to delete theme: {DeleteThemeError}", "ERROR")
    
    def edit_custom_theme(self):
        """Open JSON editor for the selected theme"""
        theme_file = self.view.theme_combo.currentData()
        theme_name = self.view.theme_combo.currentText()

        if not theme_file or theme_name == "Select a theme...":
            return
        
        filepath = os.path.join(self.theme_dir, theme_file)
        if not os.path.exists(filepath):
            return
        
        try:
            with open(filepath, "r") as file:
                content = json.load(file)
            
            clean_name = theme_file.replace(".json", "")
            is_protected = clean_name in self.default_theme_names

            dialog = ThemeEditorDialog(theme_name, content, is_protected, self)
            if dialog.exec():
                new_content = dialog.final_content

                if is_protected and dialog.new_theme_name:
                    save_name = dialog.new_theme_name
                    filename = "".join(x for x in save_name if x.isalnum() or x in " _-") + ".json"
                    save_path = os.path.join(self.theme_dir, filename)
                else:
                    save_name = theme_name
                    save_path = filepath

                with open(save_path, "w") as file:
                    json.dump(new_content, file, indent=4)
                
                self.status_bar.log(f"Theme '{save_name}' updated", "SUCCESS")
                self.refresh_theme_list()

                index = self.view.theme_combo.findText(save_name)
                if index >= 0:
                    self.view.theme_combo.setCurrentIndex(index)
        except Exception as EditThemeJSONError:
            self.status_bar.log(f"Failed to edit theme: {EditThemeJSONError}", "ERROR")
            QMessageBox.critical(self, "Error", f"Could not edit theme: {str(EditThemeJSONError)}")