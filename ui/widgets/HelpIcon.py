from PyQt6.QtCore import QSize, Qt, pyqtSignal
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import QApplication, QLabel, QStyle


class HelpIcon(QLabel):
    """Creates a clickable '?' that emits a signal to an id in the tutorial.db database"""

    clicked = pyqtSignal(str)

    def __init__(self, topic_id: str, parent=None, size=18):
        """
        Args:
            topic_id (str): The ID to fetch from the tutorial database.
            parent: The parent widget
            size (int): The width and height of the icon
        """

        super().__init__(parent)
        self.topic_id = topic_id

        try:
            style = QApplication.style()
            icon = style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxQuestion)
            pixmap = icon.pixmap(QSize(size, size))
            self.setPixmap(pixmap)
        except Exception:
            #fallback
            self.setText("?")
            self.setObjectName("HelpIconFallBack")
            self.setStyleSheet("border: 1px solid grey; border-radius: 9px; font-weight: bold; qproperty-alignment: 'AlignCenter';")
        self.setFixedSize(size, size)
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.setToolTip("Click for help")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.topic_id)
        super().mousePressEvent(event)