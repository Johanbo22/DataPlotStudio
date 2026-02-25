from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class HistogramPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"Histogram only supports one column. Using: {y_cols[0]}", "WARNING")
        
        # Use first y_col as the data source
        data_col = y_cols[0]
        general_kwargs["xlabel"] = plot_tab.xlabel_input.text() or data_col
        
        general_kwargs["bins"] = plot_tab.histogram_bins_spin.value()
        general_kwargs["show_normal"] = plot_tab.histogram_show_normal_check.isChecked()
        general_kwargs["show_kde"] = plot_tab.histogram_show_kde_check.isChecked()

        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Histogram"])
        plot_method(plot_tab.data_handler.df, data_col, **general_kwargs)

        try:
            engine._helper_format_datetime_axis(plot_tab, engine.current_ax, plot_tab.data_handler.df[data_col])
        except: pass
        return None