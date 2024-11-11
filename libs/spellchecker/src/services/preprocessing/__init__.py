import importlib
import re

from libs.spellchecker.src.config.constants import (
    PATTERNS_LIST,
    SUPPORTED_LANGUAGE_CODES,
    URL_PARTS,
)


NORMALIZE_FUNC_MAP = {
    lang: importlib.import_module(
        f".languages.{lang}", "libs.spellchecker.src.services.preprocessing"
    ).__dict__[f"normalize_{lang}_text"]
    for lang in SUPPORTED_LANGUAGE_CODES
}
COMBINED_PATTERN = re.compile("|".join(PATTERNS_LIST))


def remove_extra_characters(s):
    return re.sub(r"(?<!\w)\W|\W(?!\w)", "", s)


def normalize_text_for_language(language: str, text: str) -> str:
    base_lang = language.split("_")[0]
    if base_lang not in NORMALIZE_FUNC_MAP:
        raise ValueError(f"Unsupported language: {language}")

    if (
        text.split()[0].endswith("\xad")
        or any(part in text for part in URL_PARTS)
        or len(max(text.split(" "), key=len)) > 30
    ):
        return text

    if COMBINED_PATTERN.search(text):
        return ""

    return NORMALIZE_FUNC_MAP[base_lang](text)
