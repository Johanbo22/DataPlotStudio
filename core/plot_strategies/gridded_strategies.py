from core.plot_strategies.shared_strategies import GriddedPlotStrategy

class ImshowPlotStrategy(GriddedPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Image Show (imshow)"

class PColormeshPlotStrategy(GriddedPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "pcolormesh"

class ContourPlotStrategy(GriddedPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Contour"

class ContourFPlotStrategy(GriddedPlotStrategy):
    @property
    def plot_name(self) -> str:
        return "Contourf"