from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

try:
    import geopandas as gpd
except ImportError:
    gpd = None

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class GeoSpatialPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        if gpd is None:
            return "GeoPandas library not found. Please install it first (`pip install geopandas`) to use geospatial plotting functions."
        df = plot_tab.data_handler.df
        
        if "geometry" not in df.columns:
            return "DataFrame does not contain a 'geometry' column needed to create a geospatial plot."
        
        try:
            gdf = gpd.GeoDataFrame(df, geometry="geometry")
        except Exception as LoadGeoDataFrameError:
            return f"Failed to create GeoDataFrame: {str(LoadGeoDataFrameError)}"
        
        plot_col = y_cols[0] if y_cols else None

        if plot_col:
            general_kwargs["column"] = plot_col
        
        general_kwargs["orientation"] = plot_tab.geo_legend_loc_combo.currentText()
        general_kwargs["use_divider"] = plot_tab.geo_use_divider_check.isChecked()
        general_kwargs["cax_enabled"] = plot_tab.geo_cax_check.isChecked()
        general_kwargs["axis_off"] = plot_tab.geo_axis_off_check.isChecked()
        
        scheme = plot_tab.geo_scheme_combo.currentText()
        if plot_col and scheme != "None":
            general_kwargs["scheme"] = scheme
            general_kwargs["k"] = plot_tab.geo_k_spin.value()

        general_kwargs["edgecolor"] = plot_tab.geo_edge_color
        general_kwargs["linewidth"] = plot_tab.geo_linewidth_spin.value()
        
        if plot_tab.geo_boundary_check.isChecked():
            general_kwargs["facecolor"] = "none"
        
        if plot_kwargs:
            general_kwargs.update(plot_kwargs)
        
        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["GeoSpatial"])
        
        plot_method(gdf, **general_kwargs)

        return None