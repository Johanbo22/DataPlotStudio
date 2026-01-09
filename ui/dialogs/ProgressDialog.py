from ui.widgets.AnimatedButton import DataPlotStudioButton


from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from PyQt6.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QProgressBar, QVBoxLayout


class ProgressDialog(QDialog):
    """A dualog showing progress for long operations and datasets"""

    def __init__(self, title="Processing", message="Please wait...", parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 150)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.CustomizeWindowHint | Qt.WindowType.WindowTitleHint)

        self.init_ui(message)

    def init_ui(self, message) -> None:
        """Initialize the ui"""
        layout = QVBoxLayout()

        #msg lbl
        self.message_label = QLabel(message)
        self.message_label.setFont(QFont("Arial", 10))
        self.message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.message_label)

        layout.addSpacing(10)

        #prgs bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("QProgressBar { border: 2px solid #3498db; border-radius: 5px; text-align: center; font-weight: bold; background-color: #ecf0f1;} QProgressBar::chunk { background-color: #3498db; border-radius: 3px;}")
        layout.addWidget(self.progress_bar)

        layout.addSpacing(10)

        #status lbl
        self.status_label = QLabel("Initializing")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: #7f8c8d")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.status_label)

        layout.addSpacing(10)

        #canel btn
        self.cancel_button = DataPlotStudioButton("Cancel", parent=self)
        self.cancel_button.setMaximumWidth(100)
        self.cancel_button.clicked.connect(self.reject)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.was_cancelled = False

    def update_progress(self, value, status="") -> None:
        """ipdate the progress bar value and msg"""
        self.progress_bar.setValue(value)
        if status:
            self.status_label.setText(status)
        QApplication.processEvents()

    def set_message(self, message) -> None:
        """update main msg"""
        self.message_label.setText(message)
        QApplication.processEvents()

    def set_status(self, status) -> None:
        """update the status"""
        self.status_label.setText(status)
        QApplication.processEvents()

    def is_cancelled(self) -> bool:
        """Check if operation is cancelled"""
        return self.was_cancelled

    def reject(self) -> None:
        """Handle cnacel button"""
        self.was_cancelled = True
        super().reject()