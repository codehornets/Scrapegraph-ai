import json
import os

import pytest

from src.config.settings import Settings
from src.services.file import FileService


@pytest.fixture
def file_service():
    service = FileService(Settings())
    yield service
    # Teardown
    for file_path in service.settings.cache_file_paths.values():
        if os.path.exists(file_path):
            os.remove(file_path)


def test_hash_text(file_service):
    text = "test"
    expected_hash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    assert file_service.hash_text(text) == expected_hash


def test_cache_operations_read(file_service):
    text = "test"
    result = {"key": "value"}
    hashed_text = file_service.hash_text(text)
    cache_file = file_service.settings.cache_file_paths["word"]
    with open(cache_file, "a") as f:
        f.write(f"{hashed_text}||{json.dumps(result)}\n")

    cached_result = file_service.cache_operations(text, cache_file, operation="r")
    assert cached_result == result


def test_cache_operations_write(file_service):
    text = "test"
    result = {"key": "value"}
    cache_file = file_service.settings.cache_file_paths["word"]

    file_service.cache_operations(text, cache_file, result=result, operation="w")

    with open(cache_file, "r") as f:
        lines = f.readlines()

    assert len(lines) == 1
    _, cached_result = lines[0].strip().split("||", 1)
    assert json.loads(cached_result) == result


def test_delete_directory(file_service):
    test_dir = "test_dir"
    os.makedirs(test_dir, exist_ok=True)
    assert os.path.isdir(test_dir)

    file_service.delete_directory(test_dir)
    assert not os.path.isdir(test_dir)
