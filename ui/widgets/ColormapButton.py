from PyQt6.QtCore import QSize, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QDialog, QPushButton


class ColormapButton(QPushButton):
    currentTextChanged = pyqtSignal(str)
    currentIndexChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.current_colormap = "viridis"
        self.setText("viridis")
        self.setIconSize(QSize(100, 20))

        self._base_border_color = QColor("#ccc")
        self._hover_border_color = QColor("#707070")
        self._focus_border_color = QColor("#0078d7")
        self._animated_color = self._base_border_color
        self._is_focussed = False

        self.animation = QPropertyAnimation(self, b"animated_border_color")
        self.animation.setDuration(150)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)

        self.clicked.connect(self._open_picker)
        self._update_display()
        self._update_stylesheet(self._base_border_color)
    
    @pyqtProperty(QColor)
    def animated_border_color(self) -> QColor:
        return self._animated_color

    @animated_border_color.setter
    def animated_border_color(self, color: QColor) -> None:
        self._animated_color = color
        self._update_stylesheet(color)

    def _update_stylesheet(self, color: QColor) -> None:
        self.setStyleSheet(f"""
            QPushButton {{
                text-align: left;
                padding: 5px;
                border: 1.5px solid {color.name()};
                border-radius: 4px;
                background-color: white;
            }}
            QPushButton:hover {{
                background-color: #f0f0f0;
            }}
        """)

    def _animate_to(self, color: QColor) -> None:
        self.animation.stop()
        self.animation.setEndValue(color)
        self.animation.start()

    def enterEvent(self, event) -> None:
        if self.isEnabled() and not self._is_focussed:
            self._animate_to(self._hover_border_color)
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        if not self._is_focussed:
            self._animate_to(self._base_border_color)
        super().leaveEvent(event)

    def _open_picker(self):
        from ui.dialogs import ColormapPickerDialog
        dialog = ColormapPickerDialog(self.current_colormap, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            new_colormap = dialog.get_selected_colormap()
            if new_colormap and new_colormap != self.current_colormap:
                self.setCurrentText(new_colormap)

    def setCurrentText(self, text):
        self.current_colormap = text
        self._update_display()
        self.currentTextChanged.emit(text)

    def currentText(self):
        return self.current_colormap

    def setCurrentIndex(self, index):
        pass

    def _update_display(self):
        from ui.dialogs import ColormapPickerDialog
        self.setText(f" {self.current_colormap}")
        dialog = ColormapPickerDialog(parent=None)
        icon = dialog._generate_icon(self.current_colormap)
        self.setIcon(icon)