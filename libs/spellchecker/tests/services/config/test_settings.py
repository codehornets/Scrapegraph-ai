from unittest.mock import patch

import pytest

from src.config.settings import Settings


@pytest.fixture
def mock_constants():
    with patch("src.config.settings.APP_ENV", "test_env"), patch(
        "src.config.settings.APP_NAME", "test_app"
    ), patch("src.config.settings.AWS_BUCKET_NAME", "test_bucket"), patch(
        "src.config.settings.AWS_ENDPOINT", "test_endpoint"
    ), patch(
        "src.config.settings.AWS_REGION", "test_region"
    ), patch(
        "src.config.settings.AWS_ACCESS_KEY", "test_access_key"
    ), patch(
        "src.config.settings.AWS_SECRET_KEY", "test_secret_key"
    ), patch(
        "src.config.settings.CACHE_DIRECTORY", "/test/cache"
    ), patch(
        "src.config.settings.CACHE_FILE_PATHS", {"test": "/cache/test"}
    ), patch(
        "src.config.settings.HUNSPELL_DEFAULT_DICTIONARY_PATHS", ["/path/to/dict"]
    ), patch(
        "src.config.settings.IGNORE_UNICODE_LIST", ["\u2019"]
    ), patch(
        "src.config.settings.GLOBAL_DICTIONARY_PATH", "/path/to/global/dict"
    ), patch(
        "src.config.settings.ORDINAL_NUMBERS_REGEX", r"\d+(st|nd|rd|th)"
    ), patch(
        "src.config.settings.MLR_API_BASE_URL", "https://test.api/mlr"
    ), patch(
        "src.config.settings.QUICKAUTH_URI", "https://test.auth/quick"
    ), patch(
        "src.config.settings.QUICKAUTH_CLIENT_ID", "test_client_id"
    ), patch(
        "src.config.settings.QUICKAUTH_CLIENT_SECRET", "test_client_secret"
    ), patch(
        "src.config.settings.SUPPORTED_LANGUAGES", ["en", "fr"]
    ), patch(
        "src.config.settings.UNSUPPORTED_HUNSPELL_DICTIONARY", ["xx"]
    ):
        yield


@patch("src.config.settings.load_dotenv")  # Mock the load_dotenv function
def test_settings_initialization(mock_load_dotenv, mock_constants):
    mock_load_dotenv.return_value = None  # No need to actually load dotenv in tests

    settings = Settings()  # Create an instance of Settings

    # Check if load_dotenv was called
    mock_load_dotenv.assert_called_once()

    # Validate that all the attributes are correctly assigned
    assert settings.app_env == "test_env"
    assert settings.app_name == "test_app"
    assert settings.app_bucket == "test_bucket"
    assert settings.aws_endpoint == "test_endpoint"
    assert settings.aws_region == "test_region"
    assert settings.aws_access_key == "test_access_key"
    assert settings.aws_secret_key == "test_secret_key"
    assert settings.cache_directory == "/test/cache"
    assert settings.cache_file_paths == {"test": "/cache/test"}
    assert settings.hunspell__default_dictionary_paths == ["/path/to/dict"]
    assert settings.ignore_unicode_list == ["\u2019"]
    assert settings.global_dictionary_path == "/path/to/global/dict"
    assert settings.ordinal_numbers_regex == r"\d+(st|nd|rd|th)"
    assert settings.post_results_uri == "https://test.api/mlr"
    assert settings.quickauth_uri == "https://test.auth/quick"
    assert settings.quickauth_client_id == "test_client_id"
    assert settings.quickauth_client_secret == "test_client_secret"
    assert settings.supported_languages == ["en", "fr"]
    assert settings.unsupported_hunspell_dictionary == ["xx"]
