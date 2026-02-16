# ui/status_bar.py
from PyQt6.QtWidgets import QStatusBar, QLabel, QLineEdit, QProgressBar, QApplication
from PyQt6.QtCore import Qt, QPoint, QTimer
from datetime import datetime
from core.logger import Logger
from ui.widgets.AnimatedButton import DataPlotStudioButton
from ui.dialogs.LogHistoryPopup import LogHistoryPopup



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
        
        # Message queue for the typerwrite animation
        # Should prevent stuttering on multiple calls 
        self.message_queue: list[tuple[str, str]] = []
        self.is_typing: bool = False

        #Timer effect for type
        self.typewriter_timer = QTimer()
        self.typewriter_timer.setInterval(20)
        self.typewriter_timer.timeout.connect(self._type_next_char)
        self.current_anim_text = ""
        self.current_anim_index = 0

        self.setStyleSheet("""
            QStatusBar {
                background-color: #1e1e1e;
                color: #ffffff;
                border-top: 1px solid #3e3e42;
                padding: 4px;
            }
            QStatusBar::item {
                border: none;
            }
            QLabel{
                padding: 0 5px;
            }
        """)

        # Adding a label of data stat
        self.stats_label = QLabel("No Data")
        self.stats_label.setStyleSheet("""
            QLabel {
                color: #858585;
                font-family: 'Segoe UI', sans-serif;
                font-size: 11px;
                padding-right: 15px;
            }
        """)

        # Adding some progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(150)
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: none;
                background-color: #2d2d2d;
                border-radius: 2px;
                min-height: 4px;
                max-height: 4px;
            }
            QProgressBar::chunk {
                background-color: #007acc;
                border-radius: 2px;
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
        self.history_button = DataPlotStudioButton("≡", base_color_hex="#333", hover_color_hex="#444", text_color_hex="#ddd", padding="4px")
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
        self.status_label = QLabel()
        self.status_label.setStyleSheet("color: #00ff00;")
        
        # Add widgets to status bar
        self.addWidget(self.status_label, 0)
        self.addWidget(self.terminal, 1)
        self.addWidget(self.history_button)

        self.source_label = QLabel("")
        self.source_label.setStyleSheet("color: #3498db; font-size: 11px; padding-right: 10px;")

        self.view_context_label = QLabel("")
        self.view_context_label.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 11px; padding-right: 10px;")
        
        self.addPermanentWidget(self.progress_bar)
        self.addPermanentWidget(self.source_label)
        self.addPermanentWidget(self.view_context_label)
        self.addPermanentWidget(self.stats_label)

    def set_logger(self, logger) -> None:
        """Set the logger instance"""
        self.logger = logger
    
    def log(self, message: str, level: str = "INFO", action_type: str = None, log_to_file: bool = True) -> None:
        """Log a message to the terminal"""
        timestamp: str = datetime.now().strftime("%H:%M:%S")
        
        # set col based on actionlevel
        if level == "SUCCESS":
            color = "#00ff00"
        elif level == "WARNING":
            color = "#ffaa00"
        elif level == "ERROR":
            color = "#ff0000"
        else:
            color = "#00ff00"
        
        display_message = f"{message}"
        log_message: str = f"[{timestamp}] | {display_message}"

        # Store the log in the history
        self.log_history.append(f'<span style="color:{color}">{log_message}</span>')
        
        self.status_label.setText("Ready" if level in ("SUCCESS", "INFO") else "Warning" if level == "WARNING" else "Error")
        self.status_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 11px;")
        
        self.message_queue.append((log_message, color))
        if not self.is_typing:
            self._process_next_message()

        #log to file logger if available
        if log_to_file and self.logger:
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
    
    def _process_next_message(self) -> None:
        """Process the next messsage in the queue to animation"""
        if not self.message_queue:
            self.is_typing = False
            self.typewriter_timer.stop()
            return
        
        self.is_typing = True
        log_message, color = self.message_queue.pop(0)
        
        self.terminal.setStyleSheet(f"QLineEdit {{background-color: transparent; color: {color}; font-family: Consolas, monospace; font-size: 11px; border: none; padding: 0 5px;}}")
        self._start_typing(log_message)
    
    def _start_typing(self, text: str) -> None:
        """Initialize the typewriter effect"""
        self.typewriter_timer.stop()
        self.current_anim_text = text
        self.current_anim_index = 0
        self.terminal.setText("")
        self.typewriter_timer.start()
    
    def _type_next_char(self) -> None:
        if self.current_anim_index < len(self.current_anim_text):
            chunk_size: int = max(1, len(self.current_anim_text) // 50)

            end_index = min(self.current_anim_index + chunk_size, len(self.current_anim_text))

            current_text = self.current_anim_text[:end_index]
            self.terminal.setText(current_text)
            self.current_anim_index = end_index
        else:
            self._process_next_message()
    
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
        self.log(status_message, level, log_to_file=False)

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
        if df is not None and hasattr(df, "shape") and len(df.shape) == 2:
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

    def set_data_source(self, source_text: str) -> None:
        """Update the data source label"""
        if source_text:
            self.source_label.setText(f"Source: {source_text}")
            self.source_label.show()
        else:
            self.source_label.clear()
            self.source_label.hide()
    
    def set_view_context(self, context_text: str, context_type: str = "subset") -> None:
        """update the view context label to match current viewing"""
        if not context_text or context_type == "normal":
            self.view_context_label.clear()
            self.view_context_label.hide()
            return
        
        self.view_context_label.setText(context_text)
        self.view_context_label.show()

        # Colors
        if context_type == "aggregation":
            self.view_context_label.setStyleSheet("color: #8e44ad; font-weight: bold; font-size: 11px; padding-right: 10px;")
        else:
            self.view_context_label.setStyleSheet("color: #e67e22; font-weight: bold; font-size: 11px; padding-right: 10px;")