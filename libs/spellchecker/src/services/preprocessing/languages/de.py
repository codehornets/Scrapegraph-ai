import re
import string
import unicodedata
from collections import OrderedDict

import stopwordsiso

from libs.spellchecker.src.utils.preprocessing import remove_extra_characters_and_digits


DATE_PATTERN = r"\b(\d{1,2}[-/]\d{1,2}[-/]\d{4}|\d{1,2}-[A-Za-z]{3}-\d{4}|GMT[+-]\d{4}|\d{2}:\d{2}:\d{2})\b"
SUPERSCRIPT_PATTERN = r"(\b[A-Za-z-]+[A-Za-z])(\d+(,\d+)*)\b"
ALPHANUMERIC_HYPHEN_PATTERN = r"[\da-zA-Z]+-[\d]+"
ANY_TEXT_SPECIAL_CHAR_DIGIT_PATTERN = r"(\b\w+)\W\d+\b"
DOC_NUMBER_PATTERN = r"[A-Z]{2}-[A-Z]{3}-[A-Z]{3}-\d{4}"
BIBLIO_REF_PATTERN = r"^\d{4};\d{1,3}\(\d{1,3}\):\d{1,3}\\u2013\d{1,3};$"
COLON_SEPARATED_NUMBERS_PATTERN = r"^\d{4};\d+\(\d+\):\d+;$"
CITATION_PATTERN = r"(\d{4};\d+\(\d+\):\d+;)"
GERMAN_STOPWORDS = stopwordsiso.stopwords(["de"])


def preprocess_numbers(text):
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


def apply_transformations(text, transformations, rules):
    for rule in rules:
        if not rules.get(rule, False):
            # Skip this rule if not selected
            continue

        transform = transformations.get(rule)
        if transform:
            # Apply the transformation if it exists
            text = transform(text)

    return text.strip()  # Remove leading/trailing whitespace


def normalize_de_text(text, rules=None):
    if not text:
        return text

    transformations = OrderedDict(
        [
            ("ignore_document_numbers", lambda t: re.sub(DOC_NUMBER_PATTERN, "", t)),
            ("preprocess_numbers", preprocess_numbers),
            ("lowercase_word", lambda t: t.lower()),
            ("normalize_unicode", lambda t: unicodedata.normalize("NFKD", t)),
            ("replace_unicode_apostrophe", lambda t: t.replace("\u2019", "'")),
            (
                "replace_unicode_quotes",
                lambda t: t.replace("\u201c", '"').replace("\u201d", '"'),
            ),
            ("remove_square_brackets", lambda t: re.sub(r"\[.*?\]", "", t)),
            ("replace_url_with_tag", lambda t: re.sub(r"http\S+|www.\S+", "", t)),
            ("remove_non_word_characters", lambda t: t.strip(string.punctuation)),
            ("remove_end_period", lambda t: t.rstrip(".")),
            ("remove_double_space", lambda t: re.sub(r"\s+", " ", t)),
            (
                "remove_german_stopwords",
                lambda t: " ".join(
                    word for word in t.split() if word not in GERMAN_STOPWORDS
                ),
            ),
            ("remove_currency_symbols", lambda t: t.replace("\u20AC", "")),
            ("remove_en_dash", lambda t: t.replace("\u2013", "")),
            ("remove_unicode_accents", lambda t: unicodedata.normalize("NFKD", t)),
            ("lower_text", lambda t: t.lower()),
            ("remove_extra_characters_and_digits", remove_extra_characters_and_digits),
        ]
    )

    if rules is None:
        rules = {name: True for name in transformations.keys()}

    return apply_transformations(text, transformations, rules)
