from PyQt6.QtWidgets import QStyledItemDelegate, QStyleOptionViewItem
from PyQt6.QtCore import Qt, QModelIndex
from PyQt6.QtGui import QPainter

class DataTableDelegate(QStyledItemDelegate):
    def __init__(self, parent=None, horizontal_padding: int = 8):
        super().__init__(parent)
        self.horizontal_padding = horizontal_padding
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex) -> None:
        opt = QStyleOptionViewItem(option)
        opt.rect = opt.rect.adjusted(self.horizontal_padding, 0, -self.horizontal_padding, 0)
        
        opt.displayAlignment = Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
        
        super().paint(painter, opt, index)