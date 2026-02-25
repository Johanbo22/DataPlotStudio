from PyQt6.QtCore import QEasingCurve, QPropertyAnimation, Qt
from PyQt6.QtGui import QColor, QPainter, QPen
from PyQt6.QtWidgets import QGraphicsOpacityEffect, QLabel, QVBoxLayout, QWidget


class SubplotOverlay(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        self.hide()

        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(0, 0, 0, 0)
        self.v_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.update_notice_label = QLabel("Data has changed. Click 'Generate Plot' to update")
        self.update_notice_label.setStyleSheet("""
            QLabel {
                background-color: rgba(231, 76, 60, 0.9);
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                border: 2px solid #c0392b;
                border-radius: 8px;
                font-size: 12pt;
            }
        """)
        self.update_notice_label.hide()
        self.v_layout.addWidget(self.update_notice_label)
        
        self.label_widget = QLabel()
        self.label_widget.setStyleSheet(
            """
            QLabel {
                background-color: rgba(33, 150, 243, 0.8);
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 4px;
            }
        """
        )
        self.v_layout.addWidget(self.label_widget)

        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        self.fade_animation = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.fade_animation.setDuration(1500)
        self.fade_animation.setStartValue(1.0)
        self.fade_animation.setEndValue(0.2)
        self.fade_animation.setEasingCurve(QEasingCurve.Type.InCubic)
        self.fade_animation.finished.connect(self._on_animation_finished)
    
    def show_update_required(self, visible: bool = True) -> None:
        self.update_notice_label.setVisible(visible)
        if visible:
            self.show()
        elif not self.label_widget.text():
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
            self.fade_animation.stop()
            self.fade_animation.start()

    def paintEvent(self, event):
        """Draw a blue border around the subplot for the user to see"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        #the draw duude
        pen = QPen(QColor("#2196F3"))
        pen.setWidth(4)
        painter.setPen(pen)

        rect = self.rect().adjusted(2, 2, -2, -2)
        painter.drawRect(rect)