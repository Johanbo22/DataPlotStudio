import matplotlib
import matplotlib.pyplot as plt
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtGui import QBrush, QColor, QIcon, QLinearGradient, QPainter, QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QHBoxLayout, QLabel, QListWidgetItem, QVBoxLayout

from ui.widgets.AnimatedCheckBox import DataPlotStudioCheckBox
from ui.widgets.AnimatedLineEdit import DataPlotStudioLineEdit
from ui.widgets.AnimatedListWidget import DataPlotStudioListWidget


class ColormapPickerDialog(QDialog):

    COLORMAP_CATEGORIES = {
        "Perceptually Uniform": ["viridis", "plasma", "inferno", "magma", "cividis"],
        "Sequential": ["Greys", "Purples", "Blues", "Greens", "Oranges", "Reds","YlOrBr", "YlOrRd", "OrRd", "PuRd", "RdPu", "BuPu","GnBu", "PuBu", "YlGnBu", "PuBuGn", "BuGn", "YlGn"],
        "Diverging": ["PiYG", "PRGn", "BrBG", "PuOr", "RdGy", "RdBu","RdYlBu", "RdYlGn", "Spectral", "coolwarm", "bwr", "seismic"],
        "Qualitative": ["Pastel1", "Pastel2", "Paired", "Accent","Dark2", "Set1", "Set2", "Set3", "tab10", "tab20", "tab20b", "tab20c"],
        "Cyclic": ["twilight", "twilight_shifted", "hsv"],
        "Miscellaneous": ["flag", "prism", "ocean", "gist_earth", "terrain","gist_stern", "gnuplot", "gnuplot2", "CMRmap","cubehelix", "brg", "gist_rainbow", "rainbow", "jet", "nipy_spectral", "gist_ncar"]
    }

    def __init__(self, current_colormap=None, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Select colormap")
        self.setModal(True)
        self.resize(400, 600)

        is_reversed = False
        if current_colormap and current_colormap.endswith("_r"):
            self.selected_colormap = current_colormap[:-2]
            is_reversed = True
        
        self.selected_colormap = current_colormap

        layout = QVBoxLayout(self)

        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_input = DataPlotStudioLineEdit()
        self.search_input.setPlaceholderText("Type to filter...")
        self.search_input.textChanged.connect(self._filter_items)

        self.reverse_check = DataPlotStudioCheckBox("Reverse colormap")
        self.reverse_check.setChecked(is_reversed)

        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        layout.addWidget(self.reverse_check)

        self.list_widget = DataPlotStudioListWidget()
        self.list_widget.setIconSize(QSize(100, 20))
        self.list_widget.setUniformItemSizes(False)
        self.list_widget.setSpacing(0)
        self.list_widget.itemDoubleClicked.connect(self._on_item_double_clicked)
        layout.addWidget(self.list_widget)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

        self._populate_colormaps()

        if current_colormap:
            items = self.list_widget.findItems(current_colormap, Qt.MatchFlag.MatchExactly)
            valid_items = [i for i in items if i.data(Qt.ItemDataRole.UserRole) != "header"]
            if valid_items:
                self.list_widget.setCurrentItem(valid_items[0])
                valid_items[0].setSelected(True)
                self.list_widget.scrollToItem(valid_items[0])
        
        self._filter_items("")

    def _populate_colormaps(self) -> None:
        """Populates the list with colormaps"""
        try:
            all_maps = set([m for m in matplotlib.colormaps() if not m.endswith("_r")])
        except Exception:
            all_maps = {"viridis", "plasma", "inferno", "magma"}
        
        added_maps = set()

        def add_header(text: str):
            item = QListWidgetItem()
            item.setText(text)
            item.setData(Qt.ItemDataRole.UserRole, "header")
            item.setFlags(Qt.ItemFlag.NoItemFlags)

            font = item.font()
            font.setBold(True)
            font.setPointSize(10)
            item.setFont(font)

            item.setForeground(QBrush(QColor("black")))
            item.setBackground(QBrush(QColor("#FFFFFF")))
            item.setSizeHint(QSize(0, 25))
            self.list_widget.addItem(item)

        for category, maps_list in self.COLORMAP_CATEGORIES.items():
            available_in_cat = [m for m in maps_list if m in all_maps]
            if available_in_cat:
                add_header(category)
                for name in available_in_cat:
                    self._add_colormap_item(name)
                    added_maps.add(name)
        
        remaining = sorted(list(all_maps - added_maps))
        if remaining:
            add_header("Other")
            for name in remaining:
                self._add_colormap_item(name)
    
    def _add_colormap_item(self, name: str) -> None:
        """Creates and adds the colormap to the list"""
        item = QListWidgetItem(name)
        item.setData(Qt.ItemDataRole.UserRole, "colormap")

        item.setSizeHint(QSize(0, 24))
        icon = self._generate_icon(name)
        item.setIcon(icon)
        self.list_widget.addItem(item)

    def _generate_icon(self, colormap_name) -> QIcon:
        """Method to generate an icon that matches the color gradient of the matplotlib colormaps"""
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

    def _filter_items(self, text: str) -> None:
        """Filters the items list. Show header with one or more childs"""
        search_text = text.lower()
        current_header = None
        header_has_visible_child = False

        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            role = item.data(Qt.ItemDataRole.UserRole)

            if role == "header":
                if current_header:
                    current_header.setHidden(not header_has_visible_child)
                
                current_header = item
                header_has_visible_child = False
                item.setHidden(False)
            else:
                is_match = search_text in item.text().lower()
                item.setHidden(not is_match)

                if is_match:
                    header_has_visible_child = True
        
        if current_header:
            current_header.setHidden(not header_has_visible_child)

    def _on_item_double_clicked(self, item: QListWidgetItem) -> None:
        """Handles double click"""
        if item.data(Qt.ItemDataRole.UserRole) == "header":
            return
        
        self.selected_colormap = item.text()
        self.accept()

    def get_selected_colormap(self) -> str:
        """Returns the selected colormap name with an appending _r if the reverse checkbox is checked"""
        selected_items = self.list_widget.selectedItems()
        base_name = self.selected_colormap

        if selected_items:
            if selected_items[0].data(Qt.ItemDataRole.UserRole) != "header":
                base_name = selected_items[0].text()
        
        if base_name and self.reverse_check.isChecked():
            return f"{base_name}_r"
        
        return base_name