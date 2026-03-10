from PyQt6.QtCore import QObject, QRunnable, pyqtSignal, pyqtSlot

from core.data_handler import DataHandler
from sqlalchemy import create_engine, text
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from core.subset_manager import SubsetManager


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
    
class AggregationWorker(QRunnable):
    """Worker for performing data aggregation"""
    def __init__(self, data_handler: DataHandler, group_by: list[str], agg_config: dict[str, str], date_grouping: dict[str, str]) -> None:
        super().__init__()
        self.data_handler = data_handler
        self.group_by = group_by
        self.agg_config = agg_config
        self.date_grouping = date_grouping
        self.signals = WorkerSignals()
    
    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress.emit(10, "Preparing Aggregation...")
            self.signals.log.emit(f"Starting background aggregation task with {len(self.group_by)} groups...")
            result_df = self.data_handler.preview_aggregation(group_by=self.group_by, agg_config=self.agg_config, date_grouping=self.date_grouping, limit=None)
            
            self.signals.progress.emit(100, "Aggregation complete")
            self.signals.log.emit("Background aggregation task completed successfully.")
            self.signals.finished.emit(result_df)
        except Exception as AggWorkerError:
            self.signals.log.emit(f"Aggregation worker failed: {str(AggWorkerError)}")
            self.signals.error.emit(AggWorkerError)

class FilterWorker(QRunnable):
    """Worker for applying filters"""
    
    def __init__(self, data_handler: DataHandler, filter_config: dict):
        super().__init__()
        self.data_handler = data_handler
        self.filter_config = filter_config
        self.signals = WorkerSignals()
    
    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress.emit(10, "Applying filters...")
            
            result_df = self.data_handler.apply_filter(self.filter_config)
            self.signals.progress.emit(100, "Filtering complete")
            self.signals.finished.emit(result_df)
        except Exception as Error:
            self.signals.error.emit(Error)

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

class TestConnectionWorker(QRunnable):
    """Worker to test database connections"""

    def __init__(self, connection_string: str):
        super().__init__()
        self.connection_string = connection_string
        self.signals = WorkerSignals()
    
    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress.emit(10, "Connecting...")
            engine = create_engine(self.connection_string)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.signals.progress.emit(100, "Connection Successful")
            self.signals.finished.emit(True)
        except Exception as ConnectionError:
            self.signals.error.emit(ConnectionError)

class AutoCreateSubsetsWorker(QRunnable):
    """Worker thread for auto-creating and applying subsets"""
    
    def __init__(self, subset_manager: "SubsetManager", df, column: str):
        super().__init__()
        self.subset_manager = subset_manager
        self.df = df
        self.column = column
        self.signals = WorkerSignals()
    
    @pyqtSlot()
    def run(self):
        try:
            self.signals.progress.emit(10, f"Auto-creating subsets")
            created = self.subset_manager.create_subset_from_unique_values(self.df, self.column)
            
            total = len(created)
            if total == 0:
                self.signals.progress.emit(100, "No new subsets created.")
                self.signals.finished.emit(created)
                return
            
            for i, name in enumerate(created):
                progress = 10 + int((i / total) * 85)
                self.signals.progress.emit(progress, f"Applying subset {i+1} of {total}: {name}...")
                
                self.subset_manager.apply_subset(self.df, name)
            
            self.signals.progress.emit(100, "Finalizing...")
            self.signals.finished.emit(created)
        except Exception as Error:
            self.signals.error.emit(Error)