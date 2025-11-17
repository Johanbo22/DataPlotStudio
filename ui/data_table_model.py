import pandas as pd
import numpy as np
from PyQt6.QtCore import QAbstractTableModel, QModelIndex, Qt, QVariant

class DataTableModel(QAbstractTableModel):
    """New performance table for the data Table"""

    def __init__(self, data: pd.DataFrame, parent=None):
        super().__init__(parent)
        self._data = data

        self._is_numeric = [
            pd.api.types.is_numeric_dtype(dtype) for dtype in self._data.dtypes
        ]

    def rowCount(self, parent=QModelIndex()) -> int:
        """Returns the number of rows in a dataframe"""
        if parent.isValid():
            return 0
        return self._data.shape[0]
    
    def columnCount(self, parent=QModelIndex()) -> int:
        """Returns the number of columns in the dataframe"""
        if parent.isValid():
            return 0
        return self._data.shape[1]
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        """Returns thedata"""
        if not index.isValid():
            return QVariant()
        
        row = index.row()
        col = index.column()

        try:
            value = self._data.iloc[row, col]
            
            if pd.isna(value):
                if role == Qt.ItemDataRole.DisplayRole:
                    return "NaN"
                return QVariant()

            if role == Qt.ItemDataRole.DisplayRole:
                if isinstance(value, np.integer):
                    return int(value)
                if isinstance(value, np.floating):
                    return float(value)
                if isinstance(value, np.bool_):
                    return bool(value)
                
                if isinstance(value, (int, float, str, bool)):
                    return value
            
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                if self._is_numeric[col]:
                    return QVariant(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignCenter)
                return QVariant(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignCenter)
        
        except Exception as error:
            print(f"Error in DataTableModel.data(): {str(error)} for row: {row}, col: {col}, role: {role}")
            return QVariant()
        
        return QVariant()

    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole):
        """Returns the header of the data"""
        if role != Qt.ItemDataRole.DisplayRole:
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
    
    def sort(self, column: int, order: Qt.SortOrder):
        """Sort the model by a col"""
        if self._data.empty:
            return
        
        try:
            col_name = self._data.columns[column]
            self.layoutAboutToBeChanged.emit()

            ascending = order == Qt.SortOrder.AscendingOrder

            self._data = self._data.sort_values(by=col_name, ascending=ascending)
            self._data = self._data.reset_index(drop=True)

            self.layoutChanged.emit()
        
        except Exception as e:
            print(f"Error sorting {str(e)}")