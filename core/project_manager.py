# core/project_manager.py
import json
import xml.etree.ElementTree as XMLET
import pickle
from pathlib import Path
from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QFileDialog
import pandas as pd

class ProjectManager:
    
    PROJECT_EXTENSION = ".dps"
    DATA_EXTENSION = ".dps.data"
    APPLICATION_VERSION = "0.0.1"
    
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
                "Save Project",
                "",
                f"DataPlotStudio Files (*.{self.PROJECT_EXTENSION});;All Files (*)"
            )
            if not filepath:
                raise Exception("Save cancelled")
        
        filepath = Path(filepath)
        if not filepath.suffix == self.PROJECT_EXTENSION:
            filepath = filepath.with_suffix(self.PROJECT_EXTENSION)
        
        data_filepath = filepath.with_suffix(self.DATA_EXTENSION)

        try:
            save_data: Dict[str, Any] = project_data.copy()
            dataframe: Optional[pd.DataFrame] = None

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
            
            #root XML
            root = XMLET.Element("DPSProject")
            self._dict_to_xml(root, save_data)
            tree = XMLET.ElementTree(root)

            if hasattr(XMLET, "indent"):
                XMLET.indent(tree, space="    ", level=0)
            tree.write(filepath, encoding="utf-8", xml_declaration=True)

            self.current_project_path = filepath
            return str(filepath)
        
        except Exception as save_project_error:
            raise Exception(f"Error saving current project: {str(save_project_error)}")

    
    def load_project(self, filepath: str) -> Dict[str, Any]:
        filepath = Path(filepath)

        if not filepath.exists():
            raise FileNotFoundError(f"Project file cannot be found at: {filepath}")
        
        try:
            tree = XMLET.parse(filepath)
            root = tree.getroot()

            #convert
            project_data = self._xml_to_dict(root)

            #also load datafile
            if "data_file" in project_data:
                data_filename = project_data["data_file"]
                data_filepath = filepath.parent / data_filename

                if not data_filepath.exists():
                    raise FileNotFoundError(f"No data file for this project could be found: {data_filepath}")
                
                with open(data_filepath, "rb") as data_file:
                    dataframe = pickle.load(data_file)
                
                project_data["data"] = dataframe
                del project_data["data_file"]
            
            if "operations" not in project_data or project_data["operations"] is None:
                project_data["operations"] = []
            elif not isinstance(project_data["operations"], list):
                project_data["operations"] = [project_data["operations"]]
            
            self.current_project_path = filepath
            self.project_data = project_data
            return project_data
        
        except Exception as LoadProjectError:
            raise Exception(f"Error loading current project: {str(LoadProjectError)}")
    
    def _dict_to_xml(self, parent: XMLET.Element, data: Dict[str, Any]) -> None:
        """Convert dict to XML tree"""
        for key, value in data.items():
            if isinstance(value, dict):
                child = XMLET.SubElement(parent, key)
                self._dict_to_xml(child, value)
            
            elif isinstance(value, list):
                child = XMLET.SubElement(parent, key)
                for item in value:
                    item_element = XMLET.SubElement(child, "item")
                    if isinstance(item, dict):
                        self._dict_to_xml(item_element, item)
                    else:
                        item_element.text = str(item)
            
            elif value is None:
                XMLET.SubElement(parent, key).text = "None"
            else:
                XMLET.SubElement(parent, key).text = str(value)
    
    def _xml_to_dict(self, element: XMLET.Element) -> Any:
        """convert XML to dict"""
        children = list(element)
        if not children:
            return self._parse_value(element.text)
        
        if all(child.tag == "item" for child in children):
            return [self._xml_to_dict(child) for child in children]
        
        result = {}
        for child in children:
            result[child.tag] = self._xml_to_dict(child)
        return result
    
    def _parse_value(self, value: Optional[str]) -> Any:
        """Parsing string vals to native vals"""
        if value is None or value == "None":
            return None
        if value.lower() == "true":
            return True
        if value.lower() == "false":
            return False
        
        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        return value

    
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