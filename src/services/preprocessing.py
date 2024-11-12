import os
import re
import subprocess
from typing import List, Set
from functools import lru_cache

import nltk
import spacy
from termcolor import colored
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config.settings import SettingService
from src.services.caches import CacheService
from libs.spellchecker.src.services.spellcheck import SpellcheckService


class TextProcessor:
    def __init__(
        self,
        settings: SettingService,
        cache_service: CacheService,
        language: str = "en",
    ):
        self.setting_service = settings
        self.cache_service = cache_service
        self.language = language
        self.spellchecker = SpellcheckService()
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = self._initialize_stop_words()
        self.nlp = self._load_spacy_model()

    def _load_spacy_model(self, model_name="en_core_web_md"):
        cache_key = self.cache_service.generate_cache_key(
            f"{model_name}_{self.language}"
        )
        model = self.cache_service.load_from_cache(
            key=cache_key, cache_dir=self.setting_service.preprocessed_text_dir
        )
        if not model:
            try:
                import en_core_web_md

                model = en_core_web_md.load()
                self.cache_service.save_to_cache(
                    key=cache_key,
                    cache_dir=self.setting_service.preprocessed_text_dir,
                    data=model,
                )
            except Exception as e:
                print(f"\nDownloading spaCy model '{model_name}' - {e}\n")
                command = f"python -m spacy download {model_name}"
                subprocess.run(command, shell=True, check=True)

                # The environment variable is a workaround to ensure spaCy can locate the model
                # after installation without needing to restart the Python process
                model_path = spacy.util.get_package_path(model_name)
                os.environ["PYTHONPATH"] = (
                    str(model_path) + os.pathsep + os.environ.get("PYTHONPATH", "")
                )

                import en_core_web_md

                model = en_core_web_md.load()
                self.cache_service.save_to_cache(
                    key=cache_key,
                    cache_dir=self.setting_service.preprocessed_text_dir,
                    data=model,
                )
        return model

    def _initialize_stop_words(self) -> Set[str]:
        cache_key = self.cache_service.generate_cache_key(f"stop_words_{self.language}")
        stop_words = self.cache_service.load_from_cache(
            key=cache_key,
            cache_dir=self.setting_service.preprocessed_text_dir,
        )
        if not stop_words:
            stop_words = set(
                self.setting_service.stop_words
                if hasattr(self.setting_service, "stop_words")
                else set()
            )
            self.cache_service.save_to_cache(
                key=cache_key,
                cache_dir=self.setting_service.preprocessed_text_dir,
                data=stop_words,
            )
            custom_stops = {
                "thee",
                "thou",
                "thy",
                "ye",
                "computer",
                "gutenberg",
                "http",
                "chapter",
                "mr",
                "mrs",
                "ms",
                "dr",
            }
            stop_words = stop_words.union(custom_stops)
            self.cache_service.save_to_cache(
                key=cache_key,
                cache_dir=self.setting_service.preprocessed_text_dir,
                data=stop_words,
            )
        return stop_words

    @lru_cache(maxsize=128)
    def wordnet_pos_tags(self, treebank_tag):
        tag_map = {
            "J": wordnet.ADJ,
            "V": wordnet.VERB,
            "N": wordnet.NOUN,
            "R": wordnet.ADV,
        }
        return tag_map.get(treebank_tag[0], wordnet.NOUN)

    @lru_cache(maxsize=128)
    def process_text(self, text: str) -> dict:
        cleaned_text = self._clean_text(text)
        spelling_results = self._check_spelling(cleaned_text)
        tokens = self._tokenize_and_process(cleaned_text)

        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "spelling_results": spelling_results,
            "processed_tokens": tokens,
            "statistics": self._generate_statistics(tokens, spelling_results),
        }

    def process_text_batch(self, texts: List[str]) -> List[dict]:
        return [self.process_text(text) for text in texts]

    @lru_cache(maxsize=128)
    def _clean_text(self, text: str) -> str:
        cache_key = self.cache_service.generate_cache_key(f"clean_text_{text}")
        cleaned_text = self.cache_service.load_from_cache(
            key=cache_key,
            cache_dir=self.setting_service.preprocessed_text_dir,
        )
        if not cleaned_text:
            text = text.lower()

            # Remove multiple whitespace and linebreaks
            text = re.sub(r"\s+", " ", text)
            text = re.sub(r"\n", " ", text)

            # Remove special characters but keep apostrophes for contractions
            text = re.sub(r"[^a-zA-Z0-9\'\s]", " ", text)

            cleaned_text = text.strip()
            self.cache_service.save_to_cache(
                key=cache_key,
                cache_dir=self.setting_service.preprocessed_text_dir,
                data=cleaned_text,
            )
        return cleaned_text

    @lru_cache(maxsize=128)
    def _check_spelling(self, text: str) -> dict:
        cache_key = self.cache_service.generate_cache_key(f"spell_check_{text}")
        spelling_results = self.cache_service.load_from_cache(
            key=cache_key,
            cache_dir=self.setting_service.preprocessed_text_dir,
        )
        if not spelling_results:
            words = word_tokenize(text)
            misspelled_words = []
            corrections = {}

            for word in words:
                if not self._should_skip_spell_check(word):
                    spell_result = self.spellchecker.spell(word)
                    if spell_result.get("misspelled"):
                        misspelled_words.append(word)
                        if hasattr(self.spellchecker, "get_suggestions"):
                            corrections[word] = self.spellchecker.get_suggestions(word)

            spelling_results = {
                "misspelled_words": misspelled_words,
                "corrections": corrections,
                "total_words": len(words),
                "error_rate": len(misspelled_words) / len(words) if words else 0,
            }
            self.cache_service.save_to_cache(
                key=cache_key,
                cache_dir=self.setting_service.preprocessed_text_dir,
                data=spelling_results,
            )
        return spelling_results

    @lru_cache(maxsize=128)
    def _should_skip_spell_check(self, word: str) -> bool:
        return (
            word.lower() in self.stop_words
            or word.isnumeric()
            or len(word) <= 1
            or all(not c.isalnum() for c in word)
        )

    @lru_cache(maxsize=128)
    def _tokenize_and_process(self, text: str) -> List[str]:
        cache_key = self.cache_service.generate_cache_key(f"tokenize_{text}")
        lemmatized_tokens = self.cache_service.load_from_cache(
            key=cache_key,
            cache_dir=self.setting_service.preprocessed_text_dir,
        )
        if not lemmatized_tokens:
            doc = self.nlp(text)
            tokens = [
                token.text
                for token in doc
                if token.ent_type_ not in ("PERSON", "GPE", "LOC", "ORG", "DATE")
            ]

            tokens = word_tokenize(" ".join(tokens))
            filtered_tokens = [
                word
                for word in tokens
                if word.isalpha()
                and not re.match(r"^[ivxlcdm]+$", word)
                and word not in self.stop_words
            ]

            pos_tags = nltk.pos_tag(filtered_tokens)
            lemmatized_tokens = [
                self.lemmatizer.lemmatize(token, self.wordnet_pos_tags(pos_tag))
                for token, pos_tag in pos_tags
            ]

            lemmatized_tokens = self.cache_service.save_to_cache(
                key=cache_key,
                cache_dir=self.setting_service.preprocessed_text_dir,
                data=lemmatized_tokens,
            )
        return lemmatized_tokens

    def _generate_statistics(self, tokens: List[str], spelling_results: dict) -> dict:
        return {
            "token_count": len(tokens) if tokens else 0,
            "unique_tokens": len(set(tokens)) if tokens else 0,
            "spelling_errors": (
                len(spelling_results["misspelled_words"]) if spelling_results else 0
            ),
            "error_rate": spelling_results["error_rate"] if spelling_results else 0,
        }

    def iterate_txt_files(self, txt_dir: str) -> List[dict]:
        results = []
        for filename in os.listdir(txt_dir):
            if filename.endswith(".txt"):
                with open(
                    os.path.join(txt_dir, filename), "r", encoding="utf-8"
                ) as file:
                    text = file.read()
                    results.append(self.process_text(text))
        return results

    @staticmethod
    def download_nltk_data():
        nltk_data_dir = os.path.join(os.getcwd(), "storage", "downloads", "nltk_data")
        if not os.path.exists(nltk_data_dir):
            os.makedirs(nltk_data_dir)

        nltk.data.path.append(nltk_data_dir)
        try:
            nltk.data.find("tokenizers/punkt")
        except LookupError:
            print(colored("Downloading NLTK 'punkt' resource...", "cyan"))
            nltk.download("punkt", download_dir=nltk_data_dir)

        try:
            nltk.data.find("corpora/wordnet")
        except LookupError:
            print(colored("Downloading NLTK 'wordnet' resource...", "cyan"))
            nltk.download("wordnet", download_dir=nltk_data_dir)

        try:
            nltk.data.find("corpora/stopwords")
        except LookupError:
            print(colored("Downloading NLTK 'stopwords' resource...", "cyan"))
            nltk.download("stopwords", download_dir=nltk_data_dir)

        try:
            nltk.data.find("corpora/gutenberg")
        except LookupError:
            print(colored("Downloading NLTK 'gutenberg' resource...", "cyan"))
            nltk.download("gutenberg", download_dir=nltk_data_dir)

        try:
            nltk.data.find("corpora/averaged_perceptron_tagger_eng")
        except LookupError:
            print(
                colored(
                    "Downloading NLTK 'averaged_perceptron_tagger_eng' resource...",
                    "cyan",
                )
            )
            nltk.download("averaged_perceptron_tagger_eng", download_dir=nltk_data_dir)

    def extract_keywords_from_topics(self, topics: List[str]) -> List[str]:
        cache_key = self.cache_service.generate_cache_key(
            f"extract_keywords_from_topics_{topics}"
        )
        keywords = self.cache_service.load_from_cache(
            key=cache_key,
            cache_dir=self.setting_service.preprocessed_text_dir,
        )
        if not keywords:
            keyword_pattern = re.compile(r"\"(.*?)\"")
            keywords = {
                match.group(1)
                for topic in topics
                for match in keyword_pattern.finditer(topic)
            }
            self.cache_service.save_to_cache(
                key=cache_key,
                cache_dir=self.setting_service.preprocessed_text_dir,
                data=keywords,
            )
        return list(keywords)

    def summarize_business_profile(
        self, business_profile: dict, threshold=0.03
    ) -> dict:
        cache_key = self.cache_service.generate_cache_key(
            f"summarize_business_profile_{business_profile}"
        )
        summary = self.cache_service.load_from_cache(
            key=cache_key,
            cache_dir=self.setting_service.preprocessed_text_dir,
        )
        summary = None
        if not summary:
            company_name = business_profile.get("name")
            industry = business_profile.get("industry")
            location = (
                business_profile.get("headquarter").get("country", "us").lower().strip()
            )

            # Handle the 'specialties' field (which could be a list of strings or list of dictionaries)
            specialties = business_profile.get("specialties", [])
            if isinstance(specialties, list):
                specialties = [
                    (
                        item["fields"]
                        if isinstance(item, dict) and "fields" in item
                        else item
                    )
                    for item in specialties
                ]
                specialties = [
                    specialty
                    for sublist in specialties
                    for specialty in (
                        sublist if isinstance(sublist, list) else [sublist]
                    )
                ]
            else:
                specialties = []
            products = [
                product["name"]
                for product in business_profile.get("products_and_services", [])
            ]

            # Handle the 'about' field (which could be a list of dicts or string)
            about = business_profile.get("about", "")
            if isinstance(about, list):
                about = " ".join(
                    [
                        (
                            item["description"]
                            if isinstance(item, dict) and "description" in item
                            else str(item)
                        )
                        for item in about
                    ]
                )
            elif not isinstance(about, str):
                about = ""

            # Calculate similarity scores between products and the "about" text
            relevant_products, vectorizer = [], TfidfVectorizer()
            for product in products:
                combined_texts = [product, about]
                tfidf_matrix = vectorizer.fit_transform(combined_texts)
                similarity_score = cosine_similarity(
                    tfidf_matrix[:1], tfidf_matrix[1:2]
                )

                if similarity_score >= threshold:
                    relevant_products.append(product)
                else:
                    print(
                        colored(
                            f"Excluding external product: {product} (similarity: {similarity_score[0][0]:.2f})",
                            "yellow",
                        )
                    )

            if not relevant_products:
                print("No relevant products found based on the 'about' text.")
                return {
                    "name": company_name,
                    "industry": industry,
                    "location": location,
                    "competitors": [],
                    "keyword_analysis": None,
                }

            seed_keywords = specialties + relevant_products

            summary = {
                "name": company_name,
                "industry": industry,
                "location": location,
                "specialties": specialties,
                "relevant_products": relevant_products,
                "description": about,
                "seed_keywords": seed_keywords,
            }
            self.cache_service.save_to_cache(
                key=cache_key,
                cache_dir=self.setting_service.preprocessed_text_dir,
                data=summary,
            )
        return summary
