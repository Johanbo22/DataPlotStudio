from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

from core.data_handler import DataHandler


class WorkerSignals(QObject):
    """
    Defines the signal from a running worker thread
    signals are:

    finished
        object: data (pd.DataFrame)
    error
        Exception: The exception object
    log
        str: A message to log
    """
    finished = pyqtSignal(object)
    error = pyqtSignal(Exception)
    log = pyqtSignal(str)
    progress = pyqtSignal(int, str)


class FileImportWorker(QRunnable):
    """The worker thread for importing files"""

    def __init__(self, data_handler: DataHandler, filepath: str):
        super().__init__()
        self.data_handler = data_handler
        self.filepath = filepath
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress.emit(10, "Reading file...")
            self.data_handler.import_file(self.filepath)

            self.signals.progress.emit(70, "Processing data...")
            self.signals.finished.emit(self.data_handler.df)
        except Exception as RunError:
            self.signals.error.emit(RunError)


class GoogleSheetsImportWorker(QRunnable):
    """Worker thread for imports using Google Sheets"""
    def __init__(self, data_handler: DataHandler, sheet_id: str, sheet_name: str, delimiter: str, decimal: str, thousands: str, gid: str = None):
        super().__init__()
        self.data_handler = data_handler
        self.sheet_id = sheet_id
        self.sheet_name = sheet_name
        self.delimiter = delimiter
        self.decimal = decimal
        self.thousands = thousands
        self.gid = gid
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress.emit(10, "Connecting to Google Sheets...")
            self.data_handler.import_google_sheets(
                self.sheet_id,
                self.sheet_name,
                delimiter=self.delimiter,
                decimal=self.decimal,
                thousands=self.thousands,
                gid=self.gid
            )

            self.signals.progress.emit(70, "Processing data...")
            self.signals.finished.emit(self.data_handler.df)
        except Exception as RunError:
            self.signals.error.emit(RunError)