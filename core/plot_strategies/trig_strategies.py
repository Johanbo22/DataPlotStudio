from core.plot_strategies.shared_strategies import TriangulationPlotStrategy

class TricontourPlotStrategy(TriangulationPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Tricontour"

class TricontourfPlotStrategy(TriangulationPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Tricontourf"
    
class TripcolorPlotStrategy(TriangulationPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Tripcolor"

class TriplotPlotStrategy(TriangulationPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Triplot"