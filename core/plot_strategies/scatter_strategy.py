from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab
    
class ScatterPlotStrategy(BasePlotStrategy):
    
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        import seaborn as sns
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"Scatter only supports one y column. Using: {y_cols[0]}", "WARNING")
        
        y_col = y_cols[0]

        if axes_flipped:
            hue_val = general_kwargs.pop("hue", None)
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)

            if hue_val:
                # Use seaborn for hue logic
                sns.scatterplot(
                    data=plot_tab.data_handler.df,
                    x=y_col,
                    y=x_col,
                    hue=hue_val,
                    ax=engine.current_ax,
                    **plot_kwargs
                )
            else:
                engine.current_ax.scatter(
                    plot_tab.data_handler.df[y_col],
                    plot_tab.data_handler.df[x_col],
                    **plot_kwargs
                )

            engine._helper_apply_flipped_labels(plot_tab, x_col, [y_col], font_family)
            
            #datetime
            try:
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    plot_tab.data_handler.df[y_col],
                    plot_tab.data_handler.df[x_col]
                )
            except: pass
        else:
            plot_method = getattr(engine, engine.AVAILABLE_PLOTS["Scatter"])
            plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)

            #datetime
            try:
                engine._helper_format_datetime_axis(
                    plot_tab,
                    engine.current_ax,
                    plot_tab.data_handler.df[x_col],
                    plot_tab.data_handler.df[y_col]
                )
            except: pass

        #Regression analysis - Run after plotting, handle flipped axes inside
        if (plot_tab.regression_line_check.isChecked() or plot_tab.show_r2_check.isChecked() or 
            plot_tab.show_rmse_check.isChecked() or plot_tab.show_equation_check.isChecked() or 
            plot_tab.error_bars_combo.currentText() != "None"):
            
            if axes_flipped:
                engine._helper_add_regression_analysis(plot_tab, y_col, x_col, flipped=True)
            else:
                engine._helper_add_regression_analysis(plot_tab, x_col, y_col, flipped=False)
        return None