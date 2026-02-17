# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog (https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## v0.0.9
### Added
- A visual join diagram as a Venn Diagram in the Merge tool to preview the merge of datasets
- Data Cleaning Preview: The operations, "Remove Duplicates" and "Drop Missing Values", now highlight affected rows and requires a confirm to be removed.
- Select points in plot: A selection tool to select points in a plot will redirect to the data explorer and highlight the selected points.
- Added a colorblindess filter in the Appearance tab of the PlotTab, to allow for colorblindness accessibility
- Added a custom QGraphicsEffect SVG filter using numpy to calculate the rgba values for each colorblindess type.
- Statistical test support in `DataHandler` using `scipy.stats`
- An action to the table context menu to run statistical tests on two columns
- A separate Test results tab with the test results
- Support for a portable .dps zip format for project save files
- Internal SQLite database for each project
- Updated PlotConfigs to include all missing/newly added controls and properties.
- Regression type selection in the Scatter Plot settings panel
- Polynomial degree selection to configure polynomials
- Feature to export datasets to Google Sheets using Service Account
- Dialog for exporting datasets using Service Account credentialsJSON and target worksheets
- Menu action for "Export to Google Sheets"
### Changed
- Updated the plot engine to use matplotlib.colormaps registry
- Switched to defusedxml.ElemenTree for XML loading of project files.
- Google Sheets Import enforces data integrity by raising errors on bad lines instead of skipping them,
- Renaming columns and creating a new column validates for names that could cause issues or crashes.
- Refreshing google sheet documents now executes asynchronously
- Opening an existing project automatically renders the plot saved to the project file.
- Statistics generation is now handled by a separate class
- Changed to lazy loading of large tables in the table view.
- Disk I/O is handled by `tempfile.TemporaryDirectory()` to avoid corruption by partial save states
- Refactored scatter plot analysis to support generic *y_pred* arrays for R2, RMSE and standard errors
- Bound the canvas `SpanSelector` to right-click to avoid unintentional canvas selection when dragging annotations.
- Expanded `DataHandler` to use google-auth to export to a Service Account google sheet.
- Moved markdown_parsing from LandingPage.py to separate script in `core`
- Changed `log_action` in `StatusBar` with a flag to ensure details are only logged to file once per instance.
- Updated typing character in `StatusBar` to calculate chunk size based on string length. This ensures more consistent animation no matter length of log entry.
- Updated HTML text blocks to use transparent backgrounds that removes a blocky outline on text in Test Results Viewer and Statistics Viewer.
### Fixed
- Bug where twinx and twiny support was not properly implemented in the code editor. Would raise an error upon clicking "Run Script"
- Bug were the plotting engine would use cached data to redraw canvas, resulting in no change in redrawing even if data was changed.
- Memory leak where old Matplotlib figures were not being closed, leading to increased memory usage over time and a eventual OOM crash.
- Freezing when filter/aggregating large datasets
- Bug where flipping the axes (swtiching x and y axis) would cause a crash
- Issue where using a horizontal bar chart and adding a secondary y axis would cause the bar chart to become vertical.
- Resolved an issue where import errors were swallowed and reported as "empty" sheet when importing data from Google Sheets
- Fixed an issue where entering invalid numbers into an integer column would change the columns data type to object or corrupt the dataframe
- Fixed an issue where the SubplotOverlay would flicker upon resizing the canvas or window
- Fixed a code injection vulnerability where malicious strings could execute arbitrary code in exported scripts.
- Fixed an issue where clicking "New Project" in the menubar remained on the welcome page instead of creating an empty data table.
- Wrong arrow icons not being shown on scrollbars.
- Fixed an issue where integers cast to floating point were displayed using e-notation.
- Fixed issue where searching for values in a large dataset would cause a freezing due to indexing.
- Large spikes in latency when handling tables with >100k rows during fast scrolling
- A render bug when editing data and sorting the data table with large tables with > 100k rows
- Typos in `_load_appearance_config` mapped wrong keys for LaTeX rendering and y-label parameters
- Stuttering and text overwriting in terminal when receiving multiple log events
- File logging duplication issue with overlapping log entries.
- Method `update_data_stats` in `StatusBar` checks for the existance of df.shape before unpacking values.
- Wrong implementation of progress bar styling in the `FillMissingValuesDialog`
- Fixed aggressive caching for `generate_plot` that caused the plot not to update without prompting a data column change
- Resolved an issue where the GeoSpatial settings remained visible even when non-geospatial plot types were selected
### Removed
- Deprecated XML DOM tree proccessing for project save files and project configs

