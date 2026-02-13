import numpy as np
from PyQt6.QtWidgets import QGraphicsEffect
from PyQt6.QtGui import QImage, QPainter
from PyQt6.QtCore import Qt

class ColorBlindnessEffect(QGraphicsEffect):
    """
    Docstring for ColorBlindnessEffect
    """
    
    # Standard SVG color matricies for CBS
    MATRICES = {
        "Protanopia (No Red)": np.array([
            [0.567, 0.433, 0.000],
            [0.558, 0.442, 0.000],
            [0.000, 0.242, 0.758]
        ]),
        "Deuteranopia (No Green)": np.array([
            [0.625, 0.375, 0.000],
            [0.700, 0.300, 0.000],
            [0.000, 0.300, 0.700]
        ]),
        "Tritanopia (No Blue)": np.array([
            [0.950, 0.050, 0.000],
            [0.000, 0.433, 0.567],
            [0.000, 0.475, 0.525]
        ]),
        "Achromatopsia (Monochromacy)": np.array([
            [0.299, 0.587, 0.114],
            [0.299, 0.587, 0.114],
            [0.299, 0.587, 0.114]
        ])
    }
    
    def __init__(self, simulation_type: str = "Protanopia (No Red)", parent=None):
        super().__init__(parent)
        self.simulation_type = simulation_type
    
    def set_simulation_type(self, sim_type: str) -> None:
        """Update the simulaton type to trigger redrawEvent"""
        self.simulation_type = sim_type
        self.update()
    
    def draw(self, painter: QPainter) -> None:
        """Applies the color matrix to a pixmap"""
        pixmap, offset = self.sourcePixmap(Qt.CoordinateSystem.LogicalCoordinates)
        if pixmap.isNull():
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
        painter.drawImage(offset, new_image)