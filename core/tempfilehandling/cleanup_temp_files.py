import os
from pathlib import Path

def cleanup_temp_csv_files(temp_csv_path: Path | None) -> None:
    """Delete temporary csv file"""
    if temp_csv_path and temp_csv_path.exists():
        try:
            os.remove(temp_csv_path)
            print(f"DEBUG: Deleted temporary CSV file at: {temp_csv_path}")
        except PermissionError as DeleteTempCSVFilePermissionError:
            print(f"DEBUG: Permission denied: {str(DeleteTempCSVFilePermissionError)}")
        except Exception as CleanTempFileError:
            print(f"DEBUG: Failed to delete temp CSV file: {str(CleanTempFileError)}")