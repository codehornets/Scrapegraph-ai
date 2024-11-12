import os
from typing import Dict, List

import advertools
import dotenv
import pandas as pd
from termcolor import colored

from src.config.settings import SettingService
from src.services.keywords.classifier import IntentClassifier
from src.services.caches import CacheService
from src.services.preprocessing import TextProcessor

dotenv.load_dotenv()


class SerpService:
    def __init__(self, settings: SettingService, cache_service: CacheService):
        self.settings = settings
        self.cache_service = cache_service
        self.text_processor = TextProcessor(
            settings=self.settings, cache_service=self.cache_service
        )
        self.classifier = IntentClassifier(settings=self.settings)
        self.text_processor.download_nltk_data()

    def analyze_search_intents(
        self, keywords: List[str], locations: List[str]
    ) -> Dict[str, Dict[str, Dict[str, List[str]]]]:
        search_intents = {}

        serp_rankings = self.fetch_serp_rankings(keywords, locations)
        for keyword, serp_data in serp_rankings.items():
            if isinstance(serp_data, pd.DataFrame) and not serp_data.empty:
                search_intents[keyword] = self.process_user_intents(serp_data)
            else:
                print(colored(f"No SERP data found for keyword '{keyword}'", "yellow"))

        return search_intents

    def fetch_serp_rankings(self, keywords, locations=None):
        # sourcery skip: low-code-quality
        if locations is None:
            locations = ["us", "ca"]

        all_cached_data = {}
        uncached_keywords = []

        for keyword in keywords:
            cache_key = self.cache_service.generate_cache_key(f"{keyword}_{locations}")
            if cached_data := self.cache_service.load_from_cache(
                key=cache_key, cache_dir=self.settings.serp_cache_dir
            ):
                print(
                    colored(
                        f"--- Loading cached results for keyword: {keyword} for {locations} on desktop ---",
                        "green",
                    )
                )
                all_cached_data[keyword] = pd.DataFrame(cached_data)
            else:
                uncached_keywords.append(keyword)

        if uncached_keywords:
            print(
                colored(
                    f"\nNo cached data found, fetching SERP ranking for location: {locations}",
                    "cyan",
                )
            )

            serp_rankings = advertools.serp_goog(
                q=uncached_keywords,
                gl=locations,
                cx=os.getenv("GOOGLE_SEARCH_ENGINE_ID"),
                key=os.getenv("GOOGLE_API_KEY"),
            )

            if serp_rankings is not None and not serp_rankings.empty:
                if "searchTerms" not in serp_rankings.columns:
                    print(
                        colored(
                            "The 'searchTerms' column is missing in the SERP rankings data.",
                            "red",
                        )
                    )
                    print(f"SERP Rankings Columns: {serp_rankings.columns}")
                    return {}

                for keyword in uncached_keywords:
                    keyword_rankings = serp_rankings[
                        serp_rankings["searchTerms"] == keyword
                    ]
                    if not keyword_rankings.empty:
                        keyword_json = keyword_rankings.to_dict(orient="records")
                        keyword_json = [
                            {
                                k: (v.isoformat() if isinstance(v, pd.Timestamp) else v)
                                for k, v in entry.items()
                            }
                            for entry in keyword_json
                        ]

                        self.cache_service.save_to_cache(
                            key=cache_key,
                            cache_dir=self.settings.serp_cache_dir,
                            data=keyword_json,
                        )
                        keyword_rankings.to_csv(
                            f"{os.path.join(self.settings.keyword_storage_dir, f'{keyword}.csv')}",
                            index=False,
                        )

                        all_cached_data[keyword] = keyword_rankings
                    else:
                        print(
                            colored(f"No data found for keyword: {keyword}", "yellow")
                        )

            else:
                print(
                    colored(
                        "Failed to retrieve SERP data for the provided keywords", "red"
                    )
                )

        return all_cached_data

    def process_user_intents(
        self,
        serp_data: pd.DataFrame,
    ) -> Dict[str, Dict[str, Dict[str, List[str]]]]:

        if not isinstance(serp_data, pd.DataFrame) or serp_data.empty:
            return {"global_intents": {}, "competitor_intents": {}}

        if "rank" in serp_data.columns:
            serp_data = serp_data.sort_values(by="rank")

        corpus = [
            f"{row['title']} {row['snippet']}"
            for _, row in serp_data.iterrows()
            if "title" in row and "snippet" in row
        ]
        tokenized_corpus = self.text_processor.process_text_batch(corpus)

        corpus_string = ""
        for item in tokenized_corpus:
            # corpus_string += " ".join(item.get("processed_tokens", [])) + " "
            corpus_string += " ".join(item.get("cleaned_text").split())

        corpus_intent, corpus_keywords = self.classifier.analyze_intent(corpus_string)

        competitor_intents = {}
        all_competitor_keywords = []
        for index, row in serp_data.iterrows():
            if "title" in row and "snippet" in row:
                competitor_corpus = f"{row['title']} {row['snippet']}"
                competitor_tokenized_corpus = self.text_processor.process_text(
                    competitor_corpus
                )
                competitor_string_corpus = " ".join(
                    competitor_tokenized_corpus.get("cleaned_text", []).split()
                )
                competitor_intent, competitor_keywords = self.classifier.analyze_intent(
                    competitor_string_corpus
                )

                all_competitor_keywords.extend(
                    [{competitor_intent: competitor_keywords}]
                )
                competitor_keywords = self.extract_and_rank_keywords(
                    [all_competitor_keywords]
                )
                competitor_intents[row.get("displayLink", f"Competitor_{index}")] = {
                    "competitor_corpus": competitor_string_corpus,
                    "competitor_intent": competitor_intent,
                    "competitor_keywords": competitor_keywords,
                }

        return [
            {
                "analysis": {
                    "corpus": corpus_string,
                    "corpus_intent": corpus_intent,
                    "corpus_keywords": corpus_keywords,
                    "competitor_corpus_keywords": self.extract_and_rank_keywords(
                        [all_competitor_keywords]
                    ),
                },
                "details": competitor_intents,
            }
        ]

    def extract_and_rank_keywords(self, keywords_with_scores, top_n=None):
        keyword_dict = {}

        flattened_keywords = self.flatten_keywords(keywords_with_scores)

        # Populate keyword_dict with the highest score for each keyword
        for keyword, intent, score in flattened_keywords:
            if isinstance(keyword, str) and isinstance(score, (int, float)):
                # Store as a tuple (intent, score) only if the score is higher
                if keyword not in keyword_dict or score > keyword_dict[keyword][1]:
                    keyword_dict[keyword] = (intent, score)

        # Sort keywords by score in descending order and include intent in the output
        ranked_keywords = sorted(
            [
                (kw, intent_score[0], intent_score[1])
                for kw, intent_score in keyword_dict.items()
            ],
            key=lambda x: x[2],
            reverse=True,
        )

        return ranked_keywords[:top_n] if top_n else ranked_keywords

    @staticmethod
    def flatten_keywords(keywords_with_scores):
        flattened_keywords = []
        for outer_list in keywords_with_scores:
            for intent_dict in outer_list:
                for intent, keywords in intent_dict.items():
                    for keyword, score in keywords:
                        flattened_keywords.append((keyword, intent, score))
        return flattened_keywords
