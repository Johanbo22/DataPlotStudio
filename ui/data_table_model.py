import pandas as pd
import numpy as np
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant
from PyQt6.QtGui import QColor
from typing import Any

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
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> QVariant | int | float | bool | str | QColor:
        """Returns le data"""
        if not index.isValid() or self._data is None:
            return QVariant()
    
        row = index.row()
        column = index.column()

        try:
            if role == Qt.ItemDataRole.BackgroundRole:
                if row in self.highlighted_rows:
                    return QColor("#FFCCCC")
                
            value = self._data.iloc[row, column]
            if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
                if pd.isna(value):
                    return "" if role == Qt.ItemDataRole.EditRole else "NaN"
                
                if isinstance(value, np.integer):
                    return int(value)
                if isinstance(value, np.floating):
                    return float(value)
                if isinstance(value, np.bool):
                    return bool(value)
                
                return str(value)
            
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                if self._is_numeric[column]:
                    return QVariant(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
                return QVariant(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter)
        
        except Exception as DataModelError:
            print(f"Error in DataTableModel.data(): {str(DataModelError)} for row: {row}, column: {column}, role: {role}")
            return QVariant()

        return QVariant()
    
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