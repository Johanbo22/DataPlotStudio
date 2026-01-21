from PyQt6.QtWidgets import QSizePolicy, QStackedWidget
from PyQt6.QtCore import QSize

class AutoResizingStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

    def sizeHint(self):
        current = self.currentWidget()
        if current:
            return self.currentWidget().sizeHint()
        return QSize(0, 0)
    
    def minimumSizeHint(self):
        current = self.currentWidget()
        if current:
            return current.minimumSizeHint()
        return QSize(0, 0)