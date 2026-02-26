import pytest
import pandas as pd
from core.data_handler import DataHandler

def test_create_empty_dataframe(empty_data_handler: DataHandler) -> None:
    target_rows: int = 5
    target_columns: int = 3
    expected_columns: list[str] = ["ID", "Name", "Value"]
    
    resulting_dataframe: pd.DataFrame = empty_data_handler.create_empty_dataframe(
        rows=target_rows,
        columns=target_columns,
        column_names=expected_columns
    )
    assert isinstance(resulting_dataframe, pd.DataFrame)
    assert resulting_dataframe.shape == (target_rows, target_columns)
    assert list(resulting_dataframe.columns) == expected_columns
    
    assert empty_data_handler.file_path is None
    assert empty_data_handler.is_temp_file is False
    assert len(empty_data_handler.undo_stack) == 0
    assert len(empty_data_handler.redo_stack) == 0

def test_sort_data_ascending(empty_data_handler: DataHandler) -> None:
    """
    Test that sorting a DataFrame by a specific column in ascending order works correctly
    and that the operation is logged in the internal state.
    """
    # Arrange
    test_data: dict[str, list[int]] = {"ID": [3, 1, 2], "Value": [30, 10, 20]}
    empty_data_handler.df = pd.DataFrame(test_data)
    
    # Act
    sorted_dataframe: pd.DataFrame = empty_data_handler.sort_data(column="ID", ascending=True)
    
    # Assert
    expected_order: list[int] = [1, 2, 3]
    assert sorted_dataframe["ID"].tolist() == expected_order
    
    # Verify state tracking
    assert empty_data_handler.sort_state == ("ID", True)
    assert len(empty_data_handler.operation_log) == 1
    assert empty_data_handler.operation_log[0]["type"] == "sort"

def test_sort_data_raises_error_on_missing_column(empty_data_handler: DataHandler) -> None:
    """
    Test that attempting to sort by a non-existent column raises the appropriate ValueError.
    """
    # Arrange
    empty_data_handler.df = pd.DataFrame({"ID": [1, 2, 3]})
    invalid_column_name: str = "NonExistentColumn"

    # Act & Assert
    with pytest.raises(Exception) as expected_error:
        empty_data_handler.sort_data(column=invalid_column_name)
    
    assert "Error sorting data" in str(expected_error.value)
    assert invalid_column_name in str(expected_error.value)