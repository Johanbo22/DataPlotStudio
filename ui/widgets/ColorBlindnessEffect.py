import numpy as np
from enum import Enum
from PyQt6.QtWidgets import QGraphicsEffect
from PyQt6.QtGui import QImage, QPainter, QPixmap
from PyQt6.QtCore import Qt

class ColorBlindnessType(str, Enum):
    Protanopia = "Protanopia (No Red)"
    Deuteranopia = "Deuteranopia (No Green)"
    Tritanopia = "Tritanopia (No Blue)"
    Achromatopsia = "Achromatopsia (Monochromacy)"

class ColorBlindnessEffect(QGraphicsEffect):
    """
    Docstring for ColorBlindnessEffect
    """
    
    # Standard SVG color matricies for CBS
    MATRICES = {
        ColorBlindnessType.Protanopia: np.array([
            [0.567, 0.433, 0.000],
            [0.558, 0.442, 0.000],
            [0.000, 0.242, 0.758]
        ]),
        ColorBlindnessType.Deuteranopia: np.array([
            [0.625, 0.375, 0.000],
            [0.700, 0.300, 0.000],
            [0.000, 0.300, 0.700]
        ]),
        ColorBlindnessType.Tritanopia: np.array([
            [0.950, 0.050, 0.000],
            [0.000, 0.433, 0.567],
            [0.000, 0.475, 0.525]
        ]),
        ColorBlindnessType.Achromatopsia: np.array([
            [0.299, 0.587, 0.114],
            [0.299, 0.587, 0.114],
            [0.299, 0.587, 0.114]
        ])
    }
    
    def __init__(self, simulation_type: ColorBlindnessType | str = ColorBlindnessType.Protanopia, parent=None):
        super().__init__(parent)
        self.simulation_type = ColorBlindnessType(simulation_type) if isinstance(simulation_type, str) else simulation_type
        
        # Caching to avoid CPU overusage
        self._cached_pixmap: QPixmap | None = None
        self._last_source_cache_key: int | None = None
        self._last_sim_type: ColorBlindnessType | None = None
    
    def set_simulation_type(self, sim_type: ColorBlindnessType | str) -> None:
        """Update the simulaton type to trigger redrawEvent"""
        new_type = ColorBlindnessType(sim_type) if isinstance(sim_type, str) else sim_type
        if self.simulation_type != new_type:
            self.simulation_type = new_type
            self.update()
    
    def draw(self, painter: QPainter) -> None:
        """Applies the color matrix to a pixmap"""
        pixmap, offset = self.sourcePixmap(Qt.CoordinateSystem.LogicalCoordinates)
        if pixmap.isNull():
            return
        
        current_cache_key = pixmap.cacheKey()
        
        if (self._cached_pixmap is not None and self._last_source_cache_key == current_cache_key and self._last_sim_type == self.simulation_type):
            painter.drawPixmap(offset, self._cached_pixmap)
            return
        
        image = pixmap.toImage()
        image.convertTo(QImage.Format.Format_RGB32)
        
        device_pixel_ratio = image.devicePixelRatio()
        
        ptr = image.bits()
        ptr.setsize(image.sizeInBytes())
        arr = np.array(ptr).reshape((image.height(), image.width(), 4))
        
        matrix = self.MATRICES.get(self.simulation_type, np.eye(3))
        
        # pyqt6 format_rbg32 is little endian order for
        # memory in RGBA
        rgb = arr[:, :, :3]
        r = rgb[:, :, 2]
        g = rgb[:, :, 1]
        b = rgb[:, :, 0]
        
        shape = r.shape
        pixels = np.vstack([r.ravel(), g.ravel(), b.ravel()])
        
        transformed = matrix @ pixels
        transformed = np.clip(transformed, 0, 255).astype(np.uint8)
        
        arr[:, :, 2] = transformed[0].reshape(shape)
        arr[:, :, 1] = transformed[1].reshape(shape)
        arr[:, :, 0] = transformed[2].reshape(shape)
        
        new_image = QImage(arr.data, image.width(), image.height(), image.bytesPerLine(), QImage.Format.Format_RGB32)
        new_image.setDevicePixelRatio(device_pixel_ratio)
        
        self._cached_pixmap = QPixmap.fromImage(new_image)
        self._last_source_cache_key = current_cache_key
        self._last_sim_type = self.simulation_type
        
        painter.drawPixmap(offset, self._cached_pixmap)