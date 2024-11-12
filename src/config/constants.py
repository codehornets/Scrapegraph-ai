import os

import dotenv


dotenv.load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./outreach360.db")

FEATURE_FLAG_USE_ADVERTOOLS = os.getenv("FEATURE_FLAG_USE_ADVERTOOLS", False)

MARKETING_STRATEGIES_FILE_PATH = os.getenv(
    "MARKETING_STRATEGIES_FILE_PATH", "marketing_strategies.yml"
)

OUTPUT_FOLDER_PATH = os.getenv("OUTPUT_FOLDER_PATH", "storage/data")

OLLAMA_GRAPH_CONFIG = {
    "llm": {
        "model": "ollama/mistral",
        "temperature": 1,
        "format": "json",  # Ollama needs the format to be specified explicitly
        "model_tokens": 2000,  #  depending on the model set context length
        "base_url": "http://localhost:11434",  # set ollama URL of the local host (YOU CAN CHANGE IT, if you have a different endpoint
    },
    "embeddings": {
        "model": "ollama/nomic-embed-text",
        "temperature": 0,
        "base_url": "http://localhost:11434",  # set ollama URL
    },
}

NAVBAR_CLASSES = ["navbar", "nav", "header", "top-bar"]
FOOTER_CLASSES = ["footer", "bottom-bar", "site-footer"]

MAIN_PAGES_TO_DISCOVER = [
    "about",
    "contact",
    "team",
    "services",
    "products",
    "blog",
    "newsletters",
]
RELEVANT_SITEMAP_KEYWORDS = ["product", "newsletters", "blog"]
EXCLUDE_SITEMAP_KEYWORDS = [
    "users",
    "jobs",
    "discussions",
    "posts",
    "collections",
    "topics",
    "reviews",
    "news",
    "events",
    "press",
    "careers",
    "community",
    "support",
    "faq",
    "privacy",
    "terms",
]

INVALID_TERMS = [
    "’",
    "'s",
    "the",
    "...",
    "and",
    "ack",
]

INTENT_TERMS = {
    "Commercial": [
        "buy",
        "purchase",
        "price",
        "deal",
        "offer",
        "best",
        "top",
        "compare",
        "review",
        "vs",
        "comparison",
        "versus",
        "guide",
        "ultimate",
    ],
    "Informational": [
        "guide",
        "tutorial",
        "information",
        "details",
        "learn",
        "what is",
        "how to",
        "introduction",
        "basics",
        "what is the best",
        "what",
        "who",
        "when",
        "where",
        "which",
        "why",
        "how",
    ],
    "Navigational": [
        "location",
        "near",
        "find",
        "where",
        "official site",
        "home page",
        "profile",
    ],
    "Transactional": [
        "order",
        "subscribe",
        "checkout",
        "get",
        "buy",
        "purchase",
        "price",
        "shop",
        "best price",
        "lowest price",
        "lowest price",
        "best price",
        "cheapest",
        "discount",
        "deals",
        "coupon",
        "promo",
        "promotion",
        "special",
        "sale",
    ],
    "Local": [
        "near",
        "find",
        "location",
        "local",
        "nearby",
        "near me",
        "restaurant",
        "shop",
    ],
}

INTENT_DESCRIPTIONS = {
    "Commercial": "Content focused on pricing, buying, deals, and subscription options.",
    "Informational": "Content that provides guidance, tutorials, information, and insights.",
    "Navigational": "Content that directs users to specific resources, locations, or websites.",
    "Transactional": "Content focused on actions like ordering, subscribing, signing up, or downloading.",
    "Local": "Content related to local services, places, or 'near me' searches.",
}

KEYWORD_INTENTS = [
    {
        "intent": "Transactional",
        "description": "Content focused on actions like ordering, subscribing, signing up, or downloading.",
        "example": "Sign up for our newsletter to receive the latest updates.",
        "items": ["order", "subscribe", "checkout", "get"],
    },
    {
        "intent": "Navigational",
        "description": "Content that directs users to specific resources, locations, or websites.",
        "example": "Find the nearest location of our business.",
        "items": ["location", "near", "find", "where"],
    },
    {
        "intent": "Commercial",
        "description": "Content focused on pricing, buying, deals, and subscription options.",
        "example": "We are offering a 20% discount on our digital marketing services.",
        "items": ["buy", "purchase", "price", "deal", "offer"],
    },
    {
        "intent": "Informational",
        "description": "Content that provides guidance, tutorials, information, and insights.",
        "example": "Learn how to optimize your website for local SEO.",
        "items": ["guide", "tutorial", "information", "details", "learn"],
    },
    # {
    #     "intent": "Local business",
    #     "description": "Content focused on local businesses, products, and services.",
    #     "example": "Find the best local restaurants in the area.",
    #     "items": ["local", "nearby", "near me", "restaurant", "shop"],
    # },
]

