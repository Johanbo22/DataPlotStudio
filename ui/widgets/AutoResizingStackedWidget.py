from PyQt6.QtWidgets import QSizePolicy, QStackedWidget, QLabel, QGraphicsOpacityEffect, QWidget
from PyQt6.QtCore import QSize, Qt, QParallelAnimationGroup, QPropertyAnimation,QVariantAnimation, QEasingCurve, pyqtSlot

class AutoResizingStackedWidget(QStackedWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        
        # Animation settings
        self._transition_duration: int = 300
        self._easing_curve = QEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation_group: QParallelAnimationGroup | None = None
        self._ghost_label: QLabel | None = None

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
    
    def setCurrentIndex(self, index: int) -> None:
        if self.currentIndex() == index:
            return
        
        current_widget = self.currentWidget()
        next_widget = self.widget(index)
        
        # If transition is not possible
        # Just make the switch to that widget
        if not current_widget or not next_widget or not self.isVisible():
            super().setCurrentIndex(index)
            return
        
        current_pixmap = current_widget.grab()
        
        if self._ghost_label:
            self._ghost_label.deleteLater()
        
        self._ghost_label = QLabel(self)
        self._ghost_label.setPixmap(current_pixmap)
        self._ghost_label.setGeometry(self.rect())
        self._ghost_label.show()
        
        start_height = self.height()
        
        # Swtich to the new widget
        # to measure it
        super().setCurrentIndex(index)
        
        # Force new widget to
        # update geometry to sizeHint
        next_widget.updateGeometry()
        end_height = next_widget.sizeHint().height()
        
        self._animation_group = QParallelAnimationGroup(self)
        
        # First the resizing of container height animation
        # then fade out the ghost label 
        height_animation = QVariantAnimation(self)
        height_animation.setDuration(self._transition_duration)
        height_animation.setEasingCurve(self._easing_curve)
        height_animation.setStartValue(start_height)
        height_animation.setEndValue(end_height)
        height_animation.valueChanged.connect(self.setFixedHeight)
        self._animation_group.addAnimation(height_animation)
        
        opacity_effect = QGraphicsOpacityEffect(self._ghost_label)
        self._ghost_label.setGraphicsEffect(opacity_effect)
        
        fade_animation = QPropertyAnimation(opacity_effect, b"opacity", self)
        fade_animation.setDuration(self._transition_duration)
        fade_animation.setEasingCurve(self._easing_curve)
        fade_animation.setStartValue(1.0)
        fade_animation.setEndValue(0.0)
        self._animation_group.addAnimation(fade_animation)
        
        self._animation_group.finished.connect(self._on_transition_finished)
        self._animation_group.start()
    
    @pyqtSlot()
    def _on_transition_finished(self) -> None:
        """
        Method to clean up the mess
        """
        self.setMinimumHeight(0)
        self.setMaximumHeight(16777215)
        self.updateGeometry()
        
        if self._ghost_label:
            self._ghost_label.hide()
            self._ghost_label.deleteLater()
            self._ghost_label = None