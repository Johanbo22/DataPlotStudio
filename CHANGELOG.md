# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog (https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## Unreleashed

## v0.0.4
### Added
- Text Manipulation to string data. Trim text data, and standardize casing etc
- Calculate column. Create new columns and use arithmetic, comparative and logical operations to calculate values in the new column.
- Sorting tool added to the operations panel on the right side of the data tab.
- Interpolation as options in the fill missing values tool. Choose between linear interpolation and time interpolation.
### Changed
- The way sorting the table is done. Allows a permanent sorting of data, useful before exporting data to a new file.s
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