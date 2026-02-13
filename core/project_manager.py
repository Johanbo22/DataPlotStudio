# core/project_manager.py
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QFileDialog
import pandas as pd
from resources.version import APPLICATION_VERSION, PROJECT_EXTENSION, DATA_EXTENSION
import zipfile
import json
import sqlite3
import tempfile

class ProjectManager:
    
    PROJECT_EXTENSION = PROJECT_EXTENSION
    DATA_EXTENSION = DATA_EXTENSION
    APPLICATION_VERSION = APPLICATION_VERSION
    
    def __init__(self) -> None:
        self.current_project_path: Optional[Path] = None
        self.project_data: Dict[str, Any] = {}
    
    def new_project(self) -> None:
        
        self.current_project_path = None
        self.project_data = {
            "metadata": {
                "version": self.APPLICATION_VERSION,
                "name": "Untitled Project"
            },
            "data": None,
            "plot_config": {},
            "operations": []
        }
    
    def save_project(self, project_data: Dict[str, Any], filepath: Optional[str] = None) -> str:
        
        if filepath is None:
            filepath, _ = QFileDialog.getSaveFileName(
                None,
                "Save Project Package",
                "",
                f"DataPlotStudio Portable Files (*{self.PROJECT_EXTENSION});;All Files (*)"
            )
            if not filepath:
                raise Exception(f"Save cancelled")
        
        filepath_obj = Path(filepath)
        if not filepath_obj.suffix == ".dps":
            filepath_obj = filepath_obj.with_suffix(".dps")
        
        try:
            save_data: Dict[str, Any] = project_data.copy()
            dataframe: Optional[pd.DataFrame] = save_data.pop("data", None) if isinstance(save_data.get("data"), pd.DataFrame) else None
            
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                
                # First we archive the raw data using parquet serialization
                if dataframe is not None:
                    dataframe.to_parquet(temp_dir_path / "data.parquet", engine="pyarrow", index=True)
                
                # Then archive plot configerations which are .json files
                plot_config_path = temp_dir_path / "plot_config.json"
                with open(plot_config_path, "w", encoding="utf-8") as config_file:
                    json.dump(save_data.get("plot_config", {}), config_file, indent=4)
                
                # Then archive the total operation log which also a .json file'
                operations_path = temp_dir_path / "operations_log.json"
                with open(operations_path, "w", encoding="utf-8") as operations_file:
                    json.dump(save_data.get("operations", []), operations_file, indent=4)
                
                # Create a metadata for the session states as a SQLITE database
                db_path = temp_dir_path / "session.db"
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE session_metadata (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                """)
                metadata = save_data.get("metadata", {})
                for key, value in metadata.items():
                    cursor.execute("INSERT INTO session_metadata (key, value) VALUES (?, ?)", (str(key), str(value)))
                conn.commit()
                conn.close()
                
                # last we compress all files into a .dps package
                with zipfile.ZipFile(filepath_obj, "w", zipfile.ZIP_DEFLATED) as zip_package:
                    for file_to_zip in temp_dir_path.iterdir():
                        zip_package.write(file_to_zip, arcname=file_to_zip.name)
            
            self.current_project_path = filepath_obj
            return str(filepath_obj)
        
        except Exception as SaveProjectError:
            raise Exception(f"Error packaging project files: {str(SaveProjectError)}")
    
    def load_project(self, filepath: str) -> Dict[str, Any]:
        filepath_obj = Path(filepath)
        
        if not filepath_obj.exists():
            raise FileNotFoundError(f"Project package file cannot be found at: {filepath_obj}")
        
        try:
            project_data: Dict[str, Any] = {
                "metadata": {},
                "data": None,
                "plot_config": {},
                "operations": []
            }
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_dir_path = Path(temp_dir)
                
                with zipfile.ZipFile(filepath_obj, "r") as zip_package:
                    zip_package.extractall(temp_dir_path)
                
                # First restore the raw data
                data_path = temp_dir_path / "data.parquet"
                if data_path.exists():
                    project_data["data"] = pd.read_parquet(data_path, engine="pyarrow")
                
                # Second restore plot configs
                plot_config_path = temp_dir_path / "plot_config.json"
                if plot_config_path.exists():
                    with open(plot_config_path, "r", encoding="utf-8") as config_file:
                        project_data["plot_config"] = json.load(config_file)
                
                # Then restore the operations log
                operations_path = temp_dir_path / "operations_log.json"
                if operations_path.exists():
                    with open(operations_path, "r", encoding="utf-8") as operations_file:
                        project_data["operations"] = json.load(operations_file)
                
                # Restore session from database
                db_path = temp_dir_path / "session.db"
                if db_path.exists():
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT key, value FROM session_metadata")
                    rows = cursor.fetchall()
                    for row in rows:
                        project_data["metadata"][row[0]] = row[1]
                    conn.close()
            
            self.current_project_path = filepath_obj
            self.project_data = project_data
            return project_data
        
        except Exception as LoadProjectError:
            raise Exception(f"Error extracting files to load project: {LoadProjectError}")
    
    def open_project_dialog(self) -> Optional[str]:
        filepath, _ = QFileDialog.getOpenFileName(
            None,
            "Open Project",
            "",
            f"DataPlotStudio Portable Files (*{self.PROJECT_EXTENSION});;All Files (*)"
        )
        return filepath if filepath else None
    
    def get_current_project_path(self) -> Optional[str]:
        return str(self.current_project_path) if self.current_project_path else None