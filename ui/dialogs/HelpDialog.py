from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QDialog, QDialogButtonBox, QFrame, QLabel, QScrollArea, QVBoxLayout, QWidget


import os


class HelpDialog(QDialog):
    """
    Dialog window to display tutorial content
    """

    def __init__(self, title: str, description: str, full_image_path: str, link: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Help: {title}")
        self.resize(600, 600)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)

        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setWindowFlag(Qt.WindowType.WindowContextHelpButtonHint, False)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.title_label = QLabel(title)
        self.title_label.setObjectName("HelpDialogTitle")
        self.title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(self.title_label)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_content.setLayout(scroll_layout)

        display_description = description if description and description.strip() else "[No description available]"

        self.description_label = QLabel(display_description)
        self.description_label.setWordWrap(True)
        self.description_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        if display_description == "[No description available]":
            self.description_label.setStyleSheet("font-style: italic; color: grey;")

        scroll_layout.addWidget(self.description_label)
        scroll_layout.addStretch(1)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        if full_image_path and os.path.exists(full_image_path):
            try:
                pixmap = QPixmap(full_image_path)
                img_label = QLabel()
                img_label.setPixmap(pixmap.scaledToWidth(400, Qt.TransformationMode.SmoothTransformation))
                img_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                img_label.setStyleSheet("margin-top: 10px; margin-bottom: 5px;")
                layout.addWidget(img_label)
            except Exception as LoadHelpImageError:
                print(f"Error loadig help image: {full_image_path}: {str(LoadHelpImageError)}")
        elif full_image_path:
            # Path was given but not found
            print(f"HelpDialog: Image file not found at {full_image_path}")


        if link:
            self.link_label = QLabel(f'<a href="{link}">More Information</a>')
            self.link_label.setOpenExternalLinks(True)
            self.link_label.setStyleSheet("margin-top: 10px;")
            layout.addWidget(self.link_label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)