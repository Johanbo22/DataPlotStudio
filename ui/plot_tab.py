# ui/plot_tab.py

from re import M
from PyQt6.QtWidgets import QMessageBox, QColorDialog, QApplication
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QIcon, QColor
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from core.plot_engine import PlotEngine
from core.data_handler import DataHandler
from ui.status_bar import StatusBar
from ui.dialogs import ProgressDialog
from ui.plot_tab_ui import PlotTabUI 
import pandas as pd
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
import seaborn as sns
import matplotlib.pyplot as plt
import traceback
from matplotlib.colors import to_hex
from typing import Dict, List, Any


class PlotTab(PlotTabUI):  # Inherit from the UI class
    """Tab for creating and customizing plots"""
    
    def __init__(self, data_handler: DataHandler, status_bar: StatusBar, subset_manager=None) -> None:
        super().__init__()
        
        self.data_handler: DataHandler = data_handler
        self.status_bar: StatusBar = status_bar
        self.subset_manager = None
        self.plot_engine = PlotEngine()
        self.current_config = {}
        
        # These are now defined in the UI base 
        self.bg_color = "white"
        self.face_color = "white"
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

        #plot dispatcher
        self.plot_strategies = {
            "Line": self._plot_line_strategy,
            "Scatter": self._plot_scatter_strategy,
            "Bar": self._plot_bar_strategy,
            "Histogram": self._plot_histogram_strategy,
            "Box": self._plot_box_strategy,
            "Violin": self._plot_violin_strategy,
            "Heatmap": self._plot_heatmap_strategy,
            "KDE": self._plot_kde_strategy,
            "Area": self._plot_area_strategy,
            "Pie": self._plot_pie_strategy,
            "Count Plot": self._plot_count_strategy,
            "Hexbin": self._plot_hexbin_strategy,
            "2D Density": self._plot_2d_density_strategy,
            "Stem": self._plot_stem_strategy,
            "Stackplot": self._plot_stackplot_strategy,
            "Stairs": self._plot_stairs_strategy,
            "Eventplot": self._plot_eventplot_strategy,
            "ECDF": self._plot_ecdf_strategy,
            "2D Histogram": self._plot_hist2d_strategy,
            "Image Show (imshow)": self._plot_imshow_strategy,
            "pcolormesh": self._plot_pcolormesh_strategy,
            "Contour": self._plot_contour_strategy,
            "Contourf": self._plot_contourf_strategy,
            "Barbs": self._plot_barbs_strategy,
            "Quiver": self._plot_quiver_strategy,
            "Streamplot": self._plot_streamplot_strategy,
            "Tricontour": self._plot_tricontour_strategy,
            "Tricontourf": self._plot_tricontourf_strategy,
            "Tripcolor": self._plot_tripcolor_strategy,
            "Triplot": self._plot_triplot_strategy,
        }
        
        # Create canvas and toolbar
        self.plot_engine.create_figure()
        canvas = FigureCanvas(self.plot_engine.get_figure())
        toolbar = NavigationToolbar(canvas, self)
        
        self.init_ui(canvas, toolbar)
        
        #populate box in general tab
        for label, icon_key in self.plot_engine.AVAILABLE_PLOTS.items():
            icon_path = f"icons/plot_tab/plots/{icon_key}.png"
            icon = QIcon(icon_path)
            self.plot_type.addItem(icon, label)
        
        # Connect all signals to their logic methods
        self._connect_signals()
        
        # Load initial data
        self.update_column_combo()
        
        self.on_plot_type_changed(self.plot_type.currentText())

    def _connect_signals(self) -> None:
        """Connect all UI widget signals to their logic"""
        
        # --- Main Buttons ---
        self.plot_button.clicked.connect(self.generate_plot)
        self.clear_button.clicked.connect(self.clear_plot)
        
        # --- Tab 1: Basic ----
        self.plot_type.currentTextChanged.connect(self.on_plot_type_changed)
        self.multi_y_check.stateChanged.connect(self.toggle_multi_y)
        self.select_all_y_btn.clicked.connect(self.select_all_y_columns)
        self.clear_all_y_btn.clicked.connect(self.clear_all_y_columns)
        self.hue_column.currentTextChanged.connect(self.on_data_changed)
        
        # --- Tab 2:- Appearance ---
        self.top_spine_color_button.clicked.connect(self.choose_top_spine_color)
        self.bottom_spine_color_button.clicked.connect(self.choose_bottom_spine_color)
        self.left_spine_color_button.clicked.connect(self.choose_left_spine_color)
        self.right_spine_color_button.clicked.connect(self.choose_right_spine_color)
        self.all_spines_btn.clicked.connect(self.preset_all_spines)
        self.box_only_btn.clicked.connect(self.preset_box_only)
        self.no_spines_btn.clicked.connect(self.preset_no_spines)
        self.bg_color_button.clicked.connect(self.choose_bg_color)
        self.face_color_button.clicked.connect(self.choose_face_color)
        
        # --- Tab 3: Axes ---
        self.x_auto_check.stateChanged.connect(lambda: self.x_min_spin.setEnabled(not self.x_auto_check.isChecked()))
        self.x_auto_check.stateChanged.connect(lambda: self.x_max_spin.setEnabled(not self.x_auto_check.isChecked()))
        self.y_auto_check.stateChanged.connect(lambda: self.y_min_spin.setEnabled(not self.y_auto_check.isChecked()))
        self.y_auto_check.stateChanged.connect(lambda: self.y_max_spin.setEnabled(not self.y_auto_check.isChecked()))
        self.custom_datetime_check.stateChanged.connect(self.toggle_datetime_format)
        self.x_datetime_format_combo.currentTextChanged.connect(self.on_x_datetime_format_changed)
        self.y_datetime_format_combo.currentTextChanged.connect(self.on_y_datetime_format_changed)
        
        # --- Tab 4: Legend & Grid ---
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
        
        # --- Tab 5: Advanced ---
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
        
        # --- Tab 6: Annotations ---
        self.annotation_color_button.clicked.connect(self.choose_annotation_color)
        self.add_annotation_button.clicked.connect(self.add_annotation)
        self.textbox_bg_button.clicked.connect(self.choose_textbox_bg_color)
        self.annotations_list.itemClicked.connect(self.on_annotation_selected)
        self.clear_annotations_button.clicked.connect(self.clear_annotations)

    ### START OF LOGIC / FUNCTIONALITY

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
        self.subset_combo.setCurrentText(target_index)

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
        except Exception as e:
            print(f"Warning: Could not refresh subset list: {e}")
    
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
        except Exception as e:
            self.status_bar.log(f"Failed to apply subset, using full dataset: {str(e)}", "WARNING")
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
            self.bar_color_button.setStyleSheet(f"background-color: {facecolor}")
        
        #edge color
        edgecolor = to_hex(patch.get_edgecolor())
        if edgecolor:
            self.bar_edge_color = edgecolor
            self.bar_edge_label.setText(edgecolor)
            self.bar_edge_button.setStyleSheet(f"background-color: {edgecolor}")

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
            self.x_major_grid_color_button.setStyleSheet(f"background-color: {self.x_major_grid_color}")

    def choose_x_minor_grid_color(self):
        """Choose the colour for the minor x gridlnies"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.x_minor_grid_color = color.name()
            self.x_minor_grid_color_label.setText(self.x_minor_grid_color)
            self.x_minor_grid_color_button.setStyleSheet(f"background-color: {self.x_minor_grid_color}")
    
    def choose_y_major_grid_color(self):
        """Choose color for x-axis major gridlines"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.y_major_grid_color = color.name()
            self.y_major_grid_color_label.setText(self.y_major_grid_color)
            self.y_major_grid_color_button.setStyleSheet(f"background-color: {self.y_major_grid_color}")

    def choose_y_minor_grid_color(self):
        """Choose the colour for the minor x gridlnies"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.y_minor_grid_color = color.name()
            self.y_minor_grid_color_label.setText(self.y_minor_grid_color)
            self.y_minor_grid_color_button.setStyleSheet(f"background-color: {self.y_minor_grid_color}")
    
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
            self.bg_color_button.setStyleSheet(f"background-color: {self.bg_color}")

    def choose_face_color(self) -> None:
        """Open the color picker tool for the face of the plotting axes"""
        color = QColorDialog.getColor(QColor(self.face_color), self)
        if color.isValid():
            self.face_color = color.name()
            self.face_color_label.setText(self.face_color)
            self.face_color_button.setStyleSheet(f"background-color: {self.face_color}")

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
                self.line_color = color
                self.line_color_label.setText(color)
                self.line_color_button.setStyleSheet("background-color: { color}")

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
            self.top_spine_color_button.setStyleSheet(f"background-color: {self.top_spine_color}")
    
    def choose_bottom_spine_color(self):
        """Open color picker for bottom spine"""
        color = QColorDialog.getColor(QColor(self.bottom_spine_color), self)
        if color.isValid():
            self.bottom_spine_color = color.name()
            self.bottom_spine_color_label.setText(self.bottom_spine_color)
            self.bottom_spine_color_button.setStyleSheet(f"background-color: {self.bottom_spine_color}")
    
    def choose_left_spine_color(self):
        """Open color picker for left spine"""
        color = QColorDialog.getColor(QColor(self.left_spine_color), self)
        if color.isValid():
            self.left_spine_color = color.name()
            self.left_spine_color_label.setText(self.left_spine_color)
            self.left_spine_color_button.setStyleSheet(f"background-color: {self.left_spine_color}")
    
    def choose_right_spine_color(self):
        """Open color picker for right spine"""
        color = QColorDialog.getColor(QColor(self.right_spine_color), self)
        if color.isValid():
            self.right_spine_color = color.name()
            self.right_spine_color_label.setText(self.right_spine_color)
            self.right_spine_color_button.setStyleSheet(f"background-color: {self.right_spine_color}")
    
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
            self.line_color_button.setStyleSheet(f"background-color: {self.line_color}")
    
    def choose_marker_color(self):
        """Open color picker for marker color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.marker_color = color.name()
            self.marker_color_label.setText(self.marker_color)
            self.marker_color_button.setStyleSheet(f"background-color: {self.marker_color}")
    
    def choose_marker_edge_color(self):
        """Open color picker for marker edge color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.marker_edge_color = color.name()
            self.marker_edge_label.setText(self.marker_edge_color)
            self.marker_edge_button.setStyleSheet(f"background-color: {self.marker_edge_color}")
    
    def choose_bar_color(self):
        """Open color picker for bar color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bar_color = color.name()
            self.bar_color_label.setText(self.bar_color)
            self.bar_color_button.setStyleSheet(f"background-color: {self.bar_color}")
            self._update_bar_customization_live()
    
    def choose_bar_edge_color(self):
        """Open color picker for bar edge color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.bar_edge_color = color.name()
            self.bar_edge_label.setText(self.bar_edge_color)
            self.bar_edge_button.setStyleSheet(f"background-color: {self.bar_edge_color}")
            self._update_bar_customization_live()
    
    def choose_annotation_color(self):
        """Open color picker for annotation color"""
        color = QColorDialog.getColor()
        if color.isValid():
            self.annotation_color = color.name()
            self.annotation_color_label.setText(self.annotation_color)
            self.annotation_color_button.setStyleSheet(f"background-color: {self.annotation_color}")
    
    def choose_textbox_bg_color(self):
        """Open color picker for text box background"""
        color = QColorDialog.getColor(QColor(self.textbox_bg_color), self)
        if color.isValid():
            self.textbox_bg_color = color.name()
            self.textbox_bg_label.setText(self.textbox_bg_color)
            self.textbox_bg_button.setStyleSheet(f"background-color: {self.textbox_bg_color}")
    
    def choose_legend_bg_color(self):
        """Open color picker for legend background"""
        color = QColorDialog.getColor(QColor(self.legend_bg_color), self)
        if color.isValid():
            self.legend_bg_color = color.name()
            self.legend_bg_label.setText(self.legend_bg_color)
            self.legend_bg_button.setStyleSheet(f"background-color: {self.legend_bg_color}")
    
    def choose_legend_edge_color(self):
        """Open color picker for legend edge color"""
        color = QColorDialog.getColor(QColor(self.legend_edge_color), self)
        if color.isValid():
            self.legend_edge_color = color.name()
            self.legend_edge_label.setText(self.legend_edge_color)
            self.legend_edge_button.setStyleSheet(f"background-color: {self.legend_edge_color}")
    
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
        
        # Block signals to prevent triggering callbacks
        self.x_column.blockSignals(True)
        self.y_column.blockSignals(True)
        self.hue_column.blockSignals(True)
        self.y_columns_list.blockSignals(True)
        
        #update xcol
        self.x_column.clear()
        self.x_column.addItems(columns)

        #update singleular ycol
        self.y_column.clear()
        self.y_column.addItems(columns)

        #update more ycols
        self.y_columns_list.clear()
        for col in columns:
            self.y_columns_list.addItem(col)
        
        #update hue
        self.hue_column.clear()
        self.hue_column.addItem("None")
        self.hue_column.addItems(columns)
        
        # Unblock signals
        self.x_column.blockSignals(False)
        self.y_column.blockSignals(False)
        self.hue_column.blockSignals(False)
        self.y_columns_list.blockSignals(False)
    
    def on_plot_type_changed(self, plot_type: str):
        """Handle plot type change"""
        self.status_bar.log(f"Plot type changed to: {plot_type}")

        description = self.plot_engine.PLOT_DESCRIPTIONS.get(plot_type, "")
        self.description_label.setText(description)


        #CONTROL FOR THE VISIBLE CUSTOMIZATIONS IN ADVANCED TAB. i think i need to add more
        if plot_type != "Bar":
            self.bar_group.setVisible(False)
        else:
            self.bar_group.setVisible(False)

        if plot_type != "Histogram":
            self.histogram_group.setVisible(False)
            self.bar_group.setVisible(False)
        else:
            self.histogram_group.setVisible(True)
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
        multi_y_supported = ["Line", "Bar", "Area", "Box", "Stackplot", "Eventplot", "Contour", "Contourf"]

        #enabled based on plottype
        if plot_type in multi_y_supported:
            self.multi_y_check.setEnabled(True)
            self.multi_y_check.setToolTip("")
        else:
            self.multi_y_check.setEnabled(False)
            self.multi_y_check.setChecked(False)
            self.multi_y_check.setToolTip(f"{plot_type} plots do not support multiple y columns")

        #disable hue for certain plots
        plots_without_hue: list[str] = [
            "Heatmap", "Pie", "Histogram", "KDE", "Count Plot", "Stackplot", "Eventplot",
            "Image Show (imshow)", "pcolormesh", "Contour", "Contourf", "Tricontour",
            "Tricontourf", "Tripcolor", "Triplot", "2D Histogram", "ECDF", "Stairs", "Stem",
            "Barbs", "Quiver", "Streamplot"
        ]
        self.hue_column.setEnabled(plot_type not in plots_without_hue)

        if plot_type in plots_without_hue:
            self.hue_column.setCurrentText("None")

        #disable flipping axes on certain plots
        incompatible_plots: list[str] = [
            "Histogram", "Pie", "Heatmap", "KDE", "Stackplot", "Eventplot",
            "Image Show (imshow)", "pcolormesh", "Contour", "Contourf", "Barbs", "Quiver",
            "Streamplot", "Tricontour", "Tricontourf", "Tripcolor", "Triplot", "2D Histogram", "ECDF"
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

    def is_datetime_column(self, data) -> bool:
        """Check if data is datetime"""
        if data is None:
            return False
        
        try:
            if isinstance(data, pd.Series):
                if pd.api.types.is_datetime64_any_dtype(data):
                    return True
                if data.dtype == "object":
                    sample = data.dropna().head(1)
                    if len(sample) > 0:
                        try:
                            pd.to_datetime(sample.iloc[0], utc=True)
                            return True
                        except: pass
            elif hasattr(data, "dtype"):
                return pd.api.types.is_datetime64_any_dtype(data.dtype)
        except Exception as e:
            self.status_bar.log(f"DateTime detection warning: {str(e)}", "WARNING")
        return False

    def _format_datetime_axis(self, ax, x_data, y_data=None) -> None:
        """Format datetime axes with proper tick spacing to avoid cluttering"""
        import pandas as pd
        
        #check if axes are datetime
        is_x_datetime = self.is_datetime_column(x_data)
        is_y_datetime = self.is_datetime_column(y_data) if y_data is not None else False

        #custom fmts
        use_custom_format: bool = self.custom_datetime_check.isChecked()

        #format xaxis
        if is_x_datetime:
            try:
                if isinstance(x_data, pd.Series):
                    if x_data.dtype == "object":
                        x_data = pd.to_datetime(x_data, utc=True, errors="coerce")
                    elif not hasattr(x_data.dtype, "tz") or x_data.dtype.tz is None:
                        x_data = x_data.dt.tz_localize("UTC", nonexistent="shift_forward", ambiguous="infer")
            except Exception as e:
                self.status_bar.log(f"X-axis timezone handling: {str(e)}", "WARNING")
            
            if use_custom_format:
                format_text = self.x_datetime_format_combo.currentText()

                if format_text == "Custom":
                    custom_format = self.x_custom_datetime_input.text().strip()
                    if custom_format:
                        try:
                            ax.xaxis.set_major_formatter(mdates.DateFormatter(custom_format))
                            self._set_intelligent_locator(ax.xaxis, x_data)
                        except Exception as e:
                            self.status_bar.log(f"Invalid datetime format: {str(e)}", "WARNING")
                            self._apply_auto_datetime_format(ax.xaxis, x_data)
                    else:
                        self._apply_auto_datetime_format(ax.xaxis, x_data)
                elif format_text == "Auto":
                    self._apply_auto_datetime_format(ax.xaxis, x_data)
                else:
                    format_code = format_text.split(" ")[0]
                    try:
                        ax.xaxis.set_major_formatter(mdates.DateFormatter(format_code))
                        self._set_intelligent_locator(ax.xaxis, x_data)
                    except Exception as e:
                        self.status_bar.log(f"Invalid datetime format: {str(e)}", "WARNING")
                        self._apply_auto_datetime_format(ax.xaxis, x_data)
            else:
                self._apply_auto_datetime_format(ax.xaxis, x_data)

        #fmt yaxis
        if is_y_datetime:
            try:
                if isinstance(y_data, pd.Series):
                    if y_data.dtype == 'object':
                        y_data = pd.to_datetime(y_data, utc=True, errors='coerce')
                    elif not hasattr(y_data.dtype, 'tz') or y_data.dtype.tz is None:
                        y_data = y_data.dt.tz_localize('UTC', nonexistent='shift_forward', ambiguous='infer')
            except Exception as e:
                self.status_bar.log(f"Y-axis timezone handling: {str(e)}", "WARNING")
            
            if use_custom_format:
                format_text = self.y_datetime_format_combo.currentText()

                if format_text == "Custom":
                    custom_format = self.y_custom_datetime_input.text().strip()
                    if custom_format:
                        try:
                            ax.yaxis.set_major_formatter(mdates.DateFormatter(custom_format))
                            self._set_intelligent_locator(ax.yaxis, y_data)
                        except Exception as e:
                            self.status_bar.log(f"Invalid datetime format: {str(e)}", "WARNING")
                            self._apply_auto_datetime_format(ax.yaxis, y_data)
                    else:
                        self._apply_auto_datetime_format(ax.yaxis, y_data)
                elif format_text == "Auto":
                    self._apply_auto_datetime_format(ax.yaxis, y_data)
                else:
                    format_code = format_text.split(" ")[0]
                    try:
                        ax.yaxis.set_major_formatter(mdates.DateFormatter(format_code))
                        self._set_intelligent_locator(ax.yaxis, y_data)
                    except Exception as e:
                        self.status_bar.log(f"Invalid datetime format: {str(e)}", "WARNING")
                        self._apply_auto_datetime_format(ax.yaxis, y_data)
            else:
                self._apply_auto_datetime_format(ax.yaxis, y_data)
    
    def _apply_auto_datetime_format(self, axis, data):
        """Apply datetimeformat based on input datarange auto"""
        if data is None or len(data) < 2:
            return
        import pandas as pd

        try:
            if isinstance(data, pd.Series):
                if data.dtype == "object":
                    data = pd.to_datetime(data, utc=True, errors="coerce")
                
            data = data.dropna()

            if len(data) < 2:
                return

            date_range = data.max() - data.min()

            if date_range <= pd.Timedelta(hours=6):
                axis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
                axis.set_major_locator(mdates.MinuteLocator(interval=max(1, len(data) // 10)))
            elif date_range <= pd.Timedelta(days=1):
                axis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                axis.set_major_locator(mdates.HourLocator(interval=max(1, len(data) // 12)))
            elif date_range <= pd.Timedelta(days=7):
                axis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
                axis.set_major_locator(mdates.DayLocator(interval=1))
            elif date_range <= pd.Timedelta(days=30):
                axis.set_major_formatter(mdates.DateFormatter("%m/%d"))
                axis.set_major_locator(mdates.DayLocator(interval=max(1, date_range.days // 10)))
            elif date_range <= pd.Timedelta(days=365):
                axis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                axis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range.days // 90)))
            else:
                axis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
                axis.set_major_locator(mdates.YearLocator())
        except Exception as e:
            self.status_bar.log(f"Failed to auto-format datetime: {e}", "WARNING")
    
    def _set_intelligent_locator(self, axis, data):
        """Set tick locator based on datarange"""
        if data is None or len(data) < 2:
            return
            
        try:
            if isinstance(data, pd.Series):
                if data.dtype == "object":
                    data = pd.to_datetime(data, utc=True, errors="coerce")
            data = data.dropna()

            if len(data) < 2:
                return

            date_range = data.max() - data.min()
            
            if date_range <= pd.Timedelta(hours=6):
                axis.set_major_locator(mdates.MinuteLocator(interval=max(1, len(data) // 10)))
            elif date_range <= pd.Timedelta(days=1):
                axis.set_major_locator(mdates.HourLocator(interval=max(1, len(data) // 12)))
            elif date_range <= pd.Timedelta(days=7):
                axis.set_major_locator(mdates.DayLocator(interval=1))
            elif date_range <= pd.Timedelta(days=30):
                axis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range.days // 10)))
            elif date_range <= pd.Timedelta(days=365):
                axis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range.days // 90)))
            else:
                axis.set_major_locator(mdates.YearLocator())
        except Exception as e:
            self.status_bar.log(f"Failed to set datetime locator: {e}", "WARNING")

    
    # Plot strategies
    def _plot_line_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Line plot strategy"""
        if axes_flipped:
            #remove formatting kwargs
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            for col in y_cols:
                self.plot_engine.current_ax.plot(
                    self.data_handler.df[col],
                    self.data_handler.df[x_col],
                    label=col,
                    **plot_kwargs
                )
            
            self._apply_flipped_labels(x_col, y_cols, font_family)
            if len(y_cols) > 1 or general_kwargs.get("hue"):
                self.plot_engine.current_ax.legend()
            
            #datetime
            try:
                y_data = self.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    y_data,
                    self.data_handler.df[x_col]
                )
            except: pass
        else:
            #normal orientation
            plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Line"])
            plot_method(self.data_handler.df, x_col, y_cols, **general_kwargs)

            #datetime formatting
            try:
                y_data = self.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[x_col],
                    y_data
                )
            except: pass
    
    def _plot_area_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Area plot strategy"""
        if axes_flipped:
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            for col in y_cols:
                self.plot_engine.current_ax.fill_betweenx(
                    self.data_handler.df[x_col],
                    0,
                    self.data_handler.df[col],
                    label=col,
                    alpha=self.alpha_slider.value() # Default alpha for area
                )
            
            self._apply_flipped_labels(x_col, y_cols, font_family)
            if len(y_cols) > 1:
                self.plot_engine.current_ax.legend()
            
            #datetime
            try:
                y_data = self.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    y_data,
                    self.data_handler.df[x_col]
                )
            except: pass
        else:
            #normal orientation
            plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Area"])
            plot_method(self.data_handler.df, x_col, y_cols, **general_kwargs)

            #datetime
            try:
                y_data = self.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[x_col],
                    y_data
                )
            except: pass
    
    def _plot_scatter_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Scatter plot strategy"""
        if len(y_cols) > 1:
            self.status_bar.log(f"Scatter only supports one y column. Using: {y_cols[0]}", "WARNING")
        
        y_col = y_cols[0]

        if axes_flipped:
            hue_val = general_kwargs.pop("hue", None)
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)

            if hue_val:
                # Use seaborn for hue logic
                sns.scatterplot(
                    data=self.data_handler.df,
                    x=y_col,
                    y=x_col,
                    hue=hue_val,
                    ax=self.plot_engine.current_ax,
                    **plot_kwargs
                )
            else:
                self.plot_engine.current_ax.scatter(
                    self.data_handler.df[y_col],
                    self.data_handler.df[x_col],
                    **plot_kwargs
                )

            self._apply_flipped_labels(x_col, [y_col], font_family)
            
            #datetime
            try:
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[y_col],
                    self.data_handler.df[x_col]
                )
            except: pass
        else:
            plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Scatter"])
            plot_method(self.data_handler.df, x_col, y_col, **general_kwargs)

            #datetime
            try:
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[x_col],
                    self.data_handler.df[y_col]
                )
            except: pass

        #Regression analysis - Run after plotting, handle flipped axes inside
        if (self.regression_line_check.isChecked() or self.show_r2_check.isChecked() or 
            self.show_rmse_check.isChecked() or self.show_equation_check.isChecked() or 
            self.error_bars_combo.currentText() != "None"):
            
            if axes_flipped:
                self._add_regression_analysis(y_col, x_col, flipped=True)
            else:
                self._add_regression_analysis(x_col, y_col, flipped=False)
    
    def _plot_bar_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Bar chart plotting strategy"""
        general_kwargs["width"] = self.bar_width_spin.value()
        general_kwargs["horizontal"] = axes_flipped

        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Bar"])
        plot_method(self.data_handler.df, x_col, y_cols, **general_kwargs)

        if axes_flipped:
            self._apply_flipped_labels(x_col, y_cols, font_family)
        
        try:
            if axes_flipped:
                y_data = self.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    y_data,
                    self.data_handler.df[x_col]
                )
            else:
                y_data = self.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[x_col],
                    y_data
                )
        except: pass
    
    def _plot_box_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Box plot plotting strategy"""
        if axes_flipped:
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            self.data_handler.df[y_cols].plot(
                kind="box",
                ax=self.plot_engine.current_ax,
                vert=False,
                **plot_kwargs
            )

            self._apply_flipped_labels(x_col, y_cols, font_family)
        else:
            plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Box"])
            plot_method(self.data_handler.df, y_cols, **general_kwargs)
    
    
    def _plot_histogram_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Histogram plotting generation"""
        if len(y_cols) > 1:
            self.status_bar.log(f"Histogram only supports one column. Using: {y_cols[0]}", "WARNING")
        
        # Use first y_col as the data source
        data_col = y_cols[0]
        general_kwargs["xlabel"] = self.xlabel_input.text() or data_col
        
        general_kwargs["bins"] = self.histogram_bins_spin.value()
        general_kwargs["show_normal"] = self.histogram_show_normal_check.isChecked()
        general_kwargs["show_kde"] = self.histogram_show_kde_check.isChecked()

        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Histogram"])
        plot_method(self.data_handler.df, data_col, **general_kwargs)

        try:
            self._format_datetime_axis(self.plot_engine.current_ax, self.data_handler.df[data_col])
        except: pass
    
    def _plot_violin_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Violin plot"""
        if len(y_cols) > 1:
            self.status_bar.log(f"Violin plots support only one y column. Using {y_cols[0]}")
        
        y_col = y_cols[0]

        if axes_flipped:
            general_kwargs["x"] = y_col
            general_kwargs["y"] = x_col
            general_kwargs["orient"] = "h"
            self._apply_flipped_labels(x_col, [y_col], font_family)
        else:
            general_kwargs["x"] = x_col
            general_kwargs["y"] = y_col
            general_kwargs["orient"] = "v"
        
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Violin"])
        plot_method(self.data_handler.df, **general_kwargs) # Pass x, y, hue, orient

        try:
            if axes_flipped:
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[y_col],
                    self.data_handler.df[x_col]
                )
            else:
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[x_col],
                    self.data_handler.df[y_col]
                )
        except: pass

    def _plot_pie_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Pie chart generaton"""
        y_col = y_cols[0] if y_cols else None
        general_kwargs["show_percentages"] = self.pie_show_percentages_check.isChecked()
        general_kwargs["start_angle"] = self.pie_start_angle_spin.value()
        general_kwargs["explode_first"] = self.pie_explode_check.isChecked()
        general_kwargs["explode_distance"] = self.pie_explode_distance_spin.value()
        general_kwargs["shadow"] = self.pie_shadow_check.isChecked()

        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Pie"])
        plot_method(self.data_handler.df, y_col, x_col, **general_kwargs)

    def _plot_heatmap_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Heatmap plot generation"""
        # Heatmap ignores x/y, uses all numerical columns
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Heatmap"])
        plot_method(self.data_handler.df, **general_kwargs)
    
    def _plot_kde_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Kernel density estimation plot generation"""
        if len(y_cols) > 1:
            self.status_bar.log(f"KDE plot only supports one column. Using: {y_cols[0]}", "WARNING")
        
        data_col = y_cols[0]
        general_kwargs["xlabel"] = self.xlabel_input.text() or data_col
        
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["KDE"])
        plot_method(self.data_handler.df, data_col, **general_kwargs)

        try:
            self._format_datetime_axis(self.plot_engine.current_ax, self.data_handler.df[data_col])
        except: pass
    
    def _plot_count_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Count plot strategy"""
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Count Plot"])
        plot_method(self.data_handler.df, x_col, **general_kwargs)

    def _plot_hexbin_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Hexbin plot generation"""
        if len(y_cols) > 1:
            self.status_bar.log(f"Hexbin plot only supports one y column. Using: {y_cols[0]}", "WARNING")
        
        y_col = y_cols[0] if y_cols else None
        
        if axes_flipped:
            general_kwargs["x"] = y_col
            general_kwargs["y"] = x_col
            self._apply_flipped_labels(x_col, [y_col], font_family)
        else:
            general_kwargs["x"] = x_col
            general_kwargs["y"] = y_col
            
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Hexbin"])
        plot_method(self.data_handler.df, **general_kwargs)

    def _plot_2d_density_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """2d desnity plot generaton"""
        if len(y_cols) > 1:
            self.status_bar.log(f"2D density only supports one y column of values Using: {y_cols[0]}")
        
        y_col = y_cols[0]

        if axes_flipped:
            general_kwargs["x"] = y_col
            general_kwargs["y"] = x_col
            self._apply_flipped_labels(x_col, [y_col], font_family)
            
            try:
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[y_col],
                    self.data_handler.df[x_col]
                )
            except: pass
        else:
            general_kwargs["x"] = x_col
            general_kwargs["y"] = y_col
            
            try:
                self._format_datetime_axis(
                    self.plot_engine.current_ax,
                    self.data_handler.df[x_col],
                    self.data_handler.df[y_col]
                )
            except: pass
            
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["2D Density"])
        plot_method(self.data_handler.df, **general_kwargs)

    def _plot_stem_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Stem plot strategy"""
        if len(y_cols) > 1:
            self.status_bar.log(f"Stem only supports one y column. Using: {y_cols[0]}", "WARNING")
        y_col = y_cols[0]
        
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Stem"])
        plot_method(self.data_handler.df, x_col, y_col, **general_kwargs)
        try:
            self._format_datetime_axis(self.plot_engine.current_ax, self.data_handler.df[x_col], self.data_handler.df[y_col])
        except: pass
    
    def _plot_stackplot_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Stackplot strategy"""
        if len(y_cols) < 2:
            QMessageBox.warning(self, "Warning", "Stackplot requires at least two Y columns.")
            return

        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Stackplot"])
        plot_method(self.data_handler.df, x_col, y_cols, **general_kwargs)
        try:
            self._format_datetime_axis(self.plot_engine.current_ax, self.data_handler.df[x_col])
        except: pass

    def _plot_stairs_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Stairs plot strategy"""
        if len(y_cols) > 1:
            self.status_bar.log(f"Stairs only supports one y column. Using: {y_cols[0]}", "WARNING")
        y_col = y_cols[0]
        
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Stairs"])
        plot_method(self.data_handler.df, x_col, y_col, **general_kwargs)
        try:
            self._format_datetime_axis(self.plot_engine.current_ax, self.data_handler.df[x_col], self.data_handler.df[y_col])
        except: pass
    
    def _plot_eventplot_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Eventplot strategy"""
        
        general_kwargs["xlabel"] = self.xlabel_input.text() or "Value"
        
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["Eventplot"])
        plot_method(self.data_handler.df, y_cols, **general_kwargs)
        try:
        
            self._format_datetime_axis(self.plot_engine.current_ax, self.data_handler.df[y_cols[0]])
        except: pass
    
    def _plot_hist2d_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """2D Histogram strategy"""
        if len(y_cols) > 1:
            self.status_bar.log(f"2D Histogram only supports one y column. Using: {y_cols[0]}", "WARNING")
        y_col = y_cols[0]

        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["2D Histogram"])
        plot_method(self.data_handler.df, x_col, y_col, **general_kwargs)
        try:
            self._format_datetime_axis(self.plot_engine.current_ax, self.data_handler.df[x_col], self.data_handler.df[y_col])
        except: pass

    def _plot_ecdf_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """ECDF strategy"""
        if len(y_cols) > 1:
            self.status_bar.log(f"ECDF only supports one y column. Using: {y_cols[0]}", "WARNING")
        y_col = y_cols[0]
        general_kwargs["xlabel"] = self.xlabel_input.text() or y_col

        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS["ECDF"])
        plot_method(self.data_handler.df, y_col, **general_kwargs)
        try:
            self._format_datetime_axis(self.plot_engine.current_ax, self.data_handler.df[y_col])
        except: pass

    def _plot_gridded_strategy(self, plot_name: str, x_col, y_cols, general_kwargs):
        """Common strategy for plots requiring gridded x, y, z data."""
        if len(y_cols) < 2:
            QMessageBox.warning(self, "Warning", f"{plot_name} requires a Z column. Please select a second Y column (Z-value).")
            return
        
        y_col = y_cols[0] # Y-axis
        z_col = y_cols[1] # Z-axis (color)
        
        general_kwargs["ylabel"] = self.ylabel_input.text() or y_col
        general_kwargs["z"] = z_col
        
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS[plot_name])
        plot_method(self.data_handler.df, x_col, y_col, **general_kwargs)
    
    def _plot_imshow_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_gridded_strategy("Image Show (imshow)", x_col, y_cols, general_kwargs)

    def _plot_pcolormesh_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_gridded_strategy("pcolormesh", x_col, y_cols, general_kwargs)

    def _plot_contour_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_gridded_strategy("Contour", x_col, y_cols, general_kwargs)

    def _plot_contourf_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_gridded_strategy("Contourf", x_col, y_cols, general_kwargs)

    def _plot_vector_strategy(self, plot_name: str, x_col, y_cols, general_kwargs):
        """Common strategy for vector plots (barbs, quiver, streamplot)."""
        if len(y_cols) < 3:
            QMessageBox.warning(self, "Warning", f"{plot_name} requires 3 Y columns: Y-position, U (x-component), V (y-component).")
            return
        
        y_col = y_cols[0]
        u_col = y_cols[1]
        v_col = y_cols[2]
        
        general_kwargs["ylabel"] = self.ylabel_input.text() or y_col
        general_kwargs["u"] = u_col
        general_kwargs["v"] = v_col
        
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS[plot_name])
        plot_method(self.data_handler.df, x_col, y_col, **general_kwargs)
    
    def _plot_barbs_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_vector_strategy("Barbs", x_col, y_cols, general_kwargs)

    def _plot_quiver_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_vector_strategy("Quiver", x_col, y_cols, general_kwargs)

    def _plot_streamplot_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_vector_strategy("Streamplot", x_col, y_cols, general_kwargs)

    def _plot_triangulation_strategy(self, plot_name: str, x_col, y_cols, general_kwargs):
        """Common strategy for unstructured triangulation plots."""
        if len(y_cols) < 2 and plot_name != "Triplot":
            QMessageBox.warning(self, "Warning", f"{plot_name} requires a Z column. Please select a second Y column (Z-axis).")
            return
        elif not y_cols and plot_name == "Triplot":
            QMessageBox.warning(self, "Warning", f"{plot_name} requires a Y column.")
            return

        y_col = y_cols[0] 
        z_col = y_cols[1] if len(y_cols) > 1 else None 
        
        general_kwargs["ylabel"] = self.ylabel_input.text() or y_col
        
        plot_method = getattr(self.plot_engine, self.plot_engine.AVAILABLE_PLOTS[plot_name])

        if plot_name == "Triplot":
            plot_method(self.data_handler.df, x_col, y_col, **general_kwargs)
        else:
            if not z_col: 
                return
            general_kwargs["z"] = z_col
            plot_method(self.data_handler.df, x_col, y_col, **general_kwargs)
        
    def _plot_tricontour_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_triangulation_strategy("Tricontour", x_col, y_cols, general_kwargs)

    def _plot_tricontourf_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_triangulation_strategy("Tricontourf", x_col, y_cols, general_kwargs)

    def _plot_tripcolor_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_triangulation_strategy("Tripcolor", x_col, y_cols, general_kwargs)

    def _plot_triplot_strategy(self, x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        self._plot_triangulation_strategy("Triplot", x_col, y_cols, general_kwargs)

    def _apply_flipped_labels(self, x_col, y_cols, font_family):
        """Helper function to correctly apply labels when flipping axes"""
        
        # Flipped: X-axis label (from UI) goes to Y-axis (on plot)
        if self.xlabel_check.isChecked():
            ylabel_to_use = self.xlabel_input.text() or x_col
            self.plot_engine.current_ax.set_ylabel(
                ylabel_to_use,
                fontsize=self.xlabel_size_spin.value(), # Use X label's size
                fontweight=self.xlabel_weight_combo.currentText(), # Use X label's weight
                fontfamily=font_family
            )
        
        # Flipped: Y-axis label (from UI) goes to X-axis (on plot)
        if self.ylabel_check.isChecked():
            xlabel_to_use = self.ylabel_input.text() or (y_cols[0] if len(y_cols) == 1 else str(y_cols))
            self.plot_engine.current_ax.set_xlabel(
                xlabel_to_use,
                fontsize=self.ylabel_size_spin.value(), # Use Y label's size
                fontweight=self.ylabel_weight_combo.currentText(), # Use Y label's weight
                fontfamily=font_family
            )
        
        if self.title_check.isChecked():
            title_to_use = self.title_input.text() if self.title_input.text() else self.plot_type.currentText()
            self.plot_engine.current_ax.set_title(
                title_to_use,
                fontsize=self.title_size_spin.value(),
                fontweight=self.title_weight_combo.currentText(),
                fontfamily=font_family
            )
    
    def generate_plot(self):
        """Generate plot based on current settings"""
        if self.data_handler.df is None:
            self.status_bar.log("No data loaded", "WARNING")
            QMessageBox.warning(self, "Warning", "No data loaded")
            return
        
        # get active dataframe
        active_df = self.get_active_dataframe()

        if active_df is None or len(active_df) == 0:
            QMessageBox.warning(self, "Warning", "Selected subset is empty")
            return
        
        active_df = active_df.copy()
        x_col = self.x_column.currentText()
        y_cols = self.get_selected_y_columns()

        try:
            if x_col and self.is_datetime_column(active_df[x_col]):
                if not pd.api.types.is_datetime64_any_dtype(active_df[x_col]):
                    active_df[x_col] = pd.to_datetime(active_df[x_col], utc=True, errors="coerce")
                    self.status_bar.log(f"Converted column: '{x_col}' to datetime", "INFO")
            
            for y_col in y_cols:
                if y_col and self.is_datetime_column(active_df[y_col]):
                    if not pd.api.types.is_datetime64_any_dtype(active_df[y_col]):
                        active_df[y_col] = pd.to_datetime(active_df[y_col], utc=True, errors="coerce")
                        self.status_bar.log(f"Converted column: '{y_col}' to datetime", "INFO")
        except Exception as e:
            self.status_bar.log(f"Warning: Could not convert datetime columns: {str(e)}", "WARNING")
        
        # check dataset size
        data_size = len(self.data_handler.df)
        show_progress = data_size > 100

        progress_dialog = None

        try:
            #init
            if show_progress:
                progress_dialog = ProgressDialog(
                    title="Generating Plot",
                    message=f"Processing {data_size:,} data points",
                    parent=self
                )
                progress_dialog.show()
                progress_dialog.update_progress(5, "Initializing plotting engine")
                QApplication.processEvents()
            
            #get init params
            plot_type = self.plot_type.currentText()
            x_col = self.x_column.currentText()
            y_cols = self.get_selected_y_columns()

            # Validation ---
            plots_no_x = ["Box", "Histogram", "KDE", "Heatmap", "Pie", "ECDF", "Eventplot"]
            plots_no_y = ["Count Plot", "Heatmap"]
            plots_gridded = ["Image Show (imshow)", "pcolormesh", "Contour", "Contourf"]
            plots_vector = ["Barbs", "Quiver", "Streamplot"]
            plots_triangulation_z = ["Tricontour", "Tricontourf", "Tripcolor"]
            plots_triangulation_no_z = ["Triplot"]

            if not x_col and plot_type not in plots_no_x:
                QMessageBox.warning(self, "Warning", f"Please select an X column for {plot_type}.")
                return
            if not y_cols and plot_type not in plots_no_y:
                QMessageBox.warning(self, "Warning", f"Please select at least one Y column for {plot_type}.")
                return

            if plot_type in plots_gridded and len(y_cols) < 2:
                QMessageBox.warning(self, "Warning", f"{plot_type} requires 2 Y columns: (Y-position, Z-value).")
                return
            if plot_type in plots_vector and len(y_cols) < 3:
                QMessageBox.warning(self, "Warning", f"{plot_type} requires 3 Y columns: (Y-position, U-component, V-component).")
                return
            if plot_type in plots_triangulation_z and len(y_cols) < 2:
                QMessageBox.warning(self, "Warning", f"{plot_type} requires 2 Y columns: (Y-position, Z-value).")
                return
            if plot_type in plots_triangulation_no_z and len(y_cols) < 1:
                QMessageBox.warning(self, "Warning", f"{plot_type} requires at least one Y column (Y-position).")
                return

            hue = self.hue_column.currentText() if self.hue_column.currentText() != "None" else None
            axes_flipped = self.flip_axes_check.isChecked()
            font_family = self.font_family_combo.currentFont().family()

            if show_progress:
                progress_dialog.update_progress(10, "Preparing data")
                if progress_dialog.is_cancelled():
                    self.status_bar.log("Plot generation cancelled", "WARNING")
                    return
            
            #build kwargs
            plots_supporting_hue = ["Scatter", "Line", "Bar", "Violin", "2D Density", "Box", "Count Plot"]
            
            y_label_text = str(y_cols)
            if len(y_cols) == 1:
                y_label_text = y_cols[0]

            #handling specific y col plots roles
            if plot_type in plots_gridded:
                y_label_text = y_cols[0]
            elif plot_type in plots_vector:
                y_label_text = y_cols[0]
            elif plot_type in plots_triangulation_z or plot_type in plots_triangulation_no_z:
                y_label_text = y_cols[0]
            elif plot_type in plots_no_x:
                y_label_text = y_cols[0] if y_cols else "Value"

            general_kwargs = {
                "title": self.title_input.text() if self.title_input.text() else plot_type,
                "xlabel": self.xlabel_input.text() or x_col,
                "ylabel": self.ylabel_input.text() or y_label_text,
                "legend": self.legend_check.isChecked(),
            }

            if hue and plot_type in plots_supporting_hue:
                general_kwargs["hue"] = hue
            
            # plot specific kwargs
            plot_kwargs = {}

            if show_progress:
                progress_dialog.update_progress(20, "Building plot configurations")
                if progress_dialog.is_cancelled():
                    self.status_bar.log("Plot generation cancelled", "WARNING")
                    return
            
            #clear and setup
            if show_progress:
                progress_dialog.update_progress(30, "Clearing previous plot")
                if progress_dialog.is_cancelled():
                    return
                
            self.plot_engine.clear_plot()
            # Reset figure-level properties
            self.plot_engine.current_figure.set_size_inches(self.width_spin.value(), self.height_spin.value())
            self.plot_engine.current_figure.set_dpi(self.dpi_spin.value())
            self.plot_engine.current_figure.set_facecolor(self.bg_color)
            
            # Apply style
            try:
                plt.style.use(self.style_combo.currentText())
                # Re-apply facecolor after style, as style might override it
                self.plot_engine.current_figure.set_facecolor(self.bg_color)
                self.plot_engine.current_ax.set_facecolor(self.face_color)
            except Exception as e:
                self.status_bar.log(f"Could not apply style: {e}", "WARNING")
                self.plot_engine.current_ax.set_facecolor(self.face_color)


            if show_progress:
                progress_dialog.update_progress(35, "Setting plot style")
                if progress_dialog.is_cancelled():
                        return
                
            # auto set X/Y TICKs
            if not self.x_auto_check.isChecked():
                self.plot_engine.current_ax.set_xlim(self.x_min_spin.value(), self.x_max_spin.value())
            if not self.y_auto_check.isChecked():
                self.plot_engine.current_ax.set_ylim(self.y_min_spin.value(), self.y_max_spin.value())

            #set axes scale to current
            self.plot_engine.current_ax.set_xscale(self.x_scale_combo.currentText())
            self.plot_engine.current_ax.set_yscale(self.y_scale_combo.currentText())

            #dispatch to plotting strategy
            if show_progress:
                progress_dialog.update_progress(40, f"Creating {plot_type} plot")
                if progress_dialog.is_cancelled():
                    return
            
            #call strategy
            if plot_type in self.plot_strategies:
                # use the active df
                original_df = self.data_handler.df
                self.data_handler.df = active_df
                try:
                    self.plot_strategies[plot_type](x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs)
                finally:
                    #restore original dataframe
                    self.data_handler.df = original_df
            else:
                raise ValueError(f"Unknown plot type: {plot_type}")

            # apply tick marks
            try:
                self.plot_engine.current_ax.xaxis.set_major_locator(MaxNLocator(nbins=self.x_max_ticks_spin.value()))
                self.plot_engine.current_ax.yaxis.set_major_locator(MaxNLocator(nbins=self.y_max_ticks_spin.value()))
            except: pass

            if show_progress:
                progress_dialog.update_progress(70, "Applying formatting")
                if progress_dialog.is_cancelled():
                    return
            
            # ==== FORMATTING ====
            if not axes_flipped:
                self._apply_plot_appearance(x_col, y_cols, font_family, general_kwargs)

            
            if show_progress:
                progress_dialog.update_progress(75, "Applying customizations")
                if progress_dialog.is_cancelled():
                    return
            
            # apply customization
            self._apply_plot_customizations()

            if show_progress:
                progress_dialog.update_progress(80, "Adding legend and gridlines")
                if progress_dialog.is_cancelled():
                    return
            
            #legend
            # Only apply legend if it wasn't disabled by general_kwargs
            if general_kwargs.get("legend", True):
                self._apply_legend(font_family)
            elif self.plot_engine.current_ax.get_legend():
                self.plot_engine.current_ax.get_legend().set_visible(False)


            #gridlines
            if self.grid_check.isChecked():
                self._apply_gridlines_customizations()
            else:
                self.plot_engine.current_ax.grid(False) # Explicitly turn off

            # spines
            self._apply_spines_customization()
            
            if show_progress:
                progress_dialog.update_progress(85, "Adding annotations")
                if progress_dialog.is_cancelled():
                    return
            
            #annotations
            self._apply_annotations()

            # tick customization
            self._apply_tick_customization()

            # text box
            self._apply_textbox()

            if show_progress:
                progress_dialog.update_progress(95, "Finalizing")
                if progress_dialog.is_cancelled():
                    return
            
            # tight layout
            try:
                if self.tight_layout_check.isChecked():
                    self.plot_engine.current_figure.tight_layout()
            except Exception as e:
                # Can fail, e.g., with pie charts
                self.status_bar.log(f"Tight layout failed: {e}", "WARNING")

            
            #refresh
            self.canvas.draw()

            if show_progress:
                progress_dialog.update_progress(100, "Complete")
                QTimer.singleShot(300, progress_dialog.accept)
            
            # logging====
            plot_details = {
                "plot_type": plot_type,
                "x_column": x_col,
                "y_column": str(y_cols),
                "data_points": len(self.data_handler.df),
                "annotations": len(self.annotations)
            }

            if hue:
                plot_details["hue"] = hue

            #add subset info
            if self.use_subset_check.isChecked():
                subset_name = self.subset_combo.currentData()
                if subset_name:
                    plot_details["subset"] = subset_name
                    plot_details["subset_rows"] = len(active_df)
                    plot_details["total_rows"] = len(self.data_handler.df)

            status_msg = f"{plot_type} plot created"
            if self.use_subset_check.isChecked() and subset_name:
                status_msg += f" (Subset: {subset_name})"
            if len(self.annotations) > 0:
                status_msg += f" with {len(self.annotations)} annotations"
            
            self.status_bar.log_action(
                status_msg,
                details=plot_details,
                level="SUCCESS"
            )
        
        except Exception as e:
            if progress_dialog:
                progress_dialog.accept()
            QMessageBox.critical(self, "Error", f"Failed to generate plot: {str(e)}")
            self.status_bar.log(f"Plot generation failed: {str(e)}", "ERROR")
            traceback.print_exc()
        finally:
            if progress_dialog and progress_dialog.isVisible():
                progress_dialog.accept()
            
    def _apply_plot_appearance(self, x_col, y_cols, font_family, general_kwargs):
        """Apply title, fonts, and labels settings from the Appearance Tab"""
        # apply fonts to ticks
        for label in self.plot_engine.current_ax.get_xticklabels():
            label.set_fontfamily(font_family)
        for label in self.plot_engine.current_ax.get_yticklabels():
            label.set_fontfamily(font_family)

        # title
        if self.title_check.isChecked():
            title_text = self.title_input.text() or general_kwargs.get("title", "Plot")
            self.plot_engine.current_ax.set_title(
                title_text, 
                fontsize=self.title_size_spin.value(), 
                fontweight=self.title_weight_combo.currentText(), 
                fontfamily=font_family
            )
        else:
            #clear title
            self.plot_engine.current_ax.set_title("")
        
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
            # Note: marker size for scatter is often set with 's' in the plot call
            # This is a global override, which might be too broad.
            # collection.set_sizes([marker_size**2]) 
        
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
            return # No legend to show

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
        except Exception as e:
            self.status_bar.log(f"Failed to apply legend: {e}", "WARNING")

    
    def _apply_annotations(self):
        """Apply text annotations"""
        for ann in self.annotations:
            self.plot_engine.current_ax.text(
                ann["x"], ann["y"], ann["text"],
                transform=self.plot_engine.current_ax.transAxes,
                fontsize=ann["fontsize"],
                color=ann["color"],
                ha="center", va="center",
                bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5)
            )

    def _apply_gridlines_customizations(self) -> None:
        """Apply gridlines customizations"""
        if not self.grid_check.isChecked():
            self.plot_engine.current_ax.grid(False)
            return
        
        # Ensure grid is on, but we'll style it below
        self.plot_engine.current_ax.grid(True)
        
        if self.independent_grid_check.isChecked():
            # --- INDEPENDENT ---
            
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
            # --- GLOBAL ---
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

    def _apply_spines_customization(self):
        """Apply spines customization t the current ax"""
        if not self.plot_engine.current_ax:
            return
        
        try:
            #get the spines
            spines = self.plot_engine.current_ax.spines

            #top spine
            if self.top_spine_visible_check.isChecked():
                spines["top"].set_visible(True)
                spines["top"].set_linewidth(self.top_spine_width_spin.value())
                spines["top"].set_edgecolor(self.top_spine_color)
            else:
                spines["top"].set_visible(False)
            
            #bottom spine
            if self.bottom_spine_visible_check.isChecked():
                spines["bottom"].set_visible(True)
                spines["bottom"].set_linewidth(self.bottom_spine_width_spin.value())
                spines["bottom"].set_edgecolor(self.bottom_spine_color)
            else:
                spines["bottom"].set_visible(False)
            
            #left spine
            if self.left_spine_visible_check.isChecked():
                spines["left"].set_visible(True)
                spines["left"].set_linewidth(self.left_spine_width_spin.value())
                spines["left"].set_edgecolor(self.left_spine_color)
            else:
                spines["left"].set_visible(False)
            
            #right spine
            if self.right_spine_visible_check.isChecked():
                spines["right"].set_visible(True)
                spines["right"].set_linewidth(self.right_spine_width_spin.value())
                spines["right"].set_edgecolor(self.right_spine_color)
            else:
                spines["right"].set_visible(False)
        
        except Exception as e:
            self.status_bar.log(f"Failed to apply spine customization: {str(e)}", "ERROR")


    def clear_plot(self) -> None:
        """Clear the plot"""
        self.plot_engine.clear_plot()
        self.canvas.draw()
        
        # Clear customizations
        self.line_customizations.clear()
        self.bar_customizations.clear()
        self.annotations.clear()
        self.annotations_list.clear()
        
        self.status_bar.log_action(
            "Plot cleared",
            details={'operation': 'clear_plot'},
            level="INFO"
        )
    
    def load_config(self, config: dict) -> None:
        """Load plot configuration"""
        self.current_config = config
        self.status_bar.log("Plot Config Loaded", "INFO")
    
    def get_config(self) -> Dict[str, Any]:
        """Get current plot configuration"""
        config = {
            "version": 1.0,
            "plot_type": self.plot_type.currentText(),
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
            "subset_name": self.subset_combo.currentData()
        }

    def _get_appearance_config(self) -> Dict[str, Any]:
        """Config for the appearance tab"""
        return {
            "font_family": self.font_family_combo.currentFont().family(),
            "title": {
                "enabled": self.title_check.isChecked(),
                "text": self.title_input.text(),
                "size": self.title_size_spin.value(),
                "weight": self.title_weight_combo.currentText(),
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
            }
        }

    def clear(self) -> None:
        """Clear all plot data"""
        self.clear_plot()
        self.title_input.clear()
        self.xlabel_input.clear()
        self.ylabel_input.clear()

    def _add_regression_analysis(self, x_col: str, y_col: str, flipped: bool = False) -> None:
        try:
            import numpy as np
            from scipy import stats

            df = self.data_handler.df

            # Remove NaN/Inf values from both columns
            mask = np.isfinite(df[x_col]) & np.isfinite(df[y_col])
            x_data = df.loc[mask, x_col].values
            y_data = df.loc[mask, y_col].values

            if len(x_data) < 2:
                self.status_bar.log("Not enough data points to perform regressional analysis", "WARNING")
                return
            
            # perform linreg
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)

            # generate regression line
            x_line = np.linspace(x_data.min(), x_data.max(), 100)
            y_line = slope * x_line + intercept


            # plot regression line
            if self.regression_line_check.isChecked():
                plot_args = (x_line, y_line) if not flipped else (y_line, x_line)
                reg_line = self.plot_engine.current_ax.plot(
                    *plot_args, 
                    color="red", linestyle="-", linewidth=2, 
                    label=f"Linear Fit", alpha=0.5
                )[0]
                reg_line.set_gid("regression_line")
            
            # calculate confidence interval
            if self.confidence_interval_check.isChecked():
                confidence = self.confidence_level_spin.value() / 100.0
                
                # standard error of the fit
                residuals = y_data - (slope * x_data + intercept)
                n = len(x_data)
                residual_std = np.sqrt(np.sum(residuals**2) / (n - 2))

                #std eror for each prediction
                x_mean = np.mean(x_data)
                se_line = residual_std * np.sqrt(1/n + (x_line - x_mean)**2 / np.sum((x_data - x_mean)**2))

                from scipy.stats import t as t_dist
                t_val = t_dist.ppf((1 + confidence) / 2, n - 2)
                margin = t_val * se_line
                
                fill_args = (x_line, y_line - margin, y_line + margin) if not flipped else (y_line - margin, y_line + margin, x_line)

                if not flipped:
                    ci_poly = self.plot_engine.current_ax.fill_between(
                        fill_args[0], fill_args[1], fill_args[2],
                        color="red", alpha=0.15, label=f"{int(confidence*100)}% CI", zorder=-1
                    )
                else:
                    ci_poly = self.plot_engine.current_ax.fill_betweenx(
                        fill_args[2], fill_args[0], fill_args[1], # y, x1, x2
                        color="red", alpha=0.15, label=f"{int(confidence*100)}% CI", zorder=-1
                    )
                ci_poly.set_gid("confidence_interval")

            # calculate rmse
            y_pred = slope * x_data + intercept
            rmse = np.sqrt(np.mean((y_data - y_pred)**2))

            #b uild stats text
            stats_text = []
            
            eq_x_label = "y" if flipped else "x"
            eq_y_label = "x" if flipped else "y"


            if self.show_equation_check.isChecked():
                if intercept >= 0:
                    stats_text.append(f'{eq_y_label} = {slope:.4f}{eq_x_label} + {intercept:.4f}')
                else:
                    stats_text.append(f'{eq_y_label} = {slope:.4f}{eq_x_label} - {abs(intercept):.4f}')
            
            if self.show_r2_check.isChecked():
                stats_text.append(f"R² = {r_value**2:.4f}")
            
            if self.show_rmse_check.isChecked():
                stats_text.append(f"RMSE = {rmse:.4f}")
            
            #display on plot
            if stats_text:
                textstr = "\n".join(stats_text)
                props = dict(boxstyle="round", facecolor="wheat", alpha=0.85, edgecolor="black", linewidth=1)
                font_family = self.font_family_combo.currentFont().family()

                self.plot_engine.current_ax.text(0.05, 0.95, textstr, transform=self.plot_engine.current_ax.transAxes, fontsize=11, verticalalignment='top', bbox=props, fontfamily=font_family, zorder=15)
            
            #add errorbars
            error_bar_type = self.error_bars_combo.currentText()
            if error_bar_type == "Standard Deviation":
                # calculate residuals
                y_pred_all = slope * x_data + intercept
                residuals = y_data - y_pred_all

                # calculate std in bins
                n_bins = min(20, len(x_data) // 5)
                if n_bins > 1: # Need at least 2 bins
                    # sort by x vals
                    sorted_indices = np.argsort(x_data)
                    x_sorted = x_data[sorted_indices]
                    y_sorted = y_data[sorted_indices]
                    residuals_sorted = residuals[sorted_indices]

                    # calc std bins
                    bin_size = len(x_data) // n_bins
                    x_centers = []
                    y_centers = []
                    y_errors = []

                    for i in range(n_bins):
                        start = i * bin_size
                        end = start + bin_size if i < n_bins - 1 else len(x_data)

                        if end - start > 1: 
                            x_centers.append(np.mean(x_sorted[start:end]))
                            y_centers.append(np.mean(y_sorted[start:end]))
                            y_errors.append(np.std(residuals_sorted[start:end]))
                    
                    if x_centers:
                        err_args = (x_centers, y_centers)
                        err_kwargs = {"yerr": y_errors} if not flipped else {"xerr": y_errors}
                        
                        self.plot_engine.current_ax.errorbar(
                            *err_args, **err_kwargs,
                            fmt="o", markersize=3, ecolor="gray", alpha=0.5, 
                            capsize=4, zorder=8, markerfacecolor="none", 
                            markeredgecolor="gray", linestyle="none"
                        )
            
            elif error_bar_type == "Standard Error":
                y_pred_all = slope * x_data + intercept
                residuals = y_data - y_pred_all
                residual_std = np.sqrt(np.sum(residuals**2) / (len(x_data) - 2))

                #se for each xvals
                x_mean = np.mean(x_data)
                se_points = residual_std * np.sqrt(1/len(x_data) + (x_data - x_mean)**2 / np.sum((x_data - x_mean)**2))

                # sample points
                step = max(1, len(x_data) // 30)
                
                err_args = (x_data[::step], y_data[::step])
                err_kwargs = {"yerr": se_points[::step]} if not flipped else {"xerr": se_points[::step]}
                
                self.plot_engine.current_ax.errorbar(
                    *err_args, **err_kwargs,
                    fmt="none", ecolor="gray", markersize=3, alpha=0.5, 
                    capsize=4, zorder=8, markerfacecolor="none", 
                    markeredgecolor="none", elinewidth=1, 
                    linestyle="none"
                )

            self.status_bar.log(
                f"✓ Regression: R²={r_value**2:.4f}, RMSE={rmse:.4f}, slope={slope:.4f}, p={p_value:.4e}",
                "SUCCESS"
            )
        
        except Exception as e:
            self.status_bar.log(f"Regression analysis failed: {str(e)}", "ERROR")
            import traceback
            print(f"Regression error: {traceback.format_exc()}") 