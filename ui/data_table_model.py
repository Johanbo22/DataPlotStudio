import pandas as pd
import numpy as np
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt6.QtGui import QColor
from typing import Any
from ui.status_bar import StatusBar
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.data_handler import DataHandler

class DataTableModel(QAbstractTableModel):
    """ table for the data Table"""

    def __init__(self, data_handler: "DataHandler", editable: bool=False, parent: Any=None, highlighted_rows: list[int] | None=None, float_precision: int = 2, conditional_rules: list[dict[str, Any]] | None = None):
        super().__init__(parent)
        self.data_handler = data_handler
        self._data = self.data_handler.df
        self.editable = editable
        self.highlighted_rows = set(highlighted_rows) if highlighted_rows else set()
        self.float_precision = float_precision
        self.conditional_rules = conditional_rules if conditional_rules else []
        
        # Buffer sizes for lazy-loading
        self._chunk_size: int = 1000
        self._data_buffer: dict[int, pd.DataFrame] = {}

        if self._data is not None:
            self._is_numeric = [
                pd.api.types.is_numeric_dtype(dtype) for dtype in self._data.dtypes
            ]
    
    def set_float_precision(self, precision: int):
        """Updates the floating point precision and refreshes the datble"""
        self.float_precision = precision
        self.layoutChanged.emit()
    
    def set_conditional_rules(self, rules: list):
        """Updates the conditional formatting rules and refreshes the dtable"""
        self.conditional_rules = rules
        self.layoutChanged.emit()
    
    def set_highlighted_rows(self, rows: set) -> None:
        """Updates the highlighed rows and triggers a layout refresh on display changes"""
        self.highlighted_rows = set(rows) if rows else set()
        self.layoutChanged.emit()

    def rowCount(self, parent=QModelIndex()) -> int:
        """Returns the number of rows in a dataframe"""
        if parent.isValid() or self._data is None:
            return 0
        return self._data.shape[0]
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Returns the number of columns in the dataframe"""
        if parent.isValid() or self._data is None:
            return 0
        return self._data.shape[1]
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Returns le data"""
        if not index.isValid() or self._data is None:
            return None
        
        row: int = index.row()
        col: int = index.column()
        
        # We determine the chunk index to use a cached subset of the dataframe
        # this is to stop the frequent .iat calls on large datasets
        chunk_index: int = row // self._chunk_size
        
        if chunk_index not in self._data_buffer:
            # Maintain a strict buffer size of 5
            if len(self._data_buffer) >= 5:
                oldest_chunk_key: int = next(iter(self._data_buffer))
                del self._data_buffer[oldest_chunk_key]
            
            start_idx: int = chunk_index * self._chunk_size
            end_idx: int = start_idx + self._chunk_size
            self._data_buffer[chunk_index] = self._data.iloc[start_idx:end_idx]
        
        try:
            val: Any = self._data_buffer[chunk_index].iat[row % self._chunk_size, col]
        except Exception:
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            try:
                if pd.isna(val):
                    return "NaN"
                
                if isinstance(val, (bool, np.bool_)):
                    return str(val)
                
                if isinstance(val, (int, np.integer)):
                    return int(val)
                
                if isinstance(val, (float, np.floating)):
                    return f"{val:.{self.float_precision}f}"
                
                s_val: str = str(val)
                if len(s_val) > 64:
                    return s_val[:64] + "..."
                return s_val

            except Exception:
                return None
        
        elif role == Qt.ItemDataRole.EditRole:
            try:
                if pd.isna(val):
                    return ""
                return str(val)
            except Exception:
                return ""
        
        elif role == Qt.ItemDataRole.ForegroundRole:
            try:
                if isinstance(val, (int, float, np.number)) and not pd.isna(val):
                    for rule in self.conditional_rules:
                        operator: str = rule.get("operator", "")
                        target: float = rule.get("value", 0.0)
                        color: str = rule.get("color", "#000000")
                        
                        match: bool = False
                        if operator == "<":
                            match = val < target
                        elif operator == ">":
                            match = val > target
                        elif operator == "=":
                            match = val == target
                        elif operator == "<=":
                            match = val <= target
                        elif operator == ">=":
                            match = val >= target
                            
                        if match:
                            return QColor(color)
            except Exception:
                pass
            return None
        
        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.row() in self.highlighted_rows:
                return QColor("#ffcccc")
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            if index.column() < len(self._is_numeric) and self._is_numeric[index.column()]:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter
        
        return None
    
    def setData(self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole) -> bool:
        """data ypdater"""
        if not index.isValid() or role != Qt.ItemDataRole.EditRole or not self.editable:
            return False
        
        try:
            row = index.row()
            column = index.column()
            
            self.data_handler.update_cell(row, column, value)
            self._data_buffer.clear()

            self.dataChanged.emit(index, index, [Qt.ItemDataRole.DisplayRole, Qt.ItemDataRole.EditRole])
            return True
        
        except Exception as UpdateDataModelError:
            print(f"Error updating data: {str(UpdateDataModelError)}")
            return False
    
    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Return item flags"""
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        
        default_flags = Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable

        if self.editable:
            return default_flags | Qt.ItemFlag.ItemIsEditable
        
        return default_flags
    
    def set_editable(self, editable: bool) -> None:
        """Update the editable state of the table model"""
        self.editable = editable
        self.layoutChanged.emit()
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> QVariant | str:
        """Returns the header of the data"""
        if role != Qt.ItemDataRole.DisplayRole or self._data is None:
            return QVariant()
        
        if orientation == Qt.Orientation.Horizontal:
            try:
                return str(self._data.columns[section])
            except IndexError:
                return QVariant()
        
        if orientation == Qt.Orientation.Vertical:
            try:
                return str(self._data.index[section])
            except IndexError:
                return QVariant()
        
        return QVariant()
    
    def sort(self, column: int, order: Qt.SortOrder) -> None:
        """Sorts the dataframe based on the given column and the given order"""
        if self._data is None:
            return
        
        # Validate column index to prevent error on empty dataframe
        # Suppresses sorting errors for index -1 is out of bounds when 
        # creating a new project with 0x0 row/cols
        if column < 0 or column >= len(self._data.columns):
            return
        
        self.layoutAboutToBeChanged.emit()

        try:
            col_name = self._data.columns[column]
            ascending = (order == Qt.SortOrder.AscendingOrder)

            self.data_handler.sort_data(col_name, ascending)
            self._data = self.data_handler.df
            self._data_buffer.clear()
        except Exception as SortError:
            print(f"Error sorting data: {str(SortError)}")
            self.status_bar = StatusBar()
            self.status_bar.log(f"Error sorting data: {str(SortError)}")
        
        self.layoutChanged.emit()