import datetime
import os
import re

from dotenv import load_dotenv

load_dotenv()
__root__ = os.getcwd()
__version__ = "0.1.0"

ALLOWED_METHODS = ["HEAD", "GET", "OPTIONS", "POST"]

API_TOKEN = os.getenv("API_TOKEN")
APP_NAME = os.getenv("APP_NAME", "spellcheck")
APP_ENV = os.getenv("APP_ENV", "local")

AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME", "det-" + APP_NAME)
AWS_EFS_PATH = os.getenv("AWS_EFS_PATH", __root__ + "/storage")
AWS_ENDPOINT = os.getenv("AWS_ENDPOINT", "http://localhost:9001")
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY", "minioadmin")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY", "minioadmin")

CACHE_DIRECTORY = os.getenv("CACHE_DIRECTORY", f"{AWS_EFS_PATH}/cache")
CACHE_FILE_PATHS = os.getenv(
    "CACHE_FILE_PATHS", {"word": f"{AWS_EFS_PATH}/cache/word_dictionary.txt"}
)

DEFAULT_IGNORED_PATTERNS = [
    r"pp-\w+-\d*",  # pattern for document numbers like "PP-0004" or "pp-0004"
    r"word\d",
    r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b",  # pattern for emails
    r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",  # pattern for URLs
    r"\b\d{4}-\d{2}-\d{2}\b",  # pattern for date format: yyyy-mm-dd
    r"\b\d{2}:\d{2}:\d{2}\b",  # pattern for time format: hh:mm:ss
    r"\b\d{10}\b",  # pattern for phone numbers of 10 digits
    r"\b[\w-]+/[\w-]+\b",  # pattern for word/word compound strings
    r"[A-Za-z0-9]+/[A-Za-z0-9]+",  # pattern for alphanumeric strings separated by "/"
    "[^\x00-\x7F]+",  # pattern for non-ASCII (Unicode) characters
]

DOTENV_PATH = os.path.join(os.getcwd(), ".env")

HUNSPELL_DEFAULT_DICTIONARY_PATH = (
    "/packages/spellchecker/storage/dictionaries/libreoffice"
)
HUNSPELL_DEFAULT_DICTIONARY_PATHS = {
    "Darwin": __root__ + HUNSPELL_DEFAULT_DICTIONARY_PATH,
    "Linux": __root__ + HUNSPELL_DEFAULT_DICTIONARY_PATH,
    "Windows": __root__ + HUNSPELL_DEFAULT_DICTIONARY_PATH,
}

GLOBAL_DICTIONARY_PATH = __root__ + "/packages/spellchecker/storage/dictionaries/global"

IGNORE_UNICODE_LIST = [
    "\u00ab",
    "\u00bb",
    "\u2022",
    "\u2018",
    "\u2019",
    "\u201c",
    "\u201d",
    "\u2026",
    "\u2013",
    "\u2014",
]

QUICKAUTH_URI = os.getenv("QUICKAUTH_URI")
QUICKAUTH_CLIENT_ID = os.getenv("QUICKAUTH_CLIENT_ID")
QUICKAUTH_CLIENT_SECRET = os.getenv("QUICKAUTH_CLIENT_SECRET")
ORDINAL_NUMBERS = "[0-9]+\u00e8me"
ORDINAL_NUMBERS_REGEX = re.compile(ORDINAL_NUMBERS)

NORMALIZED_WORDS_FILE = "normalized_words_dictionary.txt"

MLR_API_BASE_URL = os.getenv("MLR_API_BASE_URL")

PATTERNS_LIST = [
    r"((http|https)://)?(www\.)?[a-zA-Z0-9]+\.[a-zA-Z]{2,3}(/[a-zA-Z0-9#./?=]*)*",  # URL pattern
    r"[a-zA-Z0-9%]+\&[a-zA-Z0-9]+=.*",  # pattern to exclude URL-like fragments
    r".*%[a-zA-Z0-9]{2}.*",  # URL-encoded pattern
    r"\b\w=\w*\b",  # pattern with '\w=\w*',
    r"\b(?:[s-z|S-Z]{2,}\.[a-zA-Z0-9-]{2,})\b",  # Domain pattern
    r"\([^)]*\)",  # Medical pattern
    r"\(\w+,\s*\d{4}\)",  # Citation pattern
    r"\d{4};\d{1,2}\(\d{1,2}\):e\d+–e\d+.",  # Citation pattern V3
    r"\([\w\s,.]+\)",  # Academic citation pattern
    r"\d{4};\d{1,2}\(\d{1,2}\):e\d+.",  # Academic citation pattern V2
    r"\bNCT\d{8}\b",  # Clinical trial identifier pattern
    r"\b\w+=\w*\b|\b\w+&\w*\b",  # pattern with '\w=\w*' and '\w&\w*'
    r"\b\w+=\w*\b|\b\w+&\w*\b|\b\w+\|\w*\b",  # pattern to exclude URL-like fragments and piped words
    r"\b\d+px\b",  # pattern to exclude pixel values
]

