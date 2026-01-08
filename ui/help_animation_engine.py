from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QTimer, QRectF, Qt, QSize
from PyQt6.QtGui import QPainter, QColor, QFont

class HelpAnimationEngine(QWidget):
    """
    Class for Help dialog animations
    This is the engine that handles the animation loop, framerate and sizing
    """

    def __init__(self, parent=None, fps=60, duration_ms=4000):
        super().__init__(parent)
        self.setFixedSize(450, 300)

        self.fps = fps
        self.duration_ms = duration_ms
        self.current_time_ms = 0

        # Timer Setyp
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._update_loop)
        self.timer.start(1000 // self.fps)

        # Styling constants for animations
        self.bg_color = QColor("#2B2B2B")
        self.text_color = QColor("#ffffff")
        self.accent_color = QColor("#4a90e2")
        self.highlight_color = QColor("#e74c3c")
        self.success_color = QColor("#2ecc71")

        # Font Setup
        self.font_main = QFont("Segoe UI", 10)
        self.font_bold = QFont("Segoe UI", 10, QFont.Weight.Bold)
    
    def _update_loop(self):
        """Function that handles internal loop of animation"""
        self.current_time_ms += (1000 // self.fps)
        if self.current_time_ms > self.duration_ms:
            self.current_time_ms = 0
        
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw the background first
        painter.fillRect(self.rect(), self.bg_color)

        # Calculate the progress from 0.0 to 1.0
        progress = self.current_time_ms / self.duration_ms

        self.draw_animation(painter, progress)

    def draw_animation(self, painter: QPainter, progress: float):
        """
        This method is overriden by the animation it self
        """
        pass

    def get_eased_progerss(self, progress, start, end):
        """Help to map the global progress to a subinterval"""
        if progress < start: return 0.0
        if progress > end: return 1.0
        return (progress - start) / (end - start)