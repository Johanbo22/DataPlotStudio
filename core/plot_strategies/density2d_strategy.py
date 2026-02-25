from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class Density2DPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"2D density only supports one y column of values Using: {y_cols[0]}")
        
        y_col = y_cols[0]

        if axes_flipped:
            general_kwargs["x"] = y_col
            general_kwargs["y"] = x_col
            engine._helper_apply_flipped_labels(plot_tab, x_col, [y_col], font_family)
            
            try:
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    plot_tab.data_handler.df[y_col],
                    plot_tab.data_handler.df[x_col]
                )
            except: pass
        else:
            general_kwargs["x"] = x_col
            general_kwargs["y"] = y_col
            
            try:
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    plot_tab.data_handler.df[x_col],
                    plot_tab.data_handler.df[y_col]
                )
            except: pass
        
        general_kwargs.update(plot_kwargs)
        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["2D Density"])
        plot_method(plot_tab.data_handler.df, **general_kwargs)
        return None