PDF_LOCAL_DIRECTORY = os.getenv("PDF_LOCAL_DIRECTORY", f"{AWS_EFS_PATH}/pdfs")
REPORT_DIRECTORY = os.getenv("REPORT_DIRECTORY", f"{AWS_EFS_PATH}/reports")
REPORT_FILE_PATH = os.path.join(
    REPORT_DIRECTORY,
    f"spellcheck_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.json",
)
S3_DICTIONARY_BASE_PATH = os.getenv(
    "S3_DICTIONARY_BASE_PATH", "/packages/spellchecker/storage/dictionaries/saved"
)

STATUS_FORCE_LIST = [429, 500, 502, 503, 504]

SUPPORTED_LANGUAGE_CODES = ["de", "en", "es", "fr", "ja", "ko", "pt", "zh"]
SUPPORTED_LANGUAGES = [
    "de_AT",  # German (Austria)
    "de_AT_frami",  # German (Austria, framit variant)
    "de_CH",  # German (Switzerland)
    "de_CH_frami",  # German (Switzerland, frami variant)
    "de_DE",  # German (Germany)
    "de_DE_frami",  # German (Germany, frami variant)
    "en_AU",  # English (Australia)
    "en_CA",  # English (Canada)
    "en_GB",  # English (Great Britain)
    "en_med_glut",  # English (International Medical Spelling variant)
    "en_US",  # English (United States)
    "en_ZA",  # English (South Africa)
    "es_AR",  # Spanish (Argentina)
    "es_BO",  # Spanish (Bolivia)
    "es_CL",  # Spanish (Chile)
    "es_CO",  # Spanish (Colombia)
    "es_CR",  # Spanish (Costa Rica)
    "es_CU",  # Spanish (Cuba)
    "es_DO",  # Spanish (Dominican Republic)
    "es_EC",  # Spanish (Ecuador)
    "es_ES",  # Spanish (Spain)
    "es_GT",  # Spanish (Guatemala)
    "es_HN",  # Spanish (Honduras)
    "es_MX",  # Spanish (Mexico)
    "es_NI",  # Spanish (Nicaragua)
    "es_PA",  # Spanish (Panama)
    "es_PE",  # Spanish (Peru)
    "es_PR",  # Spanish (Puerto Rico)
    "es_PY",  # Spanish (Paraguay)
    "es_SV",  # Spanish (El Salvador)
    "es_US",  # Spanish (United States)
    "es_UY",  # Spanish (Uruguay)
    "es_VE",  # Spanish (Venezuela)
    "fr_BE",  # French (Belgium)
    "fr_CA",  # French (Canada)
    "fr_CH",  # French (Switzerland)
    "fr_FR",  # French (France)
    "fr_LU",  # French (Luxembourg)
    "ja_JP",  # Japanese
    "ko_KR",  # Korean (South Korea)
    "pt_BR",  # Portuguese (Brazil)
    "pt_PT",  # Portuguese (Portugal)
    # "zh_CN",  # Chinese (Simplified)
]
SYMBOLS_TO_SKIP = [
    "ø",
    "ł",
    "-",
    "=",
    "+",
    "*",
    "/",
    "\\",
    "|",
    "~",
    "`",
    "!",
    "@",
    "#",
    "$",
    "%",
    "ˆ",
    "^",
    "&",
    "(",
    ")",
    "{",
    "}",
    "[",
    "]",
    "<",
    ">",
    "?",
    ";",
    ":",
    "'",
    '"',
    ",",
    ".",
    " ",
]

SPLYLLS_UNSUPPORTED_DICTIONARY_PATH = (
    __root__ + "/packages/spellchecker/storage/dictionaries/mozilla"
)
SPLYLLS_UNSUPPORTED_DICTIONARY_PATHS = {
    "Darwin": SPLYLLS_UNSUPPORTED_DICTIONARY_PATH,
    "Linux": SPLYLLS_UNSUPPORTED_DICTIONARY_PATH,
    "Windows": SPLYLLS_UNSUPPORTED_DICTIONARY_PATH,
}

UNSUPPORTED_HUNSPELL_DICTIONARY = [
    "zh_CN",  # Chinese (Simplified)
]

URL_PARTS = ["https", "http", "www", ".com", ".gov", ".org", "?", "&", "%"]

WORKFRONT_PROJECT_ID = os.getenv("WORKFRONT_PROJECT_ID")
WORKFRONT_DOCUMENT_ID = os.getenv("WORKFRONT_DOCUMENT_ID")
WORKFRONT_PDF_FILE_URL = os.getenv("WORKFRONT_PDF_FILE_URL")
