from core.plot_strategies.shared_strategies import VectorPlotStrategy

class BarbsPlotStrategy(VectorPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Barbs"

class QuiverPlotStrategy(VectorPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Quiver"
    
class StreamplotPlotStrategy(VectorPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Streamplot"