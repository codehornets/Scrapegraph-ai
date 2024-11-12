import os
import sys

from dotenv import load_dotenv

from libs.spellchecker.src.config.constants import (
    APP_ENV,
    APP_NAME,
    AWS_ACCESS_KEY,
    AWS_BUCKET_NAME,
    AWS_ENDPOINT,
    AWS_REGION,
    AWS_SECRET_KEY,
    CACHE_DIRECTORY,
    CACHE_FILE_PATHS,
    DOTENV_PATH,
    GLOBAL_DICTIONARY_PATH,
    HUNSPELL_DEFAULT_DICTIONARY_PATHS,
    IGNORE_UNICODE_LIST,
    MLR_API_BASE_URL,
    ORDINAL_NUMBERS_REGEX,
    QUICKAUTH_CLIENT_ID,
    QUICKAUTH_CLIENT_SECRET,
    QUICKAUTH_URI,
    SPLYLLS_UNSUPPORTED_DICTIONARY_PATHS,
    SUPPORTED_LANGUAGES,
    SYMBOLS_TO_SKIP,
    UNSUPPORTED_HUNSPELL_DICTIONARY,
)


class Settings:
    def __init__(self):
        self.load_dotenv()

        self.app_env = APP_ENV
        self.app_name = APP_NAME
        self.app_bucket = AWS_BUCKET_NAME
        self.aws_endpoint = AWS_ENDPOINT
        self.aws_region = AWS_REGION
        self.aws_access_key = AWS_ACCESS_KEY
        self.aws_secret_key = AWS_SECRET_KEY
        self.cache_directory = CACHE_DIRECTORY
        self.cache_file_paths = CACHE_FILE_PATHS
        self.hunspell_default_dictionary_paths = HUNSPELL_DEFAULT_DICTIONARY_PATHS
        self.ignore_unicode_list = IGNORE_UNICODE_LIST
        self.global_dictionary_path = GLOBAL_DICTIONARY_PATH
        self.ordinal_numbers_regex = ORDINAL_NUMBERS_REGEX
        self.post_results_uri = MLR_API_BASE_URL
        self.quickauth_uri = QUICKAUTH_URI
        self.quickauth_client_id = QUICKAUTH_CLIENT_ID
        self.quickauth_client_secret = QUICKAUTH_CLIENT_SECRET
        self.supported_languages = SUPPORTED_LANGUAGES
        self.symbols_to_skip = SYMBOLS_TO_SKIP
        self.spylls_unsupported_dictionary_paths = SPLYLLS_UNSUPPORTED_DICTIONARY_PATHS
        self.unsupported_hunspell_dictionary = UNSUPPORTED_HUNSPELL_DICTIONARY

    @staticmethod
    def load_dotenv():
        dotenv_file_path = (
            DOTENV_PATH
            if os.path.exists(DOTENV_PATH) or "pytest" not in sys.modules
            else os.path.join(os.path.dirname(__file__), DOTENV_PATH)
        )

        load_dotenv(dotenv_file_path)