## v0.0.8
### Added:
- HoverFocusAnimationMixin class to handle border animations
- ThemeColors for a centralised widget color system
- New toggle switch widget to complement the checkbox system.
- Persistent history of the last 5 selected colormaps with a "Recently used" header.
- Landing Page: Added links to view bug fixes and version release notes from the welcome screen.
### Changed
- Widgets in dialogs, tabs etc.
### Removed
- Individual widget styling and animations.


## v0.0.7
### Added
- **Aggregate Data**
    - Aggregate multiple columns per grouping with a function
    - Date grouping to aggregate datetime data
    - Preview table for aggregated data in the dialog. View the result of data aggregation before committing to it.
- **Calculate Column**
    - Math, Trigonometry and String functions to be used in the Calculate Column dialog.
- **Detect Outliers**
    - A histogram to view distribution of data when checking for outliers using the Detect Outliers toolbox
    - Clipping outliers from data based on the threshold instead of just removing all rows.
- **Fill Missing**
    - Fill Missing Values now allows for grouping. Fill values in a column based on a grouping of another column
    - Fill Missing Values tool now has a progress bar that shows how many cells are NaN
- **Melt data**
    - Preview Table of the Melted/pivoted dataframe while using the MeltData Dialog. Allows for seeing the new data table before it is committed
- **Database Connections**
    - Profiles in Database Connection to avoid re-entering the same information all the time. Save and load profiles to get access to a prieviously connected database.
    - Use Raw URI strings to establish a connection to a database
- **Google Sheets Import**
    - History to google sheets import. The app will now remember the sheet_id last used to prevent re-entering the same details
- **Colormap picker**
    - Categorised Colormaps: Colormaps are now grouped by type
    - Reversing colormaps: Colormaps can be reversed using the "Reverse Colormap" checkbox
    - Improved filtering: The search function has now been improved.
- **Table Customisation**
    - Floating point precision to control the number of decimal places for floating-point numbers
    - Conditional formatting using a rule builder to highlight cells based on numerical rules
- **Filter and Subset Creation**
    - Data Type Aware inputs: Better widgets based on the data type instead of an arbitrary box
    - Nested conditions: Chain queries using different conditionals (eg ```A AND B OR C```)
    - Null Checks: Adds a "Is Null" and "Is Not Null" to check for NaN values in dataset.
- **Script Editor**
    - Insert code snippets: Common complemtary code snippets from a menu allows for adding snippets of code to enhance your plot
    - Variable explorer: A side panel with info and column names for the current active dataframe to assist in using the code editor.
    - Find and Replace: Search and replace words in the editor
    - Autocompletion: A basic auto-completion of python keywords and builtin functions when typing.
- **Pivot table**
    - Added pivot table creation from regular table format.
- **Merge datasets**
    - Added a dialog for merging / joining two datasets
- **Binning/Discretization**
    - Added support for binning numerical data into groups.
### Changed
- The expression field in Calculate Column Dialog now uses the CodeEditor styling for better syntax highlighting
- Stdout and Stderr from the python code editor will now send to an widget inside the editor instead of just the the system terminal.
### Fixed
- Wrong buttons used in Melt Dialog
- Text issue for a label in the Database Connection dialog
- Issue where RadioButton did not change styling when checked/unchecked.
- Popup bug when an item in a combobox was clicked the focus changed causing a crash.

## v0.0.6
### Added
- Added EPS, TIFF, PS, RAW bitmap and RGBA as options for file formats when saving figure. 
- Drag manually added annotations around the plot canvas.
### Changed
- DPI settings are now located in the dialog when exporting/saving the figure as an image.
### Fixed
- Issue where changing DPI, figure height or width would result in a canvas that was too large to view on screen.
- Issue where the overlay graphics for the current active subplot did not draw correctly and was offset by lower bbox.
- Bug where clearing a plot would result in an empty plot when recreating the same plot using the same parameters.
- Bug where checking "Auto Annotate Points" would result in unremoveable annotations as they would persist after unchecking.
- Bug where adding a manual annotation, moving it and then recreate the plot would duplicate the annotation
### Removed
- DPI settings from plotting interface.


## v0.0.5
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