import pytest
from typing import Generator
from core.data_handler import DataHandler

@pytest.fixture
def empty_data_handler() -> Generator[DataHandler, None, None]:
    handler = DataHandler()
    yield handler
    handler.cleanup_temp_files()