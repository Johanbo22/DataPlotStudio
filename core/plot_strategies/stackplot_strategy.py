from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class StackPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        if len(y_cols) < 2:
            return "Stackplot requires at least two Y columns."

        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Stackplot"])
        plot_method(plot_tab.data_handler.df, x_col, y_cols, **general_kwargs)
        try:
            engine._helper_format_datetime_axis(plot_tab, engine.current_ax, plot_tab.data_handler.df[x_col])
        except: pass
        return None