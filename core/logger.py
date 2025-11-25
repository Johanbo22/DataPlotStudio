# core/logger.py
from datetime import datetime
from pathlib import Path
from typing import List, Optional


class LogEntry:
    """Represents a single log entry"""
    
    def __init__(self, level: str, message: str, timestamp: Optional[datetime] = None):
        self.timestamp = timestamp or datetime.now()
        self.level = level
        self.message = message
    
    def __str__(self) -> str:
        return f"[{self.timestamp.strftime('%H:%M:%S')}] [{self.level:8s}] {self.message}"
    
    def to_detailed_str(self) -> str:
        """Return detailed log entry with full timestamp"""
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] [{self.level:8s}] {self.message}"


class Logger:
    """Handles all logging for DataPlot Studio"""
    
    def __init__(self, max_entries: int = 1000):
        self.entries: List[LogEntry] = []
        self.max_entries = max_entries
    
    def _add_entry(self, level: str, message: str):
        """Add log entry"""
        entry = LogEntry(level, message)
        self.entries.append(entry)
        
        # Keep only recent entries
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def info(self, message: str):
        """Log info message"""
        self._add_entry("INFO", message)
    
    def success(self, message: str):
        """Log success message"""
        self._add_entry("SUCCESS", message)
    
    def warning(self, message: str):
        """Log warning message"""
        self._add_entry("WARNING", message)
    
    def error(self, message: str):
        """Log error message"""
        self._add_entry("ERROR", message)
    
    def data_imported(self, filename: str, rows: int, cols: int, file_size_kb: float):
        """Log data import"""
        msg = f"Data imported: {filename} ({rows:,} rows × {cols} cols, {file_size_kb:.1f} KB)"
        self.success(msg)
    
    def google_sheets_imported(self, sheet_id: str, sheet_name: str, rows: int, cols: int):
        """Log Google Sheets import"""
        msg = f"Google Sheet imported: '{sheet_name}' ({rows:,} rows × {cols} cols)"
        self.success(msg)
    
    def filter_applied(self, column: str, condition: str, value: str, rows_before: int, rows_after: int):
        """Log filter operation"""
        rows_removed = rows_before - rows_after
        msg = f"Filter applied: {column} {condition} '{value}' | Rows: {rows_before:,} → {rows_after:,} (-{rows_removed:,})"
        self.success(msg)
    
    def duplicates_removed(self, count: int):
        """Log duplicate removal"""
        msg = f"Removed {count:,} duplicate row(s)"
        self.success(msg)
    
    def missing_values_dropped(self, count: int):
        """Log missing value removal"""
        msg = f"Dropped {count:,} row(s) with missing values"
        self.success(msg)
    
    def missing_values_filled(self, count: int):
        """Log missing value filling"""
        msg = f"Filled {count:,} missing value(s) using forward fill"
        self.success(msg)
    
    def column_dropped(self, column: str):
        """Log column drop"""
        msg = f"Column dropped: '{column}'"
        self.success(msg)
    
    def column_renamed(self, old_name: str, new_name: str):
        """Log column rename"""
        msg = f"Column renamed: '{old_name}' → '{new_name}'"
        self.success(msg)
    
    def data_aggregated(self, group_by: str, agg_col: str, agg_func: str, result_rows: int):
        """Log aggregation"""
        msg = f"Data aggregated: groupby('{group_by}').{agg_func}('{agg_col}') | Result: {result_rows:,} rows"
        self.success(msg)
    
    def data_exported(self, filename: str, format_type: str, rows: int, cols: int):
        """Log data export"""
        msg = f"Data exported: {filename} ({format_type.upper()}, {rows:,} rows × {cols} cols)"
        self.success(msg)
    
    def code_exported(self, filename: str, script_type: str):
        """Log code export"""
        msg = f"Python script exported: {filename} ({script_type})"
        self.success(msg)
    
    def plot_generated(self, plot_type: str, x_col: str, y_col: str, annotations: int = 0):
        """Log plot generation"""
        ann_text = f" with {annotations} annotation(s)" if annotations > 0 else ""
        msg = f"Plot generated: {plot_type} | X: '{x_col}', Y: '{y_col}'{ann_text}"
        self.success(msg)
    
    def plot_cleared(self):
        """Log plot clear"""
        self.info("Plot cleared")
    
    def data_reset(self):
        """Log data reset"""
        msg = "Data reset to original state"
        self.success(msg)
    
    def undo_performed(self):
        """Log undo"""
        msg = "Undo: Previous state restored"
        self.info(msg)
    
    def redo_performed(self):
        """Log redo"""
        msg = "Redo: Action restored"
        self.info(msg)
    
    def project_created(self):
        """Log new project"""
        self.success("New project created")
    
    def project_loaded(self, filename: str):
        """Log project load"""
        self.success(f"Project loaded: {filename}")
    
    def project_saved(self, filename: str):
        """Log project save"""
        self.success(f"Project saved: {filename}")
    
    def get_all_logs(self) -> str:
        """Get all logs as formatted string"""
        return "\n".join(str(entry) for entry in self.entries)
    
    def get_detailed_logs(self) -> str:
        """Get detailed logs with full timestamps"""
        return "\n".join(entry.to_detailed_str() for entry in self.entries)
    
    def export_logs(self, filepath: str, detailed: bool = True) -> str:
        """Export logs to file"""
        path = Path(filepath)
        
        try:
            content: str = self._generate_log_report(detailed)
            
            with open(path, 'w', encoding="utf-8") as f:
                f.write(content)
            
            return str(path)
        except Exception as e:
            raise Exception(f"Error exporting logs: {str(e)}")
    
    def _generate_log_report(self, detailed: bool = True) -> str:
        """Generate formatted log report"""
        report = f"""
            {'='*160}
            DataPlot Studio - Session Log Report
            Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            This log is automatically generated
            {'='*160}

            SUMMARY
            -------
            Total Log Entries: {len(self.entries)}
            Session Duration: {self._get_session_duration()}

            LOG ENTRIES
            -----------
            """
        
        if detailed:
            report += self.get_detailed_logs()
        else:
            report += self.get_all_logs()
        
        report += f"""

        {'='*160}
        END OF LOG REPORT
        {'='*160}
        """
        return report
    
    def _get_session_duration(self) -> str:
        """Calculate session duration"""
        if not self.entries:
            return "0:00:00"
        
        start = self.entries[0].timestamp
        end = self.entries[-1].timestamp
        delta = end - start
        
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        return f"{hours}:{minutes:02d}:{seconds:02d}"
    
    def clear(self):
        """Clear all log entries"""
        self.entries.clear()
    
    def get_stats(self) -> dict:
        """Get log statistics"""
        levels = {}
        for entry in self.entries:
            levels[entry.level] = levels.get(entry.level, 0) + 1
        
        return {
            'total_entries': len(self.entries),
            'by_level': levels,
            'session_duration': self._get_session_duration(),
        }