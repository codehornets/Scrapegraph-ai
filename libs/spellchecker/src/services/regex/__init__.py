import importlib

from libs.spellchecker.src.config.constants import (
    DEFAULT_IGNORED_PATTERNS,
    SUPPORTED_LANGUAGE_CODES,
)

LANG_TO_PATTERNS_MAP = {
    lang: importlib.import_module(f".languages.{lang}", "libs.spellchecker.src.services.regex").__dict__[
        f"{lang.upper()}_IGNORED_PATTERNS"
    ]
    for lang in SUPPORTED_LANGUAGE_CODES
}


# @functools.lru_cache(maxsize=None)
def get_ignore_patterns_for_language(language: str):
    return list(
        set(
            LANG_TO_PATTERNS_MAP.get(language.split("_")[0], [])
            + DEFAULT_IGNORED_PATTERNS
        )
    )
