# core/plot_engine.py
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import seaborn as sns
from typing import Dict, Any, Optional, List, Tuple, TYPE_CHECKING
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
if TYPE_CHECKING:
    from ui.plot_tab import PlotTab
try:
    import geopandas as gpd
    from mpl_toolkits.axes_grid1 import make_axes_locatable
except ImportError:
    gpd = None
try:
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except:
    PLOTLY_AVAILABLE = False
try:
    import contextily as ctx
except ImportError:
    ctx = None



class PlotEngine:
    """Manages all plotting functionality"""
    
    AVAILABLE_PLOTS = {
        'Line': 'plot_line',
        'Scatter': 'plot_scatter',
        'Bar': 'plot_bar',
        'Histogram': 'plot_histogram',
        'Box': 'plot_box',
        'Violin': 'plot_violin',
        'Heatmap': 'plot_heatmap',
        'KDE': 'plot_kde',
        'Area': 'plot_area',
        'Pie': 'plot_pie',
        'Count Plot': 'plot_count',
        'Hexbin': 'plot_hexbin',
        '2D Density': 'plot_density_2d',
        "Stem": "plot_stem",
        "Stackplot": "plot_stackplot",
        "Stairs": "plot_stairs",
        "Eventplot": "plot_eventplot",
        "ECDF": "plot_ecdf",
        "2D Histogram": "plot_hist2d",
        "Image Show (imshow)": "plot_imshow",
        "pcolormesh": "plot_pcolormesh",
        "Contour": "plot_contour",
        "Contourf": "plot_contourf",
        "Barbs": "plot_barbs",
        "Quiver": "plot_quiver",
        "Streamplot": "plot_streamplot",
        "Tricontour": "plot_tricontour",
        "Tricontourf": "plot_tricontourf",
        "Tripcolor": "plot_tripcolor",
        "Triplot": "plot_triplot",
        "GeoSpatial": "plot_geospatial"
    }
    
    PLOT_DESCRIPTIONS: Dict[str, str] = {
        "Line": "A line chart is a type of graph that displays information as a series of data points connected by straight line segments. It is commonly used to visualize trends and changes in data over continuous intervals, such as time. The horizontal axis (x-axis) typically represents a sequential progression (e.g., time), and the vertical axis (y-axis) shows a quantitative value.",

        "Scatter":"A scatter plot is a graph that uses dots to represent the values of two different numeric variables, showing the relationship between them. Each dot's position on the horizontal (x-axis) and vertical (y-axis) indicates the values for an individual data point. Scatter plots are used to observe patterns, trends, and correlations between variables, such as determining if an increase in one variable corresponds with an increase or decrease in another. ",

        "Bar": "A bar chart is a data visualization tool that uses rectangular bars to represent categorical data, with the length or height of the bars proportional to the values they represent. It is used to compare different categories and show variations in data, making it useful for visualizing things like sales figures, survey responses, or monthly rainfall. Bar charts can be oriented vertically or horizontally and can display one or more sets of data.",

        "Histogram":"A histogram is a graphical representation of the distribution of a set of numerical data. It uses bars to show the frequency of data points that fall into specific, consecutive ranges or 'bins'. The height of each bar indicates the number of data points in that bin, making it useful for visualizing the shape, center, and spread of the data.",

        "Box": "A box plot is a graphical tool that visualizes the distribution of numerical data through its quartiles, providing a five-number summary: minimum, first quartile ((Q_{1})), median, third quartile ((Q_{3})), and maximum. It uses a box to represent the middle 50%  of the data (the interquartile range, or (IQR)), with a line inside for the median. 'Whiskers' extend from the box to the minimum and maximum values, and outliers may be shown as individual points beyond the whiskers.",

        "Violin": "A violin plot is a statistical visualization that combines a box plot with a kernel density plot to show the distribution of a numeric variable for one or more groups. The plot's shape is determined by the data density—it is wider where values are more frequent and narrower where they are less frequent, providing a visual representation of peaks in the data. Inside the violin shape, a miniature box plot can be included to display summary statistics like the median and interquartile range.",

        "Heatmap": "A heatmap is a data visualization technique that uses color to represent the magnitude of a variable, making complex data easier to interpret. It typically displays data as a grid of colored squares, where the intensity or shade of the color corresponds to the data's value, ranging from 'cool' (low values) to 'hot' (high values). Common uses include showing user behavior on websites, such as clicks and scroll depth, as well as representing geographical or statistical data like population density or temperature variations.",

        "KDE": "A kernel density estimation (KDE) plot is a visualization that creates a smooth curve to show the distribution of a continuous variable, acting as a smoothed-out version of a histogram. It is a non-parametric way to estimate the probability density function (PDF) of the data, helping to identify patterns, trends, and outliers in a clearer, more continuous way than with a histogram.",

        "Area": "An area chart is a type of line chart that shows quantitative data over time by filling the space between the plotted line and the axis with color or shading. It is used to emphasize the volume or magnitude of change over time, and can also be used to show how different data series contribute to a total.",

        "Pie": "A pie chart is a circular graphic that represents parts of a whole, with each 'slice' of the pie showing the proportional size of a category. The slices are proportional to the quantities they represent, and all slices combined make up the whole, typically equaling 100%.",

        "Count Plot": "A count plot can be thought of as a histogram across a categorical, instead of quantitative, variable. The basic API and options are identical to those for barplot(), so you can compare counts across nested variables.",

        "Hexbin": "A hexbin plot is a type of 2D histogram that represents the density of data points in a scatter plot by dividing the graphing area into hexagonal bins. Instead of showing individual points, it uses a color gradient to show how many data points fall into each hexagon, making it useful for visualizing large datasets where points would otherwise overlap.",

        "2D Density": "A 2D density plot visualizes the relationship between two numeric variables by showing the concentration of data points in a 2D space. It uses a color gradient to represent areas with a high density of points, making it useful for identifying patterns in large datasets where a scatterplot would result in overplotting. Common types include 2D histograms with squares or hexagons and contour plots.",
        "Stem": "A stem plot draws vertical lines at each x-position to a y-value, with a marker at the top. It is excellent for visualizing discrete time series or categorical data points.",
        "Stackplot": "A stackplot (or stacked area chart) visualizes the contribution of different groups to a whole over time or another continuous variable. Each colored area represents one group, and the areas are stacked on top of each other.",
        "Stairs": "A stairs plot creates a step-like visualization, similar to a line plot but with vertical and horizontal lines only (no diagonals). It's useful for displaying data that changes at discrete intervals.",
        "Eventplot": "An eventplot visualizes identical-looking objects (e.g., lines) at different positions. It's commonly used for plotting spike trains or other event-based data, where the position on one axis represents the time or location of an event.",
        "ECDF": "An Empirical Cumulative Distribution Function (ECDF) plot shows the proportion of data points that are less than or equal to a given value. It's a step function that provides a clear visual of the data's distribution.",
        "2D Histogram": "A 2D histogram (hist2d) bins the data into 2D rectangles and uses color to represent the number of data points in each bin. It is excellent for visualizing the joint distribution of two variables with a large number of points.",
        "Image Show (imshow)": "Displays data as an image, where the data is represented by colors. This is used for visualizing 2D arrays or matrices, such as a correlation matrix. Requires data to be in a 2D grid format (use X, Y-pos, and Z-value).",
        "pcolormesh": "Creates a pseudocolor plot of a 2D array. It's highly efficient for plotting large arrays and is often used for 2D histograms or other gridded data. Requires data to be in a 2D grid format (use X, Y-pos, and Z-value).",
        "Contour": "A contour plot displays 3D data in 2D by showing lines (contours) that connect points of equal value (like a topographical map). It requires data to be in a 2D grid (use X, Y-pos, and Z-value).",
        "Contourf": "A filled contour plot (contourf) is similar to a contour plot but fills the areas between the contour lines with colors. Requires data to be in a 2D grid (use X, Y-pos, and Z-value).",
        "Barbs": "A barb plot is used to visualize vector fields, typically in meteorology to show wind direction and speed. Requires X, Y-position and U, V vector components (4 columns).",
        "Quiver": "A quiver plot displays a 2D field of arrows. Each arrow represents a vector at a specific (x, y) point. Requires X, Y-position and U, V vector components (4 columns).",
        "Streamplot": "A streamplot visualizes a 2D vector field by drawing streamlines. It's excellent for understanding the flow of a vector field. Requires gridded X, Y-position and U, V vector components (4 columns).",
        "Tricontour": "A triangular contour plot. Similar to a regular contour plot, but it works on an unstructured grid of (x, y, z) data points by first creating a triangulation.",
        "Tricontourf": "A filled triangular contour plot. Like `contourf`, it fills the areas between the contour lines generated from an unstructured (x, y, z) dataset.",
        "Tripcolor": "Creates a pseudocolor plot from an unstructured (x, y, z) dataset. It triangulates the (x, y) points and colors each triangle based on its Z value.",
        "Triplot": "A simple plot that draws the underlying triangulation of an (x, y) dataset, showing the network of triangles used for other tri-plots.",
        "GeoSpatial": "Visualizes geospatial data using GeoPandas. Requires a GeoDataFrame (imported from .shp, .geojson, etc.). The 'X Column' can be used to select a column for choropleth coloring (values determine color)."
    }

    
    def __init__(self):
        self.current_figure: Optional[Figure] = None
        self.current_ax = None
        self.axes_flat = []
        self.current_plot_type: Optional[str] = None
        self.plot_config: Dict[str, Any] = {}
        self.secondary_ax = None
    
    def create_figure(self, figsize=(10, 6), dpi=100) -> Figure:
        """Create a new matplotlib figure"""
        self.current_figure = Figure(figsize=figsize, dpi=dpi)
        self.setup_layout(1, 1)
        return self.current_figure

    def _set_labels(self, title: Optional[str], xlabel: Optional[str], ylabel: Optional[str], legend: bool, **kwargs) -> None:
        """Function that sets labels and handles latex rendering if requqested"""
        usetex = kwargs.get("usetex", False)

        plt.rcParams["text.usetex"] = usetex

        default_weight = "normal" if usetex else "bold"
        title_weight = kwargs.get("title_weight", default_weight)

        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight=title_weight, picker=True)
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12, picker=True)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12, picker=True)
        if legend:
            self.current_ax.legend()
        
        self.current_figure.tight_layout()
    
    def generate_plotly_plot(self, df: pd.DataFrame, plot_type: str, x: str, y: List[str], **kwargs) -> str:
        """
        Generates a Plotly figure object
        Returns a plotly.graph_objects.Figure or an HTML string with the error occurred
        """
        if not PLOTLY_AVAILABLE:
            return """
            <html><body style='font-family:sans-serif; text-align:center; padding-top:20px;'>
            <h3 style='color:red;'>Plotly library not found</h3>
            <p>Please install it to use interactive plotting:</p>
            <code>pip install plotly</code>
            </body></html>
            """
        
        try:
            fig = None
            title = kwargs.get("title", f"{plot_type} Plot")
            hue = kwargs.get("hue")

            px_kwargs = {
                "title": title,
                "template": "plotly_white"
            }
            if hue:
                px_kwargs["color"] = hue
            
            if plot_type == "Line":
                if len(y) == 1:
                    fig = px.line(df, x=x, y=y[0], **px_kwargs)
                else:
                    fig = px.line(df, x=x, y=y, **px_kwargs)
            elif plot_type == "Bar":
                y_col = y[0] if y else None
                if len(y) > 1:
                    fig = px.bar(df, x=x, y=y, barmode="group", **px_kwargs)
                else:
                    if kwargs.get("horizontal", False):
                        fig = px.bar(df, x=y_col, y=x, orientation="h", **px_kwargs)
                    else:
                        fig = px.bar(df, x=x, y=y_col, **px_kwargs)

            elif plot_type == "Histogram":
                data_column = y[0] if y else None
                if not data_column: data_column = x

                bins = kwargs.get("bins", 30)
                fig = px.histogram(df, x=data_column, nbins=bins, **px_kwargs)

                if kwargs.get("show_kde", False):
                    fig.update_traces(opacity=0.75)
            
            elif plot_type == "Box":
                fig = px.box(df, y=y, x=x if x else None, **px_kwargs)
            
            elif plot_type == "Violin":
                fig = px.violin(df, y=y[0], x=x if x else None, box=True, points="all", **px_kwargs)
            
            elif plot_type == "Heatmap":
                numeric_df = df.select_dtypes(include=[np.number])
                correlation = numeric_df.corr()
                fig = px.imshow(correlation, text_auto=True, title=title, color_continuous_scale="RdBu_r")
            
            elif plot_type == "Pie":
                y_col = y[0] if y else None
                if x and y_col:
                    fig = px.pie(df, names=x, values=y_col, **px_kwargs)
                elif x:
                    fig = px.pie(df, names=x, **px_kwargs)
            
            elif plot_type == "Area":
                if len(y) == 1:
                    fig = px.area(df, x=x, y=y[0], **px_kwargs)
                else:
                    fig = px.area(df, x=x, y=y, **px_kwargs)
            
            elif plot_type == "3D Scatter" or (plot_type == "Scatter" and len(y) > 1 and kwargs.get("3d", False)):
                pass
            
            if fig is None and plot_type == "Scatter":
                if len(y) == 1:
                     fig = px.scatter(df, x=x, y=y[0], **px_kwargs)
                else:
                     fig = px.scatter(df, x=x, y=y, **px_kwargs)

            if fig is None:
                return f"""
                <html><body style='font-family:sans-serif; text-align:center; padding-top:20px;'>
                <h3 style='color:orange;'>Interactive mode not supported for '{plot_type}'</h3>
                <p>Showing static plot instead.</p>
                </body></html>
                """
            
            fig.update_layout(
                xaxis_title=kwargs.get("xlabel", x),
                yaxis_title=kwargs.get("ylabel", str(y)),
                legend_title=hue if hue else "Legend",
                margin=dict(l=40, r=40, t=40, b=40)
            )

            return fig

        except Exception as PlotlyError:
            return f"""
            <html><body style='font-family:sans-serif; text-align:center; padding-top:20px;'>
            <h3 style='color:red;'>Error generating interactive plot</h3>
            <pre>{str(PlotlyError)}</pre>
            </body></html>
            """



    def setup_layout(self, rows: int = 1, cols: int = 1, sharex: bool = False, sharey: bool = False):
        """Subplot layout grid"""
        if self.current_figure is None:
            return
        
        self.current_figure.clear()
        axes = self.current_figure.subplots(rows, cols, sharex=sharex, sharey=sharey)
        if isinstance(axes, np.ndarray):
            self.axes_flat = axes.flatten().tolist()
        else:
            self.axes_flat = [axes]
        
        self.current_ax = self.axes_flat[0]
        self.current_figure.tight_layout()

    def set_active_subplot(self, index: int):
        """Set the active subplot"""
        if 0 <= index < len(self.axes_flat):
            self.current_ax = self.axes_flat[index]
        
    def clear_current_axis(self):
        """Clear the active subplot"""
        if self.current_ax:
            if hasattr(self.current_ax, "_cax") and self.current_ax._cax is not None:
                try:
                    if self.current_figure:
                        self.current_figure.delaxes(self.current_ax._cax)
                    else:
                        self.current_ax._cax.remove()
                except Exception:
                    pass
                self.current_ax._cax = None
            
            self.current_ax.set_axes_locator(None)
            self.current_ax.clear()
    
    def get_active_axis_geometry(self) -> Optional[Tuple[int, int, int, int]]:
        """Function to calculate Qt geometry for the active axis relative to the current canvas"""

        if not self.current_ax or not self.current_figure:
            return None
        
        bbox = self.current_ax.get_position()

        width, height = self.current_figure.get_size_inches() * self.current_figure.get_dpi()

        #calculate the pixels
        x = int(bbox.x0 * width)
        w = int(bbox.width * width)
        h = int(bbox.height * height)

        y = int(height - (bbox.y0 * height) - h)

        return (x, y, w, h)
    
    def _get_colors_from_cmap(self, cmap_name, n_colors):
        """Generate a list of colors from a cmap"""
        if not cmap_name:
            return None
        
        try:
            cmap = plt.get_cmap(cmap_name)
            return [cmap(i) for i in np.linspace(0, 1, n_colors)]
        except:
            return None
    
    def _clear_axes(self):
        if self.secondary_ax:
            try:
                self.secondary_ax.remove()
            except Exception:
                pass
            self.secondary_ax = None
        
        self.current_ax.clear()
    
    def _handle_secondary_axis(self, df: pd.DataFrame, x: str, secondary_y: str, secondary_plot_type: str, **kwargs) -> Any:
        """
        Method to handle plotting data on a secondary y axis (TwinX)
        Returns the secondary axis objet
        """
        if not secondary_y or secondary_y not in df.columns:
            return None
        
        ax2 = self.current_ax.twinx()
        self.secondary_ax = ax2

        if secondary_plot_type == "Line":
            ax2.plot(df[x], df[secondary_y], label=f"{secondary_y}")
        elif secondary_plot_type == "Bar":
            ax2.bar(df[x], df[secondary_y], alpha=0.3, label=f"{secondary_y}")
        elif secondary_plot_type == "Scatter":
            ax2.scatter(df[x], df[secondary_y], label=f"{secondary_y}")
        elif secondary_plot_type == "Area":
            ax2.fill_between(df[x], 0, df[secondary_y], alpha=0.2, label=f"{secondary_y}")
        else:
            ax2.plot(df[x], df[secondary_y], label=f"{secondary_y}", linestyle="--")
        
        ax2.set_ylabel(secondary_y)
        ax2.tick_params(axis="y")

        return ax2

    def _consolidate_legends(self, ax1, ax2):
        """Combine legends from primary and secondary axes into one"""
        if not ax1 and ax2:
            return
        
        lines1, labels1 = ax1.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()

        if lines1 or lines2:
            ax1.legend(lines1 + lines2, labels1 + labels2, loc="best")
    
    def plot_line(self, df: pd.DataFrame, x: str, y: List[str], **kwargs) -> None:
        """Create a line plot"""
        self._clear_axes()
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        hue = kwargs.pop("hue", None)
        cmap_name = kwargs.pop("cmap", None)
        secondary_y = kwargs.pop("secondary_y", None)
        secondary_plot_type = kwargs.pop("secondary_plot_type", "Line")

        marker = kwargs.pop("marker", None)

        if marker in (None, ""):
            kwargs["marker"] = None
        elif marker is not None:
            kwargs["marker"] = marker

        if hue:
            groups = df[hue].unique()
            colors = self._get_colors_from_cmap(cmap_name, len(groups))

            for i, group in enumerate(groups):
                mask = (df[hue] == group) & df[x].notna()
                if colors: kwargs["color"] = colors[i]
                for col in y:
                    self.current_ax.plot(df.loc[mask, x], df.loc[mask, col], label=f"{col} - {group}", picker=5, **kwargs)
        else:
            colors = self._get_colors_from_cmap(cmap_name, len(y))
            for i, col in enumerate(y):
                mask = df[x].notna()
                if colors: kwargs["color"] = colors[i]
                self.current_ax.plot(df.loc[mask, x], df.loc[mask, col], label=col, picker=5, **kwargs)
        
        ax2 = None
        if secondary_y:
            ax2 = self._handle_secondary_axis(df, x, secondary_y, secondary_plot_type, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

        if legend:
            if ax2:
                self._consolidate_legends(self.current_ax, ax2)
            else:
                self.current_ax.legend()
    
    def plot_scatter(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a scatter plot"""
        self._clear_axes()
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        hue = kwargs.pop('hue', None)
        cmap_name = kwargs.pop("cmap", None)
        secondary_y = kwargs.pop("secondary_y", None)
        secondary_plot_type = kwargs.pop("secondary_plot_type", "Line")
        
        if hue:
            groups = df[hue].unique()
            colors = self._get_colors_from_cmap(cmap_name, len(groups))
            
            for i, group in enumerate(groups):
                mask = (df[hue] == group) & df[x].notna() & df[y].notna()
                if colors: kwargs["color"] = colors[i]
                self.current_ax.scatter(df.loc[mask, x], df.loc[mask, y], label=group, picker=5, **kwargs)
        else:
            if cmap_name: kwargs["cmap"] = cmap_name
            mask = df[x].notna() & df[y].notna()
            self.current_ax.scatter(df.loc[mask, x], df.loc[mask, y], picker=5, **kwargs)
        
        ax2 = None
        if secondary_y:
            ax2 = self._handle_secondary_axis(df, x, secondary_y, secondary_plot_type, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

        if legend:
            if ax2:
                self._consolidate_legends(self.current_ax, ax2)
            else:
                self.current_ax.legend()
    
    def plot_bar(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a bar plot"""
        self._clear_axes()
        df = df[df[x].notna()]
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        hue = kwargs.pop('hue', None)
        width = kwargs.pop("width", 0.8)
        horizontal = kwargs.pop("horizontal", False)
        palette = kwargs.pop("palette", None)
        secondary_y = kwargs.pop("secondary_y", None)
        secondary_plot_type = kwargs.pop("secondary_plot_type", "Line")
        
        if isinstance(y, str):
            y = [y]

        if len(y) == 1 and not hue:
            #single y col
            y_col_name = y[0]
            if horizontal:
                self.current_ax.barh(df[x], df[y_col_name], height=width, picker=True, **kwargs)
            else:
                self.current_ax.bar(df[x], df[y_col_name], width=width, picker=True, **kwargs)
        
        elif len(y) > 1:
            #grouped bar chart
            x_labels = df[x].unique()
            x_pos = np.arange(len(x_labels))
            bar_width = width / len(y)
            
            colors = self._get_colors_from_cmap(palette, len(y))

            for i, col in enumerate(y):
                offset = (i - len(y) / 2) * bar_width + bar_width / 2
                values = [df[df[x] == label][col].values[0] if len(df[df[x] == label]) > 0 else 0 for label in x_labels]
                
                if colors: kwargs["color"] = colors[i]

                if horizontal:
                    self.current_ax.barh(x_pos + offset, values, height=bar_width, label=col, picker=True, **kwargs)
                else:
                    self.current_ax.bar(x_pos + offset, values, width=bar_width, label=col, picker=True, **kwargs)
            
            if horizontal:
                self._helper_format_categorical_axis(self.current_ax.yaxis, x_labels)
            else:
                self._helper_format_categorical_axis(self.current_ax.xaxis, x_labels)
        
        elif hue:
            # Single y with hue using seaborn
            import seaborn as sns
            if palette: kwargs["palette"] = palette
            
            if horizontal:
                sns.barplot(data=df, y=x, x=y[0], hue=hue, ax=self.current_ax, orient="h", picker=True, **kwargs)
            else:
                sns.barplot(data=df, x=x, y=y[0], hue=hue, ax=self.current_ax, picker=True, **kwargs)
        
        ax2 = None
        if secondary_y and not horizontal:
            ax2 = self._handle_secondary_axis(df, x, secondary_y, secondary_plot_type, **kwargs)

        self._set_labels(title, xlabel, ylabel, False, **kwargs)

        if legend:
            if ax2:
                self._consolidate_legends(self.current_ax, ax2)
            else:
                handles, labels = self.current_ax.get_legend_handles_labels()
                if handles:
                    self.current_ax.legend()
    
    def plot_histogram(self, df: pd.DataFrame, column: str, **kwargs) -> None:
        """Create a histogram"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        bins = kwargs.pop('bins', 30)
        show_normal = kwargs.pop("show_normal", False)
        show_kde = kwargs.pop("show_kde", False)
        show_stats = kwargs.pop("show_stats", True)
        cmap_name = kwargs.pop("cmap", None)
        
        data = df[column].dropna()

        #calculate mean and std
        mu = data.mean()
        sigma = data.std()
        median = data.median()

        n, bins_edges, patches = self.current_ax.hist(data, bins=bins, density=show_normal or show_kde, picker=True, **kwargs)

        #add ndist
        if show_normal:
            from scipy.stats import norm
            import numpy as np
            
            x = np.linspace(data.min(), data.max(), 100)
            normal_curve = norm.pdf(x, mu, sigma)
            self.current_ax.plot(x, normal_curve, "r-", linewidth=2.5, label=f"Normal (µ={mu:.2f}, σ={sigma:.2f})")
        
        if show_kde:
            import numpy as np
            from scipy.stats import gaussian_kde
            
            #gen kde
            kde = gaussian_kde(data)
            x = np.linspace(data.min(), data.max(), 100)
            kde_curve = kde(x)

            #plot kde
            self.current_ax.plot(x, kde_curve, "g-", linewidth=2.5, label="KDE")

        if show_normal or show_kde:
            self.current_ax.legend()
        
        # add some statistics
        if show_stats and (show_normal or show_kde):
            stats_text = f"µ = {mu:.3f}\nσ = {sigma:.3f}\nmedian = {median:.3f}\nn = {len(data)}"
            props = dict(boxstyle="round", facecolor="wheat", alpha=0.85, edgecolor="black", linewidth=1)
            self.current_ax.text(0.75, 0.95, stats_text, transform=self.current_ax.transAxes, fontsize=10, verticalalignment="top", bbox=props, fontfamily="monospace")

        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_box(self, df: pd.DataFrame, columns: List[str], **kwargs) -> None:
        """Create a box plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)

        if isinstance(columns, str):
            columns = [columns]
        
        df[columns].plot(kind='box', ax=self.current_ax, picker=True, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_violin(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a violin plot using seaborn"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        
        sns.violinplot(data=df, x=x, y=y, ax=self.current_ax, picker=True, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_heatmap(self, df: pd.DataFrame, **kwargs) -> None:
        """Create a heatmap using seaborn"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        
        # Ensure numeric data
        numeric_df = df.select_dtypes(include=[np.number])
        sns.heatmap(numeric_df.corr(), annot=True, ax=self.current_ax, picker=True, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_kde(self, df: pd.DataFrame, column: str, **kwargs) -> None:
        """Create a KDE plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        
        df[column].plot(kind='kde', ax=self.current_ax, picker=True, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_area(self, df: pd.DataFrame, x: str, y: List[str], **kwargs) -> None:
        """Create an area plot"""
        self._clear_axes()
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        secondary_y = kwargs.pop("secondary_y", None)
        secondary_plot_type = kwargs.pop("secondary_plot_type", "Line")

        if isinstance(y, str):
            y = [y]
        
        df_plot = df[df[x].notna()].set_index(x)[y]
        df_plot.plot(kind="area", ax=self.current_ax, stacked=True, picker=True, **kwargs)
        
        ax2 = None
        if secondary_y:
            ax2 = self._handle_secondary_axis(df, x, secondary_y, secondary_plot_type, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

        if legend:
            if ax2:
                self._consolidate_legends(self.current_ax, ax2)
            else:
                self.current_ax.legend()
    
    def plot_pie(self, df: pd.DataFrame, values: str, names: str, **kwargs) -> None:
        """Create a pie chart"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        show_percentages = kwargs.pop("show_percentages", True)
        start_angle = kwargs.pop("start_angle", 0)
        explode_first = kwargs.pop("explode_first", False)
        explode_distance = kwargs.pop("explode_distance", 0.1)
        shadow = kwargs.pop("shadow", False)
        cmap = kwargs.pop("cmap", None)

        # create format
        autopct = "%1.2f%%" if show_percentages else None

        #explode
        explode = None
        if explode_first:
            explode = [explode_distance] + [0] * (len(df[values]) - 1)
        
        self.current_ax.pie(df[values], labels=df[names], autopct=autopct, startangle=start_angle, explode=explode, shadow=shadow, **kwargs)
        self.current_ax.set_ylabel('')

        self.current_ax.axis("equal")
        
        self._set_labels(title, None, None, False, **kwargs)
    
    def plot_count(self, df: pd.DataFrame, column: str, **kwargs) -> None:
        """Create a count plot using seaborn"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        
        sns.countplot(data=df, x=column, ax=self.current_ax, picker=True, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_hexbin(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a hexbin plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        gridsize = kwargs.pop('gridsize', 20)
        
        mask = df[x].notna() & df[y].notna()
        self.current_ax.hexbin(df.loc[mask, x], df.loc[mask, y], gridsize=gridsize, picker=True, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_density_2d(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a 2D density plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)

        # add defaults
        if "cmap" not in kwargs:
            kwargs["cmap"] = "viridis"
        if "levels" not in kwargs:
            kwargs["levels"] = 10
        if "thresh" not in kwargs:
            kwargs["thresh"] = 0.05
        
        mask = df[x].notna() & df[y].notna()
        clean_df = df.loc[mask]
        
        sns.kdeplot(data=clean_df, x=x, y=y, ax=self.current_ax, fill=True, picker=True, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def plot_stem(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a stem plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        legend = kwargs.pop("legend", False)

        line_style = kwargs.pop("linestyle", "-")
        line_width = kwargs.pop("linewidth", 1.5)
        marker = kwargs.pop("marker", "o")
        marker_size = kwargs.pop("markersize", 6)
        if "s" in kwargs:
            marker_size = kwargs.pop("s")
        
        color = kwargs.pop("color", "#1f77b4")
        if "c" in kwargs:
            color = kwargs.pop("c")
        
        alpha = kwargs.pop("alpha", 1.0)
        label = kwargs.pop("label", y)
        orientation = kwargs.pop("orientation", "vertical")
        bottom = kwargs.pop("bottom", 0)

        if orientation == "horizontal":
            markerline, stemlines, baseline = self.current_ax.stem(
                df[y], df[x],
                orientation="horizontal",
                bottom=bottom,
                label=label,
                picker=True
            )
        else:
            markerline, stemlines, baseline = self.current_ax.stem(
                df[x], df[y],
                orientation="vertical",
                bottom=bottom,
                label=label,
                picker=True
            )
        
        plt.setp(markerline, marker=marker, markersize=marker_size, color=color, alpha=alpha)
        plt.setp(stemlines, linestyle=line_style, linewidth=line_width, color=color, alpha=alpha)
        plt.setp(baseline, color="gray", linewidth=1, linestyle="-")

        self._set_labels(title, xlabel, ylabel, legend, **kwargs)
    
    def plot_stackplot(self, df: pd.DataFrame, x: str, y: List[str], **kwargs) -> None:
        """Create a stackplot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        legend = kwargs.pop("legend", True)

        df_sorted = df[df[x].notna()].sort_values(by=x)
        y_data = [df_sorted[col] for col in y]

        self.current_ax.stackplot(df_sorted[x], *y_data, labels=y, picker=True, **kwargs)

        self._set_labels(title, xlabel, ylabel, legend, **kwargs)

    def plot_stairs(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a stairs plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)

        df_sorted = df[df[x].notna()].sort_values(by=x)
        self.current_ax.stairs(df_sorted[x], df_sorted[y], picker=True, **kwargs)

        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def plot_eventplot(self, df: pd.DataFrame, y: list[str], **kwargs) -> None:
        """Create an eventplot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        _ = kwargs.pop("legend", None)

        data_to_plot = [df[col].dropna().values for col in y]

        self.current_ax.eventplot(data_to_plot, picker=True, **kwargs)

        if len(y) > 1:
            self.current_ax.set_yticks(range(len(y)))
            self.current_ax.set_yticklabels(y)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def plot_hist2d(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a 2D histogram"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        _ = kwargs.pop("legend", None)

        mask = df[x].notna() & df[y].notna()
        hist = self.current_ax.hist2d(df.loc[mask, x], df.loc[mask, y], picker=True, **kwargs)
        self.current_figure.colorbar(hist[3], ax=self.current_ax, label="counts")

        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_ecdf(self, df: pd.DataFrame, y: str, **kwargs) -> None:
        """Create an ECDF plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        _ = kwargs.pop("legend", None)

        self.current_ax.ecdf(df[y], **kwargs)

        self._set_labels(title, xlabel, "ECDF", False, picker=True, **kwargs)

    def _prepare_gridded_data(self, df: pd.DataFrame, x: str, y: str, z: str):
        """Helper func to pivot data for gridded plots"""
        try:
            if df[[x, y]].duplicated().any():
                #agg by mean
                df_agg = df.groupby([x, y])[z].mean().reset_index()
            else:
                df_agg = df
            
            pivot_df = df_agg.pivot(index=y, columns=x, values=z)
            pivot_df = pivot_df.sort_index(axis=0).sort_index(axis=1)

            X = pivot_df.columns.values
            Y = pivot_df.index.values
            Z = pivot_df.values

            
            return X, Y, Z
        except Exception as GridDataError:
            raise ValueError(f"Data could not be pivoted into a 2D grid. Is the data gridded?: Error: {str(GridDataError)}")
    
    def plot_imshow(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create an imshow plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        _ = kwargs.pop("legend", None)

        X, Y, Z = self._prepare_gridded_data(df, x, y, z)

        img = self.current_ax.imshow(Z, extent=[X.min(), X.max(), Y.min(), Y.max()], origin="lower", aspect="auto", **kwargs)
        self.current_figure.colorbar(img, ax=self.current_ax, label=z)

        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_pcolormesh(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a pcolormesh plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        _ = kwargs.pop("legend", None)

        X, Y, Z = self._prepare_gridded_data(df, x, y, z)
        X_grid, Y_grid = np.meshgrid(X, Y)

        mesh = self.current_ax.pcolormesh(X_grid, Y_grid, Z, **kwargs)
        self.current_figure.colorbar(mesh, ax=self.current_ax, label=z)

        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_contour(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a contour plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)

        X, Y, Z = self._prepare_gridded_data(df, x, y, z)
        X_grid, Y_grid = np.meshgrid(X, Y)

        cont = self.current_ax.contour(X_grid, Y_grid, Z, **kwargs)
        self.current_ax.clabel(cont, inline=True, fontsize=8)

        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def plot_contourf(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a filled contour plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)

        X, Y, Z = self._prepare_gridded_data(df, x, y, z)
        X_grid, Y_grid = np.meshgrid(X, Y)

        contf = self.current_ax.contourf(X_grid, Y_grid, Z, **kwargs)
        self.current_figure.colorbar(contf, ax=self.current_ax, label=z)

        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def plot_barbs(self, df: pd.DataFrame, x: str, y: str, u: str, v: str, **kwargs) -> None:
        """Create a barbs plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)

        self.current_ax.barbs(df[x], df[y], df[u], df[v], **kwargs)

        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_quiver(self, df: pd.DataFrame, x: str, y: str, u: str, v: str, **kwargs) -> None:
        """Create a quiver plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)
        
        self.current_ax.quiver(df[x], df[y], df[u], df[v], **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_streamplot(self, df: pd.DataFrame, x: str, y: str, u: str, v: str, **kwargs) -> None:
        """Create a streamplot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)


        
        try:
            X, Y, U_grid = self._prepare_gridded_data(df, x, y, u)
            _, _, V_grid = self._prepare_gridded_data(df, x, y, v)
            X_grid, Y_grid = np.meshgrid(X, Y)
        except Exception as PlotStreamPlotError:
            raise ValueError(f"Streamplot requires gridded data (pivoted x, y, u, v). Error: {PlotStreamPlotError}")

        self.current_ax.streamplot(X_grid, Y_grid, U_grid, V_grid, **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def plot_tricontour(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a tricontour plot from unstructured x, y, z."""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)
        
        cont = self.current_ax.tricontour(df[x], df[y], df[z], **kwargs)
        self.current_ax.clabel(cont, inline=True, fontsize=8)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def plot_tricontourf(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a filled tricontour plot from unstructured x, y, z."""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)
        
        contf = self.current_ax.tricontourf(df[x], df[y], df[z], **kwargs)
        self.current_figure.colorbar(contf, ax=self.current_ax, label=z)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def plot_tripcolor(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a tripcolor plot from unstructured x, y, z."""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)
        
        trip = self.current_ax.tripcolor(df[x], df[y], df[z], **kwargs)
        self.current_figure.colorbar(trip, ax=self.current_ax, label=z)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def plot_triplot(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a triplot from unstructured x, y."""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        _ = kwargs.pop("legend", None)
        
        self.current_ax.triplot(df[x], df[y], **kwargs)
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)

    def add_table(self, df: pd.DataFrame, loc='bottom', auto_font_size=False, fontsize=10, scale_factor=1.2, **kwargs) -> None:
        """Addin tables to the plot area"""
        if df is None or df.empty:
            return
        
        if self.current_ax:
            for table in list(self.current_ax.tables):
                table.remove()
        
        clean_kwargs = {k: v for k, v in kwargs.items() if k not in ["xlabel", "ylabel", "title", "legend"]}

        table_object = pd.plotting.table(
            self.current_ax,
            df,
            loc=loc,
            **clean_kwargs
        )

        table_object.auto_set_font_size(auto_font_size)
        if not auto_font_size:
            table_object.set_fontsize(fontsize)
        table_object.scale(scale_factor, scale_factor)
    
    def _apply_common_formatting(self, kwargs: Dict[str, Any]) -> None:
        """Apply common formatting to plots\n
        This method is now deprecated as formatting is done in individual plot methods"""
        pass
    
    def clear_plot(self) -> None:
        """Clear the current plot"""
        if self.current_figure:
            self.setup_layout(1, 1)
    
    def get_figure(self) -> Figure:
        """Return the current figure"""
        return self.current_figure

    def _helper_format_categorical_axis(self, axis, labels):
        """Format categorical axis with better tick spacing"""
        if labels is None or len(labels) == 0:
            return
        
        n_labels = len(labels)
        MAX_TICKS = 20

        if n_labels > MAX_TICKS:
            step = int(np.ceil(n_labels / MAX_TICKS))
            indices = np.arange(0, n_labels, step)
            subset_labels = [labels[i] for i in indices]

            axis.set_major_locator(ticker.FixedLocator(indices))
            axis.set_major_formatter(ticker.FixedFormatter(subset_labels))
        else:
            axis.set_major_locator(ticker.FixedLocator(np.arange(n_labels)))
            axis.set_major_formatter(ticker.FixedFormatter(labels))
        
        if axis == self.current_ax.xaxis:
            plt.setp(axis.get_xticklabels(), rotation=45, ha="right")

    def _helper_is_datetime_column(self, plot_tab: "PlotTab", data) -> bool:
        """Check if data is datetime"""
        if data is None:
            return False
        
        try:
            if isinstance(data, pd.Series):
                if pd.api.types.is_datetime64_any_dtype(data):
                    return True
                if data.dtype == "object":
                    if data.empty:
                        return False
                    sample_val = None
                    for val in data.head(50):
                        if val is not None:
                            sample_val = val
                            break
                    if sample_val is None:
                        return False
                    
                    if not isinstance(sample_val, str):
                        return False
                    try:
                        pd.to_datetime(sample_val, utc=True)
                        return True
                    except:
                        pass
            elif hasattr(data, "dtype"):
                return pd.api.types.is_datetime64_any_dtype(data.dtype)
        except Exception as DateTimeColumnError:
            plot_tab.status_bar.log(f"Datetime detection warning: {str(DateTimeColumnError)}", "WARNING")
        return False

    def _helper_apply_auto_datetime_format(self, plot_tab: "PlotTab", axis, data):
        """Apply datetime formatting based on the input datarange"""
        if data is None or len(data) < 2 or not self._helper_is_datetime_column(plot_tab, data):
            return
        
        try:
            if isinstance(data, pd.Series):
                if data.dtype == "object":
                    data = pd.to_datetime(data, utc=True, errors="coerce")
            
            data = data.dropna()

            if len(data) < 2:
                return
            
            date_range = data.max() - data.min()
            if date_range <= pd.Timedelta(hours=6):
                axis.set_major_formatter(mdates.DateFormatter("%H:%M:%S"))
                axis.set_major_locator(mdates.MinuteLocator(interval=max(1, len(data) // 10)))
            elif date_range <= pd.Timedelta(days=1):
                axis.set_major_formatter(mdates.DateFormatter("%H:%M"))
                axis.set_major_locator(mdates.HourLocator(interval=max(1, len(data) // 12)))
            elif date_range <= pd.Timedelta(days=7):
                axis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
                axis.set_major_locator(mdates.DayLocator(interval=1))
            elif date_range <= pd.Timedelta(days=30):
                axis.set_major_formatter(mdates.DateFormatter("%m/%d"))
                axis.set_major_locator(mdates.DayLocator(interval=max(1, date_range.days // 10)))
            elif date_range <= pd.Timedelta(days=365):
                axis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
                axis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range.days // 90)))
            else:
                axis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
                axis.set_major_locator(mdates.YearLocator())
        except Exception as ApplyDateTimeError:
            plot_tab.status_bar.log(f"Failed to auto-format datetime: {str(ApplyDateTimeError)}", "WARNING")

    def _helper_set_intelligent_locator(self, plot_tab: "PlotTab", axis, data):
        """Set tick locators based on tghe datarange"""
        if data is None or len(data) < 2 or not self._helper_is_datetime_column(plot_tab, data):
            return
        
        try:
            if isinstance(data, pd.Series):
                if data.dtype == "object":
                    data = pd.to_datetime(data, utc=True, errors="coerce")
            data = data.dropna()

            if len(data) < 2:
                return
            
            date_range = data.max() - data.min()
            if date_range <= pd.Timedelta(hours=6):
                axis.set_major_locator(mdates.MinuteLocator(interval=max(1, len(data) // 10)))
            elif date_range <= pd.Timedelta(days=1):
                axis.set_major_locator(mdates.HourLocator(interval=max(1, len(data) // 12)))
            elif date_range <= pd.Timedelta(days=7):
                axis.set_major_locator(mdates.DayLocator(interval=1))
            elif date_range <= pd.Timedelta(days=30):
                axis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range.days // 10)))
            elif date_range <= pd.Timedelta(days=365):
                axis.set_major_locator(mdates.MonthLocator(interval=max(1, date_range.days // 90)))
            else:
                axis.set_major_locator(mdates.YearLocator())
        except Exception as DateTimeLocatorError:
            plot_tab.status_bar.log(f"Failed to set datetime locator: {str(DateTimeLocatorError)}", "WARNING")
    
    def _helper_format_datetime_axis(self, plot_tab: "PlotTab", ax, x_data, y_data=None) -> None:
        """Format datetime axes with tick spacing"""

        #first check if datetime in cols
        is_x_datetime = self._helper_is_datetime_column(plot_tab, x_data)
        is_y_datetime = self._helper_is_datetime_column(plot_tab, y_data) if y_data is not None else False

        use_custom_format: bool = plot_tab.custom_datetime_check.isChecked()

        #format the x-axis
        if is_x_datetime:
            try:
                if isinstance(x_data, pd.Series):
                    if x_data.dtype == "object":
                        x_data = pd.to_datetime(x_data, utc=True, errors="coerce")
                    elif not hasattr(x_data.dtype, "tz") or x_data.dtype.tz is None:
                        x_data = x_data.dt.tz_localize("UTC", nonexistent="shift_forward", ambiguous="infer")
            except Exception as FormatDateTimeAxisError:
                plot_tab.status_bar.log(f"X-axis timezone handling: {str(FormatDateTimeAxisError)}", "WARNING")
            
            if use_custom_format:
                format_text = plot_tab.x_datetime_format_combo.currentText()

                if format_text == "Custom":
                    custom_format = plot_tab.x_custom_datetime_input.text().strip()
                    if custom_format:
                        try:
                            ax.xaxis.set_major_formatter(mdates.DateFormatter(custom_format))
                            self._helper_set_intelligent_locator(plot_tab, ax.xaxis, x_data)
                        except Exception as FormatDateTimeAxisError:
                            plot_tab.status_bar.log(f"Invalid datetime format: {str(FormatDateTimeAxisError)}", "WARNING")
                            self._helper_apply_auto_datetime_format(plot_tab, ax.xaxis, x_data)
                    else:
                        self._helper_apply_auto_datetime_format(plot_tab, ax.xaxis, x_data)
                elif format_text == "Auto":
                    self._helper_apply_auto_datetime_format(plot_tab, ax.xaxis, x_data)
                else:
                    format_code = format_text.split(" ")[0]
                    try:
                        ax.xaxis.set_major_formatter(mdates.DateFormatter(format_code))
                        self._helper_set_intelligent_locator(plot_tab, ax.xaxis, x_data)
                    except Exception as FormatDateTimeAxisError:
                        plot_tab.status_bar.log(f"Invalid datetime format: {str(FormatDateTimeAxisError)}", "WARNING")
                        self._helper_apply_auto_datetime_format(plot_tab, ax.xaxis, x_data)
            else:
                self._helper_apply_auto_datetime_format(plot_tab, ax.xaxis, x_data)

        #fmt yaxis
        if is_y_datetime:
            try:
                if isinstance(y_data, pd.Series):
                    if y_data.dtype == 'object':
                        y_data = pd.to_datetime(y_data, utc=True, errors='coerce')
                    elif not hasattr(y_data.dtype, 'tz') or y_data.dtype.tz is None:
                        y_data = y_data.dt.tz_localize('UTC', nonexistent='shift_forward', ambiguous='infer')
            except Exception as FormatYAxisDateTimeError:
                plot_tab.status_bar.log(f"Y-axis timezone handling: {str(FormatYAxisDateTimeError)}", "WARNING")
            
            if use_custom_format:
                format_text = plot_tab.y_datetime_format_combo.currentText()

                if format_text == "Custom":
                    custom_format = plot_tab.y_custom_datetime_format_input.text().strip()
                    if custom_format:
                        try:
                            ax.yaxis.set_major_formatter(mdates.DateFormatter(custom_format))
                            self._helper_set_intelligent_locator(plot_tab, ax.yaxis, y_data)
                        except Exception as FormatYAxisDateTimeError:
                            plot_tab.status_bar.log(f"Invalid datetime format: {str(FormatYAxisDateTimeError)}", "WARNING")
                            self._helper_apply_auto_datetime_format(plot_tab, ax.yaxis, y_data)
                    else:
                        self._helper_apply_auto_datetime_format(plot_tab, ax.yaxis, y_data)
                elif x_data is not None and hasattr(x_data, "dtype") and (x_data.dtype == "object" or isinstance(x_data.dtype, pd.CategoricalDtype)):
                    try:
                        labels = x_data.unique()
                        labels = [l for l in labels if pd.notna(l)]
                        self._helper_format_categorical_axis(ax.xaxis, labels)
                    except Exception:
                        pass
                elif format_text == "Auto":
                    self._helper_apply_auto_datetime_format(plot_tab, ax.yaxis, y_data)
                else:
                    format_code = format_text.split(" ")[0]
                    try:
                        ax.yaxis.set_major_formatter(mdates.DateFormatter(format_code))
                        self._helper_set_intelligent_locator(plot_tab, ax.yaxis, y_data)
                    except Exception as InvalidDateTimeError:
                        plot_tab.status_bar.log(f"Invalid datetime format: {str(InvalidDateTimeError)}", "WARNING")
                        self._helper_apply_auto_datetime_format(plot_tab, ax.yaxis, y_data)
            else:
                self._helper_apply_auto_datetime_format(plot_tab, ax.yaxis, y_data)
    
    def _helper_apply_flipped_labels(self, plot_tab: "PlotTab", x_col, y_cols, font_family):
        """Function to correctly apply axes labels when flipped axes is true"""
        if plot_tab.xlabel_check.isChecked():
            ylabel_to_use = plot_tab.xlabel_input.text() or x_col
            self.current_ax.set_ylabel(
                ylabel_to_use,
                fontsize=plot_tab.xlabel_size_spin.value(),
                fontweight=plot_tab.xlabel_weight_combo.currentText(),
                fontfamily=font_family
            )
        
        if plot_tab.ylabel_check.isChecked():
            xlabel_to_use = plot_tab.ylabel_input.text() or (y_cols[0] if len(y_cols) == 1 else str(y_cols))
            self.current_ax.set_xlabel(
                xlabel_to_use,
                fontsize=plot_tab.ylabel_size_spin.value(),
                fontweight=plot_tab.ylabel_weight_combo.currentText(),
                fontfamily=font_family
            )
        
        if plot_tab.title_check.isChecked():
            title_to_use = plot_tab.title_input.text() if plot_tab.title_input.text() else plot_tab.plot_type.currentText()
            self.current_ax.set_title(
                title_to_use,
                fontsize=plot_tab.title_size_spin.value(),
                fontweight=plot_tab.title_weight_combo.currentText(),
                fontfamily=font_family
            )
    
    def _helper_add_regression_analysis(self, plot_tab: 'PlotTab', x_col: str, y_col: str, flipped: bool = False) -> None:
        try:
            import numpy as np
            from scipy import stats

            df = plot_tab.data_handler.df

            if not pd.api.types.is_numeric_dtype(df[x_col]) or not pd.api.types.is_numeric_dtype(df[y_col]):
                plot_tab.status_bar.log(f"Regression analysis skipped: '{x_col}' or '{y_col}' is not numeric", "INFO")
                return

            # Remove NaN/inf values from both columns
            mask = np.isfinite(df[x_col]) & np.isfinite(df[y_col])
            x_data = df.loc[mask, x_col].values
            y_data = df.loc[mask, y_col].values

            if len(x_data) < 2:
                plot_tab.status_bar.log("Not enough data points to perform regressional analysis", "WARNING")
                return
            
            # perform linreg
            slope, intercept, r_value, p_value, std_err = stats.linregress(x_data, y_data)

            # generate regression line
            x_line = np.linspace(x_data.min(), x_data.max(), 100)
            y_line = slope * x_line + intercept


            # plot regression line
            if plot_tab.regression_line_check.isChecked():
                plot_args = (x_line, y_line) if not flipped else (y_line, x_line)
                reg_line = self.current_ax.plot(
                    *plot_args, 
                    color="red", linestyle="-", linewidth=2, 
                    label="Linear Fit", alpha=0.5
                )[0]
                reg_line.set_gid("regression_line")
            
            # calculate confidence interval
            if plot_tab.confidence_interval_check.isChecked():
                confidence = plot_tab.confidence_level_spin.value() / 100.0
                
                # standard error of the fit
                residuals = y_data - (slope * x_data + intercept)
                n = len(x_data)
                residual_std = np.sqrt(np.sum(residuals**2) / (n - 2))

                #std eror for each prediction
                x_mean = np.mean(x_data)
                se_line = residual_std * np.sqrt(1/n + (x_line - x_mean)**2 / np.sum((x_data - x_mean)**2))

                from scipy.stats import t as t_dist
                t_val = t_dist.ppf((1 + confidence) / 2, n - 2)
                margin = t_val * se_line
                
                fill_args = (x_line, y_line - margin, y_line + margin) if not flipped else (y_line - margin, y_line + margin, x_line)

                if not flipped:
                    ci_poly = self.current_ax.fill_between(
                        fill_args[0], fill_args[1], fill_args[2],
                        color="red", alpha=0.15, label=f"{int(confidence*100)}% CI", zorder=-1
                    )
                else:
                    ci_poly = self.current_ax.fill_betweenx(
                        fill_args[2], fill_args[0], fill_args[1], # y, x1, x2
                        color="red", alpha=0.15, label=f"{int(confidence*100)}% CI", zorder=-1
                    )
                ci_poly.set_gid("confidence_interval")

            # calculate rmse
            y_pred = slope * x_data + intercept
            rmse = np.sqrt(np.mean((y_data - y_pred)**2))

            #b uild stats text
            stats_text = []
            
            eq_x_label = "y" if flipped else "x"
            eq_y_label = "x" if flipped else "y"


            if plot_tab.show_equation_check.isChecked():
                if intercept >= 0:
                    stats_text.append(f'{eq_y_label} = {slope:.4f}{eq_x_label} + {intercept:.4f}')
                else:
                    stats_text.append(f'{eq_y_label} = {slope:.4f}{eq_x_label} - {abs(intercept):.4f}')
            
            if plot_tab.show_r2_check.isChecked():
                stats_text.append(f"R² = {r_value**2:.4f}")
            
            if plot_tab.show_rmse_check.isChecked():
                stats_text.append(f"RMSE = {rmse:.4f}")
            
            #display on plot
            if stats_text:
                textstr = "\n".join(stats_text)
                props = dict(boxstyle="round", facecolor="wheat", alpha=0.85, edgecolor="black", linewidth=1)
                font_family = plot_tab.font_family_combo.currentFont().family()

                self.current_ax.text(0.05, 0.95, textstr, transform=self.current_ax.transAxes, fontsize=11, verticalalignment='top', bbox=props, fontfamily=font_family, zorder=15)
            
            #add errorbars
            error_bar_type = plot_tab.error_bars_combo.currentText()
            if error_bar_type == "Standard Deviation":
                # calculate residuals
                y_pred_all = slope * x_data + intercept
                residuals = y_data - y_pred_all

                # calculate std in bins
                n_bins = min(20, len(x_data) // 5)
                if n_bins > 1: # Need at least 2 bins
                    # sort by x vals
                    sorted_indices = np.argsort(x_data)
                    x_sorted = x_data[sorted_indices]
                    y_sorted = y_data[sorted_indices]
                    residuals_sorted = residuals[sorted_indices]

                    # calc std bins
                    bin_size = len(x_data) // n_bins
                    x_centers = []
                    y_centers = []
                    y_errors = []

                    for i in range(n_bins):
                        start = i * bin_size
                        end = start + bin_size if i < n_bins - 1 else len(x_data)

                        if end - start > 1: 
                            x_centers.append(np.mean(x_sorted[start:end]))
                            y_centers.append(np.mean(y_sorted[start:end]))
                            y_errors.append(np.std(residuals_sorted[start:end]))
                    
                    if x_centers:
                        err_args = (x_centers, y_centers)
                        err_kwargs = {"yerr": y_errors} if not flipped else {"xerr": y_errors}
                        
                        self.current_ax.errorbar(
                            *err_args, **err_kwargs,
                            fmt="o", markersize=3, ecolor="black", alpha=0.5, 
                            capsize=4, zorder=10, markerfacecolor="none", 
                            markeredgecolor="gray", linestyle="none"
                        )
            
            elif error_bar_type == "Standard Error":
                y_pred_all = slope * x_data + intercept
                residuals = y_data - y_pred_all
                residual_std = np.sqrt(np.sum(residuals**2) / (len(x_data) - 2))

                #se for each xvals
                x_mean = np.mean(x_data)
                se_points = residual_std * np.sqrt(1/len(x_data) + (x_data - x_mean)**2 / np.sum((x_data - x_mean)**2))

                # sample points
                step = max(1, len(x_data) // 30)
                
                err_args = (x_data[::step], y_data[::step])
                err_kwargs = {"yerr": se_points[::step]} if not flipped else {"xerr": se_points[::step]}
                
                self.current_ax.errorbar(
                    *err_args, **err_kwargs,
                    fmt="none", ecolor="gray", markersize=3, alpha=0.5, 
                    capsize=4, zorder=8, markerfacecolor="none", 
                    markeredgecolor="none", elinewidth=1, 
                    linestyle="none"
                )

            plot_tab.status_bar.log(
                f"✓ Regression: R²={r_value**2:.4f}, RMSE={rmse:.4f}, slope={slope:.4f}, p={p_value:.4e}",
                "SUCCESS"
            )
        
        except Exception as RegressionAnalysisError:
            plot_tab.status_bar.log(f"Regression analysis failed: {str(RegressionAnalysisError)}", "ERROR")
            import traceback
            print(f"Regression error: {traceback.format_exc()}")
    
    # Plot strategies
    def strategy_line(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Line plot strategy"""
        if axes_flipped:
            #remove formatting kwargs
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            for col in y_cols:
                self.current_ax.plot(
                    plot_tab.data_handler.df[col],
                    plot_tab.data_handler.df[x_col],
                    label=col,
                    **plot_kwargs
                )
            
            self._helper_apply_flipped_labels(plot_tab, x_col, y_cols, font_family)
            if len(y_cols) > 1 or general_kwargs.get("hue"):
                self.current_ax.legend()
            
            #datetime
            try:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    y_data,
                    plot_tab.data_handler.df[x_col]
                )
            except: pass
        else:
            #normal orientation
            plot_method = getattr(self, self.AVAILABLE_PLOTS["Line"])
            plot_method(plot_tab.data_handler.df, x_col, y_cols, **general_kwargs)

            #datetime formatting
            try:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[x_col],
                    y_data
                )
            except: pass
        return None
    
    def strategy_area(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Area plot strategy"""
        if axes_flipped:
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            for col in y_cols:
                self.current_ax.fill_betweenx(
                    plot_tab.data_handler.df[x_col],
                    0,
                    plot_tab.data_handler.df[col],
                    label=col,
                    alpha=plot_tab.alpha_slider.value() # Default alpha for area
                )
            
            self._helper_apply_flipped_labels(plot_tab, x_col, y_cols, font_family)
            if len(y_cols) > 1:
                self.current_ax.legend()
            
            #datetime
            try:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    y_data,
                    plot_tab.data_handler.df[x_col]
                )
            except: pass
        else:
            #normal orientation
            plot_method = getattr(self, self.AVAILABLE_PLOTS["Area"])
            plot_method(plot_tab.data_handler.df, x_col, y_cols, **general_kwargs)

            #datetime
            try:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[x_col],
                    y_data
                )
            except: pass
        return None
    
    def strategy_scatter(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Scatter plot strategy"""
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
                    ax=self.current_ax,
                    **plot_kwargs
                )
            else:
                self.current_ax.scatter(
                    plot_tab.data_handler.df[y_col],
                    plot_tab.data_handler.df[x_col],
                    **plot_kwargs
                )

            self._helper_apply_flipped_labels(plot_tab, x_col, [y_col], font_family)
            
            #datetime
            try:
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[y_col],
                    plot_tab.data_handler.df[x_col]
                )
            except: pass
        else:
            plot_method = getattr(self, self.AVAILABLE_PLOTS["Scatter"])
            plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)

            #datetime
            try:
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[x_col],
                    plot_tab.data_handler.df[y_col]
                )
            except: pass

        #Regression analysis - Run after plotting, handle flipped axes inside
        if (plot_tab.regression_line_check.isChecked() or plot_tab.show_r2_check.isChecked() or 
            plot_tab.show_rmse_check.isChecked() or plot_tab.show_equation_check.isChecked() or 
            plot_tab.error_bars_combo.currentText() != "None"):
            
            if axes_flipped:
                self._helper_add_regression_analysis(plot_tab, y_col, x_col, flipped=True)
            else:
                self._helper_add_regression_analysis(plot_tab, x_col, y_col, flipped=False)
        return None
    
    def strategy_bar(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Bar chart plotting strategy"""
        general_kwargs["width"] = plot_tab.bar_width_spin.value()
        general_kwargs["horizontal"] = axes_flipped

        plot_method = getattr(self, self.AVAILABLE_PLOTS["Bar"])
        plot_method(plot_tab.data_handler.df, x_col, y_cols, **general_kwargs)

        if axes_flipped:
            self._helper_apply_flipped_labels(plot_tab, x_col, y_cols, font_family)
        
        try:
            if axes_flipped:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    y_data,
                    plot_tab.data_handler.df[x_col]
                )
            else:
                y_data = plot_tab.data_handler.df[y_cols[0]] if len(y_cols) == 1 else None
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[x_col],
                    y_data
                )
        except: pass
        return None
    
    def strategy_box(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Box plot plotting strategy"""
        if axes_flipped:
            general_kwargs.pop("title", None)
            general_kwargs.pop("xlabel", None)
            general_kwargs.pop("ylabel", None)
            general_kwargs.pop("legend", None)
            general_kwargs.pop("hue", None)

            plot_tab.data_handler.df[y_cols].plot(
                kind="box",
                ax=self.current_ax,
                vert=False,
                **plot_kwargs
            )

            self._helper_apply_flipped_labels(plot_tab, x_col, y_cols, font_family)
        else:
            plot_method = getattr(self, self.AVAILABLE_PLOTS["Box"])
            plot_method(plot_tab.data_handler.df, y_cols, **general_kwargs)
        return None
    
    
    def strategy_histogram(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Histogram plotting generation"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"Histogram only supports one column. Using: {y_cols[0]}", "WARNING")
        
        # Use first y_col as the data source
        data_col = y_cols[0]
        general_kwargs["xlabel"] = plot_tab.xlabel_input.text() or data_col
        
        general_kwargs["bins"] = plot_tab.histogram_bins_spin.value()
        general_kwargs["show_normal"] = plot_tab.histogram_show_normal_check.isChecked()
        general_kwargs["show_kde"] = plot_tab.histogram_show_kde_check.isChecked()

        plot_method = getattr(self, self.AVAILABLE_PLOTS["Histogram"])
        plot_method(plot_tab.data_handler.df, data_col, **general_kwargs)

        try:
            self._helper_format_datetime_axis(plot_tab, self.current_ax, plot_tab.data_handler.df[data_col])
        except: pass
        return None
    
    def strategy_violin(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Violin plot"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"Violin plots support only one y column. Using {y_cols[0]}")
        
        y_col = y_cols[0]

        if axes_flipped:
            general_kwargs["x"] = y_col
            general_kwargs["y"] = x_col
            general_kwargs["orient"] = "h"
            self._helper_apply_flipped_labels(plot_tab, x_col, [y_col], font_family)
        else:
            general_kwargs["x"] = x_col
            general_kwargs["y"] = y_col
            general_kwargs["orient"] = "v"
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS["Violin"])
        plot_method(plot_tab.data_handler.df, **general_kwargs) # Pass x, y, hue, orient

        try:
            if axes_flipped:
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[y_col],
                    plot_tab.data_handler.df[x_col]
                )
            else:
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[x_col],
                    plot_tab.data_handler.df[y_col]
                )
        except: pass
        return None

    def strategy_pie(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Pie chart generaton"""
        y_col = y_cols[0] if y_cols else None
        general_kwargs["show_percentages"] = plot_tab.pie_show_percentages_check.isChecked()
        general_kwargs["start_angle"] = plot_tab.pie_start_angle_spin.value()
        general_kwargs["explode_first"] = plot_tab.pie_explode_check.isChecked()
        general_kwargs["explode_distance"] = plot_tab.pie_explode_distance_spin.value()
        general_kwargs["shadow"] = plot_tab.pie_shadow_check.isChecked()

        plot_method = getattr(self, self.AVAILABLE_PLOTS["Pie"])
        plot_method(plot_tab.data_handler.df, y_col, x_col, **general_kwargs)
        return None

    def strategy_heatmap(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Heatmap plot generation"""
        # Heatmap ignores x/y, uses all numerical columns
        general_kwargs.update(plot_kwargs)
        plot_method = getattr(self, self.AVAILABLE_PLOTS["Heatmap"])
        plot_method(plot_tab.data_handler.df, **general_kwargs)
        return None
    
    def strategy_kde(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Kernel density estimation plot generation"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"KDE plot only supports one column. Using: {y_cols[0]}", "WARNING")
        
        data_col = y_cols[0]
        general_kwargs["xlabel"] = plot_tab.xlabel_input.text() or data_col
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS["KDE"])
        plot_method(plot_tab.data_handler.df, data_col, **general_kwargs)

        try:
            self._helper_format_datetime_axis(plot_tab, self.current_ax, plot_tab.data_handler.df[data_col])
        except: pass
        return None
    
    def strategy_count(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Count plot strategy"""
        plot_method = getattr(self, self.AVAILABLE_PLOTS["Count Plot"])
        plot_method(plot_tab.data_handler.df, x_col, **general_kwargs)
        return None

    def strategy_hexbin(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Hexbin plot generation"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"Hexbin plot only supports one y column. Using: {y_cols[0]}", "WARNING")
        
        y_col = y_cols[0] if y_cols else None
        
        if axes_flipped:
            general_kwargs["x"] = y_col
            general_kwargs["y"] = x_col
            self._helper_apply_flipped_labels(plot_tab, x_col, [y_col], font_family)
        else:
            general_kwargs["x"] = x_col
            general_kwargs["y"] = y_col
        
        general_kwargs.update(plot_kwargs)
        plot_method = getattr(self, self.AVAILABLE_PLOTS["Hexbin"])
        plot_method(plot_tab.data_handler.df, **general_kwargs)
        return None

    def strategy_2d_density(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """2d desnity plot generaton"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"2D density only supports one y column of values Using: {y_cols[0]}")
        
        y_col = y_cols[0]

        if axes_flipped:
            general_kwargs["x"] = y_col
            general_kwargs["y"] = x_col
            self._helper_apply_flipped_labels(plot_tab, x_col, [y_col], font_family)
            
            try:
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[y_col],
                    plot_tab.data_handler.df[x_col]
                )
            except: pass
        else:
            general_kwargs["x"] = x_col
            general_kwargs["y"] = y_col
            
            try:
                self._helper_format_datetime_axis(
                    plot_tab,
                    self.current_ax,
                    plot_tab.data_handler.df[x_col],
                    plot_tab.data_handler.df[y_col]
                )
            except: pass
        
        general_kwargs.update(plot_kwargs)
        plot_method = getattr(self, self.AVAILABLE_PLOTS["2D Density"])
        plot_method(plot_tab.data_handler.df, **general_kwargs)
        return None

    def strategy_stem(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Stem plot strategy"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"Stem only supports one y column. Using: {y_cols[0]}", "WARNING")
        y_col = y_cols[0]
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS["Stem"])
        plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        try:
            self._helper_format_datetime_axis(plot_tab, self.current_ax, plot_tab.data_handler.df[x_col], plot_tab.data_handler.df[y_col])
        except: pass
        return None
    
    def strategy_stackplot(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Stackplot strategy"""
        if len(y_cols) < 2:
            return "Stackplot requires at least two Y columns."

        plot_method = getattr(self, self.AVAILABLE_PLOTS["Stackplot"])
        plot_method(plot_tab.data_handler.df, x_col, y_cols, **general_kwargs)
        try:
            self._helper_format_datetime_axis(plot_tab, self.current_ax, plot_tab.data_handler.df[x_col])
        except: pass
        return None

    def strategy_stairs(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Stairs plot strategy"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"Stairs only supports one y column. Using: {y_cols[0]}", "WARNING")
        y_col = y_cols[0]
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS["Stairs"])
        plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        try:
            self._helper_format_datetime_axis(plot_tab, self.current_ax, plot_tab.data_handler.df[x_col], plot_tab.data_handler.df[y_col])
        except: pass
        return None
    
    def strategy_eventplot(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """Eventplot strategy"""
        
        general_kwargs["xlabel"] = plot_tab.xlabel_input.text() or "Value"
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS["Eventplot"])
        plot_method(plot_tab.data_handler.df, y_cols, **general_kwargs)
        try:
        
            self._helper_format_datetime_axis(plot_tab, self.current_ax, plot_tab.data_handler.df[y_cols[0]])
        except: pass
        return None
    
    def strategy_hist2d(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """2D Histogram strategy"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"2D Histogram only supports one y column. Using: {y_cols[0]}", "WARNING")
        y_col = y_cols[0]

        general_kwargs.update(plot_kwargs)
        plot_method = getattr(self, self.AVAILABLE_PLOTS["2D Histogram"])
        plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        try:
            self._helper_format_datetime_axis(plot_tab, self.current_ax, plot_tab.data_handler.df[x_col], plot_tab.data_handler.df[y_col])
        except: pass
        return None

    def strategy_ecdf(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """ECDF strategy"""
        if len(y_cols) > 1:
            plot_tab.status_bar.log(f"ECDF only supports one y column. Using: {y_cols[0]}", "WARNING")
        y_col = y_cols[0]
        general_kwargs["xlabel"] = plot_tab.xlabel_input.text() or y_col

        plot_method = getattr(self, self.AVAILABLE_PLOTS["ECDF"])
        plot_method(plot_tab.data_handler.df, y_col, **general_kwargs)
        try:
            self._helper_format_datetime_axis(plot_tab, self.current_ax, plot_tab.data_handler.df[y_col])
        except: pass
        return None

    def _strategy_gridded(self, plot_tab: 'PlotTab', plot_name: str, x_col, y_cols, general_kwargs, plot_kwargs=None):
        """Common strategy for plots requiring gridded x, y, z data."""
        if len(y_cols) < 2:
            return f"{plot_name} requires a Z column. Please select a second Y column (Z-value)."
        
        y_col = y_cols[0] # Y-axis
        z_col = y_cols[1] # Z-axis (color)
        
        general_kwargs["ylabel"] = plot_tab.ylabel_input.text() or y_col
        general_kwargs["z"] = z_col

        if plot_kwargs:
            general_kwargs.update(plot_kwargs)
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS[plot_name])
        plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        return None
    
    def strategy_imshow(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_gridded(plot_tab, "Image Show (imshow)", x_col, y_cols, general_kwargs, plot_kwargs)

    def strategy_pcolormesh(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_gridded(plot_tab, "pcolormesh", x_col, y_cols, general_kwargs, plot_kwargs)

    def strategy_contour(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_gridded(plot_tab, "Contour", x_col, y_cols, general_kwargs, plot_kwargs)

    def strategy_contourf(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_gridded(plot_tab, "Contourf", x_col, y_cols, general_kwargs, plot_kwargs)

    def _strategy_vector(self, plot_tab: 'PlotTab', plot_name: str, x_col, y_cols, general_kwargs, plot_kwargs=None):
        """Common strategy for vector plots (barbs, quiver, streamplot)."""
        if len(y_cols) < 3:
            return f"{plot_name} requires 3 Y columns: Y-position, U (x-component), V (y-component)."
        
        y_col = y_cols[0]
        u_col = y_cols[1]
        v_col = y_cols[2]
        
        general_kwargs["ylabel"] = plot_tab.ylabel_input.text() or y_col
        general_kwargs["u"] = u_col
        general_kwargs["v"] = v_col

        if plot_kwargs:
            general_kwargs.update(plot_kwargs)
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS[plot_name])
        plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        return None
    
    def strategy_barbs(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_vector(plot_tab, "Barbs", x_col, y_cols, general_kwargs, plot_kwargs)

    def strategy_quiver(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_vector(plot_tab, "Quiver", x_col, y_cols, general_kwargs, plot_kwargs)

    def strategy_streamplot(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_vector(plot_tab, "Streamplot", x_col, y_cols, general_kwargs, plot_kwargs)

    def _strategy_triangulation(self, plot_tab: 'PlotTab', plot_name: str, x_col, y_cols, general_kwargs, plot_kwargs=None):
        """Common strategy for unstructured triangulation plots."""
        if len(y_cols) < 2 and plot_name != "Triplot":
            return f"{plot_name} requires a Z column. Please select a second Y column (Z-axis)."
        elif not y_cols and plot_name == "Triplot":
            return f"{plot_name} requires a Y column."

        y_col = y_cols[0] 
        z_col = y_cols[1] if len(y_cols) > 1 else None 
        
        general_kwargs["ylabel"] = plot_tab.ylabel_input.text() or y_col

        if plot_kwargs:
            general_kwargs.update(plot_kwargs)
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS[plot_name])

        if plot_name == "Triplot":
            plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        else:
            if not z_col: 
                return f"{plot_name} requires a Z column, but it was not provided."
            general_kwargs["z"] = z_col
            plot_method(plot_tab.data_handler.df, x_col, y_col, **general_kwargs)
        return None
        
    def strategy_tricontour(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_triangulation(plot_tab, "Tricontour", x_col, y_cols, general_kwargs, plot_kwargs)

    def strategy_tricontourf(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_triangulation(plot_tab, "Tricontourf", x_col, y_cols, general_kwargs, plot_kwargs)

    def strategy_tripcolor(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_triangulation(plot_tab, "Tripcolor", x_col, y_cols, general_kwargs, plot_kwargs)

    def strategy_triplot(self, plot_tab: 'PlotTab', x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        return self._strategy_triangulation(plot_tab, "Triplot", x_col, y_cols, general_kwargs, plot_kwargs)

    def plot_geospatial(self, gdf: "gpd.GeoDataFrame", column: Optional[str] = None, **kwargs) -> None:
        """Create a geospatial plot"""

        if gpd is None:
            self.current_ax.text(0.5, 0.5, "GeoPandas is required for this plot.\nPlease install it first: pip install geopandas", ha="center", va="center", fontsize=12, color="red")
            return
        
        if not isinstance(gdf, gpd.GeoDataFrame):
            self.current_ax.text(0.5, 0.5, "Data is not a GeoDataFrame.\nEnsure a 'geometry' column is present.",ha="center", va="center", fontsize=12, color="red")
            return

        #CRS support and basemap support
        target_crs = kwargs.pop("target_crs", None)
        add_basemap = kwargs.pop("add_basemap", False)
        basemap_source = kwargs.pop("basemap_source", "OpenStreetMap")
        basemap_zoom = kwargs.pop("basemap_zoom", "auto")

        if gdf.crs is None:
            print("Warning. Data has no CRS defined.")
            try:
                gdf.set_crs("EPSG:4326")
            except Exception as SetCRSError:
                print(f"Failed to set default CRS: {SetCRSError}")

        # CRS Transformation
        if target_crs and target_crs.lower() != "none" and target_crs.strip():
            try:
                gdf = gdf.to_crs(target_crs)
            except Exception as CRSInfo:
                print(f"Warning: Coordinate Reference System Transformation failed: {CRSInfo}")
            
        # Basemap
        ## If adding a basemap an no specific CRS is chosen default to Web mercator projection
        if add_basemap and ctx:
            if not target_crs:
                try:
                    if gdf.crs and gdf.crs.to_string() != "EPSG:3857":
                        gdf = gdf.to_crs("EPSG:3857")
                except Exception as ReprojectError:
                    print(f"Warning: Auto-projection for basemap failed: {str(ReprojectError)}")
        
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        legend = kwargs.pop("legend", True)
        orientation = kwargs.pop("orientation", None)
        legend_kwds = kwargs.pop("legend_kwds", {})
        if legend_kwds is None:
            legend_kwds = {}

        use_divider = kwargs.pop("use_divider", False)
        if use_divider and column:
            legend = True
        cax_enabled = kwargs.pop("cax_enabled", False)
        axis_off = kwargs.pop("axis_off", False)

        is_categorical = False
        if column and column in gdf:
            col_dtype = gdf[column].dtype
            if pd.api.types.is_categorical_dtype(col_dtype) or pd.api.types.is_object_dtype(col_dtype):
                is_categorical = True
            if "categorical" in kwargs and kwargs["categorical"]:
                is_categorical = True
            if "scheme" in kwargs and kwargs["scheme"] is not None and kwargs["scheme"] != "None":
                is_categorical = False
        if is_categorical:
            pass
        else:
            if "loc" in legend_kwds:
                legend_kwds.pop("loc")
            if "loc" in kwargs:
                kwargs.pop("loc")

            if isinstance(orientation, str):
                orientation = orientation.lower()
                legend_kwds["orientation"] = orientation
        
        cax = None
        if use_divider and column and legend:
            try:
                divider = make_axes_locatable(self.current_ax)
                if orientation == "horizontal":
                    cax = divider.append_axes("bottom", size="5%", pad=0.1)
                else:
                    cax = divider.append_axes("right", size="5%", pad=0.1)
                
                self.current_ax._cax = cax
            except Exception as DividerError:
                print(f"Error creating axis divider: {DividerError}")
                cax = None
        elif cax_enabled and column:
            pass
        
        if legend:
            if orientation and not is_categorical:
                legend_kwds["orientation"] = orientation
        
        if "cmap" not in kwargs and not is_categorical:
            kwargs["cmap"] = "viridis"

        if column and column in gdf:
            gdf.plot(column=column, ax=self.current_ax, cax=cax, legend=legend, legend_kwds=legend_kwds, **kwargs)
        else:
            kwargs.pop("cmap", None)
            gdf.plot(ax=self.current_ax, **kwargs)
        
        if axis_off:
            self.current_ax.set_axis_off()
        
        # Adding basemap
        if add_basemap and ctx:
            try:
                #Default to OpenStreetMap from Mapnik
                provider = ctx.providers.OpenStreetMap.Mapnik

                source_map = {
                    "OpenStretMap": ctx.providers.OpenStreetMap.Mapnik,
                    "CartoDB Positron": ctx.providers.CartoDB.Positron,
                    "CartoDB DarkMatter": ctx.providers.CartoDB.DarkMatter,
                    "Esri Satellite": ctx.providers.Esri.WorldImagery,
                    "Esri Street": ctx.providers.Esri.WorldStreetMap
                }
                if basemap_source in source_map:
                    provider = source_map[basemap_source]

                if gdf.crs:
                    ctx.add_basemap(
                        self.current_ax,
                        crs=gdf.crs.to_string(),
                        source=provider,
                        zoom=basemap_zoom
                    )
                else:
                    print("Unable to add basemap: CRS is undefined")
            except Exception as BasemapError:
                print(f"Failed to add basemap: {BasemapError}")
        elif add_basemap and not ctx:
            self.current_ax.text(0.02, 0.02, "Install 'contextily' for basemaps", transform=self.current_ax.transAxes, fontsize=8, color="red", bbox=dict(facecolor="white",alpha=0.7))
        
        self._set_labels(title, xlabel, ylabel, False, **kwargs)
    
    def strategy_geospatial(self, plot_tab: "PlotTab", x_col, y_cols, axes_flipped, font_family, plot_kwargs, general_kwargs):
        """GeoSpatial plotting strategy"""
        if gpd is None:
            return "GeoPandas library not found. Please install it first: (`pip install geopandas`) to use geospatial plotting functions"
        
        df = plot_tab.data_handler.df

        if "geometry" not in df.columns:
            return "DataFrame does not contain a 'geometry' column needed to create a geospatial plot."
        
        try:
            gdf = gpd.GeoDataFrame(df, geometry="geometry")
        except Exception as LoadGeoDataFrameError:
            return f"Failed to create GeoDataFrame: {str(LoadGeoDataFrameError)}"
        
        plot_col = y_cols[0] if y_cols else None

        if plot_col:
            general_kwargs["column"] = plot_col
        
        general_kwargs["orientation"] = plot_tab.geo_legend_loc_combo.currentText()
        general_kwargs["use_divider"] = plot_tab.geo_use_divider_check.isChecked()
        general_kwargs["cax_enabled"] = plot_tab.geo_cax_check.isChecked()
        general_kwargs["axis_off"] = plot_tab.geo_axis_off_check.isChecked()
        
        scheme = plot_tab.geo_scheme_combo.currentText()
        if plot_col and scheme != "None":
            general_kwargs["scheme"] = scheme
            general_kwargs["k"] = plot_tab.geo_k_spin.value()

        general_kwargs["edgecolor"] = plot_tab.geo_edge_color
        general_kwargs["linewidth"] = plot_tab.geo_linewidth_spin.value()
        if plot_tab.geo_boundary_check.isChecked():
            general_kwargs["facecolor"] = "none"
        
        if plot_kwargs:
            general_kwargs.update(plot_kwargs)
        
        plot_method = getattr(self, self.AVAILABLE_PLOTS["GeoSpatial"])
        plot_method(gdf, **general_kwargs)

        return None