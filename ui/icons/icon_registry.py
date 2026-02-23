from enum import Enum, auto
from typing import Type, Dict, Callable
from PyQt6.QtGui import QIcon

from .icon_engine import BaseIconEngine

class IconType(Enum):
    """
    Enum of all icons available
    """
    #### Data Operations icons
    FILTER = auto()
    ADVANCED_FILTER = auto()
    CLEAR_FILTER = auto()
    REMOVE_DUPLICATES = auto()
    DROP_MISSING_VALUES = auto()
    FILL_MISSING_VALUES = auto()
    DROP_COLUMN = auto()
    RENAME_COLUMN = auto()
    DUPLICATE_COLUMN = auto()
    CALCULATOR = auto()
    CHANGE_DATATYPE = auto()
    TEXT_OPERATION = auto()
    DATA_TRANSFORM = auto()
    EDIT_COLUMNS = auto()
    DATA_CLEANING = auto()
    SORT = auto()
    
    #### File operations/menu ops
    OPEN_PROJECT = auto()
    SAVE_PROJECT = auto()
    SAVE_PROJECT_AS = auto()
    NEW_PROJECT = auto()
    IMPORT_FILE = auto()
    EXPORT_FILE = auto()
    IMPORT_DATABASE = auto()
    QUIT = auto()
    
    # Plot operation icons
    GENERATE_PLOT = auto()
    SAVE_PLOT = auto()
    CLEAR_PLOT = auto()
    OPEN_PYTHON_EDITOR = auto()
    PLOT_GENERAL_OPTIONS = auto()
    PLOT_APPEARANCE = auto()
    PLOT_AXES = auto()
    PLOT_LEGEND_GRID = auto()
    PLOT_CUSTOMIZATION = auto()
    PLOT_ANNOTATIONS = auto()
    PLOT_GEOSPATIAL = auto()
    
    # Main UI icons
    PLOT_TAB_ICON = auto()
    DATA_EXPLORER_ICON = auto()
    EXPLORE_STATISTICS_ICON = auto()
    UNDO = auto()
    REDO = auto()
    SETTINGS = auto()
    ZOOM_IN = auto()
    ZOOM_OUT = auto()
    INFORMATION = auto()
    REFRESH_ITEM = auto()
    VIEW_ITEM = auto()
    DELETE_ITEM = auto()

class IconBuilder:
    """
    Registry for QIcons
    """
    _registry: Dict[IconType, Type[BaseIconEngine]] = {}
    @classmethod
    def register(cls, icon_type: IconType) -> Callable[[Type[BaseIconEngine]], Type[BaseIconEngine]]:
        """
        Maps icontypes to subclasses
        """
        def wrapper(engine_cls: Type[BaseIconEngine]) -> Type[BaseIconEngine]:
            if icon_type in cls._registry:
                raise ValueError(f"Icon for {icon_type} already registered")
            cls._registry[icon_type] = engine_cls
            return engine_cls
        return wrapper
    
    @classmethod
    def build(cls, icon_type: IconType, resolution: int = 128) -> QIcon:
        icon_cls = cls._registry.get(icon_type)
        if not icon_cls:
            raise NotImplementedError(f"No icon registered for {icon_type.name}")
        return icon_cls().build(resolution=resolution)
    