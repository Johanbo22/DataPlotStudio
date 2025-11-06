# ui/status_bar.py
from PyQt6.QtWidgets import QStatusBar, QLabel, QLineEdit
from PyQt6.QtCore import Qt
from datetime import datetime
from core.logger import Logger



class StatusBar(QStatusBar):
    """Custom status bar with terminal output and logging"""
    
    def __init__(self) -> None:
        super().__init__()
        
        #logger will be set by main app
        self.logger = Logger()

        #track changes
        self.recent_actions = []
        self.action_timeout = 2 #secs before grouping
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
        
        # Terminal-like output area
        self.terminal = QLineEdit()
        self.terminal.setReadOnly(True)
        self.terminal.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                font-family: Consolas, 'Courier New', monospace;
                font-size: 10px;
                border: 1px solid #444;
                padding: 4px;
            }
        """)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #00ff00;")
        
        # Add widgets to status bar
        self.addWidget(self.status_label, 1)
        self.addWidget(self.terminal, 3)

    def set_logger(self, logger) -> None:
        """Set the logger instance"""
        self.logger = logger
        print(f"Logger set in StatusBar: {logger is not None}")
    
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