ALL_KEYWORDS_BY_INTENT = {
    "Commercial": [],
    "Informational": [],
    "Transactional": [],
    "Navigational": [],
    "Local": [],
}

KEYWORD_STORAGE_DIR = os.path.join(os.getcwd(), "storage", "keywords")
CACHE_DIR = os.path.join(os.getcwd(), "storage", "cache")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GRAPH_CONFIG = {
    "llm": {
        "api_key": OPENAI_API_KEY,
        "model": "openai/gpt-4o-mini",
    },
    "verbose": True,
    "headless": False,
}


SEO_SUGGESTION_SERVICES = {
    "amazon": "//completion.amazon.co.uk/search/complete?method=completion&search-alias=aps&mkt=3&callback=?&q=",
    "baidu": "//suggestion.baidu.com/su?cb=?&wd=",
    "bing": "//api.bing.com/osjson.aspx?JsonType=callback&JsonCallback=?&query=",
    "ebay": "//autosug.ebay.com/autosug?_jgr=1&sId=0&_ch=0&callback=?&kwd=",
    "google": "//suggestqueries.google.com/complete/search?client=chrome&q=",
    "google_firefox": "http://suggestqueries.google.com/complete/search?output=firefox&q=",
    "google_news": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=n&gl=${country}&callback=?&q=",
    "google_shopping": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=sh&gl=${country}&callback=?&q=",
    "google_books": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=bo&gl=${country}&callback=?&q=",
    "google_play": "//market.android.com/suggest/SuggRequest?json=1&c=0&hl=${lang}&gl=${country}&callback=?&query=",
    "google_play_apps": "//market.android.com/suggest/SuggRequest?json=1&c=3&hl=${lang}&gl=${country}&callback=?&query=",
    "google_play_movies": "//market.android.com/suggest/SuggRequest?json=1&c=4&hl=${lang}&gl=${country}&callback=?&query=",
    "google_play_books": "//market.android.com/suggest/SuggRequest?json=1&c=1&hl=${lang}&gl=${country}&callback=?&query=",
    "google_videos": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=v&gl=${country}&callback=?&q=",
    "google_images": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=i&gl=${country}&callback=?&q=",
    "twitter": "//twitter.com/i/search/typeahead.json?count=30&result_type=topics&src=SEARCH_BOX&callback=?&q=",
    "yahoo": "//search.yahoo.com/sugg/ff?output=jsonp&appid=ffd&callback=?&command=",
    "yandex": "//yandex.com/suggest/suggest-ya.cgi?callback=?&q=?&n=30&v=4&uil={lang}&part=",
    "youtube": "//suggestqueries.google.com/complete/search?client=chrome&hl=${lang}&ds=yt&gl=${country}&callback=?&q=",
}

GOOGLE_MAPS_DEFAULT_API_URL = "http://127.0.0.1:8000"
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
GOOGLE_MAPS_STORAGE_DIR = os.path.join(os.getcwd(), "storage", "gmaps")
SPACY_MODEL_CACHE_PATH = os.path.join(os.getcwd(), "storage", "spacy", "spacy_model")
STOP_WORDS_CACHE_PATH = os.path.join(os.getcwd(), "storage", "spacy", "stop_words")
CLEAN_TEXT_CACHE_PATH = os.path.join(os.getcwd(), "storage", "spacy", "clean_text")
TOKENIZE_CACHE_PATH = os.path.join(os.getcwd(), "storage", "spacy", "tokenize")
SPELL_CHECK_CACHE_PATH = os.path.join(os.getcwd(), "storage", "spacy", "spell_check")
TOPIC_CACHE_PATH = os.path.join(os.getcwd(), "storage", "spacy", "topic")
BUSINESS_PROFILE_SUMMARY_CACHE_PATH = os.path.join(
    os.getcwd(), "storage", "spacy", "business_profile_summary"
)
LEADS_STORAGE_DIR = os.path.join(os.getcwd(), "storage", "leads")
LEADS_RESPONSES_DIR = os.path.join(os.getcwd(), "storage", "leads", "responses")

GMAPS_SEARCH_QUERY_INTENT_MODIFIERS = {
    "informational": ["top-rated", "best", "recommended", "popular", "highly reviewed"],
    "commercial": [
        "affordable",
        "top services",
        "trusted",
        "highly rated",
        "reputable",
    ],
    "transactional": [
        "open now",
        "book now",
        "available nearby",
        "order from",
        "visit",
    ],
    "navigational": [
        "near me",
        "closest",
        "directions to",
        "nearby locations",
        "find nearby",
    ],
}
