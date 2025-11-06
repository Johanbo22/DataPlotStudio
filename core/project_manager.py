# core/project_manager.py
import json
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QFileDialog
import pandas as pd

class ProjectManager:
    
    PROJECT_EXTENSION = ".dps"
    
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
        
        try:
            #convert DataFrame into a dict for JSON serialization
            save_data: Dict[str, Any] = project_data.copy()
            if "dataframe" in save_data and isinstance(save_data["dataframe"], pd.DataFrame):
                save_data["dataframe"] = save_data["dataframe"].to_dict(orient="index")
            
            with open(filepath, "w") as f:
                json.dump(save_data, f, indent=4, default=str)
            
            self.current_project_path = filepath
            return str(filepath)
        
        except Exception as e:
            raise Exception(f"Error saving project: {str(e)}")
    
    def load_project(self, filepath: str) -> Dict[str, Any]:
        filepath = Path(filepath)
        
        if not filepath.exists():
            raise FileNotFoundError(f"Project file not found: {filepath}")
        
        try:
            with open(filepath, "r") as f:
                project_data = json.load(f)
                
            if "dataframe" in project_data and isinstance(project_data["dataframe"], dict):
                project_data["dataframe"] = pd.DataFrame.from_dict(
                    project_data["dataframe"], orient="index"
                )
            
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