import pandas as pd
import numpy as np
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt6.QtGui import QColor
from typing import Any
from ui.status_bar import StatusBar

class DataTableModel(QAbstractTableModel):
    """ table for the data Table"""

    def __init__(self, data_handler, editable=False, parent=None, highlighted_rows=None):
        super().__init__(parent)
        self.data_handler = data_handler
        self._data = self.data_handler.df
        self.editable = editable
        self.highlighted_rows = set(highlighted_rows) if highlighted_rows else set()

        if self._data is not None:
            self._is_numeric = [
                pd.api.types.is_numeric_dtype(dtype) for dtype in self._data.dtypes
            ]
        else:
            self._is_numeric = []

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

        if role == Qt.ItemDataRole.DisplayRole:
            try:
                row = index.row()
                col = index.column()
                val = self._data.iat[row, col]

                if pd.isna(val):
                    return "NaN"

                if isinstance(val, (bool, np.bool_)):
                    return str(val)

                if isinstance(val, (int, np.integer)):
                    return int(val)

                if isinstance(val, (float, np.floating)):
                    return f"{val:.6g}"

                s_val = str(val)
                if len(s_val) > 64:
                    return s_val[:64] + "..."
                return s_val

            except Exception:
                return None

        elif role == Qt.ItemDataRole.EditRole:
            try:
                val = self._data.iat[index.row(), index.column()]
                if pd.isna(val):
                    return ""
                return str(val)
            except Exception:
                return ""

        elif role == Qt.ItemDataRole.BackgroundRole:
            if index.row() in self.highlighted_rows:
                return QColor("#FFCCCC")
            
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
        
        self.layoutAboutToBeChanged.emit()

        try:
            col_name = self._data.columns[column]
            ascending = (order == Qt.SortOrder.AscendingOrder)

            self.data_handler.sort_data(col_name, ascending)
            self._data = self.data_handler.df
        except Exception as SortError:
            print(f"Error sorting data: {str(SortError)}")
            self.status_bar = StatusBar()
            self.status_bar.log(f"Error sorting data: {str(SortError)}")
        
        self.layoutChanged.emit()