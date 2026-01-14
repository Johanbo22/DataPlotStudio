# Changelog
All notable changes to this project will be documented in this file.

The format is based on Keep a Changelog (https://keepachangelog.com/en/1.0.0/),
and this project adheres to Semantic Versioning.

## Unreleased
### Added
- New search functionality to the data table. Allows for searching for values in the table and finds them.
- DuckDB databases as new possible database connections.
- A Test connection button so a database connection can be tested before a query is sent.
- Drag and drop files from explorer into the main view. This will load the file and import the data as normal.
### Changed
- The way filtering data is handled. The reset does not happen automatically. Allows for filter into filter operations
### Fixed
- Bug where plotting any plots that cannot have legends. Legend now not parsed as keyword args to main engine.
- Bug where data table would reset position upon toggling edit mode ON/OFF.
### Removed
- Forced reset of data before using a new filter