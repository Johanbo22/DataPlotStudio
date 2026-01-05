# DataPlotStudio

DataPlotStudio is a GUI implementation of the Matplotlib plotting and pandas data analytics capabilities. 
The program is built up of two primary functionality:
* A data driven tab where you can view, edit, manipulate and alter data based primarily on the pandas library and embedded tools.
* A plotting interface where you can plot your data, as well as tweaking the plot in a graphical environment primarily based on the matplotlib.pyplot functionality. A backend for the plotly plotting library is implemented as well.


## Features
* Import data from files: csv, Microsoft Excel, text files, JSON and GeoSpatial fileformats (shp, GeoPackage, GeoJSON)
* Import data from Google Sheets documents and from SQL databases
* Edit and manipulate your data visually using embedded tools from pandas
* View statistics about your data
* Plot the data with 30 different available plot types using matplotlib
* Interactively design the plot
* Add custom plotting code using the integrated code editor
* Export data and Python code to share or use in other tools

## Requirements
If you wish to build the application from source, a requirements.txt is provided. To install with [pip](https://pip.pypa.io/en/stable/):

```
pip install -r requirements.txt
```
Otherwise version 10.1 of [PyQt6](https://doc.qt.io/qtforpython-6/) is required.