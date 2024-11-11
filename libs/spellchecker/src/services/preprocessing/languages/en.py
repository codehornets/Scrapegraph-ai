import re
import string
import unicodedata
from collections import OrderedDict

import stopwordsiso

from libs.spellchecker.src.utils.preprocessing import remove_extra_characters_and_digits

DATE_PATTERN = r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{1,2}-[A-Za-z]{3}-\d{4}|GMT[+-]\d{4}|\d{2}:\d{2}:\d{2})\b"  # Regex pattern to identify date, GMT offset and time
SUPERSCRIPT_PATTERN = r"(\b[A-Za-z-]+[A-Za-z])(\d+(,\d+)*)\b"
ALPHANUMERIC_HYPHEN_PATTERN = r"[\da-zA-Z]+-[\d]+"
ANY_TEXT_SPECIAL_CHAR_DIGIT_PATTERN = r"(\b\w+)\W\d+\b"
DOC_NUMBER_PATTERN = r"[A-Z]{2}-[A-Z]{3}-[A-Z]{3}-\d{4}"
BIBLIO_REF_PATTERN = r"^\d{4};\d{1,3}\(\d{1,3}\):\d{1,3}\\u2013\d{1,3};$"
COLON_SEPARATED_NUMBERS_PATTERN = r"^\d{4};\d+\(\d+\):\d+;$"
CITATION_PATTERN = r"(\d{4};\d+\(\d+\):\d+;)"
ENGLISH_STOPWORDS = stopwordsiso.stopwords(["en"])


def preprocess_numbers(text: str, patterns=None, superscript_patterns=None):
    if any(
        re.fullmatch(pattern, text)
        for pattern in [
            ALPHANUMERIC_HYPHEN_PATTERN,
            BIBLIO_REF_PATTERN,
            COLON_SEPARATED_NUMBERS_PATTERN,
            CITATION_PATTERN,
        ]
    ):
        return text

    text = re.sub(ANY_TEXT_SPECIAL_CHAR_DIGIT_PATTERN, r"\1", text)

    if re.search(SUPERSCRIPT_PATTERN, text):
        return re.sub(SUPERSCRIPT_PATTERN, r"\1", text)

    if re.search(DATE_PATTERN, text):
        return text

    if any(char.isdigit() for char in text):
        return re.sub(r"(\d+)$", "", text)
    else:
        return re.sub(r"\d+", "", text)


def remove_accents(input_str):
    nfkd_form = unicodedata.normalize("NFKD", input_str)
    only_alpha = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    return only_alpha


def remove_trailing_numbers(text: str) -> str:
    return re.sub(r"(\b[A-Za-z]+)\d*[-:]?\d*\b", r"\1", text)


def apply_transformations(text: str, transformations: dict, rules: dict):
    for rule in rules:
        if not rules.get(rule, False):
            continue

        transform = transformations.get(rule)
        if transform is not None:
            text = transform(text)

    return text.strip()


def normalize_en_text(text, rules=None):
    if not text:
        return text

    transformations = OrderedDict(
        [
            (
                "ignore_document_numbers",
                lambda text: re.sub(DOC_NUMBER_PATTERN, "", text),
            ),
            ("preprocess_numbers", preprocess_numbers),
            ("lowercase_word", lambda text: text if text.istitle() else text.lower()),
            ("replace_hyphen", lambda text: text),
            ("normalize_unicode", lambda text: unicodedata.normalize("NFKD", text)),
            ("replace_unicode_apostrophe", lambda text: text.replace("\u2019", "'")),
            (
                "replace_unicode_quotes",
                lambda text: text.replace("\u201c", '"').replace("\u201d", '"'),
            ),
            ("remove_square_brackets", lambda text: re.sub(r"\[.*?\]", "", text)),
            ("replace_url_with_tag", lambda text: re.sub(r"http\S+|www.\S+", "", text)),
            ("remove_non_word_characters", lambda text: text.strip(string.punctuation)),
            (
                "replace_document_number_with_tag",
                lambda text: re.sub(r"pp-\w+-\d+", "", text, flags=re.IGNORECASE),
            ),
            ("remove_end_period", lambda text: text.rstrip(".")),
            ("remove_double_space", lambda text: re.sub(r"\s+", " ", text)),
            (
                "remove_english_stopwords",
                lambda text: " ".join(
                    word for word in text.split() if word not in ENGLISH_STOPWORDS
                ),
            ),
            ("remove_currency_symbols", lambda text: text.replace("\u20AC", "")),
            ("remove_en_dash", lambda text: text.replace("\u2013", "")),
            ("remove_unicode_accents", remove_accents),
            ("lower_text", lambda text: text.lower()),
            ("remove_extra_characters_and_digits", remove_extra_characters_and_digits),
        ]
    )

    if rules is None:
        rules = {name: True for name in transformations.keys()}

    return apply_transformations(text, transformations, rules)
