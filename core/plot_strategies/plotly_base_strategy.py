from abc import ABC, abstractmethod
from typing import List, Dict, Any, Union
import pandas as pd

try:
    import plotly.graph_objects as go
    import plotly.express as px
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
    
    def _apply_layout_updates(self, fig: "go.Figure", x: str, y: List[str], **kwargs: Dict[str, Any]) -> None:
        if fig is None:
            return
        
        hue = kwargs.get("hue")
        fig.update_layout(
            xaxis_title=kwargs.get("xlabel", x),
            yaxis_title=kwargs.get("ylabel", str(y)),
            legend_title=hue if hue else "Legend",
            margin=dict(l=40, r=40, t=40, b=40)
        )