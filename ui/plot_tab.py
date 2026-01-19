# ui/plot_tab.py

from re import M
from PyQt6.QtWidgets import QMessageBox, QColorDialog, QApplication, QHBoxLayout, QComboBox, QSpinBox, QMessageBox, QFrame, QLabel, QListWidgetItem, QFileDialog
from PyQt6.QtCore import QTimer, QSize, Qt
from PyQt6.QtGui import QIcon, QColor, QPalette, QFont
from flask.config import T
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from core.plot_engine import PlotEngine
from core.data_handler import DataHandler
from ui.SubplotOverlay import SubplotOverlay
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
from typing import Dict, List, Any
from matplotlib.lines import Line2D
from matplotlib.text import Text
from matplotlib.patches import Rectangle
from matplotlib.collections import PathCollection
from typing import Optional

from ui.widgets import DataPlotStudioButton, DataPlotStudioCheckBox, DataPlotStudioComboBox, DataPlotStudioDoubleSpinBox, DataPlotStudioSlider
from ui.widgets.AnimatedListWidget import DataPlotStudioListWidget
from ui.dialogs.PlotExportDialog import PlotExportDialog


class PlotTab(PlotTabUI):
    """Tab for creating and customizing plots"""
    
    def __init__(self, data_handler: DataHandler, status_bar: StatusBar, subset_manager=None) -> None:
        super().__init__()
        
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
        self._last_plot_signature = None
        
        # These are now defined in the UI base 
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
        
        #populate box in general tab with icons
        #
        self._populate_plot_toolbox()

        # Connect all signals to their logic methods
        self._connect_signals()

        self.selection_overlay = SubplotOverlay(self.canvas)
        self.canvas.mpl_connect("resize_event", self.on_canvas_resize)

        self.canvas.mpl_connect("pick_event", self.on_pick)
        
        # Load initial data
        self.update_column_combo()
        
        self._select_plot_in_toolbox("Line")

    def _connect_signals(self) -> None:
        """Connect all UI widget signals to their logic"""
        
        #  Main Buttons 
        self.plot_button.clicked.connect(self.generate_plot)
        self.editor_button.clicked.connect(self.open_script_editor)
        self.clear_button.clicked.connect(self.clear_plot)
        self.save_plot_button.clicked.connect(self.save_plot_image)

        #editor sync
        self.x_column.currentTextChanged.connect(self._sync_script_if_open)
        
        #  Tab 1: Basic 
        self.multi_y_check.stateChanged.connect(self.toggle_multi_y)
        self.select_all_y_btn.clicked.connect(self.select_all_y_columns)
        self.clear_all_y_btn.clicked.connect(self.clear_all_y_columns)
        self.hue_column.currentTextChanged.connect(self.on_data_changed)
        self.apply_subplot_layout_button.clicked.connect(self.apply_subplot_layout)
        self.active_subplot_combo.currentIndexChanged.connect(self.on_active_subplot_changed)
        self.add_subplots_check.stateChanged.connect(self.on_subplot_active)
        self.use_subset_check.stateChanged.connect(self.use_subset)
        self.use_plotly_check.stateChanged.connect(self.toggle_plotly_backend)
        self.secondary_y_check.stateChanged.connect(lambda state: self._toggle_secondary_input(bool(state)))
        
        #  Tab 2:- Appearance 
        self.individual_spines_check.stateChanged.connect(self.toggle_individual_spines)
        self.global_spine_color_button.clicked.connect(self.choose_global_spine_color)
        self.top_spine_color_button.clicked.connect(self.choose_top_spine_color)
        self.bottom_spine_color_button.clicked.connect(self.choose_bottom_spine_color)
        self.left_spine_color_button.clicked.connect(self.choose_left_spine_color)
        self.right_spine_color_button.clicked.connect(self.choose_right_spine_color)
        self.all_spines_btn.clicked.connect(self.preset_all_spines)
        self.box_only_btn.clicked.connect(self.preset_box_only)
        self.no_spines_btn.clicked.connect(self.preset_no_spines)
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        self.face_color_button.clicked.connect(self.choose_face_color)
        
        #  Tab 3: Axes 
        self.x_auto_check.stateChanged.connect(lambda: self.x_min_spin.setEnabled(not self.x_auto_check.isChecked()))
        self.x_auto_check.stateChanged.connect(lambda: self.x_max_spin.setEnabled(not self.x_auto_check.isChecked()))
        self.y_auto_check.stateChanged.connect(lambda: self.y_min_spin.setEnabled(not self.y_auto_check.isChecked()))
        self.y_auto_check.stateChanged.connect(lambda: self.y_max_spin.setEnabled(not self.y_auto_check.isChecked()))
        self.custom_datetime_check.stateChanged.connect(self.toggle_datetime_format)
        self.x_datetime_format_combo.currentTextChanged.connect(self.on_x_datetime_format_changed)
        self.y_datetime_format_combo.currentTextChanged.connect(self.on_y_datetime_format_changed)
        
        #  Tab 4: Legend & Grid 
        self.legend_check.stateChanged.connect(self.on_legend_toggle)
        self.legend_bg_button.clicked.connect(self.choose_legend_bg_color)
        self.legend_edge_button.clicked.connect(self.choose_legend_edge_color)
        self.legend_alpha_slider.valueChanged.connect(lambda v: self.legend_alpha_label.setText(f"{v}%"))
        self.grid_check.stateChanged.connect(self.on_grid_toggle)
        self.global_grid_alpha_slider.valueChanged.connect(lambda v: self.global_grid_alpha_label.setText(f"{v}%"))
        self.independent_grid_check.stateChanged.connect(self.on_independent_grid_toggle)
        self.x_major_grid_color_button.clicked.connect(self.choose_x_major_grid_color)
        self.x_major_grid_alpha_slider.valueChanged.connect(lambda v: self.x_major_grid_alpha_label.setText(f"{v}%"))
        self.x_minor_grid_color_button.clicked.connect(self.choose_x_minor_grid_color)
        self.x_minor_grid_alpha_slider.valueChanged.connect(lambda v: self.x_minor_grid_alpha_label.setText(f"{v}%"))
        self.y_major_grid_color_button.clicked.connect(self.choose_y_major_grid_color)
        self.y_major_grid_alpha_slider.valueChanged.connect(lambda v: self.y_major_grid_alpha_label.setText(f"{v}%"))
        self.y_minor_grid_color_button.clicked.connect(self.choose_y_minor_grid_color)
        self.y_minor_grid_alpha_slider.valueChanged.connect(lambda v: self.y_minor_grid_alpha_label.setText(f"{v}%"))
        
        #  Tab 5: Advanced 
        self.multiline_custom_check.stateChanged.connect(self.toggle_line_selector)
        self.line_selector_combo.currentTextChanged.connect(self.on_line_selected)
        self.line_color_button.clicked.connect(self.choose_line_color)
        self.save_line_custom_button.clicked.connect(self.save_line_customization)
        self.marker_color_button.clicked.connect(self.choose_marker_color)
        self.marker_edge_button.clicked.connect(self.choose_marker_edge_color)
        self.multibar_custom_check.stateChanged.connect(self.toggle_bar_selector)
        self.bar_selector_combo.currentTextChanged.connect(self.on_bar_selected)
        self.bar_color_button.clicked.connect(self.choose_bar_color)
        self.bar_edge_button.clicked.connect(self.choose_bar_edge_color)
        self.bar_edge_width_spin.valueChanged.connect(self._update_bar_customization_live)
        self.save_bar_custom_button.clicked.connect(self.save_bar_customization)
        self.alpha_slider.valueChanged.connect(lambda v: self.alpha_label.setText(f"{v}%"))
        
        #  Tab 6: Annotations 
        self.annotation_color_button.clicked.connect(self.choose_annotation_color)
        self.auto_annotate_check.clicked.connect(self.toggle_auto_annotate)
        self.add_annotation_button.clicked.connect(self.add_annotation)
        self.textbox_bg_button.clicked.connect(self.choose_textbox_bg_color)
        self.annotations_list.itemClicked.connect(self.on_annotation_selected)
        self.clear_annotations_button.clicked.connect(self.clear_annotations)
        self.table_enable_check.stateChanged.connect(self.toggle_table_controls)
        self.table_auto_font_size_check.stateChanged.connect(self.toggle_table_font_controls)

        #tab 7 geospatial
        self.geo_missing_color_btn.clicked.connect(self.choose_geo_missing_color)
        self.geo_edge_color_btn.clicked.connect(self.choose_geo_edge_color)

    def _populate_plot_toolbox(self):
        while self.plot_type.count() > 0:
            self.plot_type.removeItem(0)
        
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
                    icon_path = f"icons/plot_tab/plots/{icon_key}.png"

                    item = QListWidgetItem(QIcon(icon_path), plot_name)
                    item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    item.setToolTip(self.plot_engine.PLOT_DESCRIPTIONS.get(plot_name, ""))
                    list_widget.addItem(item)
            
            self.plot_type.addItem(list_widget, category)
            self.category_lists.append(list_widget)
    
    def _on_plot_list_item_clicked(self, item):
        if not item: return

        plot_type = item.text()
        self.current_plot_type_name = plot_type
        self.current_plot_label.setText(f"Selected Plot: {plot_type}")

        for list_w in self.category_lists:
            if list_w != item.listWidget():
                list_w.clearSelection()
        
        self.on_plot_type_changed(plot_type)
        self._sync_script_if_open()
    
    def _select_plot_in_toolbox(self, plot_type_name):
        self.current_plot_type_name = plot_type_name
        self.current_plot_label.setText(f"Selected Plot: {plot_type_name}")

        for i, (category, names) in enumerate(self.plot_categories.items()):
            if plot_type_name in names:
                self.plot_type.setCurrentIndex(i)
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

        is_plotly = self.use_plotly_check.isChecked()

        if is_plotly:
            self.plot_stack.setCurrentIndex(1)
            self.toolbar.setVisible(False)

            self.add_subplots_check.setEnabled(False)
            self.add_subplots_check.setChecked(False)
        else:
            self.plot_stack.setCurrentIndex(0)
            self.toolbar.setVisible(True)
            self.add_subplots_check.setEnabled(True)

    
    def toggle_individual_spines(self):
        """Toggles the customization of spines for each"""
        checked  = self.individual_spines_check.isChecked()
        self.individual_spines_container.setVisible(checked)
    
    def choose_global_spine_color(self):
        """Aplly the color and open diaglo"""
        color = QColorDialog.getColor(QColor(self.global_spine_color), self)
        if color.isValid():
            self.global_spine_color = color.name()
            self.global_spine_color_label.setText(self.global_spine_color)
            self.global_spine_color_button.updateColors(base_color_hex=self.global_spine_color)
    
    def on_subplot_active(self):
        """Activate subplot group for visibility"""
        subplots_enabled = self.add_subplots_check.isChecked()

        self.subplot_group.setVisible(subplots_enabled)
    
    def use_subset(self):
        """Active subset on change"""
        subset_enabled = self.use_subset_check.isChecked()
        self.subset_group.setVisible(subset_enabled)
        
    
    def apply_subplot_layout(self):
        """Apply new grid layout to subplot context"""
        rows = self.subplot_rows_spin.value()
        cols = self.subplot_cols_spin.value()
        sharex = self.subplot_sharex_check.isChecked()
        sharey = self.subplot_sharey_check.isChecked()

        confirmation = QMessageBox.question(
            self, "Update Layout",
            "Updating subplot layout will clear all existing plots on the canvas.\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if confirmation == QMessageBox.StandardButton.Yes:
            self.plot_engine.setup_layout(rows, cols, sharex=sharex, sharey=sharey)

            max_plots = rows * cols
            self.active_subplot_combo.blockSignals(True)
            self.active_subplot_combo.clear()

            for i in range(max_plots):
                self.active_subplot_combo.addItem(f"Plot {i + 1}")
            self.active_subplot_combo.blockSignals(False)

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
    
    def _update_overlay(self):
        """Recalculate geometry and overlay widgets"""
        geometry = self.plot_engine.get_active_axis_geometry()

        if geometry:
            x, y, w, h = geometry
            current_text = self.active_subplot_combo.currentText()
            self.selection_overlay.update_info(current_text, (x, y, w, h))
    
    def on_canvas_resize(self, event):
        self._update_overlay()

    def save_plot_image(self) -> None:
        """Save the plot to a file. This is the quick method for most common choices: png, pdf, and svg files"""
        if self.plot_engine.current_figure is None:
            QMessageBox.warning(self, "Warning", "No plot available to save")
            return
        
        try:
            dialog = PlotExportDialog(current_dpi=self.dpi_spin.value(), parent=self)
            if dialog.exec():
                config = dialog.get_config()
                filepath = config["filepath"]

                if filepath:
                    kwargs = {
                        "dpi": config["dpi"],
                        "bbox_inches": "tight" if self.tight_layout_check.isChecked() else None,
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
            self.custom_tabs.setCurrentIndex(1)
            if artist == self.plot_engine.current_ax.get_title():
                self.title_input.setFocus()
            elif artist == self.plot_engine.current_ax.xaxis.get_label():
                self.xlabel_input.setFocus()
            elif artist == self.plot_engine.current_ax.yaxis.get_label():
                self.ylabel_input.setFocus()
            
            self.status_bar.log(f"Selected text element: {artist.get_text()}", "INFO")
        
        elif isinstance(artist, Line2D):
            if artist.get_gid() in ["regression_line", "confidence_interval"]:
                return
            
            self.custom_tabs.setCurrentIndex(4)

            if not self.multiline_custom_check.isChecked():
                self.multiline_custom_check.setChecked(True)

            label = artist.get_label()
            if label:
                index = self.line_selector_combo.findText(label)
                if index >= 0:
                    self.line_selector_combo.setCurrentIndex(index)
                    self.status_bar.log(f"Selected line: {label}", "INFO")
                else:
                    lines = [l for l in self.plot_engine.current_ax.get_lines() if l.get_gid() not in ["regression_line", "confidence_interval"]]
                    if artist in lines:
                        idx = lines.index(artist)
                        if idx < self.line_selector_combo.count():
                            self.line_selector_combo.setCurrentIndex(idx)
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
                
                if not self.multibar_custom_check.isChecked():
                    self.multibar_custom_check.setChecked(True)
                
                for i in range(self.bar_selector_combo.count()):
                    if self.bar_selector_combo.itemData(i) == found_container:
                        self.bar_selector_combo.setCurrentIndex(i)
                        label = self.bar_selector_combo.itemText(i)
                        self.status_bar.log(f"Selected bar series: {label}", "INFO")
                        break
        
        elif isinstance(artist, PathCollection):
            self.custom_tabs.setCurrentIndex(4)
            self.status_bar.log("Selected scatter points", "INFO")

    def choose_geo_missing_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.geo_missing_color = color.name()
            self.geo_missing_color_label.setText(self.geo_missing_color)
            self.geo_missing_color_btn.updateColors(base_color_hex=self.geo_missing_color)

    def choose_geo_edge_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.geo_edge_color = color.name()
            self.geo_edge_color_label.setText(self.geo_edge_color)
            self.geo_edge_color_btn.updateColors(base_color_hex=self.geo_edge_color)
    
    def toggle_auto_annotate(self):
        """Enable auto annotation controls"""
        is_enabled = self.auto_annotate_check.isChecked()
        self.auto_annotate_col_combo.setEnabled(is_enabled)

    def activate_subset(self, subset_name: str):
        """Activates the 'Use Subset' checkbox and selects the selected subset"""
        if not self.subset_manager:
            self.status_bar.log("Cannot activate subset: SubsetManager not available", "ERROR")
            return
        
        self.refresh_subset_list()

        target_index = -1
        for i in range(self.subset_combo.count()):
            item_data = self.subset_combo.itemData(i)
            if item_data == subset_name:
                target_index = i
                break
        
        if target_index == -1:
            self.status_bar.log(f"Cannot activate subset: Subset '{subset_name}' not found", "WARNING")

        self.use_subset_check.setChecked(True)
        self.subset_combo.setCurrentIndex(target_index)

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
            self.subset_combo.blockSignals(True)
            self.subset_combo.clear()
            self.subset_combo.addItem("(Full Dataset)")
            
            for name in self.subset_manager.list_subsets():
                subset = self.subset_manager.get_subset(name)
                self.subset_combo.addItem(f"{name} ({subset.row_count} rows)", userData=name)
            
            self.subset_combo.blockSignals(False)
            
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
        if not self.use_subset_check.isChecked():
            return self.data_handler.df
        
        # Check if subset manager is available
        if not self.subset_manager:
            self.status_bar.log("Subset manager not available, using full dataset", "WARNING")
            return self.data_handler.df
        
        # Get selected subset name
        subset_name = self.subset_combo.currentData()
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
        is_enabled = self.multibar_custom_check.isChecked()
        self.bar_selector_label.setVisible(is_enabled)
        self.bar_selector_combo.setVisible(is_enabled)
        self.save_bar_custom_button.setVisible(is_enabled)

        if is_enabled:
            self.update_bar_selector()
        
    def update_bar_selector(self) -> None:
        """Update the bar selection tool with the current patches in the plot"""
        self.bar_selector_combo.blockSignals(True)
        self.bar_selector_combo.clear()

        if self.plot_engine.current_ax and self.plot_engine.current_ax.containers:
            for i, container in enumerate(self.plot_engine.current_ax.containers):
                label = container.get_label()

                if not label or label.startswith("_"):
                    handles, labels = self.plot_engine.current_ax.get_legend_handles_labels()
                    if i < len(labels):
                        label = labels[i]
                    else:
                        label = f"Bar Series {i+1}"
                self.bar_selector_combo.addItem(label, userData=container)
        
        self.bar_selector_combo.blockSignals(False)

        if self.bar_selector_combo.count() > 0:
            self.on_bar_selected(self.bar_selector_combo.currentText())
    
    def on_bar_selected(self, bar_name: str) -> None:
        """Load settings for a selected bar series"""
        if not self.multibar_custom_check.isChecked():
            return
        
        container = self.bar_selector_combo.currentData()

        if not container or not hasattr(container, "patches") or not container.patches:
            return
        
        patch = container.patches[0]

        #load color
        facecolor = to_hex(patch.get_facecolor())
        if facecolor:
            self.bar_color = facecolor
            self.bar_color_label.setText(facecolor)
            self.bar_color_button.updateColors(base_color_hex=self.bar_color)
        
        #edge color
        edgecolor = to_hex(patch.get_edgecolor())
        if edgecolor:
            self.bar_edge_color = edgecolor
            self.bar_edge_label.setText(edgecolor)
            self.bar_edge_button.updateColors(base_color_hex=self.bar_edge_color)

        #load the bar edge width
        self.bar_edge_width_spin.blockSignals(True)
        self.bar_edge_width_spin.setValue(patch.get_linewidth())
        self.bar_edge_width_spin.blockSignals(False)
    
    def _update_bar_customization_live(self) -> None:
        """Saves the current temporary bar settings to self.bar_customizations if a bar series is selected"""
        if not self.multibar_custom_check.isChecked():
            return
        
        bar_name = self.bar_selector_combo.currentText()
        if not bar_name:
            return
        
        custom = self.bar_customizations.get(bar_name, {})
        custom["facecolor"] = self.bar_color
        custom["edgecolor"] = self.bar_edge_color
        custom["linewidth"] = self.bar_edge_width_spin.value()

        self.bar_customizations[bar_name] = custom
        self.status_bar.log(f"Updated customisation settings for: {bar_name}")


    def save_bar_customization(self) -> None:
        """Save current settings for a selected bar"""
        if not self.multibar_custom_check.isChecked():
            return
        
        bar_name = self.bar_selector_combo.currentText()
        if not bar_name:
            return
        
        #store the customizations made
        self.bar_customizations[bar_name] = {
            "facecolor": self.bar_color,
            "edgecolor": self.bar_edge_color,
            "linewidth": self.bar_edge_width_spin.value()
        }

        self.status_bar.log(f"Saved customization for: {bar_name}")
        QMessageBox.information(self, "Saved", f"Settings saved for '{bar_name}'.\nClick 'Generate Plot' to apply changes.")

    def on_grid_toggle(self) -> None:
        """Handle grid checkbox toggle"""
        is_enabled = self.grid_check.isChecked()
        self.global_grid_group.setVisible(is_enabled)
        self.grid_which_type_combo.setEnabled(is_enabled)
        self.grid_axis_combo.setEnabled(is_enabled)
        self.independent_grid_check.setEnabled(is_enabled)

        if not is_enabled:
            self.grid_axis_tab.setVisible(False)
            self.independent_grid_check.setChecked(False)
    
    def on_legend_toggle(self) -> None:
        """Handle legend UI visibility"""
        is_enabled = self.legend_check.isChecked()
        self.legend_location_label.setVisible(is_enabled)
        self.legend_loc_combo.setVisible(is_enabled)
        self.legend_title_input.setVisible(is_enabled)
        self.legend_title_input.setVisible(is_enabled)
        self.legend_font_size_label.setVisible(is_enabled)
        self.legend_size_spin.setVisible(is_enabled)
        self.legend_ncols_label.setVisible(is_enabled)
        self.legend_columns_spin.setVisible(is_enabled)
        self.legend_column_spacing_label.setVisible(is_enabled)
        self.legend_colspace_spin.setVisible(is_enabled)
        self.box_styling_group.setVisible(is_enabled)

    
    def on_independent_grid_toggle(self):
        """Handle indepeendent customization of axis grids toggle"""
        is_independent = self.independent_grid_check.isChecked()
        self.grid_axis_tab.setVisible(is_independent)

        #disable global control when independent axis controls are enabeld
        self.grid_which_type_combo.setEnabled(not is_independent)
        self.grid_axis_combo.setEnabled(not is_independent)

    def choose_x_major_grid_color(self):
        """Choose color for x-axis major gridlines"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.x_major_grid_color = color.name()
            self.x_major_grid_color_label.setText(self.x_major_grid_color)
            self.x_major_grid_color_button.updateColors(base_color_hex=self.x_major_grid_color)

    def choose_x_minor_grid_color(self):
        """Choose the colour for the minor x gridlnies"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.x_minor_grid_color = color.name()
            self.x_minor_grid_color_label.setText(self.x_minor_grid_color)
            self.x_minor_grid_color_button.updateColors(base_color_hex=self.x_minor_grid_color)
    
    def choose_y_major_grid_color(self):
        """Choose color for x-axis major gridlines"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.y_major_grid_color = color.name()
            self.y_major_grid_color_label.setText(self.y_major_grid_color)
            self.y_major_grid_color_button.updateColors(base_color_hex=self.y_major_grid_color)

    def choose_y_minor_grid_color(self):
        """Choose the colour for the minor x gridlnies"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.y_minor_grid_color = color.name()
            self.y_minor_grid_color_label.setText(self.y_minor_grid_color)
            self.y_minor_grid_color_button.updateColors(base_color_hex=self.y_minor_grid_color)
    
    def toggle_multi_y(self):
        """Toggle between multi and single y slections"""
        is_multi = self.multi_y_check.isChecked()

        #show appropiate widgets
        self.y_column.setVisible(not is_multi)
        self.y_columns_list.setVisible(is_multi)
        self.select_all_y_btn.setVisible(is_multi)
        self.clear_all_y_btn.setVisible(is_multi)
        self.multi_y_info.setVisible(is_multi)

        #wen swhichtng to multi ycols, select the current ycol
        if is_multi and self.y_column.currentText():
            current_y = self.y_column.currentText()
            for i in range(self.y_columns_list.count()):
                if self.y_columns_list.item(i).text() == current_y:
                    self.y_columns_list.item(i).setSelected(True)
                    break
    
    def select_all_y_columns(self):
        """Select all availalbe ycols"""
        self.y_columns_list.selectAll()
    
    def clear_all_y_columns(self):
        """Clear all selected ycols"""
        self.y_columns_list.clearSelection()
    
    def get_selected_y_columns(self):
        """Get list of selected ycols"""
        if self.multi_y_check.isChecked():
            selected_items = self.y_columns_list.selectedItems()
            return [item.text() for item in selected_items]
        else:
            y_col_text = self.y_column.currentText()
            return [y_col_text] if y_col_text else []
    
    def choose_bg_color(self) -> None:
        """Open color picker for background"""
        color = QColorDialog.getColor(QColor(self.bg_color), self)
        if color.isValid():
            self.bg_color = color.name()
            self.bg_color_label.setText(self.bg_color)
            self.bg_color_button.updateColors(base_color_hex=self.bg_color)

    def choose_face_color(self) -> None:
        """Open the color picker tool for the face of the plotting axes"""
        color = QColorDialog.getColor(QColor(self.face_color), self)
        if color.isValid():
            self.face_color = color.name()
            self.face_color_label.setText(self.face_color)
            self.face_color_button.updateColors(base_color_hex=self.face_color)

    def toggle_line_selector(self) -> None:
        """Show/enable line selection"""
        is_enabled = self.multiline_custom_check.isChecked()
        self.line_selector_label.setVisible(is_enabled)
        self.line_selector_combo.setVisible(is_enabled)
        self.save_line_custom_button.setVisible(is_enabled)

        if is_enabled:
            self.update_line_selector()
    
    def save_line_customization(self) -> None:
        """Save current settings for a line"""
        if not self.multiline_custom_check.isChecked():
            return
        
        line_name = self.line_selector_combo.currentText()
        if not line_name:
            return
        
        linestyle_map = {'Solid': '-', 'Dashed': '--', 'Dash-dot': '-.', 'Dotted': ':'}
        linestyle_val = linestyle_map.get(self.linestyle_combo.currentText(), '-')

        # Store customizations
        self.line_customizations[line_name] = {
            'linewidth': self.linewidth_spin.value(),
            'linestyle': linestyle_val,
            'color': self.line_color,
            'marker': self.marker_combo.currentText(),
            'markersize': self.marker_size_spin.value(),
            'markerfacecolor': self.marker_color,
            'markeredgecolor': self.marker_edge_color,
            'markeredgewidth': self.marker_edge_width_spin.value(),
            'alpha': self.alpha_slider.value() / 100.0,
        }

        self.status_bar.log(f"Saved customization for: {line_name}")
        QMessageBox.information(self, "Saved", f"Settings saved for '{line_name}'.\nClick 'Generate Plot' to apply changes.")

    
    def update_line_selector(self) -> None:
        """Update the line selection with the ucrrent lines in current_ax"""
        self.line_selector_combo.blockSignals(True)
        self.line_selector_combo.clear()

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
                
                self.line_selector_combo.addItem(label, userData=i)
            
        self.line_selector_combo.blockSignals(False)

        # load
        if self.line_selector_combo.count() > 0:
            self.on_line_selected(self.line_selector_combo.currentText())
    
    def on_line_selected(self, line_name):
        """Load settings for a selected line"""
        if not self.multiline_custom_check.isChecked():
            return
        
        if not self.plot_engine.current_ax:
            return
        
        #get line idx
        line_idx = self.line_selector_combo.currentData()
        if line_idx is None:
            return
        
        lines = [l for l in self.plot_engine.current_ax.get_lines() if l.get_gid() not in ["regression_line", "confidence_interval"]]

        if line_idx < len(lines):
            line = lines[line_idx]

            #load current line props
            self.linewidth_spin.blockSignals(True)
            self.linewidth_spin.setValue(line.get_linewidth())
            self.linewidth_spin.blockSignals(False)

            linestyle_map_reverse = {"-": "Solid", "--": "Dashed", "-.": "Dash-dot", ":": "Dotted"}
            current_style = linestyle_map_reverse.get(line.get_linestyle(), "Solid")
            self.linestyle_combo.blockSignals(True)
            self.linestyle_combo.setCurrentText(current_style)
            self.linestyle_combo.blockSignals(False)

            #load color
            color = line.get_color()
            if color:
                self.line_color = to_hex(color)
                self.line_color_label.setText(self.line_color)
                self.line_color_button.updateColors(base_color_hex=self.line_color)

            #load markers
            marker = line.get_marker()
            if marker and marker != "None":
                self.marker_combo.blockSignals(True)
                self.marker_combo.setCurrentText(marker)
                self.marker_combo.blockSignals(False)

                self.marker_size_spin.blockSignals(True)
                self.marker_size_spin.setValue(int(line.get_markersize()))
                self.marker_size_spin.blockSignals(False)
    
    def choose_top_spine_color(self):
        """Open color picker for top spine"""
        color = QColorDialog.getColor(QColor(self.top_spine_color), self)
        if color.isValid():
            self.top_spine_color = color.name()
            self.top_spine_color_label.setText(self.top_spine_color)
            self.top_spine_color_button.updateColors(base_color_hex=self.top_spine_color)
    
    def choose_bottom_spine_color(self):
        """Open color picker for bottom spine"""
        color = QColorDialog.getColor(QColor(self.bottom_spine_color), self)
        if color.isValid():
            self.bottom_spine_color = color.name()
            self.bottom_spine_color_label.setText(self.bottom_spine_color)
            self.bottom_spine_color_button.updateColors(base_color_hex=self.bottom_spine_color)
    
    def choose_left_spine_color(self):
        """Open color picker for left spine"""
        color = QColorDialog.getColor(QColor(self.left_spine_color), self)
        if color.isValid():
            self.left_spine_color = color.name()
            self.left_spine_color_label.setText(self.left_spine_color)
            self.left_spine_color_button.updateColors(base_color_hex=self.left_spine_color)
    
    def choose_right_spine_color(self):
        """Open color picker for right spine"""
        color = QColorDialog.getColor(QColor(self.right_spine_color), self)
        if color.isValid():
            self.right_spine_color = color.name()
            self.right_spine_color_label.setText(self.right_spine_color)
            self.right_spine_color_button.updateColors(base_color_hex=self.right_spine_color)
    
    def preset_all_spines(self):
        """Preset: Show all spines"""
        self.top_spine_visible_check.setChecked(True)
        self.bottom_spine_visible_check.setChecked(True)
        self.left_spine_visible_check.setChecked(True)
        self.right_spine_visible_check.setChecked(True)
        self.status_bar.log("Applied preset: All Spines", "INFO")

    def preset_box_only(self):
        """Preset: Show only left and buttom spines"""
        self.top_spine_visible_check.setChecked(False)
        self.bottom_spine_visible_check.setChecked(True)
        self.left_spine_visible_check.setChecked(True)
        self.right_spine_visible_check.setChecked(False)
        self.status_bar.log("Applied preset: Box Only", "INFO")

    def preset_no_spines(self):
        """Preset: Hide all spines"""
        self.top_spine_visible_check.setChecked(False)
        self.bottom_spine_visible_check.setChecked(False)
        self.left_spine_visible_check.setChecked(False)
        self.right_spine_visible_check.setChecked(False)
        self.status_bar.log("Applied preset: No Spines", "INFO")
    
    def choose_line_color(self) -> None:
        """Open color picker for line color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.line_color = color.name()
            self.line_color_label.setText(self.line_color)
            # Show color preview
            self.line_color_button.updateColors(base_color_hex=self.line_color)
    
    def choose_marker_color(self):
        """Open color picker for marker color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.marker_color = color.name()
            self.marker_color_label.setText(self.marker_color)
            self.marker_color_button.updateColors(base_color_hex=self.marker_color)
    
    def choose_marker_edge_color(self):
        """Open color picker for marker edge color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.marker_edge_color = color.name()
            self.marker_edge_label.setText(self.marker_edge_color)
            self.marker_edge_button.updateColors(base_color_hex=self.marker_edge_color)
    
    def choose_bar_color(self):
        """Open color picker for bar color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bar_color = color.name()
            self.bar_color_label.setText(self.bar_color)
            self.bar_color_button.updateColors(base_color_hex=self.bar_color)
            self._update_bar_customization_live()
    
    def choose_bar_edge_color(self):
        """Open color picker for bar edge color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bar_edge_color = color.name()
            self.bar_edge_label.setText(self.bar_edge_color)
            self.bar_edge_button.updateColors(base_color_hex=self.bar_edge_color)
            self._update_bar_customization_live()
    
    def choose_annotation_color(self):
        """Open color picker for annotation color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.annotation_color = color.name()
            self.annotation_color_label.setText(self.annotation_color)
            self.annotation_color_button.updateColors(base_color_hex=self.annotation_color)
    
    def choose_textbox_bg_color(self):
        """Open color picker for text box background"""
        color = QColorDialog.getColor(QColor(self.textbox_bg_color), self)
        if color.isValid():
            self.textbox_bg_color = color.name()
            self.textbox_bg_label.setText(self.textbox_bg_color)
            self.textbox_bg_button.updateColors(base_color_hex=self.textbox_bg_color)
    
    def choose_legend_bg_color(self):
        """Open color picker for legend background"""
        color = QColorDialog.getColor(QColor(self.legend_bg_color), self)
        if color.isValid():
            self.legend_bg_color = color.name()
            self.legend_bg_label.setText(self.legend_bg_color)
            self.legend_bg_button.updateColors(base_color_hex=self.legend_bg_color)
    
    def choose_legend_edge_color(self):
        """Open color picker for legend edge color"""
        color = QColorDialog.getColor(QColor(self.legend_edge_color), self)
        if color.isValid():
            self.legend_edge_color = color.name()
            self.legend_edge_label.setText(self.legend_edge_color)
            self.legend_edge_button.updateColors(base_color_hex=self.legend_edge_color)
    
    def add_annotation(self):
        """Add text annotation to plot"""
        text = self.annotation_text.text().strip()
        if not text:
            QMessageBox.warning(self, "Warning", "Please enter annotation text")
            return
        
        annotation = {
            'text': text,
            'x': self.annotation_x_spin.value(),
            'y': self.annotation_y_spin.value(),
            'fontsize': self.annotation_fontsize_spin.value(),
            'color': self.annotation_color
        }
        
        self.annotations.append(annotation)
        self.annotations_list.addItem(f"{text} @ ({annotation['x']:.2f}, {annotation['y']:.2f})")
        self.annotation_text.clear()
        self.status_bar.log(f"Added annotation: {text}")
    
    def on_annotation_selected(self, item):
        """Handle annotation selection"""
        index = self.annotations_list.row(item)
        if 0 <= index < len(self.annotations):
            ann = self.annotations[index]
            self.annotation_text.setText(ann['text'])
            self.annotation_x_spin.setValue(ann['x'])
            self.annotation_y_spin.setValue(ann['y'])
            self.annotation_fontsize_spin.setValue(ann['fontsize'])
            self.annotation_color = ann['color']
            self.annotation_color_label.setText(self.annotation_color)
    
    def clear_annotations(self):
        """Clear all annotations"""
        self.annotations.clear()
        self.annotations_list.clear()
        self.annotation_text.clear()
        self.status_bar.log("Cleared all annotations")
    
    def update_column_combo(self):
        """Update column ComboBoxes with available columns"""
        if self.data_handler.df is None or len(self.data_handler.df.columns) == 0:
            return
        
        columns = list(self.data_handler.df.columns)
        self.quick_filter_input.set_columns(columns)

        # Preserve the current selection
        current_x = self.x_column.currentText()
        current_y = self.y_column.currentText()
        current_hue = self.hue_column.currentText()
        current_secondary_y = self.secondary_y_column.currentText()
        current_auto_annoate = self.auto_annotate_col_combo.currentText()
        current_multi_y = []
        if self.multi_y_check.isChecked():
            current_multi_y = [item.text() for item in self.y_columns_list.selectedItems()]

        # Block signals to prevent triggering callbacks
        self.x_column.blockSignals(True)
        self.y_column.blockSignals(True)
        self.hue_column.blockSignals(True)
        self.secondary_y_column.blockSignals(True)
        self.y_columns_list.blockSignals(True)
        self.auto_annotate_col_combo.blockSignals(True)
        
        #update xcol
        self.x_column.clear()
        self.x_column.addItems(columns)
        if current_x in columns:
            self.x_column.setCurrentText(current_x)

        #update singleular ycol
        self.y_column.clear()
        self.y_column.addItems(columns)
        if current_y in columns:
            self.y_column.setCurrentText(current_y)

        #update secondary y col
        self.secondary_y_column.clear()
        self.secondary_y_column.addItems(columns)
        if current_secondary_y in columns:
            self.secondary_y_column.setCurrentText(current_secondary_y)

        #update more ycols
        self.y_columns_list.clear()
        for col in columns:
            self.y_columns_list.addItem(col)
            if col in current_multi_y:
                item = self.y_columns_list.item(self.y_columns_list.count() - 1)
                item.setSelected(True)
        
        #update hue
        self.hue_column.clear()
        self.hue_column.addItem("None")
        self.hue_column.addItems(columns)
        if current_hue in columns:
            self.hue_column.setCurrentText(current_hue)
        else:
            self.hue_column.setCurrentIndex(0)

        #update auto annotations
        self.auto_annotate_col_combo.clear()
        self.auto_annotate_col_combo.addItem("Default (Y-value)")
        self.auto_annotate_col_combo.addItems(columns)

        if current_auto_annoate in columns:
            self.auto_annotate_col_combo.setCurrentText(current_auto_annoate)
        elif current_auto_annoate == "Default (Y-value)":
            self.auto_annotate_col_combo.setCurrentIndex(0)
        
        # Unblock signals
        self.x_column.blockSignals(False)
        self.y_column.blockSignals(False)
        self.hue_column.blockSignals(False)
        self.secondary_y_column.blockSignals(False)
        self.y_columns_list.blockSignals(False)
        self.auto_annotate_col_combo.blockSignals(False)
    
    def toggle_table_controls(self):
        """Enable and disable table controls for the user"""
        enabled = self.table_enable_check.isChecked()
        self.table_type_combo.setEnabled(enabled)
        self.table_type_combo.setVisible(enabled)
        self.table_location_combo.setEnabled(enabled)
        self.table_location_combo.setVisible(enabled)

        self.table_auto_font_size_check.setEnabled(enabled)
        self.table_scale_spin.setEnabled(enabled)
        self.table_scale_spin.setVisible(enabled)

        self.table_font_size_spin.setEnabled(enabled and not self.table_auto_font_size_check.isChecked())
        self.table_font_size_spin.setVisible(enabled and not self.table_auto_font_size_check.isChecked())
    
    def toggle_table_font_controls(self):
        self.table_font_size_spin.setEnabled(not self.table_auto_font_size_check.isChecked())
        self.table_font_size_spin.setVisible(not self.table_auto_font_size_check.isChecked())

    def _apply_table(self):
        """Generate the table and add it to the plot"""
        if not self.table_enable_check.isChecked():
            return
        
        df = self.get_active_dataframe()
        if df is None:
            return
        
        try:
            table_type = self.table_type_combo.currentText()
            x_col = self.x_column.currentText()
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
            
            loc = self.table_location_combo.currentText()
            auto_font = self.table_auto_font_size_check.isChecked()
            fontsize = self.table_font_size_spin.value()
            scale = self.table_scale_spin.value()

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
        self.description_label.setText(description)


        #CONTROL FOR THE VISIBLE CUSTOMIZATIONS IN ADVANCED TAB. i think i need to add more
        if plot_type != "Histogram" and plot_type != "Bar":
            self.histogram_group.setVisible(False)
            self.bar_group.setVisible(False)
        else:
            if plot_type == "Histogram":
                self.histogram_group.setVisible(True)
                self.bar_group.setVisible(True)
            elif plot_type == "Bar":
                self.histogram_group.setVisible(False)
                self.bar_group.setVisible(True)

        if plot_type != "Pie":
            self.pie_group.setVisible(False)
        else:
            self.pie_group.setVisible(True)

        if plot_type != "Scatter":
            self.scatter_group.setVisible(False)
        else:
            self.scatter_group.setVisible(True)

        


        #plots with multiple ycols
        multi_y_supported = ["Line", "Bar", "Area", "Box", "Stackplot", "Eventplot", "Contour", "Contourf", "Barbs", "Quiver", "Streamplot", "Tricontour", "Tricontourf", "Tripcolor", "Triplot"]

        #enabled based on plottype
        if plot_type in multi_y_supported:
            self.multi_y_check.setEnabled(True)
            self.multi_y_check.setToolTip("")
        else:
            self.multi_y_check.setEnabled(False)
            self.multi_y_check.setChecked(False)
            self.multi_y_check.setToolTip(f"{plot_type} plots do not support multiple y columns")
        
        #Disbale plots with no dual yaxis support
        dual_axis_supported = ["Line", "Bar", "Scatter", "Area"]
        if plot_type in dual_axis_supported:
            self.secondary_y_check.setEnabled(True)
        else:
            self.secondary_y_check.setChecked(False)
            self.secondary_y_check.setEnabled(False)

        #disable hue for certain plots
        plots_without_hue: list[str] = [
            "Heatmap", "Pie", "Histogram", "KDE", "Count Plot", "Stackplot", "Eventplot",
            "Image Show (imshow)", "pcolormesh", "Contour", "Contourf", "Tricontour",
            "Tricontourf", "Tripcolor", "Triplot", "2D Histogram", "ECDF", "Stairs", "Stem",
            "Barbs", "Quiver", "Streamplot", "GeoSpatial"
        ]
        self.hue_column.setEnabled(plot_type not in plots_without_hue)

        if plot_type in plots_without_hue:
            self.hue_column.setCurrentText("None")

        #disable flipping axes on certain plots
        incompatible_plots: list[str] = [
            "Histogram", "Pie", "Heatmap", "KDE", "Stackplot", "Eventplot",
            "Image Show (imshow)", "pcolormesh", "Contour", "Contourf", "Barbs", "Quiver",
            "Streamplot", "Tricontour", "Tricontourf", "Tripcolor", "Triplot", "2D Histogram", "ECDF", "GeoSpatial"
        ]
        self.flip_axes_check.setEnabled(plot_type not in incompatible_plots)
        if plot_type in incompatible_plots:
            self.flip_axes_check.setChecked(False)

    def on_data_changed(self):
        """Handle data column selection change"""
        self.status_bar.log("Data selection changed")

    def toggle_datetime_format(self):
        """Enabled/disable formating ctrsl for datetime"""
        is_enabled = self.custom_datetime_check.isChecked()
        self.x_datetime_format_combo.setEnabled(is_enabled)
        self.x_datetime_format_combo.setVisible(is_enabled)
        self.format_x_datetime_label.setVisible(is_enabled)
        self.custom_x_axis_format_label.setVisible(is_enabled)
        self.x_custom_datetime_input.setVisible(is_enabled)

        self.y_datetime_format_combo.setEnabled(is_enabled)
        self.y_datetime_format_combo.setVisible(is_enabled)
        self.format_y_datetime_label.setVisible(is_enabled)
        self.custom_y_axis_format_label.setVisible(is_enabled)
        self.y_custom_datetime_format_input.setVisible(is_enabled)

        self.format_help.setVisible(is_enabled)

        #enable the custom input if custom is selected from the box
        if is_enabled:
            self.x_custom_datetime_input.setEnabled(self.x_datetime_format_combo.currentText() == "Custom")
            self.x_custom_datetime_input.setEnabled(self.y_datetime_format_combo.currentText() == "Custom")
    
    def on_x_datetime_format_changed(self, text):
        """Handle x-axis format change"""
        self.x_custom_datetime_input.setEnabled(text == "Custom")
    
    def on_y_datetime_format_changed(self, text) -> None:
        """Handle y-axis format change"""
        self.x_custom_datetime_input.setEnabled(text == "Custom")
    
    def generate_plot(self):
        """Generate plot based on current settings"""
        if not self._validate_data_loaded():
            return

        # Get data configuration
        current_subplot_index, frozen_config = self._get_subplot_config()
        active_df, x_col, y_cols, hue, subset_name, quick_filter = self._resolve_data_config(current_subplot_index, frozen_config)

        if not self._validate_active_dataframe(active_df):
            return
        
        plot_type = self.current_plot_type_name

        # Do a collection of params to cache to the plot signature.
        current_signature = (
            id(active_df),
            active_df.shape,
            plot_type,
            tuple(y_cols) if y_cols else None,
            hue,
            subset_name,
            self.flip_axes_check.isChecked(),
            self.histogram_bins_spin.value() if plot_type == "Histogram" else None,
            self.pie_start_angle_spin.value() if plot_type == "Pie" else None,
            self.pie_explode_check.isChecked() if plot_type == "Pie" else None,
            self.geo_scheme_combo.currentText() if plot_type == "GeoSpatial" else None,
            self.geo_k_spin.value() if plot_type == "GeoSpatial" else None
        )
        keep_data = (self._last_plot_signature == current_signature) and not self.use_plotly_check.isChecked()
        self._last_plot_signature = current_signature
        
        active_df = active_df.copy()
        # Apply a quick filter if set
        if quick_filter:
            active_df = self._apply_quick_filter(active_df, quick_filter)
            if active_df is None:
                return

        # Handle the plotly backend
        if self.use_plotly_check.isChecked():
            self._generate_plotly_plot(active_df, plot_type, x_col, y_cols, hue)
            return

        if not keep_data:
            # Sample data if needed
            active_df = self._sample_data_if_needed(active_df, plot_type)
            
            #Convert datetime columns
            self._convert_datetime_columns(active_df, x_col, y_cols)
        else:
            self.status_bar.log("Using cached data to render plot", "INFO")

        # Generate main plot
        self._generate_main_plot(
            active_df, plot_type, x_col, y_cols, hue, subset_name, current_subplot_index, quick_filter, keep_data=keep_data
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
        current_subplot_index = self.active_subplot_combo.currentIndex()
        if current_subplot_index < 0:
            current_subplot_index = 0

        frozen_config = None
        if self.freeze_data_check.isChecked() and self.add_subplots_check.isChecked():
            if current_subplot_index in self.subplot_data_configs:
                frozen_config = self.subplot_data_configs[current_subplot_index]

        return current_subplot_index, frozen_config

    def _resolve_data_config(self, current_subplot_index, frozen_config):
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
            x_col = self.x_column.currentText()
            y_cols = self.get_selected_y_columns()
            hue = (self.hue_column.currentText() if self.hue_column.currentText() != "None" else None)
            subset_name = (self.subset_combo.currentData() if self.use_subset_check.isChecked() else None)
            quick_filter = self.quick_filter_input.text().strip()

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
                    self.status_bar.log(f"Subset Manager not initialized, using full dataset", "WARNING")
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
            
            html_content = self.plot_engine.generate_plotly_plot(
                active_df,
                plot_type,
                x_col,
                y_cols,
                **kwargs
            )

            if hasattr(self, "web_view") and hasattr(self.web_view, "setHtml"):
                self.web_view.setHtml(html_content)
                self.status_bar.log(f"{plot_type} plot generated with plotly")
            else:
                self.status_bar.log(f"WebEngineView not available", "ERROR")
        
        except Exception as PlotlyFetchError:
            self.status_bar.log(f"Plotting {plot_type} using plotly has failed: {str(PlotlyFetchError)}", "ERROR")
            QMessageBox.critical(self, "Plotly Plotting Error", str(PlotlyFetchError))
            traceback.print_exc()
    
    def _build_plotly_kwargs(self, plot_type, x_col, y_cols, hue):
        """Build kwargs for plotly plot"""
        kwargs = {
            "title": self.title_input.text() or f"{plot_type} plot",
            "xlabel": self.xlabel_input.text() or x_col,
            "ylabel": self.ylabel_input.text() or (y_cols[0] if y_cols else ""),
            "hue": hue,
            "show_regression": self.regression_line_check.isChecked(),
            "horizontal": self.flip_axes_check.isChecked()
        }

        if plot_type == "Histogram":
            kwargs["bins"] = self.histogram_bins_spin.value()
            kwargs["show_kde"] = self.histogram_show_kde_check.isChecked()

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
    
    def _generate_main_plot(self, active_df, plot_type, x_col, y_cols, hue, subset_name, current_subplot_index, quick_filter="", keep_data=False):
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
            axes_flipped = self.flip_axes_check.isChecked()
            font_family = self.font_family_combo.currentFont().family()

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
            self._finalize_plot(current_subplot_index, x_col, y_cols, hue, subset_name, quick_filter)

            # Log
            if not keep_data:
                self._log_plot_message(
                    plot_type, x_col, y_cols, hue, subset_name, active_df, quick_filter
                )

            self._update_progress(progress_dialog, 100, "Complete")
            if progress_dialog:
                QTimer.singleShot(300, progress_dialog.accept)

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
            "title": self.title_input.text() or plot_type,
            "xlabel": self.xlabel_input.text() or x_col,
            "ylabel": self.ylabel_input.text() or y_label_text,
            "legend": self.legend_check.isChecked()
        }

        # Add secondary y axis
        if self.secondary_y_check.isChecked() and self.secondary_y_check.isEnabled():
            general_kwargs["secondary_y"] = self.secondary_y_column.currentText()
            general_kwargs["secondary_plot_type"] = self.secondary_plot_type_combo.currentText()
        
        cmap = self.palette_combo.currentText()
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
        scheme_text = self.geo_scheme_combo.currentText()
        hatch_text = self.geo_hatch_combo.currentText()

        target_crs_input = getattr(self, "geo_target_crs_input", None)
        target_crs = target_crs_input.text() if target_crs_input else None

        basemap_check = getattr(self, "geo_basemap_check", None)
        add_basemap = basemap_check.isChecked() if basemap_check else False

        basemap_combo = getattr(self, "geo_basemap_style_combo", None)
        basemap_source = basemap_combo.currentText() if basemap_combo else "OpenStreetMap"

        kwargs = {
            "scheme": scheme_text if scheme_text != "None" else None,
            "k": self.geo_k_spin.value(),
            "cmap": self.palette_combo.currentText(),
            "legend": self.geo_legend_check.isChecked(),
            "legend_kwds": {
                "loc": "best",
                "orientation": self.geo_legend_loc_combo.currentText()
            },
            "use_divider": self.geo_use_divider_check.isChecked(),
            "cax_enabled": self.geo_cax_check.isChecked(),
            "axis_off": self.geo_axis_off_check.isChecked(),
            "missing_kwds": {
                "color": self.geo_missing_color,
                "label": self.geo_missing_label_input.text(),
                "hatch": hatch_text if hatch_text != "None" else None
            },
            "edgecolor": self.geo_edge_color,
            "linewidth": self.geo_linewidth_spin.value(),
            "target_crs": target_crs,
            "add_basemap": add_basemap,
            "basemap_source": basemap_source
        }
        if self.geo_boundary_check.isChecked():
            kwargs["facecolor"] = "none"
        
        return kwargs
    
    def _setup_plot_figure(self, clear: bool = True):
        """Setup plot figure with current settings"""
        if clear:
            self.plot_engine.clear_current_axis()
            
        self.plot_engine.current_figure.set_size_inches(self.width_spin.value(), self.height_spin.value())

        self.plot_engine.current_figure.set_dpi(self.dpi_spin.value())
        self.plot_engine.current_figure.set_facecolor(self.bg_color)

    def _apply_plot_style(self):
        """Apply plotting style"""
        try:
            plt.style.use(self.style_combo.currentText())
            self.plot_engine.current_figure.set_facecolor(self.bg_color)
            self.plot_engine.current_ax.set_facecolor(self.face_color)
        except Exception as ApplyPlotStyleError:
            self.status_bar.log(f"Could not apply plotting style. {str(ApplyPlotStyleError)}", "WARNING")
            self.plot_engine.current_ax.set_facecolor(self.face_color)
    
    def _set_axis_limits_and_scales(self):
        """Set axis limits and scales"""
        if not self.x_auto_check.isChecked():
            self.plot_engine.current_ax.set_xlim(
                self.x_min_spin.value(), self.x_max_spin.value()
            )
        if not self.y_auto_check.isChecked():
            self.plot_engine.current_ax.set_ylim(
                self.y_min_spin.value(), self.y_max_spin.value()
            )
        
        self.plot_engine.current_ax.set_xscale(self.x_scale_combo.currentText())
        self.plot_engine.current_ax.set_yscale(self.y_scale_combo.currentText())

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
            self.plot_engine.current_ax.xaxis.set_major_locator(MaxNLocator(nbins=self.x_max_ticks_spin.value()))
            self.plot_engine.current_ax.yaxis.set_major_locator(MaxNLocator(nbins=self.y_max_ticks_spin.value()))
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

    def _apply_legend_and_grid(self, general_kwargs, font_family):
        """Apply legend and gridlines"""
        if general_kwargs.get("legend", True):
            self._apply_legend(font_family)
        elif self.plot_engine.current_ax.get_legend():
            self.plot_engine.current_ax.get_legend().set_visible(False)
        
        if self.grid_check.isChecked():
            self._apply_gridlines_customizations()
        else:
            self.plot_engine.current_ax.grid(False)
    
    def _finalize_plot(self, current_subplot_index, x_col, y_cols, hue, subset_name, quick_filter) -> None:
        """Finalize plot and save configs"""
        try:
            if self.tight_layout_check.isChecked():
                self.plot_engine.current_figure.tight_layout()
        except Exception as TightLayoutError:
            self.status_bar.log(f"Tight layout not applied due to error: {str(TightLayoutError)}", "ERROR")
        
        self.canvas.draw()

        if self.add_subplots_check.isChecked():
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

        if self.use_subset_check.isChecked() and subset_name:
            plot_details["subset"] = subset_name
            plot_details["subset_rows"] = len(active_df)
            plot_details["total_rows"] = len(self.data_handler.df)
        
        status_message = f"{plot_type} plot created"
        if self.use_subset_check.isChecked() and subset_name:
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
        if self.title_check.isChecked():
            self.plot_engine.current_ax.set_title("", loc='left')
            self.plot_engine.current_ax.set_title("", loc='center')
            self.plot_engine.current_ax.set_title("", loc='right')

            title_text = self.title_input.text() or general_kwargs.get("title", "Plot")
            self.plot_engine.current_ax.set_title(
                title_text, 
                fontsize=self.title_size_spin.value(), 
                fontweight=self.title_weight_combo.currentText(), 
                fontfamily=font_family,
                loc=self.title_position_combo.currentText()
            )
        else:
            #clear title
            self.plot_engine.current_ax.set_title("")
            self.plot_engine.current_ax.set_title("", loc='left')
            self.plot_engine.current_ax.set_title("", loc='right')
        
        #xlabel
        if self.xlabel_check.isChecked():
            xlabel_text = self.xlabel_input.text() or general_kwargs.get("xlabel", "")
            self.plot_engine.current_ax.set_xlabel(
                xlabel_text, 
                fontsize=self.xlabel_size_spin.value(), 
                fontweight=self.xlabel_weight_combo.currentText(), 
                fontfamily=font_family
            )
        else:
            self.plot_engine.current_ax.set_xlabel("")
        
        # ylabel
        if self.ylabel_check.isChecked():
            ylabel_text = self.ylabel_input.text() or general_kwargs.get("ylabel", "")
            self.plot_engine.current_ax.set_ylabel(
                ylabel_text, 
                fontsize=self.ylabel_size_spin.value(), 
                fontweight=self.ylabel_weight_combo.currentText(), 
                fontfamily=font_family
            )
        else:
            self.plot_engine.current_ax.set_ylabel("")

    
    def _apply_plot_customizations(self):
        """Apply customizations to lines, markers, bars etc"""
        #globals
        alpha = self.alpha_slider.value() / 100.0
        linewidth = self.linewidth_spin.value()
        linestyle = self.linestyle_combo.currentText()
        marker = self.marker_combo.currentText()
        marker_size = self.marker_size_spin.value()
        line_color = self.line_color
        marker_color = self.marker_color
        marker_edge_color = self.marker_edge_color
        marker_edge_width = self.marker_edge_width_spin.value()
        bar_color = self.bar_color
        bar_edge_color = self.bar_edge_color
        bar_edge_width = self.bar_edge_width_spin.value()

        linestyle_map = {'Solid': '-', 'Dashed': '--', 'Dash-dot': '-.', 'Dotted': ':'}
        linestyle_val = linestyle_map.get(linestyle, linestyle)
        marker_val = "None" if marker == "None" else marker

        # customize lines
        if self.multiline_custom_check.isChecked():
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
        if self.multibar_custom_check.isChecked():
            self.update_bar_selector()

            for i in range(self.bar_selector_combo.count()):
                bar_name = self.bar_selector_combo.itemText(i)
                container = self.bar_selector_combo.itemData(i)

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
        if not self.legend_check.isChecked():
            if self.plot_engine.current_ax.get_legend():
                self.plot_engine.current_ax.get_legend().set_visible(False)
            return
            
        # Check if there's anything to make a legend for
        handles, labels = self.plot_engine.current_ax.get_legend_handles_labels()
        if not handles:
            return

        legend_kwargs = {
            "loc": self.legend_loc_combo.currentText(),
            "fontsize": self.legend_size_spin.value(),
            "ncol": self.legend_columns_spin.value(),
            "columnspacing": self.legend_colspace_spin.value(),
            "frameon": self.legend_frame_check.isChecked(),
            "fancybox": self.legend_fancybox_check.isChecked(),
            "shadow": self.legend_shadow_check.isChecked(),
            "framealpha": self.legend_alpha_slider.value() / 100.0,
            "facecolor": self.legend_bg_color,
            "edgecolor": self.legend_edge_color
        }

        try:
            legend = self.plot_engine.current_ax.legend(**legend_kwargs)

            # set edge width
            if legend and legend.get_frame():
                legend.get_frame().set_linewidth(self.legend_edge_width_spin.value())
            
            #set title
            if self.legend_title_input.text().strip():
                legend.set_title(self.legend_title_input.text().strip())
            
            # apply font
            for text in legend.get_texts():
                text.set_fontfamily(font_family)
            
            if legend.get_title():
                legend.get_title().set_fontfamily(font_family)
        except Exception as ApplyLegendError:
            self.status_bar.log(f"Failed to apply legend: {ApplyLegendError}", "WARNING")

    
    def _apply_annotations(self, df=None, x_col=None, y_cols=None):
        """Apply text annotations"""

        #manual annotations
        for ann in self.annotations:
            self.plot_engine.current_ax.text(
                ann["x"], ann["y"], ann["text"],
                transform=self.plot_engine.current_ax.transAxes,
                fontsize=ann["fontsize"],
                color=ann["color"],
                ha="center", va="center",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5)
            )
        
        #auto annotations based on datapoints
        if self.auto_annotate_check.isChecked() and df is not None and x_col and y_cols:
            try:
                label_choice = self.auto_annotate_col_combo.currentText()
                is_flipped = self.flip_axes_check.isChecked()

                MAX_POINTS = 2000
                if len(df) > MAX_POINTS:
                    self.status_bar.log(f"Auto-annotations is limited to first {MAX_POINTS} points for performance")
                    df_to_annotate = df.iloc[:MAX_POINTS]
                else:
                    df_to_annotate = df

                y_col_target = y_cols[0]
                font_size = self.annotation_fontsize_spin.value()
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
                            color=font_color if font_color else "black"
                        )
                    else:
                        self.plot_engine.current_ax.annotate(
                            text,
                            (x_val, y_val),
                            xytext=(5,5),
                            textcoords="offset points",
                            fontsize=font_size,
                            color=font_color if font_color else "black"
                        )
            except Exception as ApplyAnnotationsError:
                self.status_bar.log(f"Error applying annotations to data points: {str(ApplyAnnotationsError)}", "ERROR")
                print(f"Auto-annotation error: {str(ApplyAnnotationsError)}")

    def _apply_gridlines_customizations(self) -> None:
        """Apply gridlines customizations"""
        if not self.grid_check.isChecked():
            self.plot_engine.current_ax.grid(False)
            return
        
        # Ensure grid is on, but we'll style it below
        self.plot_engine.current_ax.grid(True)
        
        if self.independent_grid_check.isChecked():
            #  INDEPENDENT 
            
            # Helper to map text to symbol
            grid_style_map = {
                "Solid (-)": "-",
                "Dashed (--)": "--",
                "Dash-dot (-.)": "-.",
                "Dotted (:)": ":"
            }
            
            # X-Axis Major
            style = grid_style_map.get(self.x_major_grid_style_combo.currentText(), "-")
            self.plot_engine.current_ax.grid(
                visible=self.x_major_grid_check.isChecked(), which="major", axis="x",
                linestyle=style,
                linewidth=self.x_major_grid_linewidth_spin.value(),
                color=self.x_major_grid_color,
                alpha=self.x_major_grid_alpha_slider.value() / 100.0
            )
            
            # X-Axis Minor
            if self.x_minor_grid_check.isChecked():
                self.plot_engine.current_ax.minorticks_on()
                style = grid_style_map.get(self.x_minor_grid_style_combo.currentText(), ":")
                self.plot_engine.current_ax.grid(
                    visible=True, which="minor", axis="x",
                    linestyle=style,
                    linewidth=self.x_minor_grid_linewidth_spin.value(),
                    color=self.x_minor_grid_color,
                    alpha=self.x_minor_grid_alpha_slider.value() / 100.0
                )
            else:
                self.plot_engine.current_ax.grid(visible=False, which="minor", axis="x")

            # Y-Axis Major
            style = grid_style_map.get(self.y_major_grid_style_combo.currentText(), "-")
            self.plot_engine.current_ax.grid(
                visible=self.y_major_grid_check.isChecked(), which="major", axis="y",
                linestyle=style,
                linewidth=self.y_major_grid_linewidth_spin.value(),
                color=self.y_major_grid_color,
                alpha=self.y_major_grid_alpha_slider.value() / 100.0
            )

            # Y-Axis Minor
            if self.y_minor_grid_check.isChecked():
                self.plot_engine.current_ax.minorticks_on()
                style = grid_style_map.get(self.y_minor_grid_style_combo.currentText(), ":")
                self.plot_engine.current_ax.grid(
                    visible=True, which="minor", axis="y",
                    linestyle=style,
                    linewidth=self.y_minor_grid_linewidth_spin.value(),
                    color=self.y_minor_grid_color,
                    alpha=self.y_minor_grid_alpha_slider.value() / 100.0
                )
            else:
                self.plot_engine.current_ax.grid(visible=False, which="minor", axis="y")
        
        else:
            #  GLOBAL 
            which_type = self.grid_which_type_combo.currentText()
            axis = self.grid_axis_combo.currentText()

            if which_type in ["minor", "both"]:
                self.plot_engine.current_ax.minorticks_on()
            
            # Apply global settings
            self.plot_engine.current_ax.grid(
                visible=True,
                which=which_type,
                axis=axis,
                alpha=self.global_grid_alpha_slider.value() / 100.0
                # Use style-defined defaults for color/linestyle/width
            )

    
    def _apply_tick_customization(self):
        """Apply tick label customization"""
        #major ticks
        self.plot_engine.current_ax.tick_params(
            axis="x",
            labelsize=self.xtick_label_size_spin.value(),
            direction=self.x_major_tick_direction_combo.currentText(),
            width=self.x_major_tick_width_spin.value(),
            which="major"
        )
        self.plot_engine.current_ax.tick_params(
            axis="y",
            labelsize=self.ytick_label_size_spin.value(),
            direction=self.y_major_tick_direction_combo.currentText(),
            width=self.y_major_tick_width_spin.value(),
            which="major"
        )

        #xaxis position
        if self.x_top_axis_check.isChecked():
            self.plot_engine.current_ax.xaxis.tick_top()
            self.plot_engine.current_ax.xaxis.set_label_position("top")
        else:
            self.plot_engine.current_ax.xaxis.tick_bottom()
            self.plot_engine.current_ax.xaxis.set_label_position("bottom")


        #minor tickmarks
        if self.x_show_minor_ticks_check.isChecked():
            self.plot_engine.current_ax.minorticks_on()
            self.plot_engine.current_ax.tick_params(
                axis="x",
                which="minor",
                direction=self.x_minor_tick_direction_combo.currentText(),
                width=self.x_minor_tick_width_spin.value()
            )
        
        if self.y_show_minor_ticks_check.isChecked():
            self.plot_engine.current_ax.minorticks_on()
            self.plot_engine.current_ax.tick_params(
                axis="y",
                which="minor",
                direction=self.y_minor_tick_direction_combo.currentText(),
                width=self.y_minor_tick_width_spin.value()
            )
        
        #add formatts if user specified
        try:
            x_unit_str = self.x_display_units_combo.currentText()
            if x_unit_str != "None":
                x_formatter = self._create_axis_formatter(x_unit_str)
                if x_formatter:
                    self.plot_engine.current_ax.xaxis.set_major_formatter(x_formatter)
            
            y_unit_str = self.y_display_units_combo.currentText()
            if y_unit_str != "None":
                y_formatter = self._create_axis_formatter(y_unit_str)
                if y_formatter:
                    self.plot_engine.current_ax.yaxis.set_major_formatter(y_formatter)
        except Exception as ApplyDisplayUnitsError:
            self.status_bar.log(f"Failed to apply display units: {str(ApplyDisplayUnitsError)}", "WARNING")

        
        #rotation
        plt.setp(self.plot_engine.current_ax.get_xticklabels(), rotation=self.xtick_rotation_spin.value())
        plt.setp(self.plot_engine.current_ax.get_yticklabels(), rotation=self.ytick_rotation_spin.value())

        #axiss inversion
        if self.x_invert_axis_check.isChecked():
            if not self.plot_engine.current_ax.xaxis_inverted():
                self.plot_engine.current_ax.invert_xaxis()
        else:
            if self.plot_engine.current_ax.xaxis_inverted():
                self.plot_engine.current_ax.invert_xaxis()
        
        if self.y_invert_axis_check.isChecked():
            if not self.plot_engine.current_ax.yaxis_inverted():
                self.plot_engine.current_ax.invert_yaxis()
        else:
            if self.plot_engine.current_ax.yaxis_inverted():
                self.plot_engine.current_ax.invert_yaxis()

    def _apply_textbox(self):
        """Apply textbox"""
        if self.textbox_enable_check.isChecked():
            textbox_text = self.textbox_content.text().strip()
            if textbox_text:
                style_map = {
                    "Rounded": "round",
                    "Square": "square",
                    "round,pad=1": "round,pad=1",
                    "round4,pad=0.5": "round4,pad=0.5"
                }
                style = style_map.get(self.textbox_style_combo.currentText(), "round")

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

                position_name = self.textbox_position_combo.currentText()
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
            is_individual = self.individual_spines_check.isChecked()
            
            # Prepare Global settings
            global_width = self.global_spine_width_spin.value()
            global_color = self.global_spine_color

            spine_map = [
                ("top", self.top_spine_visible_check, self.top_spine_width_spin, "top_spine_color"),
                ("bottom", self.bottom_spine_visible_check, self.bottom_spine_width_spin, "bottom_spine_color"),
                ("left", self.left_spine_visible_check, self.left_spine_width_spin, "left_spine_color"),
                ("right", self.right_spine_visible_check, self.right_spine_width_spin, "right_spine_color")
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
        self.plot_engine.clear_plot()

        self.subplot_rows_spin.blockSignals(True)
        self.subplot_cols_spin.blockSignals(True)
        self.active_subplot_combo.blockSignals(True)
        self.quick_filter_input.clear()

        self.subplot_rows_spin.setValue(1)
        self.subplot_cols_spin.setValue(1)
        self.active_subplot_combo.clear()
        self.active_subplot_combo.addItem("Plot 1")

        self.subplot_rows_spin.blockSignals(False)
        self.subplot_cols_spin.blockSignals(False)
        self.active_subplot_combo.blockSignals(False)

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
            
        self.annotations_list.clear()
        
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
    
    def _toggle_secondary_input(self, enabled: bool):
        is_enabled = bool(enabled)

        self.secondary_y_column.setEnabled(is_enabled)
        if hasattr(self, "secondary_plot_type_combo"):
            self.secondary_plot_type_combo.setEnabled(is_enabled)
    
    def load_config(self, config: dict) -> None:
        """Load plot configuration"""
        self.current_config = config

        try:
            #Load the intial plottype 
            if "plot_type" in config:
                self.plot_type.blockSignals(True)
                self._select_plot_in_toolbox(config["plot_type"])
                self.plot_type.blockSignals(False)
                self.on_plot_type_changed(config["plot_type"])
            
            #Load sections
            if "basic" in config: self._load_basic_config(config["basic"])
            if "appearance" in config: self._load_appearance_config(config["appearance"])
            if "axes" in config: self._load_axes_config(config["axes"])
            if "legend" in config: self._load_legend_config(config["legend"])
            if "grid" in config: self._load_grid_config(config["grid"])
            if "advanced" in config: self._load_advanced_config(config["advanced"])
            if "annotations" in config: self._load_annotations_config(config["annotations"])

            self.status_bar.log("Plot Config Loaded", "INFO")
        
        except Exception as LoadConfigError:
            self.status_bar.log(f"Error loading plot config from saved project: {str(LoadConfigError)}", "ERROR")
            traceback.print_exc()

    def _load_basic_config(self, config: dict):
        self.x_column.setCurrentText(config.get("x_column", ""))
        self.quick_filter_input.setText(config.get("quick_filter", ""))

        # Multi Y config
        multi_y = config.get("multi_y_checked", False)
        self.multi_y_check.setChecked(multi_y)
        self.toggle_multi_y()

        y_cols = config.get("y_columns") or []
        if multi_y:
            self.y_columns_list.clearSelection()
            for i in range(self.y_columns_list.count()):
                item = self.y_columns_list.item(i)
                if item.text() in y_cols:
                    item.setSelected(True)
        else:
            if y_cols:
                self.y_column.setCurrentText(y_cols[0])
        
        self.hue_column.setCurrentText(config.get("hue_column", "None"))

        # secondary y config
        sec_y_enabled = config.get("secondary_y_enabled", False)
        self.secondary_y_check.setChecked(sec_y_enabled)
        self._toggle_secondary_inputs(sec_y_enabled)
        if sec_y_enabled:
            self.secondary_y_column.setCurrentText(config.get("secondary_y_column", ""))
            self.secondary_plot_type_combo.setCurrentText(config.get("secondary_plot_type", "Line"))

        # Subsets
        use_subset = config.get("use_subset", False)
        self.use_subset_check.setChecked(use_subset)
        if use_subset:
            subset_name = config.get("subset_name")
            if subset_name:
                index = self.subset_combo.findData(subset_name)
                if index >= 0:
                    self.subset_combo.setCurrentIndex(index)
        self.use_subset()
    
    def _load_appearance_config(self, config: dict):
        # Font
        if "font_family" in config:
            self.font_family_combo.setCurrentFont(QFont(config["font_family"]))
        self.usetex_checkbox.setChecked(config.get("usetext", False))

        # Title
        title_conf = config.get("title", {})
        self.title_check.setChecked(title_conf.get("enabled", False))
        self.title_input.setText(title_conf.get("text", ""))
        self.title_size_spin.setValue(title_conf.get("size", 12))
        self.title_weight_combo.setCurrentText(title_conf.get("weight", "normal"))
        self.title_position_combo.setCurrentText(title_conf.get("location", "center"))

        # Labels
        x_label_conf = config.get("xlabel", {})
        self.xlabel_check.setChecked(x_label_conf.get("enabled", False))
        self.xlabel_input.setText(x_label_conf.get("text", ""))
        self.xlabel_size_spin.setValue(x_label_conf.get("size", 10))
        self.xlabel_weight_combo.setCurrentText(x_label_conf.get("weight", "normal"))

        y_label_conf = config.get("xlabel", {})
        self.ylabel_check.setChecked(y_label_conf.get("enabled", False))
        self.ylabel_input.setText(y_label_conf.get("text", ""))
        self.ylabel_size_spin.setValue(y_label_conf.get("size", 10))
        self.ylabel_weight_combo.setCurrentText(y_label_conf.get("weight", "normal"))

        # Spines
        spines = config.get("spines", {})
        for side, ctrl_check, width_spin, color_attr, btn in [
            ("top", self.top_spine_visible_check, self.top_spine_width_spin, "top_spine_color", self.top_spine_color_button),
            ("bottom", self.bottom_spine_visible_check, self.bottom_spine_width_spin, "bottom_spine_color", self.bottom_spine_color_button),
            ("left", self.left_spine_visible_check, self.left_spine_width_spin, "left_spine_color", self.left_spine_color_button),
            ("right", self.right_spine_visible_check, self.right_spine_width_spin, "right_spine_color", self.right_spine_color_button)
        ]:
            if side in spines:
                s_conf = spines[side]
                ctrl_check.setChecked(s_conf.get("visible", True))
                width_spin.setValue(s_conf.get("width", 1.0))
                color = s_conf.get("color", "black")
                setattr(self, color_attr, color)
                btn.updateColors(base_color_hex=color)
        
        # Figure settings
        fig_conf = config.get("figure", {})
        self.width_spin.setValue(fig_conf.get("width", 10))
        self.height_spin.setValue(fig_conf.get("height", 6))
        self.dpi_spin.setValue(fig_conf.get("dpi", 100))

        if "bg_color" in fig_conf:
            self.bg_color = fig_conf["bg_color"] or "white"
            self.bg_color_label.setText(self.bg_color)
            self.bg_color_button.updateColors(base_color_hex=self.bg_color)
        
        if "face_facecolor" in fig_conf:
            self.face_color = fig_conf["face_facecolor"] or "white"
            self.face_color_label.setText(self.face_color)
            self.face_color_button.updateColors(self.face_color)
        
        self.palette_combo.setCurrentText(fig_conf.get("palette", "viridis"))
        self.tight_layout_check.setChecked(fig_conf.get("tight_layout", True))
        self.style_combo.setCurrentText(fig_conf.get("style", "default"))
    
    def _load_axes_config(self, config: dict):
        # X axis
        x_conf = config.get("x_axis", {})
        self.x_auto_check.setChecked(x_conf.get("auto_limits", True))
        self.x_invert_axis_check.setChecked(x_conf.get("invert", False))
        self.x_top_axis_check.setChecked(x_conf.get("top_axis", False))
        self.x_min_spin.setValue(x_conf.get("min", 0.0))
        self.x_max_spin.setValue(x_conf.get("max", 1.0))
        self.xtick_label_size_spin.setValue(x_conf.get("tick_label_size", 10))
        self.xtick_rotation_spin.setValue(x_conf.get("tick_rotation", 0))
        self.x_max_ticks_spin.setValue(x_conf.get("max_ticks", 10))
        self.x_show_minor_ticks_check.setChecked(x_conf.get("minor_ticks_enabled", False))
        self.x_major_tick_direction_combo.setCurrentText(x_conf.get("major_tick_direction", "out"))
        self.x_major_tick_width_spin.setValue(x_conf.get("major_tick_width", 0.8))
        self.x_minor_tick_direction_combo.setCurrentText(x_conf.get("minor_tick_direction", "out"))
        self.x_minor_tick_width_spin.setValue(x_conf.get("minor_tick_width", 0.6))
        self.x_scale_combo.setCurrentText(x_conf.get("scale", "linear"))
        self.x_display_units_combo.setCurrentText(x_conf.get("display_units", "None"))

        # Y Axis
        y_conf = config.get("y_axis", {})
        self.y_auto_check.setChecked(y_conf.get("auto_limits", True))
        self.y_invert_axis_check.setChecked(y_conf.get("invert", False))
        self.y_min_spin.setValue(y_conf.get("min", 0.0))
        self.y_max_spin.setValue(y_conf.get("max", 1.0))
        self.ytick_label_size_spin.setValue(y_conf.get("tick_label_size", 10))
        self.ytick_rotation_spin.setValue(y_conf.get("tick_rotation", 0))
        self.y_max_ticks_spin.setValue(y_conf.get("max_ticks", 10))
        self.y_show_minor_ticks_check.setChecked(y_conf.get("minor_ticks_enabled", False))
        self.y_major_tick_direction_combo.setCurrentText(y_conf.get("major_tick_direction", "out"))
        self.y_major_tick_width_spin.setValue(y_conf.get("major_tick_width", 0.8))
        self.y_minor_tick_direction_combo.setCurrentText(y_conf.get("minor_tick_direction", "out"))
        self.y_minor_tick_width_spin.setValue(y_conf.get("minor_tick_width", 0.6))
        self.y_scale_combo.setCurrentText(y_conf.get("scale", "linear"))
        self.y_display_units_combo.setCurrentText(y_conf.get("display_units", "None"))

        self.flip_axes_check.setChecked(config.get("flip_axes", False))

        # Datetime
        dt_conf = config.get("datetime", {})
        self.custom_datetime_check.setChecked(dt_conf.get("enabled", False))
        self.x_datetime_format_combo.setCurrentText(dt_conf.get("x_format_preset", "Auto"))
        self.x_custom_datetime_input.setText(dt_conf.get("x_format_custom", ""))
        self.y_datetime_format_combo.setCurrentText(dt_conf.get("y_format_preset", "Auto"))
        self.y_custom_datetime_format_input.setText(dt_conf.get("y_format_custom", ""))
        self.toggle_datetime_format()

    def _load_legend_config(self, config: dict):
        self.legend_check.setChecked(config.get("enabled", True))
        self.legend_loc_combo.setCurrentText(config.get("location", "best"))
        self.legend_title_input.setText(config.get("title", ""))
        self.legend_size_spin.setValue(config.get("font_size", 10))
        self.legend_columns_spin.setValue(config.get("columns", 1))
        self.legend_colspace_spin.setValue(config.get("column_spacing", 0.5))
        self.legend_frame_check.setChecked(config.get("frame", True))
        self.legend_fancybox_check.setChecked(config.get("fancy_box", True))
        self.legend_shadow_check.setChecked(config.get("shadow", False))
        self.legend_edge_width_spin.setValue(config.get("edge_width", 0.8))
        
        self.legend_bg_color = config.get("bg_color") or "white"
        self.legend_bg_label.setText(self.legend_bg_color)
        self.legend_bg_button.updateColors(base_color_hex=self.legend_bg_color)
        
        self.legend_edge_color = config.get("edge_clor") or "black"
        self.legend_edge_label.setText(self.legend_edge_color)
        self.legend_edge_button.updateColors(base_color_hex=self.legend_edge_color)
        
        alpha = config.get("alpha", 0.8)
        self.legend_alpha_slider.setValue(int(alpha * 100))

        self.on_legend_toggle()

    def _load_grid_config(self, config: dict):
        self.grid_check.setChecked(config.get("enabled", False))
        self.independent_grid_check.setChecked(config.get("independent_axes", False))

        # Global settings
        glob = config.get("global", {})
        self.grid_which_type_combo.setCurrentText(glob.get("which", "major"))
        self.grid_axis_combo.setCurrentText(glob.get("axis", "both"))
        self.global_grid_alpha_slider.setValue(int(glob.get("alpha", 0.5) * 100))

        # A function to color buttons correctly
        def load_grid_section(prefix, conf):
            getattr(self, f"{prefix}_grid_check").setChecked(conf.get("enabled", False))
            getattr(self, f"{prefix}_grid_style_combo").setCurrentText(conf.get("style", "-"))
            getattr(self, f"{prefix}_grid_linewidth_spin").setValue(conf.get("width", 0.8))
            getattr(self, f"{prefix}_grid_alpha_slider").setValue(int(conf.get("alpha", 0.5) * 100))

            color = conf.get("color", "gray")
            setattr(self, f"{prefix}_grid_color", color)
            getattr(self, f"{prefix}_grid_color_label").setText(color)
            getattr(self, f"{prefix}_grid_color_button").updateColors(base_color_hex=color)
        
        if "x_major" in config: load_grid_section("x_major", config["x_major"])
        if "x_minor" in config: load_grid_section("x_minor", config["x_minor"])
        if "y_major" in config: load_grid_section("y_major", config["y_major"])
        if "y_minor" in config: load_grid_section("y_minor", config["y_minor"])
        
        self.on_grid_toggle()
    
    def _load_advanced_config(self, config: dict):
        self.multiline_custom_check.setChecked(config.get("multi_line_custom", False))
        self.line_customizations = config.get("line_customizations", {})
        
        gl = config.get("global_line") or {}
        self.linewidth_spin.setValue(gl.get("width", 1.5))
        
        # Reverse map linestyle
        style_map = {'-': 'Solid', '--': 'Dashed', '-.': 'Dash-dot', ':': 'Dotted', 'None': 'None'}
        self.linestyle_combo.setCurrentText(style_map.get(gl.get("style", "-"), "Solid"))
        
        self.line_color = gl.get("color") or "blue"
        self.line_color_label.setText(self.line_color)
        self.line_color_button.updateColors(base_color_hex=self.line_color)
        
        gm = config.get("global_marker") or {}
        self.marker_combo.setCurrentText(gm.get("shape", "None"))
        self.marker_size_spin.setValue(gm.get("size", 6))
        self.marker_edge_width_spin.setValue(gm.get("edge_width", 1.0))
        
        self.marker_color = gm.get("color") or "blue"
        self.marker_color_label.setText(self.marker_color)
        self.marker_color_button.updateColors(base_color_hex=self.marker_color)
        
        self.marker_edge_color = gm.get("edge_color") or "black"
        self.marker_edge_label.setText(self.marker_edge_color)
        self.marker_edge_button.updateColors(base_color_hex=self.marker_edge_color)
        
        self.multibar_custom_check.setChecked(config.get("multi_bar_custom", False))
        self.bar_customizations = config.get("bar_customizations", {})
        
        gb = config.get("global_bar") or {}
        self.bar_width_spin.setValue(gb.get("width", 0.8))
        self.bar_edge_width_spin.setValue(gb.get("edge_width", 1.0))
        
        self.bar_color = gb.get("color") or "blue"
        self.bar_color_label.setText(self.bar_color)
        self.bar_color_button.updateColors(base_color_hex=self.bar_color)
        
        self.bar_edge_color = gb.get("edge_color") or "black"
        self.bar_edge_label.setText(self.bar_edge_color)
        self.bar_edge_button.updateColors(base_color_hex=self.bar_edge_color)
        
        hist = config.get("histogram") or {}
        self.histogram_bins_spin.setValue(hist.get("bins", 30))
        self.histogram_show_normal_check.setChecked(hist.get("show_normal", False))
        self.histogram_show_kde_check.setChecked(hist.get("show_kde", False))
        
        self.alpha_slider.setValue(int(config.get("global_alpha", 1.0) * 100))
        
        scat = config.get("scatter") or {}
        self.regression_line_check.setChecked(scat.get("show_regression", False))
        self.confidence_interval_check.setChecked(scat.get("show_ci", False))
        self.show_r2_check.setChecked(scat.get("show_r2", False))
        self.show_rmse_check.setChecked(scat.get("show_rmse", False))
        self.show_equation_check.setChecked(scat.get("show_equation", False))
        self.error_bars_combo.setCurrentText(scat.get("error_bars", "None"))
        self.confidence_level_spin.setValue(scat.get("ci_level", 95))
        
        pie = config.get("pie") or {}
        self.pie_show_percentages_check.setChecked(pie.get("show_percentages", True))
        self.pie_start_angle_spin.setValue(pie.get("start_angle", 0))
        self.pie_explode_check.setChecked(pie.get("explode_first", False))
        self.pie_explode_distance_spin.setValue(pie.get("explode_distance", 0.1))
        self.pie_shadow_check.setChecked(pie.get("shadow", False))

        self.toggle_line_selector()
        self.toggle_bar_selector()

    def _load_annotations_config(self, config: dict):
        # Text Annotations
        self.annotations = config.get("text_annotations") or []
        self.annotations_list.clear()
        for ann in self.annotations:
            self.annotations_list.addItem(f"{ann['text']} @ ({ann['x']:.2f}, {ann['y']:.2f})")
            
        # Textbox
        tb = config.get("textbox") or {}
        self.textbox_enable_check.setChecked(tb.get("enabled", False))
        self.textbox_content.setText(tb.get("content", ""))
        self.textbox_position_combo.setCurrentText(tb.get("position", "upper right"))
        self.textbox_style_combo.setCurrentText(tb.get("style", "Rounded"))
        
        self.textbox_bg_color = tb.get("bg_color") or "white"
        self.textbox_bg_label.setText(self.textbox_bg_color)
        self.textbox_bg_button.updateColors(base_color_hex=self.textbox_bg_color)
        
        # Table
        tab = config.get("table") or {}
        self.table_enable_check.setChecked(tab.get("enabled", False))
        self.table_type_combo.setCurrentText(tab.get("type", "Summary Stats"))
        self.table_location_combo.setCurrentText(tab.get("location", "bottom"))
        self.table_auto_font_size_check.setChecked(tab.get("auto_font_size", True))
        self.table_font_size_spin.setValue(tab.get("fontsize", 10))
        self.table_scale_spin.setValue(tab.get("scale", 1.2))
        
        self.toggle_table_controls()

    
    def get_config(self) -> Dict[str, Any]:
        """Get current plot configuration"""
        config = {
            "version": 1.0,
            "plot_type": self.current_plot_type_name,
            "basic": self._get_basic_config(),
            "appearance": self._get_appearance_config(),
            "axes": self._get_axes_config(),
            "legend": self._get_legend_config(),
            "grid": self._get_grid_config(),
            "advanced": self._get_advanced_config(),
            "annotations": self._get_annotations_config()
        }
        return config

    def _get_basic_config(self) -> Dict[str, Any]:
        """Config for the General Tab"""
        return {
            "x_column": self.x_column.currentText(),
            "y_columns": self.get_selected_y_columns(),
            "multi_y_checked": self.multi_y_check.isChecked(),
            "hue_column": self.hue_column.currentText(),
            "use_subset": self.use_subset_check.isChecked(),
            "subset_name": self.subset_combo.currentData(),
            "secondary_y_enabled": self.secondary_y_check.isChecked(),
            "secondary_y_column": self.secondary_y_column.currentText(),
            "secondary_plot_type": self.secondary_plot_type_combo.currentText(),
            "quick_filter": self.quick_filter_input.text()
        }

    def _get_appearance_config(self) -> Dict[str, Any]:
        """Config for the appearance tab"""
        return {
            "font_family": self.font_family_combo.currentFont().family(),
            "usetex": self.usetex_checkbox.isChecked(),
            "title": {
                "enabled": self.title_check.isChecked(),
                "text": self.title_input.text(),
                "size": self.title_size_spin.value(),
                "weight": self.title_weight_combo.currentText(),
                "location": self.title_position_combo.currentText(),
            },
            "xlabel": {
                "enabled": self.xlabel_check.isChecked(),
                "text": self.xlabel_input.text(),
                "size": self.xlabel_size_spin.value(),
                "weight": self.xlabel_weight_combo.currentText(),
            },
            "ylabel": {
                "enabled": self.ylabel_check.isChecked(),
                "text": self.ylabel_input.text(),
                "size": self.ylabel_size_spin.value(),
                "weight": self.ylabel_weight_combo.currentText(),
            },
            "spines": {
                "top": {
                    "visible": self.top_spine_visible_check.isChecked(),
                    "width": self.top_spine_width_spin.value(),
                    "color": self.top_spine_color,
                },
                "bottom": {
                    "visible": self.bottom_spine_visible_check.isChecked(),
                    "width": self.bottom_spine_width_spin.value(),
                    "color": self.bottom_spine_color,
                },
                "left": {
                    "visible": self.left_spine_visible_check.isChecked(),
                    "width": self.left_spine_width_spin.value(),
                    "color": self.left_spine_color,
                },
                "right": {
                    "visible": self.right_spine_visible_check.isChecked(),
                    "width": self.right_spine_width_spin.value(),
                    "color": self.right_spine_color,
                },
            },
            "figure": {
                "width": self.width_spin.value(),
                "height": self.height_spin.value(),
                "dpi": self.dpi_spin.value(),
                "bg_color": self.bg_color,
                "face_facecolor": self.face_color,
                "palette": self.palette_combo.currentText(),
                "tight_layout": self.tight_layout_check.isChecked(),
                "style": self.style_combo.currentText(),
            }
        }
    
    def _get_axes_config(self) -> Dict[str, Any]:
        """Get config from axes tab"""
        return {
            "x_axis": {
                "auto_limits": self.x_auto_check.isChecked(),
                "invert": self.x_invert_axis_check.isChecked(),
                "top_axis": self.x_top_axis_check.isChecked(),
                "min": self.x_min_spin.value(),
                "max": self.x_max_spin.value(),
                "tick_label_size": self.xtick_label_size_spin.value(),
                "tick_rotation": self.xtick_rotation_spin.value(),
                "max_ticks": self.x_max_ticks_spin.value(),
                "minor_ticks_enabled": self.x_show_minor_ticks_check.isChecked(),
                "major_tick_direction": self.x_major_tick_direction_combo.currentText(),
                "major_tick_width": self.x_major_tick_width_spin.value(),
                "minor_tick_direction": self.x_minor_tick_direction_combo.currentText(),
                "minor_tick_width": self.x_minor_tick_width_spin.value(),
                "scale": self.x_scale_combo.currentText(),
                "display_units": self.x_display_units_combo.currentText()
            },
            "y_axis": {
                "auto_limits": self.y_auto_check.isChecked(),
                "invert": self.y_invert_axis_check.isChecked(),
                "min": self.y_min_spin.value(),
                "max": self.y_max_spin.value(),
                "tick_label_size": self.ytick_label_size_spin.value(),
                "tick_rotation": self.ytick_rotation_spin.value(),
                "max_ticks": self.y_max_ticks_spin.value(),
                "minor_ticks_enabled": self.y_show_minor_ticks_check.isChecked(),
                "major_tick_direction": self.y_major_tick_direction_combo.currentText(),
                "major_tick_width": self.y_major_tick_width_spin.value(),
                "minor_tick_direction": self.y_minor_tick_direction_combo.currentText(),
                "minor_tick_width": self.y_minor_tick_width_spin.value(),
                "scale": self.y_scale_combo.currentText(),
                "display_units": self.y_display_units_combo.currentText()
            },
            "flip_axes": self.flip_axes_check.isChecked(),
            "datetime": {
                "enabled": self.custom_datetime_check.isChecked(),
                "x_format_preset": self.x_datetime_format_combo.currentText(),
                "x_format_custom": self.x_custom_datetime_input.text(),
                "y_format_preset": self.y_datetime_format_combo.currentText(),
                "y_format_custom": self.y_custom_datetime_format_input.text(),
            }
        }
    
    def _get_legend_config(self) -> Dict[str, Any]:
        """Get the legend config"""
        return {
            "enabled": self.legend_check.isChecked(),
            "location": self.legend_loc_combo.currentText(),
            "title": self.legend_title_input.text(),
            "font_size": self.legend_size_spin.value(),
            "columns": self.legend_columns_spin.value(),
            "column_spacing": self.legend_colspace_spin.value(),
            "frame": self.legend_frame_check.isChecked(),
            "fancy_box": self.legend_fancybox_check.isChecked(),
            "shadow": self.legend_shadow_check.isChecked(),
            "bg_color": self.legend_bg_color,
            "edge_clor": self.legend_edge_color,
            "edge_width": self.legend_edge_width_spin.value(),
            "alpha": self.legend_alpha_slider.value() / 100.0,
        }
    
    def _get_grid_config(self) -> Dict[str, Any]:
        """Get config for the grid"""
        return {
            "enabled": self.grid_check.isChecked(),
            "independent_axes": self.independent_grid_check.isChecked(),
            "global": {
                "which": self.grid_which_type_combo.currentText(),
                "axis": self.grid_axis_combo.currentText(),
                "alpha": self.global_grid_alpha_slider.value() / 100.0,
            },
            "x_major": {
                "enabled": self.x_major_grid_check.isChecked(),
                "style": self.x_major_grid_style_combo.currentText(),
                "width": self.x_major_grid_linewidth_spin.value(),
                "color": self.x_major_grid_color,
                "alpha": self.x_major_grid_alpha_slider.value() / 100.0,
            },
            "x_minor": {
                "enabled": self.x_minor_grid_check.isChecked(),
                "style": self.x_minor_grid_style_combo.currentText(),
                "width": self.x_minor_grid_linewidth_spin.value(),
                "color": self.x_minor_grid_color,
                "alpha": self.x_minor_grid_alpha_slider.value() / 100.0,
            },
            "y_major": {
                "enabled": self.y_major_grid_check.isChecked(),
                "style": self.y_major_grid_style_combo.currentText(),
                "width": self.y_major_grid_linewidth_spin.value(),
                "color": self.y_major_grid_color,
                "alpha": self.y_major_grid_alpha_slider.value() / 100.0,
            },
            "y_minor": {
                "enabled": self.y_minor_grid_check.isChecked(),
                "style": self.y_minor_grid_style_combo.currentText(),
                "width": self.y_minor_grid_linewidth_spin.value(),
                "color": self.y_minor_grid_color,
                "alpha": self.y_minor_grid_alpha_slider.value() / 100.0,
            },
        }
    
    def _get_advanced_config(self) -> Dict[str, Any]:
        """Get config for customization and other elemenst from advanced tab"""
        linestyle_map = {'Solid': '-', 'Dashed': '--', 'Dash-dot': '-.', 'Dotted': ':', 'None': 'None'}
        return {
            "multi_line_custom": self.multiline_custom_check.isChecked(),
            "line_customizations": self.line_customizations,
            "global_line": {
                "width": self.linewidth_spin.value(),
                "style": linestyle_map.get(self.linestyle_combo.currentText(), "-"),
                "color": self.line_color,
            },
            "global_marker": {
                "shape": self.marker_combo.currentText(),
                "size": self.marker_size_spin.value(),
                "color": self.marker_color,
                "edge_color": self.marker_edge_color,
                "edge_width": self.marker_edge_width_spin.value(),
            },
            "multi_bar_custom": self.multibar_custom_check.isChecked(),
            "bar_customizations": self.bar_customizations,
            "global_bar": {
                "width": self.bar_width_spin.value(),
                "color": self.bar_color,
                "edge_color": self.bar_edge_color,
                "edge_width": self.bar_edge_width_spin.value(),
            },
            "histogram": {
                "bins": self.histogram_bins_spin.value(),
                "show_normal": self.histogram_show_normal_check.isChecked(),
                "show_kde": self.histogram_show_kde_check.isChecked(),
            },
            "global_alpha": self.alpha_slider.value() / 100.0,
            "scatter": {
                "show_regression": self.regression_line_check.isChecked(),
                "show_ci": self.confidence_interval_check.isChecked(),
                "show_r2": self.show_r2_check.isChecked(),
                "show_rmse": self.show_rmse_check.isChecked(),
                "show_equation": self.show_equation_check.isChecked(),
                "error_bars": self.error_bars_combo.currentText(),
                "ci_level": self.confidence_level_spin.value(),
            },
            "pie": {
                "show_percentages": self.pie_show_percentages_check.isChecked(),
                "start_angle": self.pie_start_angle_spin.value(),
                "explode_first": self.pie_explode_check.isChecked(),
                "explode_distance": self.pie_explode_distance_spin.value(),
                "shadow": self.pie_shadow_check.isChecked(),
            },
        }
    
    def _get_annotations_config(self) -> Dict[str, Any]:
        """Get config for annotationsa nd txtbox"""
        return {
            "text_annotations": self.annotations,
            "textbox": {
                "enabled": self.textbox_enable_check.isChecked(),
                "content": self.textbox_content.text(),
                "position": self.textbox_position_combo.currentText(),
                "style": self.textbox_style_combo.currentText(),
                "bg_color": self.textbox_bg_color,
            },
            "table": {
                "enabled": self.table_enable_check.isChecked(),
                "type": self.table_type_combo.currentText(),
                "location": self.table_location_combo.currentText(),
                "auto_font_size": self.table_auto_font_size_check.isChecked(),
                "fontsize": self.table_font_size_spin.value(),
                "scale": self.table_scale_spin.value()
            }
        }

    def clear(self) -> None:
        """Clear all plot data"""
        self.clear_plot()
        self.title_input.clear()
        self.xlabel_input.clear()
        self.ylabel_input.clear()
    
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
            self.script_editor = ScriptEditorDialog(code, parent=self)
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
                self.title_input.setText(title)
                self.title_check.setChecked(True)
            
            xlabel = ax.get_xlabel()
            if xlabel:
                self.xlabel_input.setText(xlabel)
                self.xlabel_check.setChecked(True)
            
            ylabel = ax.get_ylabel()
            if ylabel:
                self.ylabel_input.setText(ylabel)
                self.ylabel_check.setChecked(True)
            
        except Exception as GUISyncError:
            print(f"Warning: Could not sync GUI from plot: {GUISyncError}")