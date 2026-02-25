from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class HeatmapPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        # Heatmap ignores x/y, uses all numerical columns
        general_kwargs.update(plot_kwargs)
        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Heatmap"])
        plot_method(plot_tab.data_handler.df, **general_kwargs)
        return None