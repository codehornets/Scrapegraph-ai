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
SPANISH_STOPWORDS = stopwordsiso.stopwords(["es"])


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

    if superscript_patterns is None:
        superscript_patterns = [SUPERSCRIPT_PATTERN]
    if patterns is None:
        patterns = [DATE_PATTERN]

    # Firstly, process the date pattern
    if any(pattern and re.search(pattern, text) for pattern in patterns):
        return text

    # Now check and process the superscript patterns
    if any(pattern and re.search(pattern, text) for pattern in superscript_patterns):
        return re.sub(SUPERSCRIPT_PATTERN, r"\1", text)

    # Finally, process the rest numbers
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


def normalize_es_text(text, rules=None):
    if not text:
        return text

    transformations = OrderedDict(
        [
            (
                "ignore_document_numbers",
                lambda text: re.sub(DOC_NUMBER_PATTERN, "", text),
            ),
            ("preprocess_numbers", preprocess_numbers),
            ("replace_hyphen", lambda text: text),
            ("replace_unicode_apostrophe", lambda text: text.replace("\u2019", "'")),
            (
                "replace_unicode_quotes",
                lambda text: text.replace("\u201c", '"').replace("\u201d", '"'),
            ),
            ("replace_french_contractions", lambda text: re.sub(r"\b\w'+", "", text)),
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
                "remove_spanish_stopwords",
                lambda text: " ".join(
                    word for word in text.split() if word not in SPANISH_STOPWORDS
                ),
            ),
            ("normalize_unicode", lambda text: unicodedata.normalize("NFC", text)),
            ("remove_en_dash", lambda text: text.replace("\u2013", "")),
            (
                "add_space_after_currency",
                lambda text: text.replace("\u20ac.", "\u20ac ."),
            ),
            ("remove_currency_symbols", lambda text: text.replace("\u20AC", "")),
            ("lower_text", lambda text: text.lower()),
            ("remove_extra_characters_and_digits", remove_extra_characters_and_digits),
        ]
    )

    if rules is None:
        rules = {name: True for name in transformations.keys()}

    return apply_transformations(text, transformations, rules)
