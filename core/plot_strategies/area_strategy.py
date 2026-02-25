from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class AreaPlotStrategy(BasePlotStrategy):
    
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        if axes_flipped:
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            for col in y_cols:
                engine.current_ax.fill_betweenx(
                    plot_tab.data_handler.df[x_col],
                    0,
                    plot_tab.data_handler.df[col],
                    label=col,
                    alpha=plot_tab.alpha_slider.value() # Default alpha for area
                )
            
            engine._helper_apply_flipped_labels(plot_tab, x_col, y_cols, font_family)
            if len(y_cols) > 1:
                engine.current_ax.legend()
            
            #datetime
            try:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    y_data,
                    plot_tab.data_handler.df[x_col]
                )
            except: pass
        else:
            #normal orientation
            plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Area"])
            plot_method(plot_tab.data_handler.df, x_col, y_cols, **general_kwargs)

            #datetime
            try:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    plot_tab.data_handler.df[x_col],
                    y_data
                )
            except: pass
        return None