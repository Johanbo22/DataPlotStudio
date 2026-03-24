from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QDialog, QDialogButtonBox, QFrame, QLabel, 
    QScrollArea, QVBoxLayout, QWidget, QPushButton
)
from pathlib import Path
import sys
import importlib.util
from typing import Optional
from core.resource_loader import get_resource_path
from ui.widgets import DataPlotStudioButton

class HelpDialog(QDialog):
    """Dialog window do display help content"""

    def __init__(self, parent: Optional[QWidget], topic_id: str, title: str, description: str, link: Optional[str] = None) -> None:
        super().__init__(parent)

        self.topic_id = topic_id

        self.valid_link: Optional[str] = None
        if link and isinstance(link, str) and link.strip().startswith("http"):
            self.valid_link = link.strip()
        
        # Window
        self.setWindowTitle(f"Help: {title}")
        self.resize(600, 700)
        self.setWindowModality(Qt.WindowModality.ApplicationModal)
        self.setWindowFlag(Qt.WindowType.Tool, True)
        self.setObjectName("HelpDialogMain")

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        header_frame = QFrame()
        header_frame.setObjectName("HelpDialogHeader")
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)

        # Title
        self.title_label = QLabel(title)
        self.title_label.setObjectName("HelpDialogTitle")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(self.title_label)
        layout.addWidget(header_frame)

        #Animation area
        
        content_frame = QFrame()
        content_frame.setObjectName("HelpDialogContent")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        current_dir = Path(__file__).resolve().parent
        ui_dir = current_dir.parent
        project_root = ui_dir.parent

        if project_root not in sys.path:
            sys.path.insert(0, str(project_root))
        
        clean_filename = f"{str(topic_id).lower()}.py"
        anim_path_obj = project_root / "resources" / "help_animations" / clean_filename
        anim_path = get_resource_path(str(anim_path_obj))

        animation_widget = self._load_animation(topic_id, anim_path)
        content_layout.addWidget(animation_widget, alignment=Qt.AlignmentFlag.AlignCenter)

        # Description area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.StyledPanel)
        scroll_area.setMaximumHeight(150)

        scroll_content = QWidget()
        scroll_content.setObjectName("HelpDialogScrollContent")
        scroll_layout = QVBoxLayout()
        scroll_layout.setContentsMargins(10, 10, 10, 10)
        scroll_content.setLayout(scroll_layout)

        display_desc = description if description else "No description available."
        self.description_label = QLabel(display_desc)
        self.description_label.setWordWrap(True)
        
        self.description_label.setTextFormat(Qt.TextFormat.MarkdownText)
        self.description_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.description_label.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.description_label.setProperty("styleClass", "help_description")
        
        scroll_layout.addWidget(self.description_label)
        scroll_area.setWidget(scroll_content)
        content_layout.addWidget(scroll_area)
        
        layout.addWidget(content_frame)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setObjectName("HelpDialogSeparator")
        layout.addWidget(separator)

        #Buttons
        button_container = QWidget()
        button_layout = QVBoxLayout(button_container)
        button_layout.setContentsMargins(20, 10, 20, 20)
        
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.reject)
        
        if self.valid_link:
            self.help_btn = QPushButton("More information")
            self.help_btn.setObjectName("HelpDialogInfoBtn")
            self.help_btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.help_btn.setIcon(self.style().standardIcon(self.style().StandardPixmap.SP_MessageBoxInformation))
            self.help_btn.clicked.connect(self._open_link)
            button_box.addButton(self.help_btn, QDialogButtonBox.ButtonRole.HelpRole)
        
        button_layout.addWidget(button_box)
        layout.addWidget(button_container)
    
    def _load_animation(self, topic_id, path):
        if not Path(path).exists():
            print(f"HelpDialog: Animation file missing at {path}")
            return self._create_placeholder(f"No animation found for '{topic_id}'")

        module_name = f"anim_{topic_id}"
        try:
            spec = importlib.util.spec_from_file_location(module_name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                if hasattr(module, 'Animation'):
                    animation_instance = module.Animation()
                    if isinstance(animation_instance, QWidget):
                        return animation_instance
                    
        except Exception as AnimationLoadingError:
            print(f"HelpDialog: Error loading {path}: {AnimationLoadingError}")
            sys.modules.pop(module_name, None)
        
        return self._create_placeholder("Preview unavailable")

    def _create_placeholder(self, text) -> QLabel:
        lbl = QLabel(text)
        lbl.setFixedSize(450, 300)
        lbl.setObjectName("help_animation_placeholder")
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setWordWrap(True)
        return lbl

    def _open_link(self):
        if self.valid_link:
            QDesktopServices.openUrl(QUrl(self.valid_link))