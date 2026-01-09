# ui/status_bar.py
from PyQt6.QtWidgets import QStatusBar, QLabel, QLineEdit, QProgressBar, QPushButton, QDialog, QTextEdit, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QPoint
from datetime import datetime
from core.logger import Logger
from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.dialogs import LogHistoryPopup



class StatusBar(QStatusBar):
    """Custom status bar with terminal output
       Added history viewer
    """
    
    def __init__(self) -> None:
        super().__init__()
        
        #logger will be set by main app
        self.logger = Logger()

        #track changes
        self.recent_actions = []
        self.log_history: list[str] = []
        self.action_timeout = 2 
        self.last_action_time = None

        self.setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                color: #ffffff;
                border-top: 1px solid #555;
            }
            QStatusBar::item {
                border: none;
            }
        """)

        # Adding a label of data stat
        self.stats_label = QLabel("No Data")
        self.stats_label.setStyleSheet("color: #aaaaaa; padding: 0 10px; font-family: Consolas, monospace;")

        # Adding some progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #444;
                border-radius: 2px;
                background-color: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #007acc;
            }
        """)
        self.progress_bar.hide()
        
        # Terminal-like output area
        self.terminal = QLineEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: Consolas, monospace;
                font-size: 10px;
                border: 1px solid #444;
                padding: 4px;
            }
        """)

        # Open history button
        self.history_button = DataPlotStudioButton("≡", base_color_hex="#333", hover_color_hex="#444", text_color_hex="#ddd")
        self.history_button.setToolTip("View Log History")
        self.history_button.setFixedWidth(24)
        self.history_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.history_button.setStyleSheet("""
            DataPlotStudioButton {
                background-color: #333; 
                color: #ddd; 
                border: 1px solid #444; 
                font-weight: bold;
            }
            DataPlotStudioButton:hover { background-color: #444; color: #fff; }
        """)
        self.history_button.clicked.connect(self.show_log_history)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #00ff00;")
        
        # Add widgets to status bar
        self.addWidget(self.status_label, 1)
        self.addWidget(self.terminal, 4)
        self.addWidget(self.history_button)
        self.addPermanentWidget(self.progress_bar)
        self.addPermanentWidget(self.stats_label)

    def set_logger(self, logger) -> None:
        """Set the logger instance"""
        self.logger = logger
    
    def log(self, message: str, level: str = "INFO", action_type: str = None) -> None:
        """Log a message to the terminal"""
        timestamp: str = datetime.now().strftime("%H:%M:%S")
        
        # set col based on actionlevel
        if level == "SUCCESS":
            color = "#00ff00"
            icon = "✓"
        elif level == "WARNING":
            color = "#ffaa00"
            icon = "⚠"
        elif level == "ERROR":
            color = "#ff0000"
            icon = "✗"
        else:
            color = "#00ff00"
            icon = "•"
        
        display_message = f"{icon} {message}"
        log_message: str = f"[{timestamp}] {display_message}"

        # Store the log in the history
        self.log_history.append(f'<span style="color:{color}">{log_message}</span>')

        self.terminal.setText(log_message)
        self.terminal.setStyleSheet(f"QLineEdit {{background-color: #1e1e1e; color: {color}; font-family: Consolas, 'Courier New', monospace; font-size: 11px; border: 1px solid #444; padding: 4px;}}") 
        self.status_label.setText("Updated")
        self.status_label.setStyleSheet(f"color: {color}; font-size: 11px;")

        #log to file logger if available
        if self.logger:
            if level == "INFO":
                self.logger.info(message)
            elif level == "SUCCESS":
                self.logger.success(message)
            elif level == "WARNING":
                self.logger.warning(message)
            elif level == "ERROR":
                self.logger.error(message)
        else:
            print(f"Warning: logger not present. Message not logged: {message}")
    
    def log_action(self, action: str, details: dict = None, level:str = "SUCCESS") -> None:
        """log actions"""

        # message for statusbar
        status_message = action

        #detail message for log file
        detailed_message = action
        if details:
            detail_parts = []
            for key, value in details.items():
                detail_parts.append(f"{key}={value}")
            detailed_message += f" | {', '.join(detail_parts)}"
        
        #show statusbarmsg 
        self.log(status_message, level)

        # log detailed
        if self.logger and details:
            if level == "SUCCESS":
                self.logger.success(detailed_message)
            elif level == "INFO":
                self.logger.info(detailed_message)
            elif level == "WARNING":
                self.logger.warning(detailed_message)
            elif level == "ERROR":
                self.logger.error(detailed_message)

    def update_data_stats(self, df) -> None:
        """Update the status bar widget to show dataframe dimensions"""
        if df is not None:
            rows, cols = df.shape
            self.stats_label.setText(f"Rows: {rows:,} | Columns: {cols}")
        else:
            self.stats_label.setText("No data")
    
    def show_progress(self, show: bool = True) -> None:
        """toggles the progress bar visibility"""
        if not show:
            self.progress_bar.hide()
        
        self.progress_bar.show()
        self.progress_bar.setValue(0)
    
    def set_progress(self, value: int) -> None:
        """Set the progress bar value"""
        self.progress_bar.setValue(value)
    
    def show_log_history(self) -> None:
        """Open a popup window showing all session logs"""
        self.popup = LogHistoryPopup(self.log_history, self)

        button_position = self.history_button.mapToGlobal(QPoint(0, 0))
        button_width = self.history_button.width()
        button_height = self.history_button.height()

        popup_width = self.popup.width()
        popup_height = self.popup.height()

        screen = self.history_button.screen()
        if not screen:
            screen = QApplication.primaryScreen()
        screen_geom = screen.availableGeometry()

        x = button_position.x()

        if x + popup_width > screen_geom.right():
            x = (button_position.x() + button_width) - popup_width

            if x < screen_geom.left():
                x = screen_geom.left()
        
        y = button_position.y() - popup_height
        if y < screen_geom.top():
            y = button_position.y() + button_height
        
        self.popup.move(x, y)
        self.popup.show()