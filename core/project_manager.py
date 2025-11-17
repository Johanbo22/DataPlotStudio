# core/project_manager.py
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QFileDialog
from glm import project
import pandas as pd

class ProjectManager:
    
    PROJECT_EXTENSION = ".dps"
    DATA_EXTENSION = ".dps.data"
    
    def __init__(self) -> None:
        self.current_project_path: Optional[Path] = None
        self.project_data: Dict[str, Any] = {}
    
    def new_project(self) -> None:
        
        self.current_project_path = None
        self.project_data = {
            "metadata": {
                "version": "1.0",
                "name": "Untitled Project"
            },
            "data": None,
            "plot_config": {},
            "operations": []
        }
    
    def save_project(self, project_data: Dict[str, Any], filepath: Optional[str] = None) -> str:
        
        if filepath is None:
            filepath, _ =QFileDialog.getSaveFileName(
                None,
                "Save Project",
                "",
                f"DataPlot Studio Files (*{self.PROJECT_EXTENSION});;All Files (*)"
            )
            if not filepath:
                raise Exception("Save cancelled")
    
        filepath = Path(filepath)
        if not filepath.suffix == self.PROJECT_EXTENSION:
            filepath = filepath.with_suffix(self.PROJECT_EXTENSION)

        data_filepath = filepath.with_suffix(self.DATA_EXTENSION)
        
        try:
            save_data: Dict[str, Any] = project_data.copy()
            dateframe: Optional[pd.DataFrame] = None

            #saving data to a binary file
            if "data" in save_data and isinstance(save_data["data"], pd.DataFrame):
                dataframe = save_data.pop("data", None)
            
            if dataframe is not None:
                with open(data_filepath, "wb") as data_file:
                    pickle.dump(dataframe, data_file)
                save_data["data_file"] = data_filepath.name
            else:
                if data_filepath.exists():
                    data_filepath.unlink()
                if "data_file" in save_data:
                    del save_data["data_file"]
            
            #metadata saved to json
            with open(filepath, "w") as metadata_file:
                json.dump(save_data, metadata_file, indent=4, default=str)
            
            self.current_project_path = filepath
            return str(filepath)
        
        except Exception as e:
            raise Exception(f"Error saving project: {str(e)}")
    
    def load_project(self, filepath: str) -> Dict[str, Any]:
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Project file not found: {filepath}")
        
        try:
            
            #load metadata
            with open(filepath, "r") as metadata_file:
                project_data = json.load(metadata_file)
            
            if "data_file" in project_data:
                data_filename = project_data["data_file"]
                data_filepath = filepath.parent / data_filename

                if not data_filepath.exists():
                    raise FileNotFoundError(f"Data file for project not found: {data_filepath}")

                #load datafile
                with open(data_filepath, "rb") as data_file:
                    dataframe = pickle.load(data_file)
                
                project_data["data"] = dataframe
                del project_data["data_file"]
            
            elif "data" in project_data and isinstance(project_data["data"], dict):
                project_data["data"] = pd.DataFrame.from_dict(
                    project_data["data"], orient="index"
                )
                del project_data["data"]
            
            self.current_project_path = filepath
            self.project_data = project_data
            return project_data
        
        except Exception as e:
            raise Exception(f"Error loading project: {str(e)}")

    
    def open_project_dialog(self) -> Optional[str]:
        filepath, _ = QFileDialog.getOpenFileName(
            None,
            "Open Project",
            "",
            f"DataPlot Studio Files (*{self.PROJECT_EXTENSION});;All Files (*)"
        )
        return filepath if filepath else None
    
    def get_current_project_path(self) -> Optional[str]:
        return str(self.current_project_path) if self.current_project_path else None