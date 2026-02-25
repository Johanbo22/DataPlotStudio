from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List, Dict, Any, Optional

if TYPE_CHECKING:
    from core.plot_engine import PlotEngine
    from ui.plot_tab import PlotTab
    
class BasePlotStrategy(ABC):
    @abstractmethod
    def execute(
        self,
        engine: "PlotEngine",
        plot_tab: "PlotTab",
        x_col: str,
        y_cols: List[str],
        axes_flipped: bool,
        font_family: str,
        plot_kwargs: Dict[str, Any],
        general_kwargs: Dict[str, Any]
    ) -> Optional[str]:
        pass
    