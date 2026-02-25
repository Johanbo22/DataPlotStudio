from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class PiePlotStrategy(BasePlotStrategy):
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        y_col = y_cols[0] if y_cols else None
        general_kwargs["show_percentages"] = plot_tab.pie_show_percentages_check.isChecked()
        general_kwargs["start_angle"] = plot_tab.pie_start_angle_spin.value()
        general_kwargs["explode_first"] = plot_tab.pie_explode_check.isChecked()
        general_kwargs["explode_distance"] = plot_tab.pie_explode_distance_spin.value()
        general_kwargs["shadow"] = plot_tab.pie_shadow_check.isChecked()

        plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Pie"])
        plot_method(plot_tab.data_handler.df, y_col, x_col, **general_kwargs)
        return None