from typing import List, Dict, Any, Union
import pandas as pd
import numpy as np
from core.plot_strategies.plotly_base_strategy import BasePlotlyStrategy
try:
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    px = None
    go = None

class PlotlyLineStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Any | None:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        
        if len(y) == 1:
            fig = px.line(df, x=x, y=y[0], **px_kwargs)
        else:
            fig = px.line(df, x=x, y=y, **px_kwargs)
            
        return self._apply_layout_updates(fig, df, x, y, **kwargs)

class PlotlyBarStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Union["go.Figure", None]:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        y_col = y[0] if y else None
        
        if len(y) > 1:
            fig = px.bar(df, x=x, y=y, barmode="group", **px_kwargs)
        else:
            if kwargs.get("horizontal", False):
                fig = px.bar(df, x=y_col, y=x, orientation="h", **px_kwargs)
            else:
                fig = px.bar(df, x=x, y=y_col, **px_kwargs)
                
        return self._apply_layout_updates(fig, df, x, y, **kwargs)

class PlotlyHistogramStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Any | None:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        data_column = y[0] if y else None
        if not data_column: data_column = x

        bins = kwargs.get("bins", 30)
        fig = px.histogram(df, x=data_column, nbins=bins, **px_kwargs)

        if kwargs.get("show_kde", False):
            fig.update_traces(opacity=0.75)
        
        return self._apply_layout_updates(fig, df, x, y, **kwargs)

class PlotlyBoxStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Any | None:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        fig = px.box(df, y=y, x=x if x else None, **px_kwargs)
        return self._apply_layout_updates(fig, df, x, y, **kwargs)

class PlotlyViolinStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Any | None:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        fig = px.violin(df, y=y[0], x=x if x else None, box=True, points="all", **px_kwargs)
        return self._apply_layout_updates(fig, df, x, y, **kwargs)

class PlotlyHeatmapStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Union["go.Figure", None]:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        title = px_kwargs.get("title", "Heatmap Plot")
        
        numeric_df = df.select_dtypes(include=[np.number])
        correlation = numeric_df.corr()
        
        fig = px.imshow(
            correlation, 
            text_auto=True, 
            title=title, 
            color_continuous_scale="RdBu_r"
        )
        
        return self._apply_layout_updates(fig, df, x, y, **kwargs)

class PlotlyPieStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Any | None:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        y_col = y[0] if y else None
        if x and y_col:
            fig = px.pie(df, names=x, values=y_col, **px_kwargs)
        elif x:
            fig = px.pie(df, names=x, **px_kwargs)
        
        return self._apply_layout_updates(fig, df, x, y, **kwargs)

class PlotlyAreaStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Any | None:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        if len(y) == 1:
            fig = px.area(df, x=x, y=y[0], **px_kwargs)
        else:
            fig = px.area(df, x=x, y=y, **px_kwargs)
        
        return self._apply_layout_updates(fig, df, x, y, **kwargs)

class PlotlyScatterStrategy(BasePlotlyStrategy):
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Any | None:
        px_kwargs = self._extract_common_kwargs(x, y, **kwargs)
        
        size_col = kwargs.get("size")
        if size_col and size_col in df.columns:
            px_kwargs["size"] = size_col
            px_kwargs["size_max"] = kwargs.get("size_max", 40)
            
        if len(y) == 1:
            fig = px.scatter(df, x=x, y=y[0], **px_kwargs)
        else:
            fig = px.scatter(df, x=x, y=y, **px_kwargs)
        
        return self._apply_layout_updates(fig, df, x, y, **kwargs)
class PlotlyStrategyRegistry:
    """Registry to map plot types to Plotly strategies."""
    
    _strategies: Dict[str, BasePlotlyStrategy] = {
        "Line": PlotlyLineStrategy(),
        "Bar": PlotlyBarStrategy(),
        "Histogram": PlotlyHistogramStrategy(),
        "Box": PlotlyBoxStrategy(),
        "Violin": PlotlyViolinStrategy(),
        "Pie": PlotlyPieStrategy(),
        "Area": PlotlyAreaStrategy(),
        "Scatter": PlotlyScatterStrategy(),
        "Heatmap": PlotlyHeatmapStrategy(),
    }

    @classmethod
    def get_strategy(cls, plot_type: str) -> BasePlotlyStrategy:
        strategy = cls._strategies.get(plot_type)
        if not strategy:
            raise ValueError(f"Plotly mode not supported for '{plot_type}'")
        return strategy