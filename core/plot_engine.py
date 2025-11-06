# core/plot_engine.py
import deprecated
from matplotlib.mlab import GaussianKDE
import matplotlib.pyplot as plt
import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import numpy as np
import seaborn as sns
from typing import Dict, Any, Optional, List


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
        "Triplot": "plot_triplot"
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
    }

    
    def __init__(self):
        self.current_figure: Optional[Figure] = None
        self.current_ax = None
        self.current_plot_type: Optional[str] = None
        self.plot_config: Dict[str, Any] = {}
    
    def create_figure(self, figsize=(10, 6), dpi=100) -> Figure:
        """Create a new matplotlib figure"""
        self.current_figure = Figure(figsize=figsize, dpi=dpi)
        self.current_ax = self.current_figure.add_subplot(111)
        return self.current_figure
    
    def plot_line(self, df: pd.DataFrame, x: str, y: List[str], **kwargs) -> None:
        """Create a line plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        hue = kwargs.pop("hue", None)

        marker = kwargs.pop("marker", None)

        if marker in (None, ""):
            kwargs["marker"] = None
        elif marker is not None:
            kwargs["marker"] = marker
            

        if hue:
            for group in df[hue].unique():
                mask = df[hue] == group
                for col in y:
                    self.current_ax.plot(df.loc[mask, x], df.loc[mask, col], label=f"{col} - {group}", **kwargs)
        else:
            # as a sep line
            for col in y:
                self.current_ax.plot(df[x], df[col], label=col, **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight="bold")
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        if legend and len(y) > 1:
            self.current_ax.legend()
        
        self.current_figure.tight_layout()
    
    def plot_scatter(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a scatter plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        hue = kwargs.pop('hue', None)
        
        if hue:
            for group in df[hue].unique():
                mask = df[hue] == group
                self.current_ax.scatter(df.loc[mask, x], df.loc[mask, y], label=group, **kwargs)
        else:
            self.current_ax.scatter(df[x], df[y], **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        if legend:
            self.current_ax.legend()
        
        self.current_figure.tight_layout()
    
    def plot_bar(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a bar plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        hue = kwargs.pop('hue', None)
        width = kwargs.pop("width", 0.8)
        horizontal = kwargs.pop("horizontal", False)
        
        if isinstance(y, str):
            y = [y]

        if len(y) == 1 and not hue:
            #single y col
            y_col_name = y[0]
            if horizontal:
                self.current_ax.barh(df[x], df[y_col_name], height=width, **kwargs)
            else:
                self.current_ax.bar(df[x], df[y_col_name], width=width, **kwargs)
        
        elif len(y) > 1:
            #grouped bar chart
            x_labels = df[x].unique()
            x_pos = np.arange(len(x_labels))
            bar_width = width / len(y)

            for i, col in enumerate(y):
                offset = (i - len(y) / 2) * bar_width + bar_width / 2
                values = [df[df[x] == label][col].values[0] if len(df[df[x] == label]) > 0 else 0 for label in x_labels]

                if horizontal:
                    self.current_ax.barh(x_pos + offset, values, height=bar_width, label=col, **kwargs)
                else:
                    self.current_ax.bar(x_pos + offset, values, width=bar_width, label=col, **kwargs)
            
            if horizontal:
                self.current_ax.set_yticks(x_pos)
                self.current_ax.set_yticklabels(x_labels)
            else:
                self.current_ax.set_xticks(x_pos)
                self.current_ax.set_xticklabels(x_labels)
        
        elif hue:
            # Single y with hue using seaborn
            import seaborn as sns
            if horizontal:
                sns.barplot(data=df, y=x, x=y[0], hue=hue, ax=self.current_ax, orient="h", **kwargs)
            else:
                sns.barplot(data=df, x=x, y=y[0], hue=hue, ax=self.current_ax, **kwargs)

        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        if legend and len(y) > 1:
            self.current_ax.legend()
        
        self.current_figure.tight_layout()
    
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
        
        data = df[column].dropna()

        #calculate mean and std
        mu = data.mean()
        sigma = data.std()
        median = data.median()

        n, bins_edges, patches = self.current_ax.hist(data, bins=bins, density=show_normal or show_kde, **kwargs)

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

        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        
        self.current_figure.tight_layout()
    
    def plot_box(self, df: pd.DataFrame, columns: List[str], **kwargs) -> None:
        """Create a box plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)

        if isinstance(columns, str):
            columns = [columns]
        
        df[columns].plot(kind='box', ax=self.current_ax, **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        
        self.current_figure.tight_layout()
    
    def plot_violin(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a violin plot using seaborn"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        
        sns.violinplot(data=df, x=x, y=y, ax=self.current_ax, **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        
        self.current_figure.tight_layout()
    
    def plot_heatmap(self, df: pd.DataFrame, **kwargs) -> None:
        """Create a heatmap using seaborn"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        
        # Ensure numeric data
        numeric_df = df.select_dtypes(include=[np.number])
        sns.heatmap(numeric_df.corr(), annot=True, ax=self.current_ax, **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        
        self.current_figure.tight_layout()
    
    def plot_kde(self, df: pd.DataFrame, column: str, **kwargs) -> None:
        """Create a KDE plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        
        df[column].plot(kind='kde', ax=self.current_ax, **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        
        self.current_figure.tight_layout()
    
    def plot_area(self, df: pd.DataFrame, x: str, y: List[str], **kwargs) -> None:
        """Create an area plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)

        if isinstance(y, str):
            y = [y]
    
        df_plot = df.set_index(x)[y]
        df_plot.plot(kind="area", ax=self.current_ax, stacked=True, **kwargs)
        
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        if legend and len(y) > 1:
            self.current_ax.legend()
        
        self.current_figure.tight_layout()
    
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

        # create format
        autopct = "%1.2f%%" if show_percentages else None

        #explode
        explode = None
        if explode_first:
            explode = [explode_distance] + [0] * (len(df[values]) - 1)
        
        self.current_ax.pie(df[values], labels=df[names], autopct=autopct, startangle=start_angle, explode=explode, shadow=shadow, **kwargs)
        self.current_ax.set_ylabel('')
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        
        self.current_figure.tight_layout()
    
    def plot_count(self, df: pd.DataFrame, column: str, **kwargs) -> None:
        """Create a count plot using seaborn"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        
        sns.countplot(data=df, x=column, ax=self.current_ax, **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        
        self.current_figure.tight_layout()
    
    def plot_hexbin(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a hexbin plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        legend = kwargs.pop('legend', True)
        gridsize = kwargs.pop('gridsize', 20)
        
        self.current_ax.hexbin(df[x], df[y], gridsize=gridsize, **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        
        self.current_figure.tight_layout()
    
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
        
        sns.kdeplot(data=df, x=x, y=y, ax=self.current_ax, fill=True, **kwargs)
        
        if title:
            self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel:
            self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel:
            self.current_ax.set_ylabel(ylabel, fontsize=12)
        
        self.current_figure.tight_layout()

    def plot_stem(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a stem plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        legend = kwargs.pop("legend", False)

        self.current_ax.stem(df[x], df[y], **kwargs)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight="bold")
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)

        self.current_figure.tight_layout()
    
    def plot_stackplot(self, df: pd.DataFrame, x: str, y: List[str], **kwargs) -> None:
        """Create a stackplot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)
        legend = kwargs.pop("legend", True)

        df_sorted = df.sort_values(by=x)
        y_data = [df_sorted[col] for col in y]

        self.current_ax.stackplot(df_sorted[x], *y_data, labels=y, **kwargs)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        if legend: self.current_ax.legend()

        self.current_figure.tight_layout()

    def plot_stairs(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a stairs plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)

        df_sorted = df.sort_values(by=x)
        self.current_ax.stairs(df_sorted[x], df_sorted[y], **kwargs)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        
        self.current_figure.tight_layout()

    def plot_eventplot(self, df: pd.DataFrame, y: list[str], **kwargs) -> None:
        """Create an eventplot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)

        data_to_plot = [df[col].dropna().values for col in y]

        self.current_ax.eventplot(data_to_plot, **kwargs)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if len(y) > 1:
            self.current_ax.set_yticks(range(len(y)))
            self.current_ax.set_yticklabels(y)
        
        self.current_figure.tight_layout()

    def plot_hist2d(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a 2D histogram"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)

        hist = self.current_ax.hist2d(df[x], df[y], **kwargs)
        self.current_figure.colorbar(hist[3], ax=self.current_ax, label="counts")

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)

        self.current_figure.tight_layout()
    
    def plot_ecdf(self, df: pd.DataFrame, y: str, **kwargs) -> None:
        """Create an ECDF plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)

        self.current_ax.ecdf(df[y], **kwargs)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        self.current_ax.set_ylabel("ECDF")
        self.current_figure.tight_layout()

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

            if np.isnan(Z).any():
                Z = pd.DataFrame(Z).fillna(0).values()
            
            return X, Y, Z
        except Exception as e:
            raise ValueError(f"Data could not be pivoted into a 2D grid. Is the data gridded?: Error: {str(e)}")
    
    def plot_imshow(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create an imshow plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)

        X, Y, Z = self._prepare_gridded_data(df, x, y, z)

        img = self.current_ax.imshow(Z, extent=[X.min(), X.max(), Y.min(), Y.max()], origin="lower", aspect="auto", **kwargs)
        self.current_figure.colorbar(img, ax=self.current_ax, label=z)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()
    
    def plot_pcolormesh(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a pcolormesh plot"""
        title = kwargs.pop("title", None)
        xlabel = kwargs.pop("xlabel", None)
        ylabel = kwargs.pop("ylabel", None)

        X, Y, Z = self._prepare_gridded_data(df, x, y, z)
        X_grid, Y_grid = np.meshgrid(X, Y)

        mesh = self.current_ax.pcolormesh(X_grid, Y_grid, Z, **kwargs)
        self.current_figure.colorbar(mesh, ax=self.current_ax, label=z)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()
    
    def plot_contour(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a contour plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)

        X, Y, Z = self._prepare_gridded_data(df, x, y, z)
        X_grid, Y_grid = np.meshgrid(X, Y)

        cont = self.current_ax.contour(X_grid, Y_grid, Z, **kwargs)
        self.current_ax.clabel(cont, inline=True, fontsize=8)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()

    def plot_contourf(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a filled contour plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)

        X, Y, Z = self._prepare_gridded_data(df, x, y, z)
        X_grid, Y_grid = np.meshgrid(X, Y)

        contf = self.current_ax.contourf(X_grid, Y_grid, Z, **kwargs)
        self.current_figure.colorbar(contf, ax=self.current_ax, label=z)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()

    def plot_barbs(self, df: pd.DataFrame, x: str, y: str, u: str, v: str, **kwargs) -> None:
        """Create a barbs plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)

        self.current_ax.barbs(df[x], df[y], df[u], df[v], **kwargs)

        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()
    
    def plot_quiver(self, df: pd.DataFrame, x: str, y: str, u: str, v: str, **kwargs) -> None:
        """Create a quiver plot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        
        self.current_ax.quiver(df[x], df[y], df[u], df[v], **kwargs) # type: ignore
        
        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()
    
    def plot_streamplot(self, df: pd.DataFrame, x: str, y: str, u: str, v: str, **kwargs) -> None:
        """Create a streamplot"""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)

        
        try:
            X, Y, U_grid = self._prepare_gridded_data(df, x, y, u)
            _, _, V_grid = self._prepare_gridded_data(df, x, y, v)
            X_grid, Y_grid = np.meshgrid(X, Y)
        except Exception as e:
            raise ValueError(f"Streamplot requires gridded data (pivoted x, y, u, v). Error: {e}")

        self.current_ax.streamplot(X_grid, Y_grid, U_grid, V_grid, **kwargs)
        
        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()
    
    def plot_tricontour(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a tricontour plot from unstructured x, y, z."""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        
        cont = self.current_ax.tricontour(df[x], df[y], df[z], **kwargs)
        self.current_ax.clabel(cont, inline=True, fontsize=8)
        
        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()

    def plot_tricontourf(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a filled tricontour plot from unstructured x, y, z."""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        
        contf = self.current_ax.tricontourf(df[x], df[y], df[z], **kwargs)
        self.current_figure.colorbar(contf, ax=self.current_ax, label=z)
        
        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()

    def plot_tripcolor(self, df: pd.DataFrame, x: str, y: str, z: str, **kwargs) -> None:
        """Create a tripcolor plot from unstructured x, y, z."""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        
        trip = self.current_ax.tripcolor(df[x], df[y], df[z], **kwargs)
        self.current_figure.colorbar(trip, ax=self.current_ax, label=z)
        
        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()

    def plot_triplot(self, df: pd.DataFrame, x: str, y: str, **kwargs) -> None:
        """Create a triplot from unstructured x, y."""
        title = kwargs.pop('title', None)
        xlabel = kwargs.pop('xlabel', None)
        ylabel = kwargs.pop('ylabel', None)
        
        self.current_ax.triplot(df[x], df[y], **kwargs)
        
        if title: self.current_ax.set_title(title, fontsize=14, fontweight='bold')
        if xlabel: self.current_ax.set_xlabel(xlabel, fontsize=12)
        if ylabel: self.current_ax.set_ylabel(ylabel, fontsize=12)
        self.current_figure.tight_layout()
    
    def _apply_common_formatting(self, kwargs: Dict[str, Any]) -> None:
        """Apply common formatting to plots\n
        This method is now deprecated as formatting is done in individual plot methods"""
        pass
    
    def clear_plot(self) -> None:
        """Clear the current plot"""
        if self.current_figure:
            self.current_figure.clear()
            self.current_ax = self.current_figure.add_subplot(111)
    
    def get_figure(self) -> Figure:
        """Return the current figure"""
        return self.current_figure
