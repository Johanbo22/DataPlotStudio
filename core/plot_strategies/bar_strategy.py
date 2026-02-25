from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class BarPlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        general_kwargs["width"] = plot_tab.bar_width_spin.value()
        general_kwargs["horizontal"] = axes_flipped

        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Bar"])
        plot_method(plot_tab.data_handler.df, x_col, y_cols, **general_kwargs)

        if axes_flipped:
            engine._helper_apply_flipped_labels(plot_tab, x_col, y_cols, font_family)
        
        try:
            if axes_flipped:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    y_data,
                    plot_tab.data_handler.df[x_col]
                )
            else:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    plot_tab.data_handler.df[x_col],
                    y_data
                )
        except: pass
        return None