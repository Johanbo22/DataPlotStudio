from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import pandas as pd

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
except ImportError:
    go = None
    px = None
    
class BasePlotlyStrategy(ABC):
    @abstractmethod
    def execute(self, df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Union["go.Figure", None]:
        pass
    
    def _extract_common_kwargs(self, x: str, y: List[str], **kwargs: Dict[str, Any]) -> Dict[str, Any]:
        hue = kwargs.get("hue")
        title = kwargs.get("title", "Plotly Plot")
        
        px_kwargs = {"title": title, "template": "plotly_white"}
        
        if hue:
            px_kwargs["color"] = hue
            
        return px_kwargs
    
    def _handle_secondary_axis(self, fig: "go.Figure", df: pd.DataFrame, x: str, **kwargs: Dict[str, Any]) -> "go.Figure":
        secondary_y = kwargs.get("secondary_y")
        if not secondary_y or secondary_y not in df.columns or make_subplots is None:
            return fig
        
        secondary_plot_type = kwargs.get("secondary_plot_type", "Line")
        horizontal = kwargs.get("horizontal", False)
        
        new_fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        for trace in fig.data:
            new_fig.add_trace(trace, secondary_y=False)
        
        if secondary_plot_type == "Bar":
            sec_trace = go.Bar(x=df[x] if not horizontal else df[secondary_y], y=df[secondary_y] if not horizontal else df[x], name=secondary_y, opacity=0.5, orientation="h" if horizontal else "v")
        elif secondary_plot_type == "Scatter":
            sec_trace = go.Scatter(x=df[x] if not horizontal else df[secondary_y], y=df[secondary_y] if not horizontal else df[x], mode="markers", name=secondary_y)
        elif secondary_plot_type == "Area":
            sec_trace = go.Scatter(x=df[x] if not horizontal else df[secondary_y], y=df[secondary_y] if not horizontal else df[x], fill='tozerox' if horizontal else 'tozeroy', name=secondary_y)
        else: # Default to Line
            sec_trace = go.Scatter(x=df[x] if not horizontal else df[secondary_y], y=df[secondary_y] if not horizontal else df[x], mode="lines", name=secondary_y)
        
        new_fig.add_trace(sec_trace, secondary_y=True)
        
        new_fig.layout.update(fig.layout)
        new_fig.update.yaxes(title_text=secondary_y, secondary_y=True)
        
        return new_fig
    
    def _apply_layout_updates(self, fig: "go.Figure", df: pd.DataFrame, x: str, y: List[str], **kwargs: Dict[str, Any]) -> "go.Figure":
        if fig is None:
            return
            
        fig = self._handle_secondary_axis(fig, df, x, **kwargs)
        
        hue = kwargs.get("hue")
        fig.update_layout(
            xaxis_title=kwargs.get("xlabel", x),
            yaxis_title=kwargs.get("ylabel", str(y)),
            legend_title=hue if hue else "Legend",
            margin=dict(l=40, r=40, t=40, b=40)
        )
        
        return fig