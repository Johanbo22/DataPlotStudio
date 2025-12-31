import matplotlib
import matplotlib.pyplot as plt
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon, QLinearGradient, QPainter, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QLineEdit, QListWidget, QListWidgetItem, QVBoxLayout


class ColormapPickerDialog(QDialog):

    def __init__(self, current_colormap=None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select colormap")
        self.setModal(True)
        self.resize(400, 500)
        self.selected_colormap = current_colormap

        layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to filter...")
        self.search_input.textChanged.connect(self._filter_items)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)

        self.list_widget = QListWidget()
        self.list_widget.setIconSize(QSize(100, 20))
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self._populate_colormaps()

        if current_colormap:
            items = self.list_widget.findItems(current_colormap, Qt.MatchFlag.MatchExactly)
            if items:
                self.list_widget.setCurrentItem(items[0])
                items[0].setSelected(True)

    def _populate_colormaps(self) -> None:
        try:
            maps = sorted([m for m in matplotlib.colormaps() if not m.endswith("_r")])
        except Exception:
            maps = ["viridis", "plasma", "inferno", "magma"]

        for name in maps:
            item = QListWidgetItem(name)
            icon = self._generate_icon(name)
            item.setIcon(icon)
            self.list_widget.addItem(item)

    def _generate_icon(self, colormap_name) -> QIcon:
        width = 100
        height = 20
        pixmap = QPixmap(width, height)
        pixmap.fill(Qt.GlobalColor.transparent)

        painter = QPainter(pixmap)

        try:
            try:
                colormap = matplotlib.colormaps[colormap_name]
            except Exception:
                colormap = plt.get_cmap(colormap_name)

            gradient = QLinearGradient(0, 0, width, 0)
            steps = 40
            for i in range(steps + 1):
                position = i / steps
                rgba = colormap(position)
                color = QColor.fromRgbF(rgba[0], rgba[1], rgba[2], 1.0)
                gradient.setColorAt(position, color)

            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRect(0, 0, width, height)

        except:
            painter.setBrush(QBrush(Qt.GlobalColor.gray))
            painter.drawRect(0, 0, width, height)
        finally:
            painter.end()
        return QIcon(pixmap)

    def _filter_items(self, text) -> None:
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def _on_item_double_clicked(self, item) -> None:
        self.selected_colormap = item.text()
        self.accept()

    def get_selected_colormap(self):
        selected_items = self.list_widget.selectedItems()
        if selected_items:
            return selected_items[0].text()
        return self.selected_colormap