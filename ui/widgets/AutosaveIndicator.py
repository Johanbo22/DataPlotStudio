from PyQt6.QtWidgets import QWidget, QLabel, QGraphicsOpacityEffect, QHBoxLayout
from PyQt6.QtCore import QTimer, Qt, QPropertyAnimation

from ui.icons import IconBuilder, IconType

class AutosaveIndicator(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setObjectName("AutosaveIndicatorWidget")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        self.icon_label = QLabel()
        self.icon_label.setObjectName("AutosaveIcon")
        pixmap = IconBuilder.build(IconType.AppIcon, resolution=24).pixmap(24, 24)
        self.icon_label.setPixmap(pixmap)
        
        self.text_label = QLabel("Saving...")
        self.text_label.setObjectName("AutosaveText")
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)
        
        self.hide()
        
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.animation.setDuration(300)
        
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)
    
    def show_indicator(self) -> None:
        """Defines the position and exposes the indicator"""
        parent_rect = self.parent().rect()
        self.adjustSize()
        self.move(parent_rect.width() - self.width() - 20, 20)
        self.raise_()
        self.show()
        
        self.animation.stop()
        self.animation.setStartValue(self.opacity_effect.opacity())
        self.animation.setEndValue(1.0)
        self.animation.start()
        
        self.hide_timer.start(1500)
    
    def fade_out(self) -> None:
        self.animation.stop()
        self.animation.setStartValue(self.opacity_effect.opacity())
        self.animation.setEndValue(0.0)
        
        try:
            self.animation.finished.disconnect(self._on_fade_finished)
        except TypeError:
            pass
        
        self.animation.finished.connect(self._on_fade_finished)
        self.animation.start()
    
    def _on_fade_finished(self) -> None:
        if self.opacity_effect.opacity() == 0:
            self.hide()