from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class KDEPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"KDE plot only supports one column. Using: {y_cols[0]}", "WARNING")
        
        data_col = y_cols[0]
        general_kwargs["xlabel"] = plot_tab.xlabel_input.text() or data_col
        
        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["KDE"])
        plot_method(plot_tab.data_handler.df, data_col, **general_kwargs)

        try:
            engine._helper_format_datetime_axis(plot_tab, engine.current_ax, plot_tab.data_handler.df[data_col])
        except: pass
        return None