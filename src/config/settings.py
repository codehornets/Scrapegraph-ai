import os
import queue
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
    FEATURE_FLAGS_SEGMENTATION,
    FULLCONTACT_API_KEY,
    GMAPS_SEARCH_QUERY_INTENT_MODIFIERS,
    GOOGLE_MAPS_API_KEY,
    GOOGLE_MAPS_DEFAULT_API_URL,
    GOOGLE_MAPS_STORAGE_DIR,
    GRAPH_CONFIG,
    INTENT_TERMS,
    KEYWORD_STORAGE_DIR,
    KEYWORD_INTENTS,
    LEADS_STORAGE_DIR,
    MARKETING_GOALS_FILE_PATH,
    MARKETING_STRATEGIES_FILE_PATH,
    OPENAI_API_KEY,
    OPENCORPORATES_API_KEYS,
    SEO_SUGGESTION_SERVICES,
    SPACY_MODEL_CACHE_PATH,
    SPELL_CHECK_CACHE_PATH,
    STOP_WORDS_CACHE_PATH,
    TOKENIZE_CACHE_PATH,
    TOPIC_CACHE_PATH,
    WHOISXML_API_KEY,
)

dotenv.load_dotenv()

os.makedirs(CACHE_DIR, exist_ok=True)
os.makedirs(KEYWORD_STORAGE_DIR, exist_ok=True)
os.makedirs(LEADS_STORAGE_DIR, exist_ok=True)

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


def log_kwargs(**kwargs):
    print(f"Function called with kwargs: {kwargs}")


def log_exception(exception: Exception):
    print(f"An exception occurred: {str(exception)}")


class EventQueue:
    def __init__(self):
        self.queue = queue.Queue()
        self.publish = "leads"


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
        self.event_queue = EventQueue()
        self.feature_flags_segmentation = FEATURE_FLAGS_SEGMENTATION
        self.fullcontact_api_key = FULLCONTACT_API_KEY
        self.gmaps_api_key = GOOGLE_MAPS_API_KEY
        self.gmaps_default_api_url = GOOGLE_MAPS_DEFAULT_API_URL
        self.gmaps_search_query_intent_modifiers = GMAPS_SEARCH_QUERY_INTENT_MODIFIERS
        self.intent_analysis_cache_path = self.cache_dir + "/intent_analysis"
        self.intents_keywords = INTENT_TERMS.keys()
        self.intent_descriptions = INTENT_TERMS.values()
        self.intent_classifier_weights = (0.4, 0.4, 0.2)
        self.intent_classifier_threshold = 0.015
        self.keyword_intents = KEYWORD_INTENTS
        self.keyword_relevance_threshold = 0.2
        self.keyword_storage_dir = KEYWORD_STORAGE_DIR
        self.leads_storage_dir = LEADS_STORAGE_DIR + "/"
        self.leads_responses_dir = LEADS_STORAGE_DIR + "/responses/"
        self.leads_queries_dir = LEADS_STORAGE_DIR + "/queries/"
        self.max_keywords = 1000
        self.marketing_goals_file_path = MARKETING_GOALS_FILE_PATH
        self.marketing_strategies_file_path = MARKETING_STRATEGIES_FILE_PATH
        self.openai = client
        self.opencorporates_api_key = OPENCORPORATES_API_KEYS
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
        self.whoisxml_api_key = WHOISXML_API_KEY

    def load_config(self) -> Dict[str, Any]:
        with open(self.config_file_path, "r") as file:
            config = yaml.safe_load(file)
        return config["keyword_intents"]
