import pandas as pd
import json
from typing import Optional, Dict, Any, List, Callable, Union
from pathlib import Path


class HistoryManager:
    """
    Manages data states such as undo/redo, memory enforcements, and operation logging
    """
    def __init__(self) -> None:
        self.undo_stack: List[tuple[pd.DataFrame, list, Optional[tuple[str, bool]]]] = []
        self.redo_stack: List[tuple[pd.DataFrame, list, Optional[tuple[str, bool]]]] = []
        self.max_history_memory_bytes: int = 1024 * 1024 * 1024
        self.current_memory_bytes: int = 0
        self.memory_update_callback: Optional[Callable[[int, int], None]] = None
        self.operation_log: List[Dict[str, Any]] = []
        self.sort_state: Optional[tuple[str, bool]] = None
    
    def _get_dataframe_memory_bytes(self, dataframe: pd.DataFrame) -> int:
        """Calculate shallow memory footprint of a DataFrame in bytes."""
        if dataframe is None or dataframe.empty:
            return 0
        return dataframe.memory_usage(deep=False).sum()
    
    def _notify_memory_usage(self) -> None:
        """Compute total history memory and fire the registered callback."""
        if self.memory_update_callback:
            self.memory_update_callback(self.current_memory_bytes, self.max_history_memory_bytes)
    
    def _enforce_history_memory_limits(self) -> None:
        """
        Drop the oldest undo states (then redo states) until total history
        memory is within self.max_history_memory_bytes.
        """
        while self.current_memory_bytes > self.max_history_memory_bytes:
            if self.undo_stack:
                dropped_state = self.undo_stack.pop(0)
                dropped_bytes = self._get_dataframe_memory_bytes(dropped_state[0])
                self.current_memory_bytes -= dropped_bytes
                print(
                    f"DEBUG: Memory limit reached. Dropped oldest undo state "
                    f"freeing {dropped_bytes / (1024 * 1024):.2f} MB."
                )
            elif self.redo_stack:
                dropped_state = self.redo_stack.pop(0)
                dropped_bytes = self._get_dataframe_memory_bytes(dropped_state[0])
                self.current_memory_bytes -= dropped_bytes
                print(
                    f"DEBUG: Memory limit reached. Dropped oldest redo state "
                    f"freeing {dropped_bytes / (1024 * 1024):.2f} MB."
                )
            else:
                break

        self._notify_memory_usage()
    
    def save_state(self, dataframe: pd.DataFrame) -> None:
        """Push a deep copy of *df* onto the undo stack and clear the redo stack."""
        if dataframe is not None:
            state_memory = self._get_dataframe_memory_bytes(dataframe)
            
            self.undo_stack.append((dataframe.copy(), self.operation_log.copy(), self.sort_state))
            self.current_memory_bytes += state_memory
            
            for state in self.redo_stack:
                self.current_memory_bytes -= self._get_dataframe_memory_bytes(state[0])
            self.redo_stack.clear()
            
            self._enforce_history_memory_limits()
            print(f"DEBUG: State saved. Undo stack size: {len(self.undo_stack)}")
    
    def undo(self, current_dataframe: pd.DataFrame) -> tuple[Optional[pd.DataFrame], bool]:
        """
        Pop the most-recent undo state.

        Returns:
            (restored_df, success) — restored_df is None when the stack was empty.
        """
        print(f"DEBUG: Undo called. Stack size: {len(self.undo_stack)}")
        if not self.undo_stack:
            return None, False

        if current_dataframe is not None:
            state_memory = self._get_dataframe_memory_bytes(current_dataframe)
            self.redo_stack.append((current_dataframe.copy(), self.operation_log.copy(), self.sort_state))
            self.current_memory_bytes += state_memory

        state = self.undo_stack.pop()
        self.current_memory_bytes -= self._get_dataframe_memory_bytes(state[0])
        
        if len(state) == 3:
            restored_df, restored_log, restored_sort = state
            self.sort_state = restored_sort
        else:
            restored_df, restored_log = state[:2]
            self.sort_state = None
        
        self.operation_log = restored_log.copy()
        
        self._enforce_history_memory_limits()
        print(f"DEBUG: Undo complete. Remaining stack: {len(self.undo_stack)}")
        return restored_df.copy(), True

    def redo(self, current_dataframe: pd.DataFrame) -> tuple[Optional[pd.DataFrame], bool]:
        """
        Pop the most-recent redo state.

        Returns:
            (restored_df, success) — restored_df is None when the stack was empty.
        """
        print(f"DEBUG: Redo called. Stack size: {len(self.redo_stack)}")
        if not self.redo_stack:
            return None, False

        if current_dataframe is not None:
            state_memory = self._get_dataframe_memory_bytes(current_dataframe)
            self.undo_stack.append((current_dataframe.copy(), self.operation_log.copy(), self.sort_state))
            self.current_memory_bytes += state_memory

        state = self.redo_stack.pop()
        self.current_memory_bytes -= self._get_dataframe_memory_bytes(state[0])
        
        if len(state) == 3:
            restored_df, restored_log, restored_sort = state
            self.sort_state = restored_sort
        else:
            restored_df, restored_log = state[:2]
            self.sort_state = None
        
        self.operation_log = restored_log.copy()
        
        self._enforce_history_memory_limits()
        print(f"DEBUG: Redo complete. Remaining stack: {len(self.redo_stack)}")
        return restored_df.copy(), True
    
    def can_undo(self) -> bool:
        return len(self.undo_stack) > 0
    
    def can_redo(self) -> bool:
        return len(self.redo_stack) > 0
    
    def clear(self) -> None:
        """Wipe both stacks, the operation log, and the sort state."""
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.operation_log.clear()
        self.sort_state = None
        self.current_memory_bytes = 0
        self._notify_memory_usage()
        
    def get_history_info(self) -> Dict[str, Any]:
        """
        Return the full operation log merged with any redo operations that
        are still navigable.
        """
        full_log = self.operation_log.copy()
        current_index = len(full_log)

        temporary_log = full_log
        redo_operations = []

        for i in range(len(self.redo_stack) - 1, -1, -1):
            _, state_log = self.redo_stack[i][:2]
            if len(state_log) > len(temporary_log):
                new_operations = state_log[len(temporary_log):]
                redo_operations.extend(new_operations)
                temporary_log = state_log

        return {"history": full_log + redo_operations, "current_index": current_index}
    
    def export_pipeline_macro(self, filepath: Union[str, Path]) -> None:
        """
        Write the current operation_log to a filepath as a JSON macro
        """
        if not self.operation_log:
            raise ValueError("No data operations to save")
        
        target_path = Path(filepath)
        with target_path.open("w", encoding="utf-8") as macro_file:
            json.dump(self.operation_log, macro_file, indent=4)
    
    def load_pipeline_macro(self, macro_source: Union[str, Path, List[Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """
        Load a macro from a JSON filepath or as pre parsed list
        """
        if isinstance(macro_source, (str, Path)):
            source_path = Path(macro_source)
            with source_path.open("r", encoding="utf-8") as file:
                operations = json.load(file)
        elif isinstance(macro_source, list):
            operations = macro_source
        else:
            raise ValueError( "macro_source must be a filepath string, Path or a list of operations" )
        if not isinstance(operations, list):
            raise ValueError( "Invalid file format. Expected a list of operations in JSON format")
        return operations