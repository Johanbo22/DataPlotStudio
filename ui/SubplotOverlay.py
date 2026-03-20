from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt, pyqtProperty, QSequentialAnimationGroup, QPauseAnimation, QRectF
from PyQt6.QtGui import QColor, QPainter, QPen, QPaintEvent
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget


class SubplotOverlay(QWidget):

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._border_color: QColor = QColor("#2196F3")
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.hide()

        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.update_notice_label = QLabel("Data has changed. Click 'Generate Plot' to update")
        self.update_notice_label.setObjectName("update_notice_label")
        self.update_notice_label.hide()
        self.v_layout.addWidget(self.update_notice_label)
        
        self.label_widget = QLabel()
        self.label_widget.setObjectName("subplot_overlay_label")
        self.v_layout.addWidget(self.label_widget)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(1000)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.1)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        
        self.animation_sequence = QSequentialAnimationGroup(self)
        
        self.pause_animation = QPauseAnimation(1000, self)
        self.animation_sequence.addAnimation(self.pause_animation)
        self.animation_sequence.addAnimation(self.fade_animation)
        
        self.fade_animation.finished.connect(self._on_animation_finished)
        
    @pyqtProperty(QColor)
    def border_color(self) -> QColor:
        return self._border_color
    
    @border_color.setter
    def border_color(self, color: QColor) -> None:
        self._border_color = color
        self.update()
    
    def show_update_required(self, visible: bool = True) -> None:
        self.update_notice_label.setVisible(visible)
        if visible:
            self.animation_sequence.stop()
            self.opacity_effect.setOpacity(1.0)
            self.show()
        elif not self.label_widget.text() and self.opacity_effect.opacity() == 1.0:
            self.hide()

    def _on_animation_finished(self):
        """CAlled when the animation is finished to remove text but retain border values"""
        self.label_widget.hide()

    def update_info(self, text: str, geometry: tuple[int, int, int, int], is_resize: bool = False):
        """
        Updater for text and geometry when information is changed
        Args:
            text (str): The text to display in the overlay
            geometry (tuple[int, int, int, int]): The geometry (x, y, w, h) for the overlay
            is_resize (bool): Flag indicating if the update is triggered by a resize event
        """
        self.setGeometry(*geometry)
        if not is_resize:
            self.label_widget.setText(text)
            self.label_widget.show()
            self.show()

            self.opacity_effect.setOpacity(1.0)
            self.animation_sequence.stop()
            self.animation_sequence.start()

    def paintEvent(self, event: QPaintEvent):
        """Draw a blue border around the subplot for the user to see"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        #the draw duude
        pen = QPen(self._border_color)
        pen.setWidth(4)
        
        pen.setCapStyle(Qt.PenCapStyle.SquareCap)
        pen.setJoinStyle(Qt.PenJoinStyle.MiterJoin)
        painter.setPen(pen)

        rect = QRectF(self.rect()).adjusted(2.0, 2.0, -2.0, -2.0)
        painter.drawRect(rect)