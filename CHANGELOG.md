# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog (https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## Unreleashed
### Added
- Coordinate Reference System Transformation for geospatial plots
- Adding basemap tiles from Esri, OpenStreetMap, CartoDB as background maps.
- Picker tools for canvas. Allows for clicking on elements in plot canvas and be moved to appropriate settings for that element
- TwinX support: Allows a secondary y axis to be plotted with its own scale.
- Export plot button: Added a button that gets relevant settings before exporting the plot. Is easier to find that the embedded tool from matplotlib that is hidden in the navigatortoolbar of the canvas.
- Quick Filter: Added a quick filter tool that can be used before plotting to write queries that filter the data based on an expression.
- Theme creator: Add default and custom themes to the plot. These are predefined JSON files where custom themes can be loaded.
- Edit theme: Edit custom themes or create copies of the default themes using the JSON editor. 
### Changed
- The plot selection is now a gridded format, instead of a list. Makes it easier to find and select the correct plot
- The visibility of certain UI in the "Customization" tab of the PlotStudio. Hides elements not useful for the current plot
- The support for the Plotly backend, Extended it to accomodate for more styling options directly from the matplotlib backend.
### Fixed
- Bug where freezing selected data for subplotting was ignored and overriden.
- Issues with slow table scrolling and slow plot rendering when using large datasets. Now using a cache system to store information about the plot. If the changes are styling based, the dataframe is not read again, instead cache data is used.
- Bug where coloraxis and color legends for geospatial plots was not parsed correctly and would either not show up or create duplicates.
- Bug where the data table on a plot was duplicated each time the placement parameter was changed. Caused multiple of the same table to be plotted.

## v0.0.4
### Added
- Text Manipulation to string data. Trim text data, and standardize casing etc
- Calculate column. Create new columns and use arithmetic, comparative and logical operations to calculate values in the new column.
- Sorting tool added to the operations panel on the right side of the data tab.
- Interpolation as options in the fill missing values tool. Choose between linear interpolation and time interpolation.
### Changed
- The way sorting the table is done. Allows a permanent sorting of data, useful before exporting data to a new file.
### Fixed
- Text error in Create and calculate column dialog
### Removed
-

## v0.0.3-alpha
### Added
- New search functionality to the data table. Allows for searching for values in the table and finds them.
- DuckDB databases as new possible database connections.
- A Test connection button so a database connection can be tested before a query is sent.
- Drag and drop files from explorer into the main view. This will load the file and import the data as normal.
- Welcome page with actions for opening existing project, creating new empty project, importing data from file, sheet, database
- Welcome page with what's new information
### Changed
- The way filtering data is handled. The reset does not happen automatically. Allows for filter into filter operations
### Fixed
- Bug where plotting any plots that cannot have legends. Legend now not parsed as keyword args to main engine.
- Bug where data table would reset position upon toggling edit mode ON/OFF.
### Removed
- Forced reset of data before using a new filter