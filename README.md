# DataPlotStudio

DataPlotStudio is a GUI implementation of the Matplotlib plotting and pandas data analytics capabilities. 
The program is built up of two primary functionalities:
* A data driven tab where you can view, edit, manipulate and alter data based primarily on the pandas library and embedded tools.
* A plotting interface where you can plot your data, as well as tweaking the plot in a graphical environment primarily based on the Matplotlib's `pyplot` functionality.


## Features
* Import data from files: csv, Microsoft Excel, text files, JSON and GeoSpatial fileformats (shp, GeoPackage, GeoJSON)
* Import data from Google Sheets documents and from SQLite, PostgreSQL and SQL databases
* Edit and manipulate your data visually using tools from pandas and embedded custom tools
* View statistics about your data
* Plot the data with 30 different available plot types using Matplotlib, Seaborn and Plotly
* Interactively design and customize your plots
* Add custom plotting code using the integrated Python editor to augment the your data visualization even further
* Export data and Python code to share or use in other tools

## Requirements
Following Python packages are required for the application to run:
```text
pandas==2.2.3
duckdb==1.1.3
pyarrow>=14.0.1
contextily>=1.7.0
numpy==2.2.3
requests==2.32.3
SQLAlchemy==2.0.36
geopandas==1.0.1
scikit-learn==1.6.1
scipy==1.14.1
matplotlib==3.9.2
seaborn==0.13.2
plotly==5.24.1
PyQt6==6.10.0
PyQt6-Qt6==6.10.1
PyQt6-WebEngine==6.10.0
PyQt6-WebEngine-Qt6==6.10.1
PyQt6_sip==13.10.2
```

## Building from source
If you wish to build the application from source, a requirements.txt is provided. 

1. Clone the repository:
```
git clone https://github.com/Johanbo22/DataPlotStudio.git
```

2. Install the dependencies using the `requirements.txt` file with [pip](https://pip.pypa.io/en/stable/):

```
pip install -r requirements.txt
```
Alternatively, install the required packages individually:
```
pip install pandas duckdb numpy requests SQLAlchemy geopandas scikit-learn scipy matplotlib seaborn plotly PyQt6 PyQt6-Qt6 PyQt6-WebEngine PyQt6-WebEngine-Qt6 PyQt6_sip contextily pyarrow
```

3. Navigate into the DataPlotStudio root directory and run main
```
cd DataPlotStudio
python ./main.py
```