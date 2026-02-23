# ui/plot_tab_ui.py

from PyQt6.QtWidgets import (
    QSplitter, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QFontComboBox, QStackedWidget, QToolBox 
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QKeySequence
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt import NavigationToolbar2QT as NavigationToolbar
from core.resource_loader import get_resource_path
from ui.widgets import (
    DataPlotStudioButton
)
from ui.components.plot_settings_panel import PlotSettingsPanel
from ui.icons import IconBuilder, IconType

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEB_ENGINE_AVAILABLE = True
    print(WEB_ENGINE_AVAILABLE)
except:
    WEB_ENGINE_AVAILABLE = False
    print(f"{WEB_ENGINE_AVAILABLE} QtWebEngineWidgets not installed")
    from PyQt6.QtWidgets import QLabel as QWebEngineView

class PlotTabUI(QWidget):
    """"""
    def __init__(self) -> None:
        super().__init__()
    
    def init_ui(self, canvas: FigureCanvas, toolbar: NavigationToolbar) -> None:
        main_layout = QHBoxLayout(self)
        
        left_layout = QVBoxLayout()
        self.canvas = canvas
        self.toolbar = toolbar
        left_layout.addWidget(self.toolbar)
        self.plot_stack = QStackedWidget()
        self.plot_stack.addWidget(self.canvas)
        
        if WEB_ENGINE_AVAILABLE:
            self.web_view = QWebEngineView()
            self.web_view.setHtml("<html><body><h3 style='color:gray; font-family:sans-serif; text-align:center; margin-top:20%;'>Plotly Plot Area</h3></body></html>")
        else:
            self.web_view = QLabel("Interactive plotting requires 'PyQt6-WebEngine'.\nPlease install it: pip install PyQt6-WebEngine")
            self.web_view.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.web_view.setStyleSheet("QLabel { background-color: white; color: red; font-size: 14px; }")
        
        self.plot_stack.addWidget(self.web_view)
        
        left_layout.addWidget(self.plot_stack, 1)
        
        right_layout = QVBoxLayout()
        
        self.settings_panel = PlotSettingsPanel(parent=self)
        self.custom_tabs = self.settings_panel.custom_tabs
        
        for name, obj in vars(self.settings_panel).items():
            if isinstance(obj, (QWidget, QToolBox, QFontComboBox)) and not name.startswith("_"):
                setattr(self, name, obj)
            if name in ["las_latex"]:
                setattr(self, name, obj)
        
        right_layout.addWidget(self.settings_panel, 1)
        
        # Buttons at bottom
        button_layout = QHBoxLayout()
        
        self.plot_button = DataPlotStudioButton(
            "Generate Plot",
            parent=self,
            base_color_hex="#4CAF50",    
            hover_color_hex="#5cb85c",
            pressed_color_hex="#4a9c4d",
            text_color_hex="#FFFFFF",
            border_style="none",
            typewriter_effect=True
        )
        self.plot_button.setMinimumHeight(40)
        self.plot_button.setIcon(IconBuilder.build(IconType.GENERATE_PLOT))
        self.plot_button.setShortcut(QKeySequence("Ctrl+Return"))
        button_layout.addWidget(self.plot_button)

        self.save_plot_button = DataPlotStudioButton(
            "Save Plot",
            parent=self,
            base_color_hex="#ff9800",
            hover_color_hex="#ffb74d",
            pressed_color_hex="#f57c00",
            text_color_hex="#ffffff",
            border_style="none",
            typewriter_effect=True
        )
        self.save_plot_button.setMinimumHeight(40)
        self.save_plot_button.setIcon(IconBuilder.build(IconType.SAVE_PLOT))
        self.save_plot_button.setToolTip("Export the current plot to PNG, PDF or SVG")
        button_layout.addWidget(self.save_plot_button)
        
        self.clear_button = DataPlotStudioButton(
            "Clear",
            parent=self,
            base_color_hex="#ededed",    
            hover_color_hex="#f5f5f5",
            pressed_color_hex="#dcdcdc",
            text_color_hex="#000000",
            border_style="1px solid #c9c9c9",
            typewriter_effect=True
        )
        self.clear_button.setMinimumHeight(40)
        self.clear_button.setIcon(IconBuilder.build(IconType.CLEAR_PLOT))
        button_layout.addWidget(self.clear_button)
        
        self.editor_button = DataPlotStudioButton(
            "Open Python Editor",
            parent=self,
            base_color_hex="#2196F3",
            hover_color_hex="#42A5F5",
            pressed_color_hex="#1e88e5",
            text_color_hex="#ffffff",
            border_style="none",
            typewriter_effect=True
        )
        self.editor_button.setMinimumHeight(40)
        self.editor_button.setIcon(IconBuilder.build(IconType.OPEN_PYTHON_EDITOR))
        self.editor_button.setToolTip("Open the code editor to view/write python code for the plot.")
        button_layout.addWidget(self.editor_button)
        
        right_layout.addLayout(button_layout)
        
        # Set layouts
        left_widget = QWidget()
        left_widget.setLayout(left_layout)
        right_widget = QWidget()
        right_widget.setLayout(right_layout)
        
        # Create splitter
        splitter: QSplitter = self._create_splitter(left_widget, right_widget)
        main_layout.addWidget(splitter)
        
        self.setLayout(main_layout)
    
    def _create_splitter(self, left, right) -> QSplitter:
        """Create a splitter for resizable panels"""
        from PyQt6.QtWidgets import QSplitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setSizes([700, 300])
        return splitter