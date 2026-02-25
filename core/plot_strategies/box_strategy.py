from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab
    
class BoxPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        if axes_flipped:
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            plot_tab.data_handler.df[y_cols].plot(
                kind="box",
                ax=engine.current_ax,
                vert=False,
                **plot_kwargs
            )

            engine._helper_apply_flipped_labels(plot_tab, x_col, y_cols, font_family)
        else:
            plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Box"])
            plot_method(plot_tab.data_handler.df, y_cols, **general_kwargs)
        return None