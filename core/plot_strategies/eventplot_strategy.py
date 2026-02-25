from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class EventplotPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        general_kwargs["xlabel"] = plot_tab.xlabel_input.text() or "Value"
        
        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Eventplot"])
        plot_method(plot_tab.data_handler.df, y_cols, **general_kwargs)
        try:
        
            engine._helper_format_datetime_axis(plot_tab, engine.current_ax, plot_tab.data_handler.df[y_cols[0]])
        except: pass
        return None