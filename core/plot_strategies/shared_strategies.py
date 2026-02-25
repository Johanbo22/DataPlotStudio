from abc import abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any, Optional
from core.plot_engine import PlotEngine
from core.plot_strategies.base_strategy import BasePlotStrategy
from ui.plot_tab import PlotTab

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab

class GriddedPlotStrategy(BasePlotStrategy):
    """Base strategy for plots requireing gridded data"""
    @property
    @abstractmethod
    def plot_name(self) -> str:
        pass
    
    def execute(self, engine: PlotEngine, plot_tab: PlotTab, x_col: str, y_cols: List[str], axes_flipped: bool, font_family: str, plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]) -> str | None:
        if len(y_cols) < 2:
            return f"{self.plot_name} requires a Z column. Please select a second Y column (Z-value)."
        
        y_col = y_cols[0] # Y-axis
        z_col = y_cols[1] # Z-axis (color)
        
        general_kwargs["ylabel"] = plot_tab.ylabel_input.text() or y_col
        general_kwargs["z"] = z_col

        if plot_kwargs:
            general_kwargs.update(plot_kwargs)
        
        plot_method = getattr(engine, engine.AVAILABLE_PLOTS[self.plot_name])
        plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        return None

class VectorPlotStrategy(BasePlotStrategy):
    """Base strategy for vector fields requiring (X, Y, U, V)."""
    
    @property
    @abstractmethod
    def plot_name(self) -> str:
        pass

    def execute(
        self, engine: 'PlotEngine', plot_tab: 'PlotTab', x_col: str, 
        y_cols: List[str], axes_flipped: bool, font_family: str, 
        plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]
    ) -> Optional[str]:
        
        if len(y_cols) < 3:
            return f"{self.plot_name} requires 3 Y columns: Y-position, U (x-component), V (y-component)."
        
        y_col = y_cols[0]
        u_col = y_cols[1]
        v_col = y_cols[2]
        
        general_kwargs["ylabel"] = plot_tab.ylabel_input.text() or y_col
        general_kwargs["u"] = u_col
        general_kwargs["v"] = v_col

        if plot_kwargs:
            general_kwargs.update(plot_kwargs)
        
        plot_method = getattr(engine, engine.AVAILABLE_PLOTS[self.plot_name])
        plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        
        return None

class TriangulationPlotStrategy(BasePlotStrategy):
    """Base strategy for unstructured triangulation plots."""
    
    @property
    @abstractmethod
    def plot_name(self) -> str:
        pass

    def execute(
        self, engine: 'PlotEngine', plot_tab: 'PlotTab', x_col: str, 
        y_cols: List[str], axes_flipped: bool, font_family: str, 
        plot_kwargs: Dict[str, Any], general_kwargs: Dict[str, Any]
    ) -> Optional[str]:
        
        if len(y_cols) < 2 and self.plot_name != "Triplot":
            return f"{self.plot_name} requires a Z column. Please select a second Y column (Z-axis)."
        elif not y_cols and self.plot_name == "Triplot":
            return f"{self.plot_name} requires a Y column."

        y_col = y_cols[0] 
        z_col = y_cols[1] if len(y_cols) > 1 else None 
        
        general_kwargs["ylabel"] = plot_tab.ylabel_input.text() or y_col

        if plot_kwargs:
            general_kwargs.update(plot_kwargs)
        
        plot_method = getattr(engine, engine.AVAILABLE_PLOTS[self.plot_name])

        if self.plot_name == "Triplot":
            plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        else:
            if not z_col: 
                return f"{self.plot_name} requires a Z column, but it was not provided."
            general_kwargs["z"] = z_col
            plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
            
        return None