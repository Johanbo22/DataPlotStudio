from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_strategies.base_strategy import BasePlotStrategy

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class LinePlotStrategy(BasePlotStrategy):
    """Strategy for generating Line plots."""

    def execute(
        self,
        engine: 'PlotEngine',
        plot_tab: 'PlotTab',
        x_col: str,
        y_cols: List[str],
        axes_flipped: bool,
        font_family: str,
        plot_kwargs: Dict[str, Any],
        general_kwargs: Dict[str, Any]
    ) -> Optional[str]:
        
        if axes_flipped:
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            for col in y_cols:
                engine.current_ax.plot(
                    plot_tab.data_handler.df[col],
                    plot_tab.data_handler.df[x_col],
                    label=col,
                    **plot_kwargs
                )
            
            engine._helper_apply_flipped_labels(plot_tab, x_col, y_cols, font_family)
            if len(y_cols) > 1 or general_kwargs.get("hue"):
                engine.current_ax.legend()
            
            try:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    y_data,
                    plot_tab.data_handler.df[x_col]
                )
            except Exception: 
                pass
        else:
            plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Line"])
            plot_method(plot_tab.data_handler.df, x_col, y_cols, **general_kwargs)

            try:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    plot_tab.data_handler.df[x_col],
                    y_data
                )
            except Exception: 
                pass
                
        return None