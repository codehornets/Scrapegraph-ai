import os
from typing import Any, Dict

import dotenv
import yaml
import instructor
import stopwordsiso
from nltk.corpus import stopwords
from openai import OpenAI

from .constants import (
    BUSINESS_PROFILE_SUMMARY_CACHE_PATH,
    CACHE_DIR,
    CLEAN_TEXT_CACHE_PATH,
    GMAPS_SEARCH_QUERY_INTENT_MODIFIERS,
    GOOGLE_MAPS_API_KEY,
    GOOGLE_MAPS_DEFAULT_API_URL,
    GOOGLE_MAPS_STORAGE_DIR,
    GRAPH_CONFIG,
    INTENT_TERMS,
    KEYWORD_STORAGE_DIR,
    MARKETING_STRATEGIES_FILE_PATH,
    OPENAI_API_KEY,
    KEYWORD_INTENTS,
    SEO_SUGGESTION_SERVICES,
    SPACY_MODEL_CACHE_PATH,
    SPELL_CHECK_CACHE_PATH,
    STOP_WORDS_CACHE_PATH,
    TOKENIZE_CACHE_PATH,
    TOPIC_CACHE_PATH,
)

dotenv.load_dotenv()

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(KEYWORD_STORAGE_DIR, exist_ok=True)
os.makedirs(GOOGLE_MAPS_STORAGE_DIR, exist_ok=True)
os.makedirs(SPACY_MODEL_CACHE_PATH, exist_ok=True)
os.makedirs(STOP_WORDS_CACHE_PATH, exist_ok=True)
os.makedirs(CLEAN_TEXT_CACHE_PATH, exist_ok=True)
os.makedirs(SPELL_CHECK_CACHE_PATH, exist_ok=True)
os.makedirs(TOKENIZE_CACHE_PATH, exist_ok=True)
os.makedirs(TOPIC_CACHE_PATH, exist_ok=True)
os.makedirs(BUSINESS_PROFILE_SUMMARY_CACHE_PATH, exist_ok=True)

KEYWORD_PATH = os.path.join(KEYWORD_STORAGE_DIR, "keywords.pkl")
GMAPS_STORAGE_PATH = os.path.join(GOOGLE_MAPS_STORAGE_DIR, "gmaps")
SPACY_MODEL_PATH = os.path.join(SPACY_MODEL_CACHE_PATH, "spacy_model.pkl")
STOP_WORDS_PATH = os.path.join(STOP_WORDS_CACHE_PATH, "stop_words.pkl")
CLEAN_TEXT_PATH = os.path.join(CLEAN_TEXT_CACHE_PATH, "clean_text.pkl")
SPELL_CHECK_PATH = os.path.join(SPELL_CHECK_CACHE_PATH, "spell_check.pkl")
TOKENIZE_PATH = os.path.join(TOKENIZE_CACHE_PATH, "tokenize.pkl")
TOPIC_PATH = os.path.join(TOPIC_CACHE_PATH, "topic.pkl")
BUSINESS_PROFILE_SUMMARY_PATH = os.path.join(
    BUSINESS_PROFILE_SUMMARY_CACHE_PATH, "business_profile_summary.pkl"
)


# Define hook functions
def log_kwargs(**kwargs):
    print(f"Function called with kwargs: {kwargs}")


def log_exception(exception: Exception):
    print(f"An exception occurred: {str(exception)}")


class SettingService:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")

        client = instructor.from_openai(OpenAI(api_key=OPENAI_API_KEY))
        client.on("completion:kwargs", log_kwargs)
        client.on("completion:error", log_exception)

        self.business_profile_summary_cache_path = BUSINESS_PROFILE_SUMMARY_CACHE_PATH
        self.cache_dir = CACHE_DIR
        self.clean_text_cache_path = CLEAN_TEXT_CACHE_PATH
        self.intents_keywords = INTENT_TERMS.keys()
        self.intent_descriptions = INTENT_TERMS.values()
        self.intent_classifier_weights = (0.4, 0.4, 0.2)
        self.intent_classifier_threshold = 0.015
        self.gmaps_api_key = GOOGLE_MAPS_API_KEY
        self.gmaps_default_api_url = GOOGLE_MAPS_DEFAULT_API_URL
        self.gmaps_storage_dir = GOOGLE_MAPS_STORAGE_DIR + "/"
        self.gmaps_queries_dir = self.gmaps_storage_dir + "/queries/"
        self.gmaps_responses_dir = self.gmaps_storage_dir + "/responses/"
        self.gmaps_output_dir = self.gmaps_storage_dir + "/output/"
        self.gmaps_search_query_intent_modifiers = GMAPS_SEARCH_QUERY_INTENT_MODIFIERS
        self.intent_analysis_cache_path = self.cache_dir + "/intent_analysis"
        self.keyword_storage_dir = KEYWORD_STORAGE_DIR
        self.keyword_intents = KEYWORD_INTENTS
        self.keyword_relevance_threshold = 0.2
        self.max_keywords = 1000
        self.marketing_strategies_file_path = MARKETING_STRATEGIES_FILE_PATH
        self.openai = client
        self.preprocessed_text_dir = self.cache_dir + "/preprocessed_text"
        self.scrapegraphai_config = GRAPH_CONFIG
        self.serp_cache_dir = self.cache_dir + "/serp"
        self.seo_suggestion_services = SEO_SUGGESTION_SERVICES
        self.spacy_model_cache_path = SPACY_MODEL_CACHE_PATH
        self.spell_check_cache_path = SPELL_CHECK_CACHE_PATH
        self.stop_words_cache_path = STOP_WORDS_CACHE_PATH
        self.tokenize_cache_path = TOKENIZE_CACHE_PATH
        self.topic_cache_path = TOPIC_CACHE_PATH
        self.stop_words = set(stopwords.words("english")).union(
            stopwordsiso.stopwords("en")
        )

    def load_config(self) -> Dict[str, Any]:
        with open(self.config_file_path, "r") as file:
            config = yaml.safe_load(file)
        return config["keyword_intents"]
