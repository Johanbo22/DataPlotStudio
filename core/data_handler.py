# core/data_handler.py
from itertools import groupby
from tkinter import N
from duckdb import connect
from flask.cli import F
import pandas as pd
import numpy as np
import json
from pathlib import Path
from typing import Optional, Dict, Any, List
import requests
import os, tempfile, atexit
from sqlalchemy import create_engine
from sqlalchemy.sql import text
try:
    import geopandas as gpd
except ImportError:
    gpd = None



class DataHandler:
    """Handles all data import, export, and manipulation"""
    
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
        self.original_df: Optional[pd.DataFrame] = None  # For undo operations
        self.file_path: Optional[Path] = None
        self.undo_stack: List[tuple[pd.DataFrame, list]] = []  
        self.redo_stack: List[tuple[pd.DataFrame, list]] = []
        #operation log
        self.operation_log: List[Dict[str, Any]] = []

        #temporary file tracking
        self.temp_csv_path: Optional[Path] = None
        self.is_temp_file: bool = False

        #google sheets credentials tracking
        self.last_gsheet_id: Optional[str] = None
        self.last_gsheet_name: Optional[str] = None
        self.last_gsheet_delimiter: Optional[str] = None
        self.last_gsheet_decimal: Optional[str] = None
        self.last_gsheet_thousands: Optional[str] = None

        #Track database credentials
        self.last_db_connection_string: Optional[str] = None
        self.last_db_query: Optional[str] = None

        # Register clean up upon exit
        atexit.register(self.cleanup_temp_files)

    def cleanup_temp_files(self):
        """Delete temp csv file"""
        if self.temp_csv_path and self.temp_csv_path.exists():
            try:
                os.remove(self.temp_csv_path)
                print(f"DEBUG: Cleaned up and deleted file: {self.temp_csv_path}")
            except PermissionError as e:
                print(f"DEBUG: Permission Denied: {str(e)}")
            except Exception as e:
                print(f"DEBUG: Failed to delete temp file: {str(e)}")
            finally:
                self.temp_csv_path = None
                self.is_temp_file: bool = False
    
    def _create_temp_csv(self, df: pd.DataFrame, source_name: str = "google_sheets") -> Path:
        """Creates a temporary csv file from the dataframe when importing a google sheets sheet"""
        try:
            #create temp directory if it doesnt exists
            temp_dir = Path(tempfile.gettempdir()) / "DataPlotStudio"
            temp_dir.mkdir(exist_ok=True)

            #generate filename
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%HS")
            temp_filename = f"{source_name}_{timestamp}.csv"
            temp_path = temp_dir / temp_filename

            # save the dataframe  to the file
            df.to_csv(temp_path, index=False)

            print(f"DEBUG: Created temporary csv file at: {temp_path}")
            return temp_path
        except Exception as e:
            raise Exception(f"Failed to create a temporary csv: {str(e)}")

    
    def _save_state(self) -> None:
        """Save current state to undo stack"""
        if self.df is not None:
            # make deep copy
            self.undo_stack.append((self.df.copy(), self.operation_log.copy()))
            #clear redo stack when new action is perfoermed
            self.redo_stack.clear()
            print(f"DEBUG: State saved: Undo stack size: {len(self.undo_stack)}")
    
    def undo(self) -> bool:
        """Undo last action"""
        print(f"DEBUG: Undo called. Stack Size: {len(self.undo_stack)}")
        if len(self.undo_stack) == 0:
            return False
        
        # Save current state to redo stack
        if self.df is not None:
            self.redo_stack.append((self.df.copy(), self.operation_log.copy()))
        
        # Restore from undo stack
        restored_df, restored_log = self.undo_stack.pop()
        self.df = restored_df.copy()
        self.operation_log = restored_log.copy()
        print(f"DEBUG: Undo complete. Remaining stack: {len(self.undo_stack)}")
        return True
    
    def redo(self) -> bool:
        """Redo last undone action"""
        print(f"DEBUG: Redo called. Stack size: {len(self.redo_stack)}")
        if len(self.redo_stack) == 0:
            return False
        
        # Save current state to undo stack
        if self.df is not None:
            self.undo_stack.append((self.df.copy(), self.operation_log.copy()))
        
        # Restore from redo stack
        restored_df, restored_log = self.redo_stack.pop()
        self.df = restored_df.copy()
        self.operation_log = restored_log.copy()
        print(f"DEBUG: Redo complete. Remaining stack: {len(self.redo_stack)}")
        return True
    
    def can_undo(self) -> bool:
        """Check if undo is available"""
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        """Check if redo is available"""
        return len(self.redo_stack) > 0
    
    def import_file(self, filepath: str) -> pd.DataFrame:
        """Import data from various file formats
        
        Args:
            filepath (str): The path to file file that is imported
        
        Returns:
            data (pd.DataFrame):
        """

        #check if any tempfiles exist
        if self.is_temp_file:
            self.cleanup_temp_files()
        
        path = Path(filepath)
        extension = path.suffix.lower()
        
        try:
            if extension in ['.xlsx', '.xls']: # xls format is sometimes janky
                self.df = pd.read_excel(filepath)
            elif extension == '.csv':
                con = connect(database=':memory:', read_only=False)
                try:
                    self.df = con.execute(f"SELECT * FROM read_csv_auto('{path.as_posix()}')").df()
                except Exception as import_file_error:
                    con.close()
                    print(f"DEBUG: DuckDB failed ({str(import_file_error)}), falling back to pandas")
                    self.df = pd.read_csv(filepath)
                finally:
                    con.close()
            elif extension == '.txt':
                con = connect(database=":memory:", read_only=False)
                try:
                    self.df = con.execute(f"SELECT * FROM read_csv_auto('{path.as_posix()}', delim='\t')").df()
                except Exception as import_file_error:
                    con.close()
                    print(f"DEBUG: DuckDB failed: ({str(import_file_error)}), falling back to pandas")
                    self.df = pd.read_csv(filepath, sep="\t")
                finally:
                    con.close()
            elif extension == '.json':
                self.df = pd.read_json(filepath)
            elif extension in [".geojson", ".shp", ".gpkg"]:
                if gpd is None:
                    raise ImportError("GeoPandas is not installed. Please install GeoPandas to load spatial data")
                self.df = gpd.read_file(filepath)
            elif extension == ".shx":
                raise ValueError("This is an shapefile index (.shx) file.\nPlease open the shapefile (.shp) fil instead.")
            else:
                raise ValueError(f"Unsupported file format: {extension}")
            
            self.original_df = self.df.copy()
            self.file_path = path
            self.is_temp_file = False
            self.last_gsheet_id = None
            self.last_gsheet_name = None
            self.last_gsheet_delimiter = None
            self.last_gsheet_decimal = None
            self.last_gsheet_thousands = None
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.operation_log.clear()
            return self.df
        
        except Exception as e:
            raise Exception(f"Error importing file: {str(e)}")
    
    def import_google_sheets(self, sheet_id: str, sheet_name: str, delimiter: str = ",", decimal: str = ".", thousands: str = None) -> pd.DataFrame:
        """Import data from Google Sheets using sheet_id and sheet_name"""
        try:
            #delete existing tempfiles
            if self.is_temp_file:
                self.cleanup_temp_files()

            if not sheet_id or not sheet_name:
                raise ValueError("Sheet ID and Sheet Name cannot be empty")
            
            sheet_id = sheet_id.strip()
            sheet_name = sheet_name.strip()

            #store params so user can refresh without adding writing it again
            self.last_gsheet_id = sheet_id
            self.last_gsheet_name = sheet_name
            self.last_gsheet_delimiter = delimiter
            self.last_gsheet_decimal = decimal
            self.last_gsheet_thousands = thousands

            print(f"DEBUG data_handler.py->import_google_sheets: Storing parameters:")
            print(f"  - Delimiter: '{self.last_gsheet_delimiter}'")
            print(f"  - Decimal: '{self.last_gsheet_decimal}'")
            print(f"  - Thousands: {repr(self.last_gsheet_thousands)}")
            
            # Try multiple URL formats for better compatibility
            urls_to_try = [
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}",
                f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}",
            ]
            
            df = None
            last_error = None
            
            for url in urls_to_try:
                try:
                    response: requests.Response = requests.get(url, timeout=10)
                    response.raise_for_status()
                    
                    # Check if response is valid CSV
                    if response.text and len(response.text) > 10:
                        from io import StringIO
                        df = pd.read_csv(StringIO(response.text), sep=delimiter, decimal=decimal, thousands=thousands, encoding="utf-8", on_bad_lines="skip", engine="python")
                        
                        if df is not None and len(df) > 0:
                            break  # 
                except Exception as e:
                    last_error = e
                    continue
            
            if df is None or len(df) == 0:
                raise ValueError("The sheet appears to be empty or inaccessible. The data could not be retrieved.")
            
            self.df = df
            self.original_df = self.df.copy()

            #create temp csv
            safe_sheet_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in sheet_name)
            self.temp_csv_path = self._create_temp_csv(self.df, f"gsheet_{safe_sheet_name}")
            self.file_path = self.temp_csv_path
            self.is_temp_file = True

            self.undo_stack.clear()
            self.redo_stack.clear()
            self.operation_log.clear()
            return self.df
            
        except requests.exceptions.Timeout:
            raise Exception("Connection timeout: Google Sheets took too long to respond.\n\nTry again in a moment or check your internet connection.")
        except requests.exceptions.ConnectionError:
            raise Exception("Connection error: Unable to connect to Google Sheets.\n\nCheck your internet connection.")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise Exception("Sheet not found (404)\n\nPossible causes:\n• Sheet ID is incorrect\n• Sheet has been deleted\n• Sheet is not publicly accessible\n\nDouble-check the Sheet ID and verify sharing settings.")
            elif e.response.status_code == 403:
                raise Exception("Permission denied (403)\n\nThe sheet is not publicly accessible.\n\nTo fix:\n1. Open the Google Sheet\n2. Click 'Share' (top right)\n3. Select 'Anyone with the link'\n4. Choose 'Viewer' or higher\n5. Try importing again")
            else:
                raise Exception(f"HTTP Error {e.response.status_code}: {str(e)}")
        except ValueError as e:
            raise Exception(f"Invalid input or empty sheet:\n{str(e)}")
        except Exception as e:
            error_msg = str(e)
            raise Exception(f"Error importing Google Sheet:\n{error_msg}\n\nVerification checklist:\n✓ Sheet ID is correct\n✓ Sheet name matches exactly (case-sensitive)\n✓ Sheet is shared publicly\n✓ Internet connection is active\n✓ Try with Sheet1 first")
    def has_google_sheet_import(self) -> bool:
        """Check if the last import was a google sheet"""
        return self.last_gsheet_id is not None and self.last_gsheet_name is not None
    
    
    def import_from_database(self, connection_string: str, query: str) -> pd.DataFrame:
        """Import data from a database witha connection and a query request"""
        try:
            #first delete temp files
            if self.is_temp_file:
                self.cleanup_temp_files()
            
            #raise error if there is no connection string or no query
            if not connection_string or not query:
                raise ValueError("A connection string and a query are needed to import from a database.")
            
            #store parameters so we can refresh the data again
            self.last_db_connection_string = connection_string
            self.last_db_query = query

            #remove any other import source information to not make conflicts
            self.last_gsheet_id = None
            self.last_gsheet_name = None
            self.file_path = None
            self.is_temp_file = False

            #create and connect
            engine = create_engine(connection_string)
            with engine.connect() as connection:
                df = pd.read_sql_query(text(query), connection)
            
            #raise error if connection is empty or returns none
            if df is None or len(df) == 0:
                raise ValueError("Query returned no data.")
            
            self.df = df
            self.original_df = self.df.copy()

            #from the database data we create a temp_csv file for the storing and saving logic to better work.
            self.temp_csv_path = self._create_temp_csv(self.df, "db_import")
            self.file_path = self.temp_csv_path
            self.is_temp_file = True

            self.undo_stack.clear()
            self.redo_stack.clear()
            self.operation_log.clear()
            return self.df
        
        except ImportError:
            raise Exception("SQLAlchemy or database driver is not installed.\nPlease install 'sqlalchemy' and appropriate drivers (e.g., 'psycopg2-binary').")
        except Exception as e:
            self.last_db_connection_string = None
            self.last_db_query = None
            raise Exception(f"Database import failed:\n{str(e)}")
        
    def update_cell(self, row_index: int, column_index: int, value: Any) -> None:
        """Update a cell in the data table"""
        if self.df is None:
            return
        
        try:
            self._save_state()

            column_name = self.df.columns[column_index]
            column_datatype = self.df[column_name].dtype

            if value is not None:
                if pd.api.types.is_integer_dtype(column_datatype):
                    try:
                        value = int(value)
                    except ValueError:
                        pass
                elif pd.api.types.is_float_dtype(column_datatype):
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                elif pd.api.types.is_bool_dtype(column_datatype):
                    if isinstance(value, str):
                        value = value.lower() in ("true", "1", "t", "yes", "y")
            
            self.df.iat[row_index, column_index] = value

            self.operation_log.append({
                "type": "update_cell",
                "row": row_index,
                "col": column_index,
                "value": value
            })
        
        except Exception as update_cell_error:
            raise Exception(f"Error updating cell: {str(update_cell_error)}")
    
    def create_empty_dataframe(self, rows: int, columns: int, column_names: List[str] = None) -> pd.DataFrame:
        """Creates a new empty dataframe"""
        try:
            self._save_state()

            if not column_names:
                column_names = [f"Column_{i + 1}" for i in range(columns)]

            self.df = pd.DataFrame(index=range(rows), columns=column_names)

            self.original_df = self.df.copy()

            #have to clear sources 
            self.file_path = None
            self.is_temp_file = False
            self.last_gsheet_id = None
            self.last_gsheet_name = None
            self.last_db_connection_string = None
            self.last_db_query = None

            self.undo_stack.clear()
            self.redo_stack.clear()
            self.operation_log.clear()

            return self.df
        except Exception as create_empty_dataframe_error:
            raise Exception(f"Error creating DataFrame: {str(create_empty_dataframe_error)}")

    def get_data_info(self) -> Dict[str, Any]:
        """Get comprehensive statistics about the data"""
        if self.df is None:
            return {}
        
        info = {
            'shape': self.df.shape,
            'columns': list(self.df.columns),
            'dtypes': self.df.dtypes.to_dict(),
            'missing_values': self.df.isnull().sum().to_dict(),
            'statistics': self.df.describe().to_dict(),
            'memory_usage': self.df.memory_usage(deep=True).to_dict(),
        }
        return info
    
    def filter_data(self, column: str, condition: str, value: Any) -> pd.DataFrame:
        """Filter data based on conditions (>, <, ==, !=, etc.)"""
        if self.df is None:
            raise ValueError("No data loaded")

        if not isinstance(self.df, pd.DataFrame):
            raise TypeError(f"self.df is {type(self.df)}, expected pandas DataFrame")

        try:
            # Ensure column exists
            if column not in self.df.columns:
                raise KeyError(f"Column '{column}' not found in DataFrame")

            # Match value type to column dtype
            col_dtype = self.df[column].dtype
            try:
                if pd.api.types.is_integer_dtype(col_dtype):
                    value = int(value)
                elif pd.api.types.is_float_dtype(col_dtype):
                    value = float(value)
                elif pd.api.types.is_object_dtype(col_dtype):
                    value = str(value)
            except (ValueError, TypeError):
                pass

            # Apply filtering
            if condition == '>':
                self.df = self.df[self.df[column] > value]
            elif condition == '<':
                self.df = self.df[self.df[column] < value]
            elif condition == '==':
                self.df = self.df[self.df[column] == value]
            elif condition == '!=':
                self.df = self.df[self.df[column] != value]
            elif condition == '>=':
                self.df = self.df[self.df[column] >= value]
            elif condition == '<=':
                self.df = self.df[self.df[column] <= value]
            elif condition == 'contains':
                self.df = self.df[self.df[column].astype(str).str.contains(str(value), na=False)]
            elif condition == 'in':
                if not isinstance(value, (list, tuple, set)):
                    value = [value]
                self.df = self.df[self.df[column].isin(value)]
            else:
                raise ValueError(f"Unknown filter condition: {condition}")
            
            self.operation_log.append({
                "type": "filter",
                "column": column,
                "condition": condition,
                "value": value
            })

            return self.df

        except Exception as e:
            raise Exception(f"Error filtering data: {str(e)}")

    
    def aggregate_data(self, group_by: List[str], agg_columns: List[str], agg_func: str) -> pd.DataFrame:
        """Aggregate data with groupby operations"""
        if self.df is None:
            raise ValueError("No data loaded")
        
        try:
            self._save_state()

            #build aggregation dict
            agg_dict = {col: (col, agg_func) for col in agg_columns}

            self.df = self.df.groupby(group_by).agg(**agg_dict).reset_index()

            self.operation_log.append({
                "type": "aggregate",
                "group_by": group_by,
                "agg_columns": agg_columns,
                "agg_func": agg_func
            })

            return self.df
        except Exception as e:
            raise Exception(f"Error aggregating data: {str(e)}")
    
    def melt_data(self, id_vars: List[str], value_vars: List[str], var_name: str, value_name: str) -> pd.DataFrame:
        """Use melt to unpivot a dataframe"""
        if self.df is None:
            raise ValueError("No data loaded")
        
        try:
            self._save_state()

            v_vars = value_vars if value_vars else None

            self.df = pd.melt(
                self.df,
                id_vars=id_vars,
                value_vars=v_vars,
                var_name=var_name,
                value_name=value_name
            )

            self.operation_log.append({
                "type": "melt",
                "id_vars": id_vars,
                "value_vars": value_vars,
                "var_name": var_name,
                "value_name": value_name
            })

            return self.df
        except Exception as melt_error:
            raise Exception(f"Error melting data: {str(melt_error)}")
    
    def clean_data(self, action: str, **kwargs) -> pd.DataFrame:
        """Clean data: remove duplicates, handle missing values, etc."""
        if self.df is None:
            raise ValueError("No data loaded")
        
        try:
            #Save state efore changes
            self._save_state()


            if action == 'drop_duplicates':
                self.df = self.df.drop_duplicates()
            elif action == 'drop_missing':
                self.df = self.df.dropna()
            elif action == 'fill_missing':
                method = kwargs.get("method", "ffill")
                column = kwargs.get("column", "All Columns")
                fill_value = kwargs.get("value", None)

                if column == "All Columns" or column is None:
                    target_cols = self.df.columns
                else:
                    target_cols = [column]
                
                if method == "static_value":
                    for col in target_cols:
                        val_to_use = fill_value
                        if pd.api.types.is_numeric_dtype(self.df[col]) and isinstance(fill_value, str):
                            try:
                                if "." in fill_value:
                                    val_to_use = float(fill_value)
                                else:
                                    val_to_use = int(fill_value)
                            except ValueError:
                                pass
                        
                        self.df[col] = self.df[col].fillna(val_to_use)
                
                elif method in ["mean", "median", "mode"]:
                    for col in target_cols:
                        if method in ["mean", "median"] and not pd.api.types.is_numeric_dtype(self.df[col]):
                            continue
                        if method == "mean":
                            fill_val = self.df[col].mean()
                        elif method == "median":
                            fill_val = self.df[col].median()
                        elif method == "mode":
                            modes = self.df[col].mode()
                            fill_val = modes[0] if not modes.empty else None
                        
                        if fill_val is not None:
                            self.df[col] = self.df[col].fillna(fill_val)
                
                elif method in ["ffill", "bfill"]:
                    for col in target_cols:
                        self.df[col] = self.df[col].fillna(method=method)
            elif action == 'drop_column':
                column = kwargs.get('column')
                self.df = self.df.drop(columns=[column])
            elif action == 'rename_column':
                old_name = kwargs.get('old_name')
                new_name = kwargs.get('new_name')
                self.df = self.df.rename(columns={old_name: new_name})
            elif action == "change_data_type":
                column = kwargs.get("column")
                new_type = kwargs.get("new_type")

                if not column or not new_type:
                    raise ValueError("Column and new_type are need to change change_type")
                
                if new_type == "string":
                    self.df[column] = self.df[column].astype(pd.StringDtype())
                elif new_type == "int":
                    #convert errors to NaN
                    self.df[column] = pd.to_numeric(self.df[column], errors="coerce")
                    self.df[column] = self.df[column].astype(pd.Int64Dtype())
                elif new_type == "float":
                    #convert errors to NaN
                    self.df[column] = pd.to_numeric(self.df[column], errors="coerce")
                    self.df[column] = self.df[column].astype(pd.Float64Dtype())
                elif new_type == "category":
                    self.df[column] = self.df[column].astype("category")
                elif new_type == "datetime":
                    #convert errors to NaT
                    self.df[column] = pd.to_datetime(self.df[column], errors="coerce")
                else:
                    raise ValueError(f"Unsupported data type conversion: {new_type}")
                
            log_entry = {"type": action, **kwargs}
            self.operation_log.append(log_entry)
                
            print(f"DEBUG: clean_data({action}) completed. Undo stack: {len(self.undo_stack)}")
            return self.df
        except Exception as e:
            raise Exception(f"Error cleaning data: {str(e)}")
    
    def reset_data(self) -> None:
        """Reset data to original state"""
        if self.original_df is not None:
            # Dont save state when resset 
            #clear stacks
            self.undo_stack.clear()
            self.redo_stack.clear()
            self.operation_log.clear()
            self.df = self.original_df.copy()
            print(f"DEBUG: Data reset. Stacks cleared")
    
    def export_data(self, filepath: str, format: str = 'csv') -> None:
        """Export data to file"""
        if self.df is None:
            raise ValueError("No data loaded")
        
        try:
            if format == 'csv':
                self.df.to_csv(filepath, index=False)
            elif format == 'xlsx':
                self.df.to_excel(filepath, index=False)
            elif format == 'json':
                self.df.to_json(filepath)
        except Exception as e:
            raise Exception(f"Error exporting data: {str(e)}")
    
    def get_data_source_info(self) -> Dict[str, Any]:
        """Get info about the data source"""
        return {
            "file_path": str(self.file_path) if self.file_path else None,
            "is_temp_file": self.is_temp_file,
            "temp_csv_path": str(self.temp_csv_path) if self.temp_csv_path else None,
            "has_data": self.df is not None,
            "last_db_connection_string": self.last_db_connection_string,
            "last_db_query": self.last_db_query
        }
    
    def refresh_google_sheets(self) -> pd.DataFrame:
        """Refresh the CSV data from the last imported Google Sheets document 
        without the user having to re-enter SheetID"""
        if not self.last_gsheet_id or not self.last_gsheet_name:
            raise ValueError("No history a Google Sheet Import")
        
        print(f"DEBUG refresh_google_sheets: Using stored parameters:")
        print(f"  - Sheet ID: {self.last_gsheet_id}")
        print(f"  - Sheet Name: {self.last_gsheet_name}")
        print(f"  - Delimiter: '{self.last_gsheet_delimiter}'")
        print(f"  - Decimal: '{self.last_gsheet_decimal}'")
        print(f"  - Thousands: {repr(self.last_gsheet_thousands)}")

        thousands_param = None if self.last_gsheet_thousands in [None, "None", ""] else self.last_gsheet_thousands
        
        return self.import_google_sheets(
            self.last_gsheet_id,
            self.last_gsheet_name,
            delimiter=self.last_gsheet_delimiter,
            decimal=self.last_gsheet_decimal,
            thousands=thousands_param
        )
    
    def has_google_sheets_import(self) -> bool:
        """Check if a Google Sheet can be refreshed"""
        return bool(self.last_gsheet_id and self.last_gsheet_name)