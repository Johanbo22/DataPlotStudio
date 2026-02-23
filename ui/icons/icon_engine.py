import abc
from PyQt6.QtGui import QIcon, QPainter, QPixmap
from PyQt6.QtCore import QRect, Qt, QSize

class BaseIconEngine(abc.ABC):
    """
    Abstract base class for rendering vector icons.
    """
    
    @abc.abstractmethod
    def draw_icon(self, painter: QPainter, rect: QRect, mode: QIcon.Mode) -> None:
        """
        Main drawing routine.
        painter = The target paint device
        rect = bounding box for icon
        mode = QIcon.Modes, normal, disabled, active
        """
        # Gets draw by icon subclass
        pass
    
    def build(self, resolution: int = 128) -> QIcon:
        icon = QIcon()
        rect = QRect(0, 0, resolution, resolution)
        
        for mode in [QIcon.Mode.Normal, QIcon.Mode.Disabled]:
            pixmap = QPixmap(QSize(resolution, resolution))
            pixmap.fill(Qt.GlobalColor.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            
            self.draw_icon(painter, rect, mode)
            
            painter.end()
            icon.addPixmap(pixmap, mode, QIcon.State.Off)
        return icon