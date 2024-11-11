from unittest.mock import MagicMock
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_storage_service():
    with patch("src.services.spellcheck.StorageService", autospec=True) as mock_storage:
        mock_storage_instance = mock_storage.return_value
        mock_storage_instance.get_pdf_file.return_value = MagicMock()
        mock_storage_instance.get_dictionary_words.return_value = set()
        yield mock_storage_instance


@pytest.fixture
def mock_file_service():
    with patch("src.services.spellcheck.FileService", autospec=True) as mock_file:
        yield mock_file.return_value


@pytest.fixture
def mock_load_hunspell_dictionary():
    with patch(
        "src.services.spellcheck.load_hunspell_dictionary",
        autospec=True,
    ) as mock_load_dict:
        mock_load_dict.return_value = (MagicMock(), MagicMock())
        yield mock_load_dict


@pytest.fixture
def mock_get_ignore_patterns():
    with patch(
        "src.services.spellcheck.get_ignore_patterns_for_language",
        autospec=True,
    ) as mock_patterns:
        mock_patterns.return_value = ["word\\d"]
        yield mock_patterns


@pytest.fixture
def mock_spellcheck_service():
    with patch(
        "src.services.spellcheck.SpellcheckService", autospec=True
    ) as mock_service:
        yield mock_service


def test_spellcheck_service_initialization(
    mock_storage_service,
    mock_file_service,
    mock_load_hunspell_dictionary,
    mock_spellcheck_service,
):
    service = mock_spellcheck_service.return_value
    service.language = "en"
    service.pdf_document = [MagicMock()]
    service.custom_dictionary = set()

    assert service.language == "en"
    assert service.pdf_document is not None
    assert service.custom_dictionary == set()


def test_spellcheck_service_get_spelling_errors(
    mock_storage_service,
    mock_file_service,
    mock_load_hunspell_dictionary,
    mock_get_ignore_patterns,
    mock_spellcheck_service,
):
    service = mock_spellcheck_service.return_value
    mock_page = MagicMock()
    mock_page.get_text.return_value = [("word", 0, 0, 0, 0, "word")]
    service.pdf_document = [mock_page]
    service.get_spelling_errors.return_value = ([], 0)

    matches, words_count = service.get_spelling_errors()

    assert isinstance(matches, list)
    assert isinstance(words_count, int)
