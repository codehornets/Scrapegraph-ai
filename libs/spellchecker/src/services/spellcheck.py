import json
import logging
import re
import string

import validators
from fitz import Page

from libs.spellchecker.src.config.settings import Settings
from libs.spellchecker.src.services.file import FileService
from libs.spellchecker.src.services.preprocessing import (
    normalize_text_for_language,
    remove_extra_characters,
)
from libs.spellchecker.src.services.regex import get_ignore_patterns_for_language
from libs.spellchecker.src.services.storage import StorageService
from libs.spellchecker.src.utils.file import (
    load_hunspell_dictionary,
    load_spylls_dictionary_path,
)
from libs.spellchecker.src.utils.shape import Rect


class SpellcheckService:
    _dictionaries = {}

    def __init__(
        self,
        language="en_US",
        pdf_temporary_url=None,
        custom_dictionary_url=None,
        settings=None,
    ):
        self.settings = settings or Settings()
        if language not in self.settings.supported_languages:
            raise ValueError(f"Unsupported language: {language}")

        self.language = language
        self.storage_service = StorageService(self.settings)
        self.file_service = FileService(self.settings)
        self.pdf_document = (
            self.storage_service.get_pdf_file(pdf_temporary_url)
            if pdf_temporary_url
            else None
        )

        self.custom_dictionary = self._load_custom_dictionary(custom_dictionary_url)
        self.initialize_spellchecker_for_language(language)

        # Caches
        self.correct_words_cache = set()
        self.incorrect_words_cache = set()
        self.ordinal_numbers_regex = re.compile(self.settings.ordinal_numbers_regex)
        self.pp_pattern = re.compile(r"pp-\w+-\w+-\d+")

    def _load_custom_dictionary(self, custom_dictionary_url):
        custom_words = set(
            self.storage_service.get_dictionary_words(custom_dictionary_url)
        )
        return {word.lower() for word in custom_words}.union(
            {word.upper() for word in custom_words}
        )

    def initialize_spellchecker_for_language(self, lang):
        if lang not in self._dictionaries:
            try:
                from hunspell import HunSpell

                dic_path, aff_path = load_hunspell_dictionary(self.settings, lang)
                hunspell_checker = HunSpell(dic_path, aff_path)
                for word in self.custom_dictionary:
                    hunspell_checker.add(word)
                self._dictionaries[lang] = {
                    "spellchecker": hunspell_checker,
                    "type": "hunspell",
                }
            except ImportError:
                self._fallback_spellchecker(lang)

        self.spellchecker = self._dictionaries[lang]["spellchecker"]

    def _fallback_spellchecker(self, lang):
        try:
            from spylls.hunspell import Dictionary

            dic_path = load_spylls_dictionary_path(self.settings, lang)
            spylls_checker = Dictionary.from_files(dic_path)
            self._dictionaries[lang] = {
                "spellchecker": spylls_checker,
                "type": "spylls",
            }
        except ImportError:
            from spellchecker import SpellChecker

            pyspellchecker = SpellChecker()
            self._dictionaries[lang] = {
                "spellchecker": pyspellchecker,
                "type": "pyspellchecker",
            }

    def get_spelling_errors(self):
        if self.pdf_document:
            return self._spellcheck_pdf()
        else:
            raise ValueError(
                "No PDF document available. Use `spellcheck_corpus` for text inputs."
            )

    def spellcheck_corpus(self, corpus):
        """Process and spellcheck the provided text corpus."""
        matches, total_words = [], 0
        ignored_patterns = get_ignore_patterns_for_language(self.language)

        for line in corpus:
            line_words = line.split()
            total_words += len(line_words)
            matches.extend(
                [
                    self._process_word(word, page=None, coordinates=None)
                    for word in line_words
                    if self._should_check_word(word, ignored_patterns)
                ]
            )

        self._finalize_output(matches)
        return matches, total_words

    def _spellcheck_pdf(self):
        matches, total_words = [], 0
        for page in self.pdf_document:
            try:
                page_matches, page_word_count = self.process_spellcheck_page(page)
                matches.extend(page_matches)
                total_words += page_word_count
            except Exception as e:
                logging.error(
                    f"Error processing page {page.number}: {e}", exc_info=True
                )
                continue
        self._finalize_output(matches)
        return matches, total_words

    def process_spellcheck_page(self, page: Page):
        ignored_patterns = get_ignore_patterns_for_language(self.language)
        words = page.get_text("words")
        matches = [
            self._process_word(
                word_info[4],
                page,
                (word_info[0], word_info[1], word_info[2], word_info[3]),
            )
            for word_info in words
            if self._should_check_word(word_info[4], ignored_patterns)
        ]
        return [match for match in matches if match], len(words)

    def _process_word(self, word, page=None, coordinates=None):
        if self._is_word_correct(word):
            return None

        preprocessed_word = normalize_text_for_language(self.language, word)
        if not self._validate_word(preprocessed_word):
            return None

        misspelled = self.spell(preprocessed_word).get("misspelled")
        return (
            {
                "value": remove_extra_characters(word),
                "misspelled": misspelled,
                "page": page.number + 1 if page else "N/A",
                "coordinates": Rect(coords=coordinates) if coordinates else None,
                "data": {
                    "language": self.language,
                    "preprocessed_text": preprocessed_word,
                },
            }
            if misspelled
            else None
        )

    def _is_word_correct(self, word):
        if word in self.correct_words_cache:
            return True
        elif word in self.incorrect_words_cache:
            return False

        checker_type = self._dictionaries[self.language]["type"]
        spellchecker = self._dictionaries[self.language]["spellchecker"]

        if checker_type == "hunspell" and spellchecker.spell(word):
            self.correct_words_cache.add(word)
            return True
        elif checker_type == "spylls" and spellchecker.lookup(word):
            self.correct_words_cache.add(word)
            return True
        elif checker_type == "pyspellchecker" and word not in spellchecker.unknown(
            [word]
        ):
            self.correct_words_cache.add(word)
            return True

        self.incorrect_words_cache.add(word)
        return False

    def _should_check_word(self, word, ignored_patterns):
        if validators.url(word) or word.lower() in ignored_patterns:
            return False
        return word not in self.settings.ignore_unicode_list

    def _validate_word(self, word):
        is_symbol = all(char in string.punctuation for char in word)
        return not (
            is_symbol
            or word in self.settings.symbols_to_skip
            or self._is_greek_letter_or_path(word)
        )

    def _is_greek_letter_or_path(self, word):
        return bool(re.search(r"[\u0370-\u03FF\u1F00-\u1FFF]", word)) or bool(
            re.search(r"(\/|\\)[\w\/\.-]+", word)
        )

    def spell(self, word):
        if self._is_word_correct(word):
            return {"text": word, "language": self.language, "misspelled": []}
        return {"text": word, "language": self.language, "misspelled": [word]}

    def _finalize_output(self, matches):
        with open(self.settings.report_file_path, "w") as f:
            json.dump(matches, f)
        self.file_service.delete_directory(self.settings.cache_directory)
