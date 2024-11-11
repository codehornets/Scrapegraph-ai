import os
from unittest.mock import patch

import boto3
from moto import mock_s3

from src.config.settings import Settings
from src.services.storage import StorageService


@patch("requests.get")
@patch("fitz.open")
def test_get_pdf_file(mock_fitz_open, mock_requests_get):
    # setup
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.content = b"pdf file content"
    mock_fitz_open.side_effect = lambda x: f"Mocked pdf object for {x}"

    service = StorageService(Settings())
    result = service.get_pdf_file("https://some_test_url.pdf")

    mock_requests_get.assert_called_once_with("https://some_test_url.pdf")
    assert "Mocked pdf object for" in result


@mock_s3
@patch("requests.get")
@patch.object(StorageService, "load_words_from_directory", return_value=set())
def test_get_dictionary_words(mock_load_words, mock_requests_get):
    mock_requests_get.return_value.status_code = 200
    mock_requests_get.return_value.content = b"word1\nword2\nword3"
    conn = boto3.client("s3", region_name="us-east-1")
    conn.create_bucket(Bucket="my_bucket")
    conn.put_object(Bucket="my_bucket", Key="dictionary.txt", Body="")
    os.environ["AWS_ACCESS_KEY_ID"] = "fake_access_key"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "fake_secret_key"
    os.environ["AWS_SECURITY_TOKEN"] = "fake_session_token"
    os.environ["AWS_SESSION_TOKEN"] = "fake_session_token"

    service = StorageService(Settings())
    result = service.get_dictionary_words("https://some_test_url.txt")

    assert result == {"word1", "word2", "word3"}
