import json
import os
from typing import Any, Dict, List, Tuple

import dotenv
import pandas as pd
import requests
from termcolor import colored

from src.config.settings import SettingService
from src.services.caches import CacheService
from src.services.keywords.researcher import SeoKeywordResearch
from src.services.keywords.serp import SerpService
from src.services.sanitizers import TextSanitizerService

dotenv.load_dotenv()


class KeywordService:
    def __init__(
        self,
        business_profile: Dict[str, Any],
        setting_service: SettingService,
        cache_service: CacheService,
    ):
        self.competitor_keywords_limit = 2
        self.business_profile = business_profile
        self.setting_service = setting_service
        self.cache_service = cache_service

        self.text_sanitizer_service = TextSanitizerService(
            settings=self.setting_service, cache_service=self.cache_service
        )
        self.serp_service = SerpService(
            settings=self.setting_service, cache_service=self.cache_service
        )
        self.researcher = SeoKeywordResearch(
            settings=self.setting_service, api_key=os.getenv("SERP_API_KEY")
        )

    def generate_seo_keywords(
        self,
    ) -> Dict[str, Dict[str, List[str]]]:
        serp_analysis = None  # TODO: add cache
        if not serp_analysis:
            serp_analysis, company_name, industry, locations, seed_keywords = (
                self.extract_competitors_keywords()
            )

        validated_queries = []
        processed_count = 0

        for keyword, analysis in serp_analysis.items():
            print(colored(f"\nProcessing keyword: {keyword}", "cyan"))

            # Filtering competitor keywords based on KPIs
            for _, details in analysis[0].items():
                competitor_keywords = details.get("competitor_corpus_keywords", [])
                for competitor_keyword, intent, weight in competitor_keywords:
                    if weight >= self.setting_service.keyword_relevance_threshold:
                        suggestions = self.suggest_queries_for_keyword(
                            competitor_keyword
                        )
                        another_suggestion = self.researcher.process_query(
                            competitor_keyword
                        )
                        related_questions = another_suggestion.get(
                            "related_questions", []
                        )
                        intent_questions = self.serp_service.classifier.analyze_intent(
                            related_questions
                        )

                        merged_keywords = []

                        # Step 2: Merge suggestions
                        for suggestion in suggestions:
                            if isinstance(suggestion, tuple):
                                _, suggestion_text = suggestion
                                merged_keywords.append(
                                    {
                                        "text": suggestion_text,
                                        "intent": intent,
                                        "weight": weight,
                                    }
                                )
                            elif isinstance(suggestion, str):
                                merged_keywords.append(
                                    {
                                        "text": suggestion,
                                        "intent": intent,
                                        "weight": weight,
                                    }
                                )

                        # Step 3: Unpack and merge intent questions
                        intent_type, question_score_list = intent_questions
                        for question_data in question_score_list:
                            for question, score in question_data:
                                merged_keywords.append(
                                    {
                                        "text": question,
                                        "intent": intent_type,
                                        "weight": score,
                                    }
                                )

                        validated_queries.extend(
                            self.validate_suggested_queries(
                                self.extract_and_rank_keywords(merged_keywords)
                            )
                        )

                        # Increment the counter and check if the limit is reached
                        processed_count += 1
                        if processed_count >= self.competitor_keywords_limit:
                            print(
                                colored(
                                    f"\nLimit of {self.competitor_keywords_limit} competitor keywords reached.",
                                    "red",
                                )
                            )
                            # return self.clean_and_save_keywords(
                            #     validated_queries, keyword
                            # )
                            return (
                                validated_queries,
                                locations,
                                industry,
                                company_name,
                                seed_keywords,
                            )

            # return self.clean_and_save_keywords(validated_queries, keyword)
            return validated_queries, locations, industry, company_name, seed_keywords

    def extract_and_rank_keywords(
        self, merged_keywords: List[Dict[str, Any]], top_n=None
    ) -> List[Tuple[str, str, float]]:
        keyword_dict = {}

        # Populate keyword_dict with the highest score for each keyword
        for item in merged_keywords:
            keyword = item["text"]
            intent = item["intent"]
            score = item.get("weight", 0)  # Use 0 if no weight is provided

            # Filter out one-word keywords
            if (
                len(keyword.split()) > 1
            ):  # Only process if the keyword has more than one word
                # Store as a tuple (intent, score) only if the score is higher
                if isinstance(keyword, str) and isinstance(score, (int, float)):
                    if keyword not in keyword_dict or score > keyword_dict[keyword][1]:
                        keyword_dict[keyword] = (intent, score)

        # Sort keywords by score in descending order
        ranked_keywords = sorted(
            [
                (kw, intent_score[0], intent_score[1])
                for kw, intent_score in keyword_dict.items()
            ],
            key=lambda x: x[2],
            reverse=True,
        )

        return ranked_keywords[:top_n] if top_n else ranked_keywords

    def extract_competitors_keywords(self) -> dict:
        print(colored("\nStarting SERP analysis...", "cyan"))
        business_profile = self.text_sanitizer_service.summarize_business_profile(
            self.business_profile
        )
        company_name = business_profile.get("name")
        industry = business_profile.get("industry")
        locations = [business_profile.get("location")]
        seed_keywords = business_profile.get("seed_keywords", [])

        seed_keywords = [
            seed_keywords[0]
        ]  # TODO: remove this in production or set a proper limiter

        if not company_name or not industry or not seed_keywords:
            raise ValueError(
                "Missing essential business profile data (name, industry, or seed keywords)."
            )

        serp_analysis = self.serp_service.analyze_search_intents(
            seed_keywords, locations
        )

        return serp_analysis, company_name, industry, locations, seed_keywords

    def suggest_queries_for_keyword(self, keyword: str) -> List[str]:
        keywords = [keyword]

        url = self.setting_service.seo_suggestion_services["google_firefox"] + keyword
        response = requests.get(url, verify=False)
        suggestions = json.loads(response.text)

        for word in suggestions[1]:
            keywords.append(word)

        # functions for getting more kws, cleaning and search volume
        self.prefixes(keyword, keywords)
        self.suffixes(keyword, keywords)
        self.numbers(keyword, keywords)
        self.get_more(keyword, keywords)

        return self.clean_and_save_keywords(keywords, keyword)

    def prefixes(self, keyword, keywords):
        # we can add more suffixes tailored to the company or type of search we are looking. E.g: food delivery, delivery,etc
        prefixes = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "y",
            "x",
            "y",
            "z",
            "how",
            "which",
            "why",
            "where",
            "who",
            "when",
            "are",
            "what",
        ]

        for prefix in prefixes:
            url = (
                self.setting_service.seo_suggestion_services["google_firefox"]
                + prefix
                + " "
                + keyword
            )
            response = requests.get(url, verify=False)
            suggestions = json.loads(response.text)

            kws = suggestions[1]
            length = len(kws)

            for n in range(length):
                keywords.append(kws[n])

    def suffixes(self, keyword, keywords):
        # we can add more suffixes tailored to the company or type of search we are looking. E.g: food delivery, delivery,etc
        suffixes = [
            "a",
            "b",
            "c",
            "d",
            "e",
            "f",
            "g",
            "h",
            "i",
            "j",
            "k",
            "l",
            "m",
            "n",
            "o",
            "p",
            "q",
            "r",
            "s",
            "t",
            "u",
            "v",
            "y",
            "x",
            "y",
            "z",
            "like",
            "for",
            "without",
            "with",
            "versus",
            "vs",
            "to",
            "near",
            "except",
            "has",
        ]

        for suffix in suffixes:
            url = (
                self.setting_service.seo_suggestion_services["google_firefox"]
                + keyword
                + " "
                + suffix
            )
            response = requests.get(url, verify=False)
            suggestions = json.loads(response.text)

            kws = suggestions[1]
            length = len(kws)

            for n in range(length):
                keywords.append(kws[n])

    def numbers(self, keyword, keywords):
        # we can add more numbers
        for num in range(0, 10):
            url = (
                self.setting_service.seo_suggestion_services["google_firefox"]
                + keyword
                + " "
                + str(num)
            )
            response = requests.get(url, verify=False)
            try:
                suggestions = json.loads(response.text)
            except json.JSONDecodeError:
                print("Failed to decode JSON. Response was:", response)
                return []

            kws = suggestions[1]
            length = len(kws)

            for n in range(length):
                keywords.append(kws[n])

    def get_more(self, keyword, keywords):
        for i in keywords:
            url = self.setting_service.seo_suggestion_services["google_firefox"] + i
            response = requests.get(url, verify=False)
            suggestions = json.loads(response.text)

            keywords2 = suggestions[1]
            length = len(keywords2)

            for n in range(length):
                keywords.append(keywords2[n])

            if (
                len(keywords) >= 1000
            ):  # we can increase this number if we want more keywords
                break

    def clean_and_save_keywords(self, keywords: List[str], keyword: str) -> str:
        if not isinstance(keyword, str):
            raise ValueError(
                f"Expected a string for 'keyword', but got {type(keyword).__name__}"
            )

        keywords = list(dict.fromkeys(keywords))
        filtered_keywords = [
            word for word in keywords if all(val in word for val in keyword.split(" "))
        ]

        df = pd.DataFrame(filtered_keywords, columns=["Keywords"])

        output_dir = os.path.join(os.getcwd(), "storage", "keywords")
        os.makedirs(output_dir, exist_ok=True)

        output_file = os.path.join(output_dir, f"{keyword}-keywords.csv")
        df.to_csv(output_file, index=False)

        print(colored(f"\nKeywords saved to: {output_file}", "green"))

        # this is just in case we want to create an API response
        json_hist = df.to_json(orient="columns")
        queries = json.loads(json_hist).get("Keywords")

        return queries.items()

    def validate_suggested_queries(
        self, queries: List[Tuple[str, str, float]]
    ) -> List[str]:
        # TODO: Implement validation logic
        return queries
