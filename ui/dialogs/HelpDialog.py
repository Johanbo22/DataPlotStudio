from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFrame, QLabel, 
    QScrollArea, QVBoxLayout, QWidget, QPushButton
)
from pathlib import Path
import sys
import importlib.util
from core.resource_loader import get_resource_path

class HelpDialog(QDialog):
    """Dialog window do display help content"""

    def __init__(self, parent, topic_id: str, title: str, description: str, link=None):
        super().__init__(parent)

        self.topic_id = topic_id

        self.valid_link = None
        if link and isinstance(link, str) and link.strip().startswith("http"):
            self.valid_link = link.strip()
        
        # Window
        self.setWindowTitle(f"Help: {title}")
        self.resize(600, 700)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlag(Qt.WindowType.Tool, True)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("HelpDialogTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        #Animation area
        current_dir = Path(__file__).resolve().parent
        ui_dir = current_dir.parent
        project_root = ui_dir.parent

        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        clean_filename = f"{str(topic_id).lower()}.py"
        anim_path_obj = project_root / "resources" / "help_animations" / clean_filename
        anim_path = get_resource_path(str(anim_path_obj))

        animation_widget = self._load_animation(topic_id, anim_path)
        layout.addWidget(animation_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Description area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        scroll_area.setMaximumHeight(180)

        scroll_content = QWidget()
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(0, 15, 0, 0)
        scroll_content.setLayout(scroll_layout)

        display_desc = description if description else "No description available."
        self.description_label = QLabel(display_desc)
        self.description_label.setWordWrap(True)
        self.description_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.description_label.setProperty("styleClass", "help_description")
        
        scroll_layout.addWidget(self.description_label)
        scroll_area.setWidget(scroll_content)
        layout.addWidget(scroll_area)

        #Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)

        if self.valid_link:
            self.help_btn = QPushButton("More Information")
            self.help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.help_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation))
            self.help_btn.clicked.connect(self._open_link)
            button_box.addButton(self.help_btn, QDialogButtonBox.ButtonRole.HelpRole)

        layout.addWidget(button_box)
    
    def _load_animation(self, topic_id, path):
        if not Path(path).exists():
            print(f"HelpDialog: Animation file missing at {path}")
            return self._create_placeholder(f"No animation found for '{topic_id}'")

        try:
            spec = importlib.util.spec_from_file_location(f"anim_{topic_id}", path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[f"anim_{topic_id}"] = module
                spec.loader.exec_module(module)

                if hasattr(module, 'Animation'):
                    return module.Animation()
        except Exception as AnimationLoadingError:
            print(f"HelpDialog: Error loading {path}: {AnimationLoadingError}")
        
        return self._create_placeholder("Preview unavailable")

    def _create_placeholder(self, text) -> QLabel:
        lbl = QLabel(text)
        lbl.setFixedSize(450, 300)
        lbl.setObjectName("help_animation_placeholder")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return lbl

    def _open_link(self):
        if self.valid_link:
            QDesktopServices.openUrl(QUrl(self.valid_